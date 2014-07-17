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

import rigger.builds.ori.data as data
reload(data)

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
    else:
        bindGrp = nt.Transform(u'CT_bnd_grp')
    
    #--------------------------------------------------------- sec motion system
    if 'sec_motion_system' in data.build_actions:
        face.buildSecondaryControlSystem(placementGrp, bindGrp, mesh)
     
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
        else:
            pm.warning('no data for pri ctl system')
            
    #-------------------------------------------------------------- load weights
    if 'load_weights' in data.build_actions:
        priCtlMappings = data.priCtlMappings
        priCtl.setPriCtlFirstPassWeights(priCtlMappings)
            
    #--------------------------------------------------------------------- clean
    if 'clean' in data.build_actions:
        print 'clean'
        face.cleanFaceRig()
        
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
        
    #--------------------------------------------------------------- sticky lips
    if 'sticky_lips' in data.build_actions:
        pass

def buildEyeRig(pGrp):
    #--------------------------------------------------------- ADD LEFT EYE DEFORMER
    edgeLoop = [pm.PyNode(edge) for edge in pGrp.leftEyelidLoop.get()]
    eyePivot = pm.PyNode('LT_eyeball_geo')
    rigidLoops = 2
    falloffLoops = 6
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