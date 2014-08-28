'''
Created on Aug 17, 2014

@author: Leon
'''
"""
import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import maya.cmds as mc
"""
"""
# import shaders
filepath = mc.fileDialog2(fm=1, cap='Choose advanced shader file', ff='mathilda_adv_shaders.ma (shaders_v004.ma)')
if filepath is None:
    mc.error('Shader file not provided.')
mc.file(filepath[0], i=True, ns='SHADERS')

# create shaders layer if it does not exist
allLayers = mc.ls(type='renderLayer')
if 'shaders_layer' not in allLayers:
    geoGrp = ['RIG:GEO:CT_geo_grp', 'RIG:FACE:CT_mouth_geo_grp']
    layer = mc.createRenderLayer(geoGrp, n='shaders_layer')
    mc.editRenderLayerGlobals(crl=layer)
else:
    layer = 'shaders_layer'
    mc.editRenderLayerGlobals(crl=layer)
    
# assign shaders
shd_dict = {u'_defaultMat7': [u'NEWGEO:LT_jacketPatch_geoShapeDeformed',
                   u'NEWGEO:LT_jacketPocket_geoShapeDeformed',
                   u'NEWGEO:RT_jacketPocket_geoShapeDeformed',
                   u'NEWGEO:CT_jacket_geoShapeDeformed'],
 u'anisotropic1SG': [u'NEWGEO:CT_pendant_geoShapeDeformed'],
 u'anisotropic_ziperSG': [u'NEWGEO:RT_zipper_geoShapeDeformed',
                          u'NEWGEO:LT_zipper_geoShapeDeformed',
                          u'GEO:LT_shoe_geo.f[160:287]',
                          u'GEO:RT_shoe_geo.f[160:287]',
                          u'NEWGEO:CT_pantsZipper_geoShapeDeformed'],
 u'blinn1SG': [u'GEO:LT_shoe_geo.f[288:289]',
               u'GEO:LT_shoe_geo.f[308:309]',
               u'GEO:LT_shoe_geo.f[345]',
               u'GEO:LT_shoe_geo.f[348]',
               u'GEO:LT_shoe_geo.f[353]',
               u'GEO:LT_shoe_geo.f[355]',
               u'GEO:LT_shoe_geo.f[357]',
               u'GEO:LT_shoe_geo.f[359]',
               u'GEO:LT_shoe_geo.f[361]',
               u'GEO:LT_shoe_geo.f[374]',
               u'GEO:LT_shoe_geo.f[376]',
               u'GEO:LT_shoe_geo.f[385]',
               u'GEO:LT_shoe_geo.f[388]',
               u'GEO:LT_shoe_geo.f[403]',
               u'GEO:LT_shoe_geo.f[406]',
               u'GEO:LT_shoe_geo.f[409]',
               u'GEO:LT_shoe_geo.f[415]',
               u'GEO:LT_shoe_geo.f[422]',
               u'GEO:LT_shoe_geo.f[425]',
               u'GEO:LT_shoe_geo.f[428]',
               u'GEO:LT_shoe_geo.f[435]',
               u'GEO:LT_shoe_geo.f[438]',
               u'GEO:LT_shoe_geo.f[441]',
               u'GEO:LT_shoe_geo.f[444]',
               u'GEO:LT_shoe_geo.f[448]',
               u'GEO:LT_shoe_geo.f[477:563]',
               u'GEO:LT_shoe_geo.f[566:567]',
               u'GEO:LT_shoe_geo.f[603:729]',
               u'GEO:LT_shoe_geo.f[758:783]',
               u'GEO:LT_shoe_geo.f[789]',
               u'GEO:LT_shoe_geo.f[792]',
               u'GEO:LT_shoe_geo.f[795:798]',
               u'GEO:LT_shoe_geo.f[801]',
               u'GEO:RT_shoe_geo.f[288:289]',
               u'GEO:RT_shoe_geo.f[308:309]',
               u'GEO:RT_shoe_geo.f[345]',
               u'GEO:RT_shoe_geo.f[348]',
               u'GEO:RT_shoe_geo.f[353]',
               u'GEO:RT_shoe_geo.f[355]',
               u'GEO:RT_shoe_geo.f[357]',
               u'GEO:RT_shoe_geo.f[359]',
               u'GEO:RT_shoe_geo.f[361]',
               u'GEO:RT_shoe_geo.f[374]',
               u'GEO:RT_shoe_geo.f[376]',
               u'GEO:RT_shoe_geo.f[385]',
               u'GEO:RT_shoe_geo.f[388]',
               u'GEO:RT_shoe_geo.f[403]',
               u'GEO:RT_shoe_geo.f[406]',
               u'GEO:RT_shoe_geo.f[409]',
               u'GEO:RT_shoe_geo.f[415]',
               u'GEO:RT_shoe_geo.f[422]',
               u'GEO:RT_shoe_geo.f[425]',
               u'GEO:RT_shoe_geo.f[428]',
               u'GEO:RT_shoe_geo.f[435]',
               u'GEO:RT_shoe_geo.f[438]',
               u'GEO:RT_shoe_geo.f[441]',
               u'GEO:RT_shoe_geo.f[444]',
               u'GEO:RT_shoe_geo.f[448]',
               u'GEO:RT_shoe_geo.f[477:563]',
               u'GEO:RT_shoe_geo.f[566:567]',
               u'GEO:RT_shoe_geo.f[603:729]',
               u'GEO:RT_shoe_geo.f[758:783]',
               u'GEO:RT_shoe_geo.f[789]',
               u'GEO:RT_shoe_geo.f[792]',
               u'GEO:RT_shoe_geo.f[795:798]',
               u'GEO:RT_shoe_geo.f[801]'],
 u'blinn_shoesSG': [u'GEO:LT_shoe_geo.f[0:159]',
                    u'GEO:LT_shoe_geo.f[290:307]',
                    u'GEO:LT_shoe_geo.f[310:344]',
                    u'GEO:LT_shoe_geo.f[346:347]',
                    u'GEO:LT_shoe_geo.f[349:352]',
                    u'GEO:LT_shoe_geo.f[354]',
                    u'GEO:LT_shoe_geo.f[356]',
                    u'GEO:LT_shoe_geo.f[358]',
                    u'GEO:LT_shoe_geo.f[360]',
                    u'GEO:LT_shoe_geo.f[362:373]',
                    u'GEO:LT_shoe_geo.f[375]',
                    u'GEO:LT_shoe_geo.f[377:384]',
                    u'GEO:LT_shoe_geo.f[386:387]',
                    u'GEO:LT_shoe_geo.f[389:402]',
                    u'GEO:LT_shoe_geo.f[404:405]',
                    u'GEO:LT_shoe_geo.f[407:408]',
                    u'GEO:LT_shoe_geo.f[410:414]',
                    u'GEO:LT_shoe_geo.f[416:421]',
                    u'GEO:LT_shoe_geo.f[423:424]',
                    u'GEO:LT_shoe_geo.f[426:427]',
                    u'GEO:LT_shoe_geo.f[429:434]',
                    u'GEO:LT_shoe_geo.f[436:437]',
                    u'GEO:LT_shoe_geo.f[439:440]',
                    u'GEO:LT_shoe_geo.f[442:443]',
                    u'GEO:LT_shoe_geo.f[445:447]',
                    u'GEO:LT_shoe_geo.f[449:476]',
                    u'GEO:LT_shoe_geo.f[564:565]',
                    u'GEO:LT_shoe_geo.f[568:602]',
                    u'GEO:LT_shoe_geo.f[730:757]',
                    u'GEO:LT_shoe_geo.f[784:788]',
                    u'GEO:LT_shoe_geo.f[790:791]',
                    u'GEO:LT_shoe_geo.f[793:794]',
                    u'GEO:LT_shoe_geo.f[799:800]',
                    u'GEO:LT_shoe_geo.f[802:1047]',
                    u'GEO:RT_shoe_geo.f[0:159]',
                    u'GEO:RT_shoe_geo.f[290:307]',
                    u'GEO:RT_shoe_geo.f[310:344]',
                    u'GEO:RT_shoe_geo.f[346:347]',
                    u'GEO:RT_shoe_geo.f[349:352]',
                    u'GEO:RT_shoe_geo.f[354]',
                    u'GEO:RT_shoe_geo.f[356]',
                    u'GEO:RT_shoe_geo.f[358]',
                    u'GEO:RT_shoe_geo.f[360]',
                    u'GEO:RT_shoe_geo.f[362:373]',
                    u'GEO:RT_shoe_geo.f[375]',
                    u'GEO:RT_shoe_geo.f[377:384]',
                    u'GEO:RT_shoe_geo.f[386:387]',
                    u'GEO:RT_shoe_geo.f[389:402]',
                    u'GEO:RT_shoe_geo.f[404:405]',
                    u'GEO:RT_shoe_geo.f[407:408]',
                    u'GEO:RT_shoe_geo.f[410:414]',
                    u'GEO:RT_shoe_geo.f[416:421]',
                    u'GEO:RT_shoe_geo.f[423:424]',
                    u'GEO:RT_shoe_geo.f[426:427]',
                    u'GEO:RT_shoe_geo.f[429:434]',
                    u'GEO:RT_shoe_geo.f[436:437]',
                    u'GEO:RT_shoe_geo.f[439:440]',
                    u'GEO:RT_shoe_geo.f[442:443]',
                    u'GEO:RT_shoe_geo.f[445:447]',
                    u'GEO:RT_shoe_geo.f[449:476]',
                    u'GEO:RT_shoe_geo.f[564:565]',
                    u'GEO:RT_shoe_geo.f[568:602]',
                    u'GEO:RT_shoe_geo.f[730:757]',
                    u'GEO:RT_shoe_geo.f[784:788]',
                    u'GEO:RT_shoe_geo.f[790:791]',
                    u'GEO:RT_shoe_geo.f[793:794]',
                    u'GEO:RT_shoe_geo.f[799:800]',
                    u'GEO:RT_shoe_geo.f[802:1047]'],
 u'lambert5SG': [u'NEWGEO:RT_sock_geoShapeDeformed',
                 u'NEWGEO:LT_sock_geoShapeDeformed',
                 u'GEO:CT_pantsString_geo.f[0:367]'],
 u'lambert_IrisSG': [u'FACE:RT_eyeIris_geoShape',
                     u'GEO:LT_eyeIris_geoShapeDeformed',
                     u'GEO:RT_eyeIris_geoShapeDeformed',
                     u'FACE:LT_eyeIris_geoShape'],
 u'lambert_pantsSG': [u'NEWGEO:CT_pants_geoShapeDeformed',
                      u'NEWGEO:CT_pantsPocket_geoShapeDeformed'],
 u'lambert_vestSG': [u'NEWGEO:CT_shirt_geoShapeDeformed'],
 u'mia_material_x_passes1SG': [u'GEO:RT_eyeball_geoShapeDeformed',
                               u'GEO:LT_eyeball_geoShapeDeformed'],
 u'misss_fast_skin_maya1SG': [u'GEO:CT_body_geo.f[0:3541]'],
 u'misss_fast_skin_maya2SG': [u'FACE:CT_tongue_geoShape',
                              u'FACE:CT_upperGums_geoShape',
                              u'FACE:CT_lowerGums_geoShape'],
 u'misss_fast_skin_maya3SG': [u'FACE:CT_upperTeeth_geoShape',
                              u'FACE:CT_lowerTeeth_geoShape'],
 u'misss_fast_skin_maya4SG': [u'GEO:CT_body_geo.f[3542:8037]'],
 u'phong1SG': [u'GEO:CT_pantsString_geo.f[368:655]'],
 u'surfaceShader1SG': [u'GEO:RT_eyelashes_geoShape',
                       u'FACE:LT_eyelashes_geoShape',
                       u'FACE:RT_eyelashes_geoShape',
                       u'GEO:LT_eyelashes_geoShape']}

for shdGrp, objs in shd_dict.items():
    # shdGrp should be in SHADERS namespace
    shdGrpNS = 'SHADERS:'+shdGrp
    # objs should be in RIG namespace
    objsNS = ['RIG:'+name for name in objs]
    mc.sets(objsNS, e=True, forceElement=shdGrpNS)
    
"""

"""
pm.ls(type='renderLayer')
# transfer SGs on masterLayer first
masterLyr = pm.PyNode('defaultRenderLayer')
masterSGs = getSGsOnLayer(masterLyr)
masterSGs = filter(lambda sg: 'SHADERS' in sg.namespaceList(), masterSGs)
for sg in masterSGs:
    transferSG(sg, 'SHADERS', 'RIG')

advLyr = pm.PyNode('SHADERS'+':'+'advanced_shading')
advSGs = getSGsOnLayer(advLyr)
advSGs = filter(lambda sg: 'SHADERS' in sg.namespaceList(), advSGs)
for sg in advSGs:
    transferSG(sg, 'SHADERS', 'RIG')
"""
import pymel.core as pm
import sys

def getSGsOnLayer(layer):
    '''
    return list of sgs connected to layer
    '''
    returnSGs = []
    allSGs = pm.ls(type='shadingEngine')
    for sg in allSGs:
        renderLyrs = sg.dagSetMembers.inputs()
        if layer in renderLyrs:
            returnSGs.append(sg)
    return returnSGs

def transferSG(sg, srcNS, destNS, srcLyr, destLyr):
    pm.editRenderLayerGlobals(crl=srcLyr)
    srcObjs = pm.sets(sg, q=True)
    pm.editRenderLayerGlobals(crl=destLyr)
    for srcObj in srcObjs:
        destName = srcObj.replace(srcNS, destNS)
        try:
            destObj = pm.PyNode(destName)
            # print 'assign: ' + destObj
            pm.sets(sg, e=True, fe=destObj)
        except pm.MayaObjectError as e:
            destName = destName.replace('GEO', 'NEWGEO')
            destObj = pm.PyNode(destName)
            # print 'assign: ' + destObj
            pm.sets(sg, e=True, fe=destObj)
        except:
            print "Unexpected error...", sys.exc_info()[0]

def removeAdvancedShaders():
    '''
    '''
    # remove layer
    try:
        layer = pm.nt.RenderLayer('advanced_shading')
        pm.editRenderLayerGlobals(crl='defaultRenderLayer')
        pm.delete(layer)
    except pm.MayaObjectError:
        pass
        
    # remove imported namespace
    try:
        pm.namespace(dnc=True, rm='SHADERS')
    except RuntimeError:
        pass

def loadAdvancedShaders():
    '''
    '''
    # check if shader already loaded
    # check SHADER namespace or shading_layer
    removeAdvancedShaders()
    # delete if already loaded
    
    # load shader file
    # import shaders
    filepath = pm.fileDialog2(fm=1, cap='Choose advanced shader file', ff='mathilda_advanced_shaders.ma (mathilda_advanced_shaders.ma)')
    if filepath is None:
        pm.error('Shader file not provided.')
    pm.importFile(filepath[0], i=True, ns='SHADERS')
    
    # create renderlayer
    allGeoShapes = []
    bodyGeoGrp = pm.PyNode('RIG:GEO'+':'+'CT_geo_grp')
    faceGeoGrp = pm.PyNode('RIG:FACE:CT_mouth_geo_grp')
    for shape in bodyGeoGrp.getChildren(ad=True, s=True):
        if 'simple' not in shape.name():
            allGeoShapes.append(shape)
    for shape in faceGeoGrp.getChildren(ad=True, s=True):
        allGeoShapes.append(shape)
    allGeoShapes.append('RIG:frontHair_pfx')
    allGeoShapes.append('RIG:backHair_pfx')
    layer = pm.createRenderLayer(allGeoShapes, n='advanced_shading')
    pm.editRenderLayerGlobals(crl=layer)
    
    # get all advanced shaders
    allSGs = pm.ls(type='shadingEngine')
    advSGs = filter(lambda sg: 'SHADERS' in sg.namespaceList(), allSGs)
    
    # transfer SGs on masterLayer first
    masterLyr = pm.PyNode('defaultRenderLayer')
    for sg in advSGs:
        transferSG(sg, 'SHADERS'+':', 'RIG:', masterLyr, layer)
        
    # transfer SGs on advanced_shading
    # this should override masterLayer
    advLyr = pm.PyNode('SHADERS'+':'+'advanced_shading')
    for sg in advSGs:
        transferSG(sg, 'SHADERS'+':', 'RIG:', advLyr, layer)
        
    # clean up imported data
    importedGeo = pm.PyNode('SHADERS'+':'+'CT_shaders_geo_grp')
    pm.delete(importedGeo)
    pm.delete(advLyr)