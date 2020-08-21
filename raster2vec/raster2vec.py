# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Raster2Vec
                                 A QGIS plugin
 This plugin takes a raster image, and converts it as a vectorial image
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-06-29
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Paul-Alexandre Nasr
        email                : paul_alexandre99@yahoo.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
from qgis.core import *

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .raster2vec_dialog import Raster2VecDialog
import os.path
import numpy as np
from osgeo import gdal
import sys

sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "./parallel-cut-pursuit/python/wrappers"))
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "./multilabel-potrace/python/wrappers"))
#sys.path.append('./parallel-cut-pursuit-master/python/wrappers')
#sys.path.append('./multilabel-potrace-master/python/wrappers')

from cp_kmpp_d0_dist import cp_kmpp_d0_dist
from multilabel_potrace_shp import multilabel_potrace_shp
#from cp_pfdr_d1_ql1b import cp_pfdr_d1_ql1b 
#from cp_pfdr_d1_lsx import cp_pfdr_d1_lsx 

class Raster2Vec:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Raster2Vec_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Raster to Vector')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Raster2Vec', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/raster2vec/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Raster to Vector'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Raster to Vector'),
                action)
            self.iface.removeToolBarIcon(action)


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            # Code below is read when the plugin is launched for the first time
            self.first_start = False
            self.dlg = Raster2VecDialog()
            self.dlg.open_output_vector.clicked.connect(self.select_output_file)
            self.dlg.open_input_raster.clicked.connect(self.select_output_file)
		
        alllayers = QgsProject.instance().mapLayers().values()
#        alllayers.sort()
        allrasterlayers = []
        for elt in alllayers:
            if elt.type() == QgsMapLayer.RasterLayer:
                allrasterlayers.append(elt)
        allrasterlayers_paths = [layer.source() for layer in allrasterlayers]
        
        self.dlg.input_raster2.clear()
        self.dlg.raster_band.clear()
        self.dlg.input_weight_raster2.clear()
        self.dlg.weight_raster_band.clear()
        self.dlg.line_weight_value.clear()
        self.dlg.line_output_vector.clear()
        self.dlg.line_output_layer_name.clear()
        
        self.dlg.input_raster2.addItems([layer.name() for layer in allrasterlayers])
        self.dlg.input_weight_raster2.addItems([layer.name() for layer in allrasterlayers])
        
#        raster_tri = sorted(allrasterlayers)
        allrasterlayers.sort
        print(allrasterlayers)
        print([elt.name() for elt in allrasterlayers])
        
        def layer_field_raster():
            """
            Adds the band values of the raster selected in Input Raster
            """
            # Identify selected layer by its index
            selectedLayerIndex = self.dlg.input_raster2.currentIndex()
            selectedLayer = allrasterlayers[selectedLayerIndex]
#            print(selectedLayer.name())
            # Counts the number of bands of the current layer, then adds the bands on the raster band comboBox
            amount_of_bands = selectedLayer.bandCount()
            self.dlg.raster_band.clear()
            self.dlg.raster_band.addItems([selectedLayer.bandName(i) for i in range(amount_of_bands)])
    
        def layer_field_wraster():
            """
            Adds the band values of the raster selected in Weight Raster
            """
            # Same comments as above
            selectedLayerIndex = self.dlg.input_weight_raster2.currentIndex()
            selectedLayer = allrasterlayers[selectedLayerIndex]
            amount_of_bands = selectedLayer.bandCount()
            self.dlg.weight_raster_band.clear()            
            self.dlg.weight_raster_band.addItems([selectedLayer.bandName(i) for i in range(amount_of_bands)])

        # Everytime the user selects a raster, the band values will change
        self.dlg.input_raster2.currentIndexChanged.connect(layer_field_raster)
        self.dlg.input_weight_raster2.currentIndexChanged.connect(layer_field_wraster)
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and substitute with your code.
            weight = self.dlg.line_weight_value.text()
            output_vector = self.dlg.line_output_vector.text()
            output_layer_name = self.dlg.line_output_layer_name.text()
            
            if weight == '0' or weight is None:
                print(weight)
                weight = self.dlg.line_weight_value.setText('1')
                weight = float(self.dlg.line_weight_value.text())
            
            print(weight)
            
#            print(alllayers)
#            print(allrasterlayers)
#            print(allrasterlayers_paths)
            selectedLayerIndex = self.dlg.input_raster2.currentIndex()
#            print(selectedLayerIndex)
            selectedLayer = allrasterlayers[selectedLayerIndex]
            current_path_raster = selectedLayer.source()
            selectedLayer_width = selectedLayer.width()
            selectedLayer_height = selectedLayer.height()
            selectedLayer_crs = selectedLayer.crs()
#            print("CRS: ", selectedLayer_crs)
            
            selectedBandIndex = self.dlg.raster_band.currentIndex()
            print("Band number: ", selectedBandIndex)
            
#            selectedLayerIndex2 = self.dlg.input_weight_raster2.currentIndex()
##            print(selectedLayerIndex)
#            selectedLayer2 = allrasterlayers[selectedLayerIndex2]
#            current_path_wraster = selectedLayer2.source()
#            selectedLayer2_width = selectedLayer2.width()
#            selectedLayer2_height = selectedLayer2.height()
#            selectedLayer2_crs = selectedLayer2.crs()
            
            shplayer = QgsVectorLayer("Polygon", "temporary_polygon", "memory")
            shplayer.setCrs(selectedLayer_crs)
            provider = shplayer.dataProvider()
#            shplayer.startEditing()
            
            provider.addAttributes([QgsField("id", QVariant.Int), QgsField("value", QVariant.Double)])
            
            ext = selectedLayer.extent()
            x_min = ext.xMinimum()
            x_max = ext.xMaximum()
            y_min = ext.yMinimum()
            y_max = ext.yMaximum()
            print("Coordinates: ", x_min, x_max, y_min, y_max)
            
            poly = QgsFeature()
                        
            pts = [QgsPointXY(x_min, y_min), QgsPointXY(x_min, y_max), QgsPointXY(x_max, y_max), QgsPointXY(x_max, y_min)]
#            poly.setGeometry(QgsGeometry.fromPolygonXY([pts]))
#            poly.setAttributes([0, 3])
            
            poly2 = QgsFeature()
                        
            pts = [QgsPointXY(x_min, y_min), QgsPointXY(x_min, y_max), QgsPointXY(x_max, y_max)]
#            poly2.setGeometry(QgsGeometry.fromPolygonXY([pts]))
#            poly2.setAttributes([0, 3])
#            provider.addFeatures([poly])
#            provider.addFeatures([np.nan])
#            provider.addFeatures([poly2])
             
            for f in shplayer.getFeatures():
                print("Feature:", f.id(), f.attributes(), f.geometry().asPolygon())
            
            dataset = gdal.Open(current_path_raster)
            band1 = np.array(dataset.GetRasterBand(selectedBandIndex + 1).ReadAsArray())
#            band2 = np.array(dataset.GetRasterBand(2).ReadAsArray())
#            band3 = np.array(dataset.GetRasterBand(3).ReadAsArray())
            moy = np.nanmean(band1)
            avrg = np.average(band1)
            number_rows = band1.shape[0]
            number_columns = band1.shape[1]
            
            dataset = gdal.Open(current_path_wraster)
            band1_2 = np.array(dataset.GetRasterBand(selectedBandIndex + 1).ReadAsArray())
            avrg = np.average(band1_2)
            number_rows2 = band1_2.shape[0]
            number_columns2 = band1_2.shape[1]
            
#            print(selectedLayer.name())
            print(band1)
#            print(band1_2)
            print(band1.dtype)
            print(band1.data.contiguous)
#            print(band2)
#            print(band3)
            print(moy)
            print(avrg)
            print((band1==band1).all())
            print("Number of rows for raster: ", number_rows)
            print("Number of columns for raster: ", number_columns)
            print("Number of rows for weight raster: ", number_rows2)
            print("Number of columns for weight raster", number_columns2)
            
            #Ci-dessous le code à tester du grid, après résoudre le problème de la Bounding Box
            
            def compute_grid(lin, col):
                """
                Compute the Astar representation of a 8-neighborhood,grid graph
                INPUT:
                lin, col = size of the grid
                OUTPUT:
                first_edge, adj_vertices = Astar graph
                edgeweight = associated edge weight
                """
                A = np.arange(lin*col).reshape(lin,col)
                # down arrow
                source  = A[:-1,:]
                target   = A[1:,:]
                down = np.stack((source.flatten(), target.flatten()),0)
                # right arrow
                source  = A[:,:-1]
                target  = A[:,1:]
                right = np.stack((source.flatten(), target.flatten()),0)
                # down-right arrow
                source = A[:-1,:-1]
                target  = A[1:,1:]
                down_right = np.stack((source.flatten(), target.flatten()),0)
                # up-right arrow
                source = A[1:,:-1]
                target = A[:-1,1:]
                up_right = np.stack((source.flatten(), target.flatten()),0)
                #mergeing
                T = np.concatenate((right, down, down_right, up_right), axis=1)
                #weighting, see "Computing Geodesics and Minimal Surfaces via Graph Cuts", Boyjob & Kolmogorov 2003
                weights = np.ones((T.shape[1],),dtype='f4')
                weights[int(T.shape[1]/2):] = 1/np.sqrt(2)
                #formatting
                reorder = T[0,:].argsort()
                T = T[:,reorder]
                weights = weights[reorder]
                v = np.concatenate(([0],np.where((T[0,:-1]==T[0,1:])==False)[0]+1,[T.shape[1], T.shape[1]]))
                first_edge = np.array(v, dtype='uint32')
                adj_vertices = np.array(T[1,:],dtype='uint32') 
                return first_edge, adj_vertices, weights
            #input raster
            obs = band1
            #bounding box
#            min_x = 0	
#            min_y = 0
#            max_x = 10
#            max_y = 10		
            true_size_x = x_max-x_min
            true_size_y = y_max-y_min
            print(true_size_x)
            print(true_size_y)
            lin = obs.shape[0]
            col = obs.shape[1]
            print("Ligne: ", lin)
            print("Colonne: ", col)
            delta_x = true_size_x/col
            delta_y = true_size_y/lin
            first_edge, adj_vertices, edg_weights = compute_grid(lin, col)
            edg_weights = edg_weights.astype(obs.dtype)
            
            Comp, rX, dump = cp_kmpp_d0_dist(1, obs.flatten(), first_edge, adj_vertices, edge_weights = edg_weights*0.05)
            print('cp results')
            #print(Comp.reshape(obs.shape))
            bb, nparts, npoints, parts, points = multilabel_potrace_shp(col, lin, Comp, rX.shape[1])
            print('potrace results')
            #print(bb)
            #print(nparts)
            #print(npoints)
            #print(parts)
#            print(points)
            
            n_comp = nparts.shape[0]
            print("n_comp: ", n_comp)
            index_parts = 0
            index_points = 0
            polygons = []
            for i_comp in range(n_comp):
#                print("Valeur i_comp", i_comp)
#                print("Valeur rX[i_comp]: ", rX[0][i_comp])
                poly = QgsFeature()
                poly.setAttributes([i_comp, rX[0][i_comp]])
                vertices = [[]]   #Liste de liste de QgsPointXY
                pivots = np.append(index_points +parts[index_parts:index_parts + nparts[i_comp]], index_points + npoints[i_comp])
                index_parts = index_parts + nparts[i_comp]
                index_points = index_points + npoints[i_comp]
                for i_parts in range(nparts[i_comp]):   #Créer une polyligne, utiliser add
                    contour = range(pivots[i_parts],pivots[i_parts+1])
                    vertices.append([QgsPointXY((min_x + points[0,i] * delta_x), (min_y + points[1,i] * delta_y)) for i in contour]) #replace with QGIS Points; ajouter un np.nan à la fin de la ligne
#                    break
                poly.setGeometry(QgsGeometry.fromPolygonXY(vertices))
                provider.addFeatures([poly])
                
#            print(vertices)
            # Commit changes
            shplayer.updateFields()
            shplayer.updateExtents()
            # Show in project
            QgsProject.instance().addMapLayer(shplayer)
            
            print("No. fields:", len(provider.fields()))
            print("No. features:", provider.featureCount())
            e = shplayer.extent()
            print("Extent:", e.xMinimum(), e.yMinimum(), e.xMaximum(), e.yMaximum())

            coords_list = []

#            def draw_polygons(polygons):
#                c = 0
#                x_total = []
#                y_total = []
#                for i_poly in range(len(polygons)):
#                    for i_ring in range(len(polygons[i_poly])):
##                        print(min_y)
##                        print(delta_y)
#
#                        x = [max_y-(min_y + p[0] * delta_y) for p in polygons[i_poly][i_ring]]        # Translation dilatation, en utilisant les lignes 98 et 99
#                        y = [max_x - (min_x + p[1] * delta_x) for p in polygons[i_poly][i_ring]]
#                        x_total = x_total + x + [np.nan]      #Le np.nan indique une discontinuité
#                        y_total = y_total + y + [np.nan]
#                        
##                        print(x_total)
##                        print(y_total)
#                        
#                        
#                        coords_list.append(QgsPointXY(x_total[c], y_total[c]))
#                        c += 1
                
#                for e in x_total:
                    
#                print(x_total)
#                print(y_total)
                        
            draw_polygons(polygons)
            print("Liste des points limite: ", coords_list)
            poly.setGeometry(QgsGeometry.fromPolylineXY(coords_list))
            provider.addFeatures([poly])

            #print("Dimension of the selected raster: ", current_layer.width(), current_layer.height())
#            self.iface.messageBar().pushMessage("Success", "Output file written at " + filename, level=Qgis.Success, duration=3)
            pass

    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(self.dlg, "Select output file: ", "", 'Image file (*.jpg, *.png, *.tif)')
        self.dlg.lineEdit.setText(filename)