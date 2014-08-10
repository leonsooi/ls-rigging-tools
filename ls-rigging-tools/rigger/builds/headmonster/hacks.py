'''
Created on Jul 13, 2014

@author: Leon
'''
import pymel.core as pm
import pymel.core.nodetypes as nt

import rigger.modules.priCtl as priCtl
reload(priCtl)

import rigger.utils.weights as weights
reload(weights)

def connectEyeDeformerToEyeMover(aimJntsGrp, moverBnd):
    '''
    transform eye deformer with eyeMover ctrl
    '''
    masterGrp = aimJntsGrp.getParent()
    consGrp = pm.group(em=True, n=aimJntsGrp+'_PR_SC')
    moverMat = moverBnd.getMatrix(ws=True)
    consGrp.setMatrix(moverMat, ws=True)
    masterGrp | consGrp | aimJntsGrp
    # constraints
    pCtl = pm.PyNode(moverBnd.attached_pri_ctl.get())
    pm.parentConstraint(pCtl, consGrp)
    pm.scaleConstraint(pCtl, consGrp)

def addBndsToEyeMover():
    '''
    '''
    pBnd = nt.Joint(u'LT__eyeMover_bnd')
    pCtl = priCtl.addPrimaryCtlToBnd(pBnd)
    bnds = [nt.Joint(u'LT_inner_eyelid_bnd'),
            nt.Joint(u'LT_inner_eyeSocket_bnd'),
            nt.Joint(u'LT_upperInner_eyelid_bnd'),
            nt.Joint(u'LT_upperInner_eyeSocket_bnd'),
            nt.Joint(u'LT_upper_eyelid_bnd'),
            nt.Joint(u'LT_upper_eyeSocket_bnd'),
            nt.Joint(u'LT_upperOuter_eyelid_bnd'),
            nt.Joint(u'LT_upperOuter_eyeSocket_bnd'),
            nt.Joint(u'LT_outer_eyelid_bnd'),
            nt.Joint(u'LT_outer_eyeSocket_bnd'),
            nt.Joint(u'LT_lowerOuter_eyeSocket_bnd'),
            nt.Joint(u'LT_lowerOuter_eyelid_bnd'),
            nt.Joint(u'LT_lower_eyeSocket_bnd'),
            nt.Joint(u'LT_lower_eyelid_bnd'),
            nt.Joint(u'LT_lowerInner_eyeSocket_bnd'),
            nt.Joint(u'LT_lowerInner_eyelid_bnd'),
            nt.Joint(u'CT_mid_squint_bnd'),
            nt.Joint(u'CT_mid_temple_bnd'),
            nt.Joint(u'LT_outerA_temple_bnd'),
            nt.Joint(u'LT_outerA_squint_bnd'),
            nt.Joint(u'LT_upperCorner_cheek_bnd'),
            nt.Joint(u'LT_upperPinch_outCrease_bnd'),
            nt.Joint(u'LT_upperSneer_outCrease_bnd'),
            nt.Joint(u'LT_upperSide_outCrease_bnd'),
            nt.Joint(u'CT_upper_cheek_bnd'),
            nt.Joint(u'CT_upper_outCrease_bnd'),
            nt.Joint(u'LT_upperSide_midCrease_bnd'),
            nt.Joint(u'LT_upperSneer_midCrease_bnd'),
            nt.Joint(u'LT_upperPinch_midCrease_bnd'),
            nt.Joint(u'LT_upperCorner_outCrease_bnd')]
    for bnd in bnds:
        priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
    bnds = [nt.Joint(u'LT_inner_eyelid_bnd'),
            nt.Joint(u'LT_upper_eyelid_bnd'),
            nt.Joint(u'LT_outer_eyelid_bnd'),
            nt.Joint(u'LT_lower_eyelid_bnd')]
    for bnd in bnds:
        priCtl.driveAttachedPriCtl(bnd, pCtl)
        
    # same thing for right side
    pBnd = nt.Joint(u'RT__eyeMover_bnd')
    pCtl = priCtl.addPrimaryCtlToBnd(pBnd)
    bnds = [nt.Joint(u'RT_inner_eyelid_bnd'),
            nt.Joint(u'RT_inner_eyeSocket_bnd'),
            nt.Joint(u'RT_upperInner_eyelid_bnd'),
            nt.Joint(u'RT_upperInner_eyeSocket_bnd'),
            nt.Joint(u'RT_upper_eyelid_bnd'),
            nt.Joint(u'RT_upper_eyeSocket_bnd'),
            nt.Joint(u'RT_upperOuter_eyelid_bnd'),
            nt.Joint(u'RT_upperOuter_eyeSocket_bnd'),
            nt.Joint(u'RT_outer_eyelid_bnd'),
            nt.Joint(u'RT_outer_eyeSocket_bnd'),
            nt.Joint(u'RT_lowerOuter_eyeSocket_bnd'),
            nt.Joint(u'RT_lowerOuter_eyelid_bnd'),
            nt.Joint(u'RT_lower_eyeSocket_bnd'),
            nt.Joint(u'RT_lower_eyelid_bnd'),
            nt.Joint(u'RT_lowerInner_eyeSocket_bnd'),
            nt.Joint(u'RT_lowerInner_eyelid_bnd'),
            nt.Joint(u'CT_mid_squint_bnd'),
            nt.Joint(u'CT_mid_temple_bnd'),
            nt.Joint(u'RT_outerA_temple_bnd'),
            nt.Joint(u'RT_outerA_squint_bnd'),
            nt.Joint(u'RT_upperCorner_cheek_bnd'),
            nt.Joint(u'RT_upperPinch_outCrease_bnd'),
            nt.Joint(u'RT_upperSneer_outCrease_bnd'),
            nt.Joint(u'RT_upperSide_outCrease_bnd'),
            nt.Joint(u'CT_upper_cheek_bnd'),
            nt.Joint(u'CT_upper_outCrease_bnd'),
            nt.Joint(u'RT_upperSide_midCrease_bnd'),
            nt.Joint(u'RT_upperSneer_midCrease_bnd'),
            nt.Joint(u'RT_upperPinch_midCrease_bnd'),
            nt.Joint(u'RT_upperCorner_outCrease_bnd')]
    for bnd in bnds:
        priCtl.connectBndToPriCtl(bnd, pCtl, False)
    
    bnds = [nt.Joint(u'RT_inner_eyelid_bnd'),
            nt.Joint(u'RT_upper_eyelid_bnd'),
            nt.Joint(u'RT_outer_eyelid_bnd'),
            nt.Joint(u'RT_lower_eyelid_bnd')]
    for bnd in bnds:
        priCtl.driveAttachedPriCtl(bnd, pCtl)
    
    # zero scale weights for DQ skinning
    weights.zeroAllMatrixScaleWeights()

def addEyelidNoScaleJoints():
    # eyelid no-scale joints
    scaleNull = nt.Transform(u'null2')
    jntsGrp = nt.Transform(u'RT_eye_aimJnts_grp_0')
    allBnds = jntsGrp.getChildren(ad=True, type='joint')
    allBnds = [jnt for jnt in allBnds if '_bnd_' in jnt.nodeName()]
    
    noscale_bnds_grp = pm.group(em=True, n=jntsGrp+'_noscale_grp')
    for bnd in allBnds:
        decMat = pm.createNode('decomposeMatrix', n=bnd+'_noscale_dcm')
        bnd.worldMatrix >> decMat.inputMatrix
        pm.select(cl=True)
        noscale_bnd = pm.joint(n=bnd+'_noscale_bnd')
        decMat.ot >> noscale_bnd.t
        decMat.outputRotate >> noscale_bnd.r
        noscale_bnds_grp | noscale_bnd
        
def setJointLabels():
    # set joint labels by second token
    jnts = pm.ls(sl=True)
    for jnt in jnts:
        label = jnt.split('_')[1]
        jnt.drawLabel.set(True)
        jnt.attr('type').set('Other')
        jnt.otherType.set(label)
        # jnt.drawLabel.set(False)
        
def setSneerWeightsFromCenterLips():
    '''
    set weights for center lips upper & lower first
    then run this to get left sneer weights
    then mirror
    # loop through all LT_ bnds
    # assign sneer weights based on center lip weights
    '''
    weights = {'LT_upperCorner':1.0,
    'LT_upperPinch':1.0,
    'LT_upperSneer':1.0,
    'LT_upperSide':0.8,
    'CT_upper':0.5,
    'RT_upperSide':0.2,
    'LT_lowerCorner':1.0,
    'LT_lowerPinch':1.0,
    'LT_lowerSneer':1.0,
    'LT_lowerSide':0.8,
    'CT_lower':0.5,
    'RT_lowerSide':0.2,
    'LT_lower':1.0,
    'LT_lowerInner':0.8,
    'RT_lowerInner':0.2}
    
    bndGrp = pm.PyNode('CT_bnd_grp')
    allBnds = bndGrp.getChildren(type='joint', ad=True)
    # uppers
    for bnd in allBnds:
        if bnd.attr('CT_upper_lip_pri_ctrl_weight_').get():
            ctr_weight = bnd.attr('CT_upper_lip_pri_ctrl_weight_').get()
            bndToken = '_'.join(bnd.split('_')[:2])
            weight = weights.get(bndToken, 0.0)
            bnd.attr('LT_upperSneer_lip_pri_ctrl_weight_').set(ctr_weight*weight)
            bnd.attr('RT_upperSneer_lip_pri_ctrl_weight_').set(ctr_weight*(1-weight))
    # lowers 
    for bnd in allBnds:
        if bnd.attr('CT_lower_lip_pri_ctrl_weight_').get():
            ctr_weight = bnd.attr('CT_lower_lip_pri_ctrl_weight_').get()
            bndToken = '_'.join(bnd.split('_')[:2])
            weight = weights.get(bndToken, 0.0)
            bnd.attr('LT_lowerSneer_lip_pri_ctrl_weight_').set(ctr_weight*weight)
            bnd.attr('RT_lowerSneer_lip_pri_ctrl_weight_').set(ctr_weight*(1-weight))