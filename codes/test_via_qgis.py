from PyQt5.QtCore import QCoreApplication, QVariant
from qgis.core import  (QgsProcessing, 
                        QgsField, 
                        QgsFields, 
                        QgsProcessingException, 
                        QgsProcessingAlgorithm, 
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterFeatureSink,
                        QgsProcessingParameterField,
                        QgsVectorLayer,
                        )

import processing
import os

path_to_raster = "D:/ENSG/A_New_Era_G2/A_Stages/Projet_Stage/codes/NDVI.tif"
rlayer = QgsRasterLayer(path_to_raster, "NDVI")
if not rlayer.isValid():
    print("Layer failed to load")
else:
    print("Layer loaded successfuly")
    
iface.addRasterLayer(path_to_raster, "NDVI")

pixelSizeX = rlayer.rasterUnitsPerPixelX()
pixelSizeY = rlayer.rasterUnitsPerPixelY()
crs = rlayer.crs().authid()

print(pixelSizeX, pixelSizeY, crs)

writer = QgsVectorFileWriter("D:/ENSG/A_New_Era_G2/A_Stages/Projet_Stage/codes/test.shp",
                             "Premier_shape",
                             fields,
                             QgsWkbTypes.Point, #### instead of QGis.WKBPoint
                             QgsCoordinateReferenceSystem(), #### instead of None
                             "ESRI Shapefile")

qgs.exitQgis()