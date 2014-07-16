'''
Created on Jul 5, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt

import rigger.modules.face as face
# from misc.hacks import priCtlAttrs
from rigger.builds.ori.data import priCtlMappings
reload(face)

import rigger.modules.priCtl as priCtl
reload(priCtl)

import rigger.builds.headmonster.data as data
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
        face.cleanFaceRig()
        
    #-------------------------------------------------------- surface constraint
    if 'surface_constraint' in data.build_actions:
        createSurfaceContraint()
        
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
        addStickyLips()
        
def addStickyLips():
    '''
    '''
    import rigger.modules.sticky as sticky
    reload(sticky)
    ct_stick = sticky.Sticky(up_bnd=pm.PyNode('CT_upper_lip_bnd'), 
                      low_bnd=pm.PyNode('CT_lower_lip_bnd'), 
                      center=pm.PyNode('CT_jaw_pri_ctrl'))
    lf_side = sticky.Sticky(up_bnd=pm.PyNode('LT_upper_side_lip_bnd'), 
                      low_bnd=pm.PyNode('LT_lower_side_lip_bnd'), 
                      center=pm.PyNode('CT_jaw_pri_ctrl'))
    lf_sneer = sticky.Sticky(up_bnd=pm.PyNode('LT_upper_sneer_lip_bnd'), 
                      low_bnd=pm.PyNode('LT_lower_sneer_lip_bnd'), 
                      center=pm.PyNode('CT_jaw_pri_ctrl'))
    lf_pinch = sticky.Sticky(up_bnd=pm.PyNode('LT_upper_pinch_lip_bnd'), 
                      low_bnd=pm.PyNode('LT_lower_pinch_lip_bnd'), 
                      center=pm.PyNode('CT_jaw_pri_ctrl'))
    rt_side = sticky.Sticky(up_bnd=pm.PyNode('RT_upper_side_lip_bnd'), 
                      low_bnd=pm.PyNode('RT_lower_side_lip_bnd'), 
                      center=pm.PyNode('CT_jaw_pri_ctrl'))
    rt_sneer = sticky.Sticky(up_bnd=pm.PyNode('RT_upper_sneer_lip_bnd'), 
                      low_bnd=pm.PyNode('RT_lower_sneer_lip_bnd'), 
                      center=pm.PyNode('CT_jaw_pri_ctrl'))
    rt_pinch = sticky.Sticky(up_bnd=pm.PyNode('RT_upper_pinch_lip_bnd'), 
                      low_bnd=pm.PyNode('RT_lower_pinch_lip_bnd'), 
                      center=pm.PyNode('CT_jaw_pri_ctrl'))
    # store data in dict
    # stickyData = {'lf_side': [lf_side, {lf_keys}, {rt_keys}}
    sticky.addStickyToFRS()
    
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
    
    

def transferPriCtlWeightsFromOri():
    '''
    '''
    import rigger.builds.ori.data as ori_data
    priCtlMappings = ori_data.priCtlMappings
    
    for pCtl, weightsTable in priCtlMappings.items():
        attrName = pCtl + '_weight_'
        for bndName, weight in weightsTable.items():
            try:
                bnd = pm.PyNode(bndName)
                bnd.attr(attrName).set(weight)
            except pm.MayaNodeError as e:
                pm.warning('Does not exist: ' + bndName)
                
def createSurfaceContraint():
    '''
    use geometry and normal constraint to slide bnds along surface
    for volume maintainence
    '''
    surf = nt.NurbsSurface(u'CT_volume_surfShape')
    bnds = [pm.PyNode(name) for name in data.slidingBnds]
    
    for bnd in bnds:
        addSurfaceConstraintToBnd(bnd, surf)
    

def addSurfaceConstraintToBnd(bnd, surface):
    '''
    '''
    secDrv = bnd.getParent()
    matrix = secDrv.getMatrix(worldSpace=True)
    
    # create additional nulls
    gc = pm.group(em=True, n=bnd.nodeName().replace('_bnd', '_gc'))
    gc_offset = pm.group(em=True, n=bnd.nodeName().replace('_bnd', '_gc_offset'))
    acs = pm.group(em=True, n=bnd.nodeName().replace('_bnd', '_acs'))
    
    # point constraint first to get precise position to secDrv
    pm.pointConstraint(secDrv, gc)
    # geometry constraint to surface
    pm.geometryConstraint(surface, gc)
    # normal constraint, using secDrv-Y as up
    pm.normalConstraint(surface, gc, aim=(0,0,1), u=(0,1,0),
                        wuo=secDrv, wut='objectrotation', wu=(0,1,0))
    
    # ensure that gc_offset stores offset to secDrv
    gc_offset.setMatrix(matrix, worldSpace=True)
    acs.setMatrix(matrix, worldSpace=True)
    
    # hierarchy
    secDrv | gc | gc_offset | acs | bnd
    
def removeScaleWeights():
    '''
    remove scale to fix DQ problem
    '''
    allBnds = pm.PyNode('CT_bnd_grp').getChildren(type='joint', ad=True)
    for src_bnd in allBnds:
        all_attrs = src_bnd.listAttr(ud=True, u=True)
        all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weight_s' in attr.name()]
        all_attrs = [attr for attr in all_attrs if attr.isFreeToChange() == 0]
        
        for src_attr in all_attrs:
            src_attr.set(0)