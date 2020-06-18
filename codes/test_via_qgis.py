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
raster_width = rlayer.width()
raster_height = rlayer.height()
crs = rlayer.crs().authid()

print(raster_width, raster_height, crs)

shplayer = QgsVectorLayer("D:/ENSG/A_New_Era_G2/A_Stages/Projet_Stage/codes/shp_modifies/COMMUNE_Chelles.shp", "testlayer_shp", "ogr")
pr = shplayer.dataProvider()
if not shplayer.isValid():
    print("Layer failed to load")
else:
    print("Layer loaded successfuly")
    
poly = QgsFeature()
pts = [QgsPointXY(0, 0), QgsPointXY(0, raster_height), QgsPointXY(raster_width, raster_height), QgsPointXY(raster_width, 0)]
poly.setGeometry(QgsGeometry.fromPolygonXY([pts]))
pr.addFeatures([poly])
# Commit changes
shplayer.updateExtents()
# Show in project
QgsProject.instance().addMapLayer(shplayer)