'''
Created on Jul 5, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt

import rigger.modules.face as face
reload(face)

import rigger.modules.priCtl as priCtl
reload(priCtl)

import rigger.builds.lipsHuman.data as data
reload(data)
import rigger.builds.lipsHuman.skinLayers as skin
reload(skin)

mel = pm.language.Mel()
import maya.cmds as mc
import rigger.modules.eye as eye
reload(eye)
import utils.symmetry as sym
import rigger.utils.weights as weights
reload(weights)



def build():
    '''
    '''
    mesh = nt.Mesh(u'CT_face_geoShape')   
    placementGrp = nt.Transform(u'CT_placement_grp')
    
    #---------------------------------------------------------------------- bind
    if 'bind' in data.build_actions:
        bindGrp = face.createBndsFromPlacement(placementGrp)
        pm.refresh()
    else:
        bindGrp = nt.Transform(u'CT_bnd_grp')
    
    #--------------------------------------------------------- sec motion system
    if 'sec_motion_system' in data.build_actions:
        face.buildSecondaryControlSystem(placementGrp, bindGrp, mesh)
        pm.refresh()
     
    #------------------------------------------------------------ pri ctl system first
    if 'primary_ctl_system_first' in data.build_actions:
        # run a simple first pass
        # which can be used to block out mappings
        bndsForPriCtls = data.all_bnds_for_priCtls
        priCtl.setupPriCtlFirstPass(bindGrp, bndsForPriCtls)
        priCtl.driveAttachedPriCtlsRun(bindGrp)
            
    #------------------------------------------------------------ pri ctl system second
    if 'primary_ctl_system_second' in data.build_actions:
        if data.priCtlMappings:
            # if priCtlMappings is set up, use the data
            priCtlMappings = data.priCtlMappings
            priCtl.setupPriCtlSecondPass(priCtlMappings)
            priCtl.driveAttachedPriCtlsRun(bindGrp)
            pm.refresh()
        else:
            pm.warning('no data for pri ctl system')
            
    #-------------------------------------------------------------- load weights
    if 'load_weights' in data.build_actions:
        priCtlWeights = data.priCtlWeights
        priCtl.setPriCtlSecondPassWeights(priCtlWeights)
        pm.refresh()
            
    #--------------------------------------------------------------------- clean
    if 'clean' in data.build_actions:
        print 'clean'
        face.cleanFaceRig()
        pm.select(cl=True)
        pm.refresh()
        
    #--------------------------------------------------------------- skin_layers
    if 'skin_layers' in data.build_actions:
        # initial bind
        mll = skin.setupSkinLayers(None, layers=[['base', None]])
        
        # split masks for up and low lips
        upVerts, lowVerts = skin.splitLipsVertices(mll)

        mll = skin.setupSkinLayers(mll, layers=[['neck', None],
                                                ('jaw', lowVerts),
                                                ('cheeks', upVerts),
                                                ('chin', lowVerts),
                                                ('crease', upVerts),
                                                ('lips', None),
                                                ('nose', None),
                                                ('brow', None)
                                                ])
        
        _, skn = mll.getTargetInfo()
        pm.PyNode(skn).skinningMethod.set(1)
        pm.PyNode(skn).deformUserNormals.set(0)
        
        
    #---------------------------------------------------------------------- eyes
    if 'eyes' in data.build_actions:
        buildEyeRig(placementGrp)
        
    #------------------------------------------------------------------ eyeballs
    if 'eyeballs' in data.build_actions:
        #------------------------------------------ EYEBALL RIG (SIMPLE AIM CONSTRAINTS)
        eye.buildEyeballRig()
        eye.addEyeAim(prefix='LT_', distance=25) # BROKEN if there is already a
        # node named LT_eyeball_grp!!!
        eye.addEyeAim(prefix='RT_', distance=25) # BROKEN
    
    #--------------------------------------------------------------- fleshy_eyes
    if 'fleshy_eyes' in data.build_actions:
        import rigger.modules.poseReader as poseReader
        reload(poseReader)
        xfo = pm.PyNode('LT_eyeball_bnd')
        poseReader.radial_pose_reader(xfo)
        xfo = pm.PyNode('RT_eyeball_bnd')
        poseReader.radial_pose_reader(xfo)
        eye.addFleshyEye()
        
    #--------------------------------------------------------------- sticky lips
    if 'sticky_lips' in data.build_actions:
        import rigger.modules.sticky as sticky
        reload(sticky)
        sticky.Sticky(up_bnd=pm.PyNode('CT_upper_lip_bnd'), 
                          low_bnd=pm.PyNode('CT_lower_lip_bnd'), 
                          center=pm.PyNode('CT__jaw_pri_ctrl'))
        sticky.Sticky(up_bnd=pm.PyNode('LT_upperSide_lip_bnd'), 
                          low_bnd=pm.PyNode('LT_lowerSide_lip_bnd'), 
                          center=pm.PyNode('CT__jaw_pri_ctrl'))
        sticky.Sticky(up_bnd=pm.PyNode('LT_upperSneer_lip_bnd'), 
                          low_bnd=pm.PyNode('LT_lowerSneer_lip_bnd'), 
                          center=pm.PyNode('CT__jaw_pri_ctrl'))
        sticky.Sticky(up_bnd=pm.PyNode('LT_upperPinch_lip_bnd'), 
                          low_bnd=pm.PyNode('LT_lowerPinch_lip_bnd'), 
                          center=pm.PyNode('CT__jaw_pri_ctrl'))
        sticky.Sticky(up_bnd=pm.PyNode('RT_upperSide_lip_bnd'), 
                          low_bnd=pm.PyNode('RT_lowerSide_lip_bnd'), 
                          center=pm.PyNode('CT__jaw_pri_ctrl'))
        sticky.Sticky(up_bnd=pm.PyNode('RT_upperSneer_lip_bnd'), 
                          low_bnd=pm.PyNode('RT_lowerSneer_lip_bnd'), 
                          center=pm.PyNode('CT__jaw_pri_ctrl'))
        sticky.Sticky(up_bnd=pm.PyNode('RT_upperPinch_lip_bnd'), 
                          low_bnd=pm.PyNode('RT_lowerPinch_lip_bnd'), 
                          center=pm.PyNode('CT__jaw_pri_ctrl'))
        
        sticky.addStickyToFRS()
        sticky.patchOldSticky()
        
    #----------------------------------------------------------------- auto_sdks
    if 'auto_sdks' in data.build_actions:
        import utils.rigging as rt
        pCtl = pm.PyNode('CT__mouthMover_pri_ctrl')
        offsetGrp = priCtl.addOffset(pCtl, 'child', suffix='_autoRotate')
        rt.connectSDK(pCtl.tx, offsetGrp.ry, {-1.2:-15, 0:0, 1.2:15})
        rt.connectSDK(pCtl.tx, offsetGrp.rz, {-1.2:-12, 0:0, 1.2:12})
        rt.connectSDK(pCtl.tx, offsetGrp.tz, {-1.2:0.4, 0:0, 1.2:0.4})
        
        # squint
        pCtl = pm.PyNode('LT__squint_pri_ctrl')
        offsetGrp = priCtl.addOffset(pCtl, 'parent', suffix='_autoVolume')
        rt.connectSDK(pCtl.ty, offsetGrp.tz, {0:0, 1:0.5})
        pCtl = pm.PyNode('RT__squint_pri_ctrl')
        offsetGrp = priCtl.addOffset(pCtl, 'parent', suffix='_autoVolume')
        rt.connectSDK(pCtl.ty, offsetGrp.tz, {0:0, 1:0.5})
        
        # inbrow
        import rigger.modules.secCtl as secCtl
        reload(secCtl)
        sCtl = pm.PyNode('LT_in_brow_ctrl')
        offsetGrp = secCtl.addOffset(sCtl, 'parent', suffix='_autoVolume')
        rt.connectSDK(sCtl.tx, offsetGrp.tz, {0:0, -1:0.2})
        sCtl = pm.PyNode('RT_in_brow_ctrl')
        offsetGrp = secCtl.addOffset(sCtl, 'parent', suffix='_autoVolume')
        rt.connectSDK(sCtl.tx, offsetGrp.tz, {0:0, 1:0.2})
        
    if 'finish_mathilda' in data.build_actions:
        # a few mathilda specific things to finalize rig
        # for demo reel purposes
        
        # 1. lock all TZs for better volume
        allCtls = pm.ls('*_ctrl', type='transform')
        for ctl in allCtls:
            ctl.tz.set(l=True, k=False)
            
        # 2. hide eye aim locators
        eyeAimLocs = [nt.Transform(u'LT_eye_aim_loc'),
                      nt.Transform(u'RT_eye_aim_loc')]
        for loc in eyeAimLocs:
            loc.v.set(False)
            
        # 3. go to object mode so we can select controls
        pm.selectMode(object=True)
        
        # 4. bind tongue and teeth
        geos = [nt.Transform(u'CT_lowerGums_geo'),
                nt.Transform(u'CT_tongue_geo'),
                nt.Transform(u'CT_lowerTeeth_geo')]
        for geo in geos:
            pm.parentConstraint(pm.PyNode('CT__jaw_bnd'), geo, mo=True)
        
        '''
        # 5. reference all geos to make it easier to select controls
        allGeos = pm.PyNode('CT_geo_grp').getChildren(ad=True, type='mesh')
        for geo in allGeos:
            geo.overrideEnabled.set(True)
            geo.overrideDisplayType.set(True)
        '''
            
        # 6. smooth face mesh to make it look nicer
        pm.PyNode('CT_face_geoShape').displaySmoothMesh.set(2)
        
def buildEyeRig(pGrp):
    #--------------------------------------------------------- ADD LEFT EYE DEFORMER
    edgeLoop = [pm.PyNode(edge) for edge in pGrp.leftEyelidLoop.get()]
    eyePivot = pm.PyNode('LT_eyeball_geo')
    rigidLoops = 2
    falloffLoops = 4
    eye.buildEyeRigCmd('LT_eye', eyePivot, edgeLoop, rigidLoops, falloffLoops)
    
    #---------------------------------------------------------- RIGHT EYE DEFORMER
    # sym table - switch off deformers first to get perfect sym
    pm.PyNode('skinCluster1').envelope.set(0)
    symTable = sym.buildSymTable('CT_face_geo')
    pm.PyNode('skinCluster1').envelope.set(1)
    # mirror loop to right side
    pm.select(edgeLoop)
    mel.ConvertSelectionToVertices()
    vertsLoop = mc.ls(sl=True, fl=True)
    sym.flipSelection(vertsLoop, symTable)
    mel.ConvertSelectionToContainedEdges()
    edgeLoop = pm.ls(sl=True)
    eyePivot = pm.PyNode('RT_eyeball_geo')
    eye.buildEyeRigCmd('RT_eye', eyePivot, edgeLoop, rigidLoops, falloffLoops)
    
    weights.setEyelidLoopWeights('LT')
    weights.setEyelidLoopWeights('RT')