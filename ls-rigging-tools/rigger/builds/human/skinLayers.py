'''
Created on Aug 29, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

from ngSkinTools.mllInterface import MllInterface

import rigger.utils.weighting.layer_weighting as layer_weighting
reload(layer_weighting)

import rigger.utils.weighting.loop_weighting as loop_weighting
reload(loop_weighting)

def layer_base(mll):
    '''
    '''
    mesh, skn = mll.getTargetInfo()
    layerId = mll.createLayer('Base', True)
    # pm.select(mesh)
    mll.setCurrentLayer(layerId)
    mel.ngAssignWeights(mesh, bnj=True, ij='CT__base_bnd', intensity=1.0)

def layer_brow(mll):
    '''
    '''
    mesh, skn = mll.getTargetInfo()
    mesh = pm.PyNode(mesh)
    jntInfs = [u'CT__brow_bnd',
            u'LT_in_brow_bnd',
            u'LT_mid_brow_bnd',
            u'LT_out_brow_bnd',
            u'LT_in_forehead_bnd',
            u'LT_out_forehead_bnd',
            u'LT__temple_bnd']
    periLocs = [u'RT_in_forehead_pLoc',
                u'LT_in_forehead_pLoc',
                u'LT_out_forehead_pLoc',
                u'LT__temple_pLoc',
                u'LT_out_brow_pLoc',
                u'LT_mid_brow_pLoc',
                u'LT_in_brow_pLoc',
                u'CT__brow_pLoc',
                u'RT_in_brow_pLoc']
    inMaskInfsGrp = layer_weighting.addPerimeterBndSystem(mesh, periLocs, 
                                                          vecScale=1.0, suffix='_in')
    inMaskInfs = inMaskInfsGrp.getChildren(ad=True, type='joint')
    inMaskInfs = [inf.name() for inf in inMaskInfs]
    outMaskInfsGrp = layer_weighting.addPerimeterBndSystem(mesh, periLocs, 
                                                           vecScale=1.75, suffix='_out')
    outMaskInfs = outMaskInfsGrp.getChildren(ad=True, type='joint')
    outMaskInfs = [inf.name() for inf in outMaskInfs]
    
    layerInfo = 'Brow', jntInfs, inMaskInfs, outMaskInfs
    layerId = layer_weighting.buildLayer(mll, layerInfo)
    
    layer_weighting.mirrorLayer(mll, layerId)
    layer_weighting.smoothLayerMask(mll, layerId, [10.0, 20.0, 10.0])
    layer_weighting.relaxLayerInfluences(mll, layerId, 
                                         [41,23], [0.2333,0.0941])
    
    pm.delete(outMaskInfsGrp, inMaskInfsGrp)
    
def layer_mouthbag(mll):
    '''
    '''
    meshName, skn = mll.getTargetInfo()
    mesh = pm.PyNode(meshName)
    
    # this layer is currently hard-coded for mathilda
    # its simple to do by hand, but difficult to generalize and automate
    # TODO: need a way to get this from the UI or something
    mouthBagVertRingsIds = [1559, 1560, 1561, 1562, 1563, 1564, 1565, 1566, 1567, 1568, 1569, 1570, 1571, 1572, 1573, 1574, 1575, 1796, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3513]
    mouthBagVerts = [pm.PyNode('%s.vtx[%d]'%(mesh, vertId)) for vertId in mouthBagVertRingsIds]
    pm.select(mouthBagVerts, r=True)
    for i in range(5):
        mel.GrowPolygonSelectionRegion()
    allMouthBagVerts = pm.ls(sl=True, fl=True)
    allMouthBagVertsIds = [vert.index() for vert in allMouthBagVerts]
    
    # create layer
    layerId = mll.createLayer('MouthBag', True)
    mll.setCurrentLayer(layerId)
    
    # mask
    weightsList = []
    vertCount = mll.getVertCount()
    for vertId in range(vertCount):
        if vertId in allMouthBagVertsIds:
            weightsList.append(1)
        else:
            weightsList.append(0)
            
    mll.setLayerMask(layerId, weightsList)
    
    # weight between base and jaw
    # above 99.6 - weight to base
    # below - weight to jaw
    # weight all to base first
    mel.ngAssignWeights(meshName, bnj=True, ij='CT__base_bnd', intensity=1.0)

    weightsList = []
    for vertId in range(vertCount):
        vert = pm.PyNode('%s.vtx[%d]'%(meshName, vertId))
        if vert.getPosition()[1] < 99.6:
            weightsList.append(1)
        else:
            weightsList.append(0)
    infIdMap = layer_weighting.getInfluenceIdMap(mll, layerId)
    infId = infIdMap['CT__jaw_bnd'] 
    mll.setInfluenceWeights(layerId, infId, weightsList)
    
    layer_weighting.smoothLayerMask(mll, layerId, [3.0, 2.0, 1.0])
    layer_weighting.relaxLayerInfluences(mll, layerId, 
                                         [41,41,23], [0.2333,0.2333,0.0941])

def layer_nose(mll):
    '''
    '''
    meshName, skn = mll.getTargetInfo()
    mesh = pm.PyNode(meshName)
    jntInfs = [u'CT__noseBridge_bnd',
                u'CT__noseTip_bnd',
                u'LT__nostril_bnd']
    
    # helper bnds to get better influence weights
    inbtInfTargets = [[nt.Joint(u'CT__noseBridge_bnd'),
                   nt.Joint(u'CT__noseTip_bnd')],
                  [nt.Joint(u'CT__noseBridge_bnd'),
                   nt.Joint(u'LT__nostril_bnd')]]
    inbtInfGrp = layer_weighting.addInbetweenBndSystem(inbtInfTargets, mesh)
    inbtInfNames = [bnd.name() for bnd in inbtInfGrp.getChildren(type='joint')]
    jntInfs = jntInfs + inbtInfNames
    
    # helper bnds to get better mask weighting
    inbtBndTargetsMask = [[nt.Joint(u'CT__noseBridge_bnd'),
                       nt.Joint(u'LT_up_crease_bnd')],
                      [nt.Joint(u'CT__noseTip_bnd'),
                       nt.Joint(u'CT__philtrum_bnd')],
                      [nt.Joint(u'LT__nostril_bnd'),
                       nt.Joint(u'LT__philtrum_bnd')]]
    inbtBndMaskGrp = layer_weighting.addInbetweenBndSystem(inbtBndTargetsMask, mesh)
    inbtBndsMaskNames = [bnd.name() for bnd in inbtBndMaskGrp.getChildren(type='joint')]
    
    maskInInfs = jntInfs + inbtBndsMaskNames
    
    maskOutInfs = [u'CT__brow_bnd',
                u'LT_in_brow_bnd',
                u'LT_inner_eyelid_bnd',
                u'LT_in_cheek_bnd',
                u'LT_up_crease_bnd',
                u'LT__philtrum_bnd',
                u'CT__philtrum_bnd',
                u'LT_mid_crease_bnd']
    layerInfo = 'Nose', jntInfs, maskInInfs, maskOutInfs
    layerId = layer_weighting.buildLayer(mll, layerInfo)
    pm.delete(inbtBndMaskGrp)
    layer_weighting.mergeBlockWeights(mll, layerId, inbtInfNames, 'CT__noseBridge_bnd')
    pm.delete(inbtInfGrp)
    
    layer_weighting.mirrorLayer(mll, layerId)
    layer_weighting.smoothLayerMask(mll, layerId, [2.0, 1.5, 1.0])
    layer_weighting.relaxLayerInfluences(mll, layerId, 
                                         [41,41,23], [0.2333,0.2333,0.0941])
    
    
def layer_lips(mll):
    '''
    '''
    meshName, skn = mll.getTargetInfo()
    vertCount = mll.getVertCount()
    mesh = pm.PyNode(meshName)
    jntInfs = [u'CT_upper_lip_bnd',
                u'LT_upperSide_lip_bnd',
                u'LT_upperSneer_lip_bnd',
                u'LT_upperPinch_lip_bnd',
                u'LT_corner_lip_bnd',
                u'LT_lowerPinch_lip_bnd',
                u'LT_lowerSneer_lip_bnd',
                u'LT_lowerSide_lip_bnd',
                u'CT_lower_lip_bnd']
    maskInfs = [u'CT__philtrum_bnd',
                u'LT__philtrum_bnd',
                u'LT_mid_crease_bnd',
                u'LT_low_crease_bnd',
                u'LT_mid_chin_bnd',
                u'CT_mid_chin_bnd']
    
    layerInfo = 'Lips', jntInfs, jntInfs, maskInfs
    layerId = layer_weighting.buildLayer(mll, layerInfo)
    
    # apply loop weighting to split upper and lower lips
    pGrp = pm.PyNode('CT_placement_grp')
    lipWeights, treeRoot = layer_weighting.generateLipWeights(mll, pGrp, 10, layerId)
    with mll.batchUpdateContext():
        for infId, weightsList in lipWeights.items():
            mll.setInfluenceWeights(layerId, infId, weightsList)
            
    # relax weights between bnds
    crv = pm.PyNode('CT_placement_grp_mouthLipLoopCrv')
    bndToVertsRingMap = loop_weighting.populateBndToVertsRingMap(crv, treeRoot)
    vertIdsToHold = []
    for vertIdsList in bndToVertsRingMap.values():
        vertIdsToHold += vertIdsList
    vertsToRelax = [meshName+'.vtx[%d]'%vertId for vertId in range(vertCount)
                    if vertId not in vertIdsToHold]
    # actual relax command
    layer_weighting.relaxLayer(mll, layerId, 41, 0.2333, vertsToRelax)
    # mirror
    layer_weighting.mirrorLayer(mll, layerId)
    # one more smaller relax
    layer_weighting.relaxLayer(mll, layerId, 29, 0.1392)
    
    # smooth mask
    layer_weighting.smoothLayerMask(mll, layerId, [2.0, 1.0])
    
def layer_crease(mll):
    '''
    '''
    mesh, skn = mll.getTargetInfo()
    mesh = pm.PyNode(mesh)
    jntInfs = [u'CT__philtrum_bnd',
                u'LT__philtrum_bnd',
                u'LT_up_crease_bnd',
                u'LT_mid_crease_bnd',
                u'LT_low_crease_bnd',
                u'LT_mid_chin_bnd',
                u'CT_mid_chin_bnd']
    periLocs = [u'RT_up_crease_pLoc',
                u'LT_up_crease_pLoc',
                u'LT_mid_crease_pLoc',
                u'LT_low_crease_pLoc',
                u'LT__chin_pLoc',
                u'CT__chin_pLoc',
                u'RT__chin_pLoc']
    maskInfs = [u'CT__noseBridge_bnd',
                u'LT_in_cheek_bnd',
                u'LT_up_cheek_bnd',
                u'LT_mid_cheek_bnd',
                u'LT_low_cheek_bnd',
                u'LT_low_jaw_bnd',
                u'LT__chin_bnd',
                u'CT__chin_bnd']
    
    layerInfo = 'Crease', jntInfs, jntInfs, maskInfs
    
    layerId = layer_weighting.buildLayer(mll, layerInfo)
    layer_weighting.mirrorLayer(mll, layerId)
    layer_weighting.smoothLayerMask(mll, layerId, [1.0, 1.0])
    layer_weighting.relaxLayerInfluences(mll, layerId, 
                                         [41,23], [0.2333,0.0941])
    
def layer_cheeks(mll):
    '''
    '''
    mesh, skn = mll.getTargetInfo()
    mesh = pm.PyNode(mesh)
    jntInfs = [u'LT_in_cheek_bnd',
                u'LT_up_cheek_bnd',
                u'LT_mid_cheek_bnd',
                u'LT__squint_bnd',
                u'LT_low_cheek_bnd',
                u'LT_low_jaw_bnd',
                u'LT__chin_bnd',
                u'CT__chin_bnd']
    maskInfs = [u'CT__noseBridge_bnd',
                u'LT_inner_eyelid_bnd',
                u'LT_innerLower_eyelid_bnd',
                u'LT_lower_eyelid_bnd',
                u'LT_outerLower_eyelid_bnd',
                u'LT_outer_eyelid_bnd',
                u'LT__temple_bnd',
                u'LT_up_jaw_bnd',
                u'LT_corner_jaw_bnd',
                u'LT__neck_bnd',
                u'CT__neck_bnd']
    
    layerInfo = 'Cheeks', jntInfs, jntInfs, maskInfs
    
    layerId = layer_weighting.buildLayer(mll, layerInfo)
    layer_weighting.mirrorLayer(mll, layerId)
    layer_weighting.smoothLayerMask(mll, layerId, [2.0, 2.0, 2.0])
    layer_weighting.relaxLayerInfluences(mll, layerId, 
                                         [41,41,41], [0.2333,0.2333,0.2333])

def layer_jaw(mll):
    '''
    '''
    mesh, skn = mll.getTargetInfo()
    mesh = pm.PyNode(mesh)
    jntInfs = [u'LT_in_cheek_bnd',
                u'LT_up_cheek_bnd',
                u'LT__squint_bnd',
                u'LT_up_jaw_bnd',
                u'LT_corner_jaw_bnd',
                u'LT__neck_bnd',
                u'CT__neck_bnd']
    periLocs = [u'RT_in_cheek_pLoc',
                u'LT_in_cheek_pLoc',
                u'LT_up_cheek_pLoc',
                u'LT__squint_pLoc',
                u'LT_up_jaw_pLoc',
                u'LT_corner_jaw_pLoc',
                u'LT__neck_pLoc',
                u'CT__neck_pLoc',
                u'RT__neck_pLoc']
    
    maskInfsGrp = layer_weighting.addPerimeterBndSystem(mesh, periLocs)
    maskInfs = maskInfsGrp.getChildren(ad=True, type='joint')
    maskInfs = [inf.name() for inf in maskInfs]
    
    layerInfo = 'Jaw', jntInfs, jntInfs, maskInfs
    
    layerId = layer_weighting.buildLayer(mll, layerInfo)
    layer_weighting.mirrorLayer(mll, layerId)
    layer_weighting.smoothLayerMask(mll, layerId, [2.0, 2.0, 2.0])
    layer_weighting.relaxLayerInfluences(mll, layerId, 
                                         [41,41,41], [0.2333,0.2333,0.2333])
    
    pm.delete(maskInfsGrp)
    
    

def initBind():
    '''
    '''
    bndGrp = nt.Transform(u'CT_bnd_grp')
    mesh = nt.Transform(u'CT_face_geo')
    allBnds = bndGrp.getChildren(type='joint', ad=True)
    
    # initial bind all with closestJoint
    pm.select(cl=True)
    skn = pm.skinCluster(allBnds, mesh, bindMethod=0, 
                         maximumInfluences=1, omi=False)
    
    mll = layer_weighting.initLayers(bndGrp, mesh)
    
    
    return mll

def setupSkinLayers(mll=None, layers=[]):
    '''
    main skinning script to be called from build
    '''
    progressAmt = 0
    pm.progressWindow(title='Skin Layers Setup',
                      status='Initialize skinCluster...',
                      max=len(layers),
                      progress=progressAmt)
    
    if mll is None:
        mll = initBind()
    
    for layer in layers:
        
        progressAmt += 1
        pm.progressWindow(e=True,
                          progress=progressAmt,
                          status='Setup layer "%s"...'%layer)
        
        try:
            func = globals()['layer_'+layer]
        except KeyError:
            print 'No function defined for layer ' + layer
        else:
            func(mll)
            
    pm.progressWindow(endProgress=True)
    pm.select(cl=True)
    
    return mll