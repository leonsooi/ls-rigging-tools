'''
Created on Jul 14, 2014

@author: Leon
'''
import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
import utils.rigging as rt
mel = Mel()

import rigger.utils.modulate as modulate
reload(modulate)

def fixBendyRibbonsGo():
    '''
    '''
    # left arm
    cons = [nt.AimConstraint(u'Mathilda_lf_armRibbon_1_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_lf_armRibbon_2_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_lf_armRibbon_3_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_lf_armRibbon_4_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_lf_armRibbon_5_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_lf_armRibbon_6_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_lf_armRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')
        
    # right arm
    cons = [nt.AimConstraint(u'Mathilda_rt_armRibbon_1_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_rt_armRibbon_2_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_rt_armRibbon_3_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_rt_armRibbon_4_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_rt_armRibbon_5_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_rt_armRibbon_6_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(u'Mathilda_rt_armRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')
        
    # left leg
    
    cons =[nt.AimConstraint(u'Mathilda_lf_legRibbon_1_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_lf_legRibbon_2_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_lf_legRibbon_3_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_lf_legRibbon_4_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_lf_legRibbon_5_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_lf_legRibbon_6_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_lf_legRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')
        
    # right leg
    cons =[nt.AimConstraint(u'Mathilda_rt_legRibbon_1_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_rt_legRibbon_2_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_rt_legRibbon_3_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_rt_legRibbon_4_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_rt_legRibbon_5_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_rt_legRibbon_6_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(u'Mathilda_rt_legRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')

def setBendyConstraintOnRibbon(con, aimVec, upVec, tangent):
    '''
    con - nt.AimConstraint
    aimVector - vector to align to normal
    upVector - vector to align to tangent
    tangent - 'tangentU' or 'tangentV'
    '''
    con.aimVector.set(aimVec)
    con.upVector.set(upVec)
    posi = con.worldUpVector.inputs()[0]
    posi.attr(tangent) >> con.worldUpVector

def addEyelashCollidersGo():
    '''
    '''
    '''
    # left side
    browCrv = pm.PyNode(u'LT_eyeBrowCollide_crv')
    bnds = [nt.Joint(u'FACE:LT_eye_aimAt_bnd_19'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_18'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_17'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_16'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_15'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_14'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_13'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_12'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_11'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_10'),
            nt.Joint(u'FACE:LT_eye_aimAt_bnd_9')]
    
    allGrps = pm.group(em=True, n='LT_eyelashColliders_grp')
    for bnd in bnds:
        grp = addEyelashCollider(bnd, browCrv)
        bndId = bnd.name().split('_')[-1]
        attrName = 'rotateLimit'+bndId
        allGrps.addAttr(attrName, k=True, dv=10)
        allGrps.attr(attrName) >> grp.minRotate
        allGrps | grp'''
    
    # right side
    browCrv = pm.PyNode(u'RT_eyeBrowCollide_crv')
    bnds = [nt.Joint(u'FACE:RT_eye_aimAt_bnd_19'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_18'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_17'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_16'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_15'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_14'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_13'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_12'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_11'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_10'),
            nt.Joint(u'FACE:RT_eye_aimAt_bnd_9')]
    
    allGrps = pm.group(em=True, n='RT_eyelashColliders_grp')
    for bnd in bnds:
        grp = addEyelashCollider(bnd, browCrv)
        bndId = bnd.name().split('_')[-1]
        attrName = 'rotateLimit'+bndId
        allGrps.addAttr(attrName, k=True, dv=10)
        allGrps.attr(attrName) >> grp.minRotate
        allGrps | grp


def addEyelashCollider(bnd, browCrv):
    '''
    browCrv = pm.PyNode(u'LT_eyeBrowCollide_crv')
    bnd = pm.PyNode('FACE:LT_eye_aimAt_bnd_16')
    '''
    childGrp = bnd.getChildren()[0]
    # create vertCrv
    vertCrv = pm.curve(p=((0,-10,0),(0,10,0)), n=bnd+'_vertCrv', d=1)
    # constrain to bnd
    pm.pointConstraint(bnd, vertCrv)
    # intersect
    crvInt = pm.createNode('curveIntersect', n=bnd+'_collider_int')
    browCrv.worldSpace >> crvInt.inputCurve1
    vertCrv.worldSpace >> crvInt.inputCurve2
    crvInt.useDirection.set(True)
    # calculate direction of bnd's x-axis
    mat = bnd.getMatrix(ws=True)
    dir = pm.dt.Vector(1,0,0) * mat
    crvInt.direction.set(dir)
    # get point on crv
    poci = pm.createNode('pointOnCurveInfo', n=bnd+'_collider_poci')
    browCrv.worldSpace >> poci.inputCurve
    crvInt.parameter1[0] >> poci.parameter
    # aim loc
    aimLoc = pm.spaceLocator(n=bnd+'_collide_aimLoc')
    aimLoc.localScale.set(0.1,0.1,0.1)
    poci.position >> aimLoc.t
    # limit null
    limitNull = pm.group(em=True, n=bnd+'_collider_limit')
    bnd | limitNull
    limitNull.setMatrix(pm.dt.Matrix())
    # aim to aimLoc
    pm.aimConstraint(aimLoc, limitNull, aim=(1,0,0), 
    wuo=bnd, wu=(0,1,0), u=(0,1,0), wut='objectrotation')
    # limit childGrp while keeping bnd's orientation
    limitNull | childGrp
    pm.orientConstraint(bnd, childGrp)
    childGrp.minRotZLimit.set(10)
    childGrp.minRotZLimitEnable.set(True)
    # cleanup
    grp = pm.group(vertCrv, aimLoc, n=bnd+'_collide_grp')
    grp.addAttr('minRotate', k=True, dv=10)
    grp.minRotate >> childGrp.minRotZLimit
    
    return grp

def addLipCurlsSDKs():
    '''
    '''
    # upper lips
    coeffs = pm.group(em=True, n='CT_upperLipCurls_coeffs')
    coeffs.addAttr('leftPinch', k=True)
    coeffs.addAttr('leftSneer', k=True)
    coeffs.addAttr('leftSide', k=True)
    coeffs.addAttr('centerMid', k=True)
    coeffs.addAttr('rightSide', k=True)
    coeffs.addAttr('rightSneer', k=True)
    coeffs.addAttr('rightPinch', k=True)
    rt.connectSDK('FACE:LT_upper_pinch_lip_ctrl.rx',
    coeffs.leftPinch, {-90:1, 0:0, 90:-1})
    rt.connectSDK('FACE:LT_upper_sneer_lip_ctrl.rx',
    coeffs.leftSneer, {-90:1, 0:0, 90:-1})
    rt.connectSDK('FACE:LT_upper_side_lip_ctrl.rx',
    coeffs.leftSide, {-90:1, 0:0, 90:-1})
    rt.connectSDK('FACE:CT_upper_lip_ctrl.rx',
    coeffs.centerMid, {-90:1, 0:0, 90:-1})
    rt.connectSDK('FACE:RT_upper_sneer_lip_ctrl.rx',
    coeffs.rightSneer, {-90:1, 0:0, 90:-1})
    rt.connectSDK('FACE:RT_upper_side_lip_ctrl.rx',
    coeffs.rightSide, {-90:1, 0:0, 90:-1})
    rt.connectSDK('FACE:RT_upper_pinch_lip_ctrl.rx',
    coeffs.rightPinch, {-90:1, 0:0, 90:-1})
    
    priCtls = [nt.Transform(u'FACE:RT_upper_sneer_lip_pri_ctrl'),
                nt.Transform(u'FACE:CT_upper_lip_pri_ctrl'),
                nt.Transform(u'FACE:LT_upper_sneer_lip_pri_ctrl')]
                
    attrs = ['leftPinch',
    'leftSneer',
    'leftSide',
    'centerMid',
    'rightSide',
    'rightSneer',
    'rightPinch']
           
    import rigger.utils.modulate as modulate     
    for pCtl in priCtls:
        token = pCtl.split(':')[1].split('_')[0]
        for attr in attrs:
            mod = modulate.addInput(coeffs.attr(attr), 0, token)
            rt.connectSDK(pCtl.rx, mod, {-90:1, 0:0, 90:-1})
            
    rt.connectSDK(coeffs.leftPinch, 
    'FACE:blendShapeCt_face_geo.upLipTweakPinch_curlOut_Lf', {0:0, 1:1})
    rt.connectSDK(coeffs.leftPinch, 
    'FACE:blendShapeCt_face_geo.upLipTweakPinch_curlIn_Lf', {0:0, -1:1})
    
    rt.connectSDK(coeffs.leftSneer, 
    'FACE:blendShapeCt_face_geo.upLipTweakSneer_curlOut_Lf', {0:0, 1:1})
    rt.connectSDK(coeffs.leftSneer, 
    'FACE:blendShapeCt_face_geo.upLipTweakSneer_curlIn_Lf', {0:0, -1:1})
    
    rt.connectSDK(coeffs.leftSide, 
    'FACE:blendShapeCt_face_geo.upLipTweakSide_curlOut_Lf', {0:0, 1:1})
    rt.connectSDK(coeffs.leftSide, 
    'FACE:blendShapeCt_face_geo.upLipTweakSide_curlIn_Lf', {0:0, -1:1})
    
    rt.connectSDK(coeffs.centerMid, 
    'FACE:blendShapeCt_face_geo.upLipTweakMid_curlOut_Ct', {0:0, 1:1})
    rt.connectSDK(coeffs.centerMid, 
    'FACE:blendShapeCt_face_geo.upLipTweakMid_curlIn_Ct', {0:0, -1:1})
    
    rt.connectSDK(coeffs.rightPinch, 
    'FACE:blendShapeCt_face_geo.upLipTweakPinch_curlOut_Rt', {0:0, 1:1})
    rt.connectSDK(coeffs.rightPinch, 
    'FACE:blendShapeCt_face_geo.upLipTweakPinch_curlIn_Rt', {0:0, -1:1})
    
    rt.connectSDK(coeffs.rightSneer, 
    'FACE:blendShapeCt_face_geo.upLipTweakSneer_curlOut_Rt', {0:0, 1:1})
    rt.connectSDK(coeffs.rightSneer, 
    'FACE:blendShapeCt_face_geo.upLipTweakSneer_curlIn_Rt', {0:0, -1:1})
    
    rt.connectSDK(coeffs.rightSide, 
    'FACE:blendShapeCt_face_geo.upLipTweakSide_curlOut_Rt', {0:0, 1:1})
    rt.connectSDK(coeffs.rightSide, 
    'FACE:blendShapeCt_face_geo.upLipTweakSide_curlIn_Rt', {0:0, -1:1})
    
    # lower lips
    coeffs = pm.group(em=True, n='CT_lowerLipCurls_coeffs')
    coeffs.addAttr('leftPinch', k=True)
    coeffs.addAttr('leftSneer', k=True)
    coeffs.addAttr('leftSide', k=True)
    coeffs.addAttr('centerMid', k=True)
    coeffs.addAttr('rightSide', k=True)
    coeffs.addAttr('rightSneer', k=True)
    coeffs.addAttr('rightPinch', k=True)
    rt.connectSDK('FACE:LT_lower_pinch_lip_ctrl.rx',
    coeffs.leftPinch, {-90:-1, 0:0, 90:1})
    rt.connectSDK('FACE:LT_lower_sneer_lip_ctrl.rx',
    coeffs.leftSneer, {-90:-1, 0:0, 90:1})
    rt.connectSDK('FACE:LT_lower_side_lip_ctrl.rx',
    coeffs.leftSide, {-90:-1, 0:0, 90:1})
    rt.connectSDK('FACE:CT_lower_lip_ctrl.rx',
    coeffs.centerMid, {-90:-1, 0:0, 90:1})
    rt.connectSDK('FACE:RT_lower_sneer_lip_ctrl.rx',
    coeffs.rightSneer, {-90:-1, 0:0, 90:1})
    rt.connectSDK('FACE:RT_lower_side_lip_ctrl.rx',
    coeffs.rightSide, {-90:-1, 0:0, 90:1})
    rt.connectSDK('FACE:RT_lower_pinch_lip_ctrl.rx',
    coeffs.rightPinch, {-90:-1, 0:0, 90:1})
    
    priCtls = [nt.Transform(u'FACE:RT_lower_sneer_lip_pri_ctrl'),
                nt.Transform(u'FACE:CT_lower_lip_pri_ctrl'),
                nt.Transform(u'FACE:LT_lower_sneer_lip_pri_ctrl')]
                
    attrs = ['leftPinch',
    'leftSneer',
    'leftSide',
    'centerMid',
    'rightSide',
    'rightSneer',
    'rightPinch']
           
    import rigger.utils.modulate as modulate     
    for pCtl in priCtls:
        token = pCtl.split(':')[1].split('_')[0]
        for attr in attrs:
            mod = modulate.addInput(coeffs.attr(attr), 0, token)
            rt.connectSDK(pCtl.rx, mod, {-90:-1, 0:0, 90:1})
            
    rt.connectSDK(coeffs.leftPinch, 
    'FACE:blendShapeCt_face_geo.lowLipTweakPinch_curlOut_Lf', {0:0, 1:1})
    rt.connectSDK(coeffs.leftPinch, 
    'FACE:blendShapeCt_face_geo.lowLipTweakPinch_curlIn_Lf', {0:0, -1:1})
    
    rt.connectSDK(coeffs.leftSneer, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSneer_curlOut_Lf', {0:0, 1:1})
    rt.connectSDK(coeffs.leftSneer, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSneer_curlIn_Lf', {0:0, -1:1})
    
    rt.connectSDK(coeffs.leftSide, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSide_curlOut_Lf', {0:0, 1:1})
    rt.connectSDK(coeffs.leftSide, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSide_curlIn_Lf', {0:0, -1:1})
    
    rt.connectSDK(coeffs.centerMid, 
    'FACE:blendShapeCt_face_geo.lowLipTweakMid_curlOut_Ct', {0:0, 1:1})
    rt.connectSDK(coeffs.centerMid, 
    'FACE:blendShapeCt_face_geo.lowLipTweakMid_curlIn_Ct', {0:0, -1:1})
    
    rt.connectSDK(coeffs.rightPinch, 
    'FACE:blendShapeCt_face_geo.lowLipTweakPinch_curlOut_Rt', {0:0, 1:1})
    rt.connectSDK(coeffs.rightPinch, 
    'FACE:blendShapeCt_face_geo.lowLipTweakPinch_curlIn_Rt', {0:0, -1:1})
    
    rt.connectSDK(coeffs.rightSneer, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSneer_curlOut_Rt', {0:0, 1:1})
    rt.connectSDK(coeffs.rightSneer, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSneer_curlIn_Rt', {0:0, -1:1})
    
    rt.connectSDK(coeffs.rightSide, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSide_curlOut_Rt', {0:0, 1:1})
    rt.connectSDK(coeffs.rightSide, 
    'FACE:blendShapeCt_face_geo.lowLipTweakSide_curlIn_Rt', {0:0, -1:1})

def addLowerLipCurls():
    coeffs = pm.group(em=True, n='CT_lowerLipCurls_add_coeffs')
    bsp = pm.PyNode('FACE:blendShapeCt_face_geo')
    
    coeffs.addAttr('leftPinch', k=True)
    coeffs.addAttr('leftSneer', k=True)
    coeffs.addAttr('leftSide', k=True)
    coeffs.addAttr('leftMid', k=True)
    coeffs.addAttr('centerMid', k=True)
    coeffs.addAttr('rightMid', k=True)
    coeffs.addAttr('rightSide', k=True)
    coeffs.addAttr('rightSneer', k=True)
    coeffs.addAttr('rightPinch', k=True)
    
    # direct connect main curls
    jawCtl = pm.PyNode('FACE:CT_jaw_pri_ctrl')
    rt.connectSDK(jawCtl.leftLowerLipCurl, coeffs.leftPinch, {-1:1, 0:0, 1:-1})
    rt.connectSDK(jawCtl.leftLowerLipCurl, coeffs.leftSneer, {-1:1, 0:0, 1:-1})
    rt.connectSDK(jawCtl.leftLowerLipCurl, coeffs.leftSide, {-1:1, 0:0, 1:-1})
    rt.connectSDK(jawCtl.leftLowerLipCurl, coeffs.leftMid, {-1:1, 0:0, 1:-1})
    rt.connectSDK(jawCtl.rightLowerLipCurl, coeffs.rightPinch, {-1:1, 0:0, 1:-1})
    rt.connectSDK(jawCtl.rightLowerLipCurl, coeffs.rightSneer, {-1:1, 0:0, 1:-1})
    rt.connectSDK(jawCtl.rightLowerLipCurl, coeffs.rightSide, {-1:1, 0:0, 1:-1})
    rt.connectSDK(jawCtl.rightLowerLipCurl, coeffs.rightMid, {-1:1, 0:0, 1:-1})
    
    # average for center
    pma = pm.createNode('plusMinusAverage', n='CT_lowerLipCurlsMidAvg_pma')
    pma.operation.set(3)
    coeffs.leftMid >> pma.input1D[0]
    coeffs.rightMid >> pma.input1D[1]
    pma.output1D >> coeffs.centerMid
    
    # disconnect secCtl rotateX
    ctls = [nt.Transform(u'FACE:RT_lower_pinch_lip_ctrl'),
            nt.Transform(u'FACE:RT_lower_sneer_lip_ctrl'),
            nt.Transform(u'FACE:RT_lower_side_lip_ctrl'),
            nt.Transform(u'FACE:CT_lower_lip_ctrl'),
            nt.Transform(u'FACE:LT_lower_side_lip_ctrl'),
            nt.Transform(u'FACE:LT_lower_sneer_lip_ctrl'),
            nt.Transform(u'FACE:LT_lower_pinch_lip_ctrl')]
    for ctl in ctls:
        outNode = ctl.r.outputs()[0]
        ctl.ry >> outNode.ry
        ctl.rz >> outNode.rz
        ctl.r // outNode.r
        
    # add secCtls to coeffs
    import rigger.utils.modulate as modulate
    reload(modulate)
    import utils.rigging as rt
    reload(rt)
    mod = modulate.addInput(coeffs.leftPinch, 0, '_secCtl')
    rt.connectSDK(ctls[6].rx, mod, {45:-1, 0:0, -45:1})
    mod = modulate.addInput(coeffs.leftSneer, 0, '_secCtl')
    rt.connectSDK(ctls[5].rx, mod, {45:-1, 0:0, -45:1})
    mod = modulate.addInput(coeffs.leftSide, 0, '_secCtl')
    rt.connectSDK(ctls[4].rx, mod, {45:-1, 0:0, -45:1})
    mod = modulate.addInput(coeffs.centerMid, 0, '_secCtl')
    rt.connectSDK(ctls[3].rx, mod, {45:-1, 0:0, -45:1})
    mod = modulate.addInput(coeffs.rightSide, 0, '_secCtl')
    rt.connectSDK(ctls[2].rx, mod, {45:-1, 0:0, -45:1})
    mod = modulate.addInput(coeffs.rightSneer, 0, '_secCtl')
    rt.connectSDK(ctls[1].rx, mod, {45:-1, 0:0, -45:1})
    mod = modulate.addInput(coeffs.rightPinch, 0, '_secCtl')
    rt.connectSDK(ctls[0].rx, mod, {45:-1, 0:0, -45:1})
    
    # connect to bsp
    coeffs.leftPinch >> bsp.lowLipPinchTweak_curl_Lf
    coeffs.leftSneer >> bsp.lowLipSneerTweak_curl_Lf
    coeffs.leftSide >> bsp.lowLipSideTweak_curl_Lf
    coeffs.centerMid >> bsp.lowLipTweak_curl_Ct
    coeffs.rightSide >> bsp.lowLipSideTweak_curl_Rt
    coeffs.rightSneer >> bsp.lowLipSneerTweak_curl_Rt
    coeffs.rightPinch >> bsp.lowLipPinchTweak_curl_Rt

def disableLipCtlsRotateX():
    '''
    '''
    # disable lip controls rotateX
    # use rotateX to drive 
    
    def useSurrogateXfo(ctl, blockChannels=[]):
        '''
        reroute priCtl matrix outputs
        assume priCtl only have local matrix outputs
        '''
        xfo = pm.group(em=True, n=ctl+'_surrXfo')
        ctlParent = ctl.getParent()
        ctlParent | xfo
        xfo.setMatrix(pm.dt.Matrix())
        
        allChannels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        for channel in allChannels:
            if channel not in blockChannels:
                ctl.attr(channel) >> xfo.attr(channel)
                
        # reroute matrix outputs
        allMatrixPlugs = ctl.matrix.outputs(p=True)
        for plug in allMatrixPlugs:
            xfo.matrix >> plug
            
    ctls = [nt.Transform(u'FACE:RT_upper_sneer_lip_pri_ctrl'),
            nt.Transform(u'FACE:CT_upper_lip_pri_ctrl'),
            nt.Transform(u'FACE:LT_upper_sneer_lip_pri_ctrl'),
            nt.Transform(u'FACE:LT_lower_sneer_lip_pri_ctrl'),
            nt.Transform(u'FACE:CT_lower_lip_pri_ctrl'),
            nt.Transform(u'FACE:RT_lower_sneer_lip_pri_ctrl')]
    for ctl in ctls:
        useSurrogateXfo(ctl, ['rx'])
    


def addCenterLipsPriCtls():
    '''
    '''
    import rigger.modules.priCtl as priCtl
    reload(priCtl)
    
    # add upper lip priCtl
    priBnd = nt.Joint(u'FACE:CT_upper_lip_bnd')
    secBnds = [nt.Joint(u'FACE:RT_upper_pinch_lip_bnd'),
                nt.Joint(u'FACE:RT_upper_sneer_lip_bnd'),
                nt.Joint(u'FACE:RT_upper_side_lip_bnd'),
                nt.Joint(u'FACE:CT_upper_lip_bnd'),
                nt.Joint(u'FACE:LT_upper_side_lip_bnd'),
                nt.Joint(u'FACE:LT_upper_sneer_lip_bnd'),
                nt.Joint(u'FACE:LT_upper_pinch_lip_bnd')]
    newCtl = priCtl.addPrimaryCtlToBnd(priBnd)
    for secBnd in secBnds:
        priCtl.connectBndToPriCtl(secBnd, newCtl, False)
        
    # get all priCtls driving this bnd
    attachedCtl = priBnd.attr('attached_pri_ctl').get()
    all_attrs = priBnd.listAttr(ud=True, l=True)
    all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weights' in attr.name()]
    all_priCtls = [attr.attrName().replace('_weights','') for attr in all_attrs]
    
    # let other priCtl drive the new priCtl
    for ctl in all_priCtls:
        # add namespace
        ctl = 'FACE:'+ctl
        if ctl != attachedCtl:
            priCtl.driveAttachedPriCtl(priBnd, pm.PyNode(ctl))
        else:
            # don't drive an attached ctl
            pass
            
    # new priCtl should also drive other priCtls      
    priCtl.driveAttachedPriCtl(nt.Joint(u'FACE:LT_upper_sneer_lip_bnd'), newCtl)
    priCtl.driveAttachedPriCtl(nt.Joint(u'FACE:RT_upper_sneer_lip_bnd'), newCtl)
    
    # add lower lip priCtl
    priBnd = nt.Joint(u'FACE:CT_lower_lip_bnd')
    secBnds = [nt.Joint(u'FACE:RT_lower_pinch_lip_bnd'),
                nt.Joint(u'FACE:RT_lower_sneer_lip_bnd'),
                nt.Joint(u'FACE:RT_lower_side_lip_bnd'),
                nt.Joint(u'FACE:CT_lower_lip_bnd'),
                nt.Joint(u'FACE:LT_lower_side_lip_bnd'),
                nt.Joint(u'FACE:LT_lower_sneer_lip_bnd'),
                nt.Joint(u'FACE:LT_lower_pinch_lip_bnd')]
    newCtl = priCtl.addPrimaryCtlToBnd(priBnd)
    for secBnd in secBnds:
        priCtl.connectBndToPriCtl(secBnd, newCtl, False)
        
    # get all priCtls driving this bnd
    attachedCtl = priBnd.attr('attached_pri_ctl').get()
    all_attrs = priBnd.listAttr(ud=True, l=True)
    all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weights' in attr.name()]
    all_priCtls = [attr.attrName().replace('_weights','') for attr in all_attrs]
    
    # let other priCtl drive the new priCtl
    for ctl in all_priCtls:
        # add namespace
        ctl = 'FACE:'+ctl
        if ctl != attachedCtl:
            priCtl.driveAttachedPriCtl(priBnd, pm.PyNode(ctl))
        else:
            # don't drive an attached ctl
            pass
            
    # new priCtl should also drive other priCtls      
    priCtl.driveAttachedPriCtl(nt.Joint(u'FACE:LT_lower_sneer_lip_bnd'), newCtl)
    priCtl.driveAttachedPriCtl(nt.Joint(u'FACE:RT_lower_sneer_lip_bnd'), newCtl)

def moveClaviclePivot():
    '''
    '''
    # move clavicle pivot
    newPos = pm.dt.Vector([-1.06312130585, 91.7071256576, -1.76231053414])
    moveNode = nt.Transform(u'Mathilda_rt_clavicleTrans_ctrl_zeroFrzGrp')
    jnt = nt.Joint(u'Mathilda_rt_clavicle_jnt')
    newPivot = pm.spaceLocator(n='rt_newpivot')
    newPivot.t.set(newPos)
    
    incomingCons = set(jnt.inputs(type='constraint'))
    outgoingCons = set(jnt.outputs(type='constraint'))
    outgoingCons = [con for con in outgoingCons if con not in incomingCons]
    
    wMatDict = {}
    # store world matrices for constrainees
    for con in outgoingCons:
        dag = con.ctx.outputs()[0]
        wMat = dag.getMatrix(worldSpace=True)
        wMatDict[con] = wMat
    
    mel.moveJointsMode(True)
    
    # assume move node is currently an identity matrix
    # so we can just use translate for offset
    newPos = newPivot.getTranslation(space='world')
    moveNode.setTranslation(newPos, space='world')
    
    # restore world matrices for constainees
    for con in outgoingCons:
        dag = con.ctx.outputs()[0]
        wMat = wMatDict[con]
        dag.setMatrix(wMat, worldSpace=True)
        pm.parentConstraint(jnt, dag, mo=True, e=True)
        
    mel.moveJointsMode(False)

def addFingerRotateControl():
    
    sides = ['Mathilda_lf_', 'Mathilda_rt_']
    fingers = ['index', 'middle', 'ring', 'pinky']
    sections = {'_b':'Mid', '_c':'Tip'}
    channels = ['rx', 'rz']
    
    for side in sides:
        for finger in fingers:
            for jntSec, ctlSec in sections.items():
                ctl = side + finger + ctlSec + '_fk_ctrl'
                ctl = pm.PyNode(ctl)
                jnt = side + finger + jntSec + '_jnt'
                jnt = pm.PyNode(jnt)
                for channel in channels:
                    mod = modulate.addInput(jnt.attr(channel), 0, '_ctlRotate')
                    ctl.attr(channel) >> mod
    
    fingers = ['thumb']
    channels = ['rx', 'ry']
    
    for side in sides:
        for finger in fingers:
            for jntSec, ctlSec in sections.items():
                ctl = side + finger + ctlSec + '_fk_ctrl'
                ctl = pm.PyNode(ctl)
                jnt = side + finger + jntSec + '_jnt'
                jnt = pm.PyNode(jnt)
                for channel in channels:
                    mod = modulate.addInput(jnt.attr(channel), 0, '_ctlRotate')
                    ctl.attr(channel) >> mod

def addEyelidReaders():
    '''
    '''
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:LT_eye_aimAt_bnd_19'), 
                                    pm.PyNode('FACE:LT_eye_aimJnts_grp_0'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:LT_eye_aimAt_bnd_15'), 
                                    pm.PyNode('FACE:LT_eye_aimJnts_grp_0'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:LT_eye_aimAt_bnd_12'), 
                                    pm.PyNode('FACE:LT_eye_aimJnts_grp_0'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:LT_eye_aimAt_bnd_9'), 
                                    pm.PyNode('FACE:LT_eye_aimJnts_grp_0'))
    
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:RT_eye_aimAt_bnd_19'), 
                                    pm.PyNode('FACE:RT_eye_aimJnts_grp_0'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:RT_eye_aimAt_bnd_16'), 
                                    pm.PyNode('FACE:RT_eye_aimJnts_grp_0'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:RT_eye_aimAt_bnd_13'), 
                                    pm.PyNode('FACE:RT_eye_aimJnts_grp_0'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:RT_eye_aimAt_bnd_9'), 
                                    pm.PyNode('FACE:RT_eye_aimJnts_grp_0'))

def addBrowReaders():
    '''
    '''
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:LT_in_brow_bnd'), 
                                    pm.PyNode('FACE:LT_in_brow_bnd_hm'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:LT_mid_brow_bnd'), 
                                    pm.PyNode('FACE:LT_mid_brow_bnd_hm'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:LT_out_brow_bnd'), 
                                    pm.PyNode('FACE:LT_out_brow_bnd_hm'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:RT_in_brow_bnd'), 
                                    pm.PyNode('FACE:RT_in_brow_bnd_hm'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:RT_mid_brow_bnd'), 
                                    pm.PyNode('FACE:RT_mid_brow_bnd_hm'))
    worldSpaceTranslateOffsetReader(pm.PyNode('FACE:RT_out_brow_bnd'), 
                                    pm.PyNode('FACE:RT_out_brow_bnd_hm'))

def worldSpaceTranslateOffsetReader(node, inverseNode):
    '''
    calculate a node's translate offset
    and add as attribute
    '''
    mm = pm.createNode('multMatrix', n=node+'_translateOffsetReader_mm')
    pmm = pm.createNode('pointMatrixMult', n=node+'_translateOffsetReader_pmm')
    
    node.worldMatrix >> mm.matrixIn[0]
    inverseNode.worldInverseMatrix >> mm.matrixIn[1]
    
    mm.matrixSum >> pmm.inMatrix
    
    for channel in ['x','y','z']:
        node.addAttr('translateOffsetReader_'+channel, k=True)
        pmm.attr('o'+channel) >> node.attr('translateOffsetReader_'+channel)

def modulateEyelashACS():
    '''
    '''
    """
    # left side 9 to 19
    acsNodes = [pm.PyNode('FACE:LT_eye_aimAt_bnd_%d_eyelash_acs'%jntId)
                for jntId in range(9,20)]
    
    drv = pm.PyNode('FACE:LT_eyelid_upper_pri_ctrl')
    drv.addAttr('eyelidDownMod')
    rt.connectSDK(drv.ty, drv.eyelidDownMod, {0:1, -0.5:0})
    
    for node in acsNodes:
        mod = modulate.multiplyInput(node.rz, 1, '_eyelidDownMod')
        drv.eyelidDownMod >> mod 
        """
    # right side 9 to 19
    acsNodes = [pm.PyNode('FACE:RT_eye_aimAt_bnd_%d_eyelash_acs'%jntId)
                for jntId in range(9,20)]
    
    drv = pm.PyNode('FACE:RT_eyelid_upper_pri_ctrl')
    drv.addAttr('eyelidDownMod')
    rt.connectSDK(drv.ty, drv.eyelidDownMod, {0:1, -0.5:0})
    
    for node in acsNodes:
        mod = modulate.multiplyInput(node.rz, 1, '_eyelidDownMod')
        drv.eyelidDownMod >> mod 
        
    

def addAllEyelashBnds():
    '''
    '''
    # left side 9 to 19
    baseName = 'FACE:LT_eye_aimAt_bnd_'
    for jntId in range(9,20):
        addEyelashBnds(baseName+str(jntId))
        
    # right side 9 to 19
    baseName = 'FACE:RT_eye_aimAt_bnd_'
    for jntId in range(9,20):
        addEyelashBnds(baseName+str(jntId))

def addEyelashBnds(eyelidBnd):
    '''
    '''
    pm.select(cl=True)
    bnd = pm.joint(n=eyelidBnd+'_eyelash_bnd')
    bnd.radius.set(0.1)
    bne = pm.joint(n=eyelidBnd+'_eyelash_bne', p=(0.5,0,0))
    bne.radius.set(0.1)
    
    offset = pm.group(em=True, n=eyelidBnd+'_eyelash_offset')
    acs = pm.group(offset, n=eyelidBnd+'_eyelash_acs')
    grp = pm.group(acs, n=eyelidBnd+'_eyelash_grp')
    
    offset | bnd
    
    eyelidBnd = pm.PyNode(eyelidBnd)
    mat = eyelidBnd.getMatrix(worldSpace=True)
    grp.setMatrix(mat, worldSpace=True)
    
    eyelidBnd | grp
    
    

def modulateFleshyEyesUp():
    '''
    DONT USE THIS
    '''
    node = nt.Transform(u'FACE:LT_eyeball_bnd')
    node.addAttr('finalVectorAngle', k=True)
    # replace outputs
    outAttrs = node.vectorAngle.outputs(p=True)
    node.vectorAngle >> node.finalVectorAngle
    for plug in outAttrs:
        node.finalVectorAngle >> plug
    # modulate finalVectorAngle
    mod = modulate.multiplyInput(node.finalVectorAngle, 1, '_eyeY_mod')
    rt.connectSDK('FACE:LT_eyeball_bnd.paramNormalized', mod, {0:0.2, 0.4:1, 0.6:1, 1:0.2})


def addEyelashCollideAimLocGo():
    '''
    '''
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_inner_upper_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_in_brow_ctrl')
    addEyelashCollideAimLoc(eyelidCtl, collideCtl)
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_upper_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_mid_brow_ctrl')
    addEyelashCollideAimLoc(eyelidCtl, collideCtl)
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_outer_upper_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_out_brow_ctrl')
    addEyelashCollideAimLoc(eyelidCtl, collideCtl)
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_outer_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_out_brow_ctrl')
    addEyelashCollideAimLoc(eyelidCtl, collideCtl)

def addEyelashBnd(eyelashBase, aimLoc):
    '''
    import rigger.builds.mathilda.hacks as hacks
    reload(hacks)
    
    eyelashBase = nt.Transform(u'FACE:LT_eye_aimAt_bnd_15')
    aimLoc = nt.Transform(u'FACE:LT_eyelid_upper_ctrl_aimLoc')
    hacks.addEyelashBnd(eyelashBase, aimLoc)
    
    eyelashBase = nt.Transform(u'FACE:LT_eye_aimAt_bnd_18')
    aimLoc = nt.Transform(u'FACE:LT_eyelid_inner_upper_ctrl_aimLoc')
    hacks.addEyelashBnd(eyelashBase, aimLoc)
    
    eyelashBase = nt.Transform(u'FACE:LT_eye_aimAt_bnd_12')
    aimLoc = nt.Transform(u'FACE:LT_eyelid_outer_upper_ctrl_aimLoc')
    hacks.addEyelashBnd(eyelashBase, aimLoc)
    
    eyelashBase = nt.Transform(u'FACE:LT_eye_aimAt_bnd_9')
    aimLoc = nt.Transform(u'FACE:LT_eyelid_outer_ctrl_aimLoc')
    hacks.addEyelashBnd(eyelashBase, aimLoc)
    '''
    pm.select(cl=True)
    bnd = pm.joint(n=aimLoc.replace('_aimLoc', 'eyelash_bnd'))
    
    mat = eyelashBase.getMatrix(worldSpace=True)
    bnd.setMatrix(mat, worldSpace=True)
    eyelashBase | bnd
    
    bne = pm.joint(n=aimLoc.replace('_aimLoc', 'eyelash_bne'),
                   p=aimLoc.getTranslation(space='world'))
    
    #orient jnt
    pm.makeIdentity(bnd, a=True)
    bnd.orientJoint('xyz', sao='yup')
    
    # aim constraint
    pm.aimConstraint(aimLoc, bnd, aim=(1,0,0))

def addEyelashCollideAimLoc(jnt, eyelidCtl, collideCtl):
    '''
    eyeCtl - actually bnd of eye
    jnt - actually a loc (for aiming)
    
    position 4 joints first, then run:
    jnt = nt.Transform(u'locator1')
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_upper_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_mid_brow_ctrl')
    hacks.addEyelashCollideAimLoc(jnt, eyelidCtl, collideCtl)
    
    jnt = nt.Transform(u'locator2')
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_inner_upper_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_in_brow_ctrl')
    hacks.addEyelashCollideAimLoc(jnt, eyelidCtl, collideCtl)
    
    jnt = nt.Transform(u'locator3')
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_outer_upper_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_out_brow_ctrl')
    hacks.addEyelashCollideAimLoc(jnt, eyelidCtl, collideCtl)
    
    jnt = nt.Transform(u'locator4')
    eyelidCtl = nt.Transform(u'FACE:LT_eyelid_outer_ctrl')
    collideCtl = nt.Transform(u'FACE:LT_out_brow_ctrl')
    hacks.addEyelashCollideAimLoc(jnt, eyelidCtl, collideCtl)
    '''
    name = eyelidCtl.replace('_bnd','_eyelash')
    jnt.rename(name+'_aimLoc')
    # build hierarchy
    # one nodes on the collideCtl
    grp = pm.group(em=True, n=name+'_upLimit_grp')
    
    # two nodes on the eyelidCtl
    offset = pm.group(em=True, n=name+'_offset')
    collide = pm.group(offset, n=name+'_collide')
    mat = jnt.getMatrix(worldSpace=True)
    collide.setMatrix(mat, worldSpace=True)
    offset | jnt
    
    # get bnds in local-rig space
    eyelidBnd = pm.PyNode(eyelidCtl.replace('_ctrl','_bnd'))
    collideBnd = pm.PyNode(collideCtl.replace('_ctrl','_bnd'))
    
    # constraint to collideBnd
#     dcm = pm.createNode('decomposeMatrix', n=name+'_constraintCollide_dcm')
#     collideBnd.worldMatrix >> dcm.inputMatrix
#     dcm.outputTranslate >> grp.t
#     dcm.outputRotate >> grp.r
    pm.pointConstraint(collideBnd, grp)
    
    # constraint to collideBnd
#     dcm = pm.createNode('decomposeMatrix', n=name+'_constraintEyelid_dcm')
#     mm = pm.createNode('multMatrix', n=name+'_constraintEyelid_mm')
#     eyelidBnd.worldMatrix >> mm.matrixIn[0]
#     collide.parentInverseMatrix >> mm.matrixIn[1]
#     mm.matrixSum>> dcm.inputMatrix
#     dcm.outputTranslate >> collide.t
#     dcm.outputRotate >> collide.r
    pm.parentConstraint(eyelidBnd, collide, mo=True)
    grp | collide
    
    # ceiling val
    jnt.addAttr('transY_ceiling', at='float', k=True)
    collide.maxTransYLimitEnable.set(True)
    jnt.attr('transY_ceiling') >> collide.maxTransYLimit
    
    
    

def connectHairToGlobalScale():
    '''
    import rigger.builds.mathilda.hacks as hacks
    reload(hacks)
    hacks.connectHairToGlobalScale()
    '''
    
    crvGrp = nt.Transform(u'CT_hairStartCurves_grp')
    mesh = nt.Transform(u'CT_headHair_geo')
    root = nt.Transform(u'Mathilda_root_ctrl')
    
    # connect masterscale to scale curves
    root.masterScale >> crvGrp.sx
    root.masterScale >> crvGrp.sy
    root.masterScale >> crvGrp.sz
    
    # multiply matrix for follicles
    mm = pm.createNode('multMatrix', n='CT_hairFolliclesGlobalScale_mm')
    mesh.worldMatrix >> mm.matrixIn[0]
    crvGrp.worldInverseMatrix >> mm.matrixIn[1]
    
    # get all follicles
    allFols = crvGrp.getChildren(ad=True, type='follicle')
    
    # connect worldMatrix
    for fol in allFols:
        mm.matrixSum >> fol.inputWorldMatrix
    
    # scale hairSystems
    attrsToScale = ['backHairSystemShape.clumpWidth',
                    'backHairSystemShape.hairWidth',
                    'frontHairSystemShape.clumpWidth',
                    'frontHairSystemShape.hairWidth']
    for attr in attrsToScale:
        mod = modulate.multiplyInput(attr, 1, '_gscale')
        root.masterScale >> mod
    

def connectHairFolliclesToMesh():
    '''
    for each follicle under hairCrvsGrp,
    - unparent the child curve to WS (to maintain ws-position)
    - find closest uv on mesh
    - set uv on follicle
    - mesh.worldMatrix >> follicle.inputWorldMatrix
    - mesh.outMesh >> follicle.inputMesh
    - follicle.outT/R >> follicleDag.t/r
    - reparent curve under follicle
    '''
    mesh = nt.Transform(u'CT_headCollide_geo')
    hairCrvsGrp = nt.Transform(u'CT_hairCurves_grp')
    
    allFollicles = hairCrvsGrp.getChildren(ad=True, type='follicle')
    
    for eachFol in allFollicles:
        folDag = eachFol.getParent()
        # assume only one curve per follicle
        crvDag = folDag.getChildren(ad=True, type='transform')[0]
        
        # unparent to maintain WS
        crvDag.setParent(None)
        
        # calculate UVs
        startPt = crvDag.cv[0].getPosition()
        uVal, vVal = mesh.getUVAtPoint(startPt)
        uvSet = mesh.getCurrentUVSetName()
        eachFol.parameterU.set(uVal)
        eachFol.parameterV.set(vVal)
        eachFol.startDirection.set(1)
        
        # connect mesh to follicle
        mesh.worldMatrix >> eachFol.inputWorldMatrix
        mesh.outMesh >> eachFol.inputMesh
        
        # connect follicle t/r
        eachFol.outTranslate >> folDag.t
        eachFol.outRotate >> folDag.r
        
        # parent curve under follicle
        folDag | crvDag
        

def faceEvaluationSwitch():
    '''
    find all deformers on geos
    when switchAttr = False,
    set nodes to HasNoEffect
    '''
    geos = [nt.Transform(u'FACE:LT_eyelashes_geo'),
            nt.Transform(u'FACE:RT_eyelashes_geo'),
            nt.Transform(u'FACE:CT_face_geo'),
            nt.Transform(u'CT_face_geo_lattice'),
            nt.Transform(u'CT_face_geo_latticeWeights')]
    
    # add switch to face ctrl
    faceCtl = pm.PyNode('FACE:CT_face_ctrl')
    faceCtl.addAttr('disableFace', at='bool', dv=0)
    faceCtl.attr('disableFace').showInChannelBox(True)
    
    for geo in geos:
        dfmNames = mel.findRelatedDeformer(geo)
        for dfmName in dfmNames:
            dfm = pm.PyNode(dfmName)
            faceCtl.attr('disableFace') >> dfm.nodeState
            
    # also hide inner mouth geo
    mouthGeoGrp = pm.PyNode('FACE:CT_mouth_geo_grp')
    rt.connectSDK(faceCtl.attr('disableFace'), 
                  mouthGeoGrp.v, {0:1, 1:0})
        

def addJacketCollarNoRotBinds():
    # add collar joint no-rotate
    collarjnts = pm.ls(sl=True)
    
    for jnt in collarjnts:
        pm.select(cl=True)
        noRotJnt = pm.joint(n=jnt.replace('_jnt', '_norot_bnd'))
        wMat = jnt.getMatrix(worldSpace=True)
        noRotJnt.setMatrix(wMat, worldSpace=True)
        pm.makeIdentity(noRotJnt, a=True)
        noRotJnt.radius.set(0.5)
        grp = jnt.getParent(3)
        grp | noRotJnt
        pm.pointConstraint(jnt, noRotJnt)

def addJacketCollarRig():
    # jacket collar rig
    collarjnts = pm.ls(sl=True)
    # add hm, grp and auto nulls
    for jnt in collarjnts:
        ctl = pm.circle(r=0.5, sweep=359, normal=(1,0,0), n=jnt.replace('_jnt', '_ctl'))
        auto = pm.group(ctl, n=jnt.replace('_jnt', '_auto'))
        grp = pm.group(auto, n=jnt.replace('_jnt', '_grp'))
        hm = pm.group(grp, n=jnt.replace('_jnt', '_hm'))
        wMat = jnt.getMatrix(worldSpace=True)
        hm.setMatrix(wMat, worldSpace=True)
        collarparent = jnt.getParent()
        collarparent | hm
        auto | jnt
    # auto
    import rigger.modules.poseReader as poseReader
    reload(poseReader)
    xfo = nt.Joint(u'Mathilda_neck_jnt')
    poseReader.radial_pose_reader(xfo, (1,0,0), (1,0,0))
    # connect auto to sdks
    import utils.rigging as rt
    import rigger.utils.modulate as modulate
    angleMult = pm.PyNode('Mathilda_neck_jnt.vectorAngle')
    # Left collar A
    rt.connectSDK('Mathilda_neck_jnt.param', 'LT_collarA_auto.rz',
                    {3.25:0, 4.6:50, 5.5:0})
    mod = modulate.multiplyInput(pm.PyNode('LT_collarA_auto.rz'), 0, '_angle')
    angleMult >> mod
    # Letf collar B
    rt.connectSDK('Mathilda_neck_jnt.param', 'LT_collarB_auto.rz',
                    {4:0, 5:180, 6:180, 7:0})
    mod = modulate.multiplyInput(pm.PyNode('LT_collarB_auto.rz'), 0, '_angle')
    angleMult >> mod
    # Letf collar C
    rt.connectSDK('Mathilda_neck_jnt.param', 'LT_collarC_auto.rz',
                    {0:200, 1.4:0, 4:0, 5.5:200, 6.6:280, 8:0})
    mod = modulate.multiplyInput(pm.PyNode('LT_collarC_auto.rz'), 0, '_angle')
    angleMult >> mod
    # center collar
    rt.connectSDK('Mathilda_neck_jnt.param', 'CT_collar_auto.rz',
                    {0:320, 2.5:0, 5.5:0, 8:320})
    mod = modulate.multiplyInput(pm.PyNode('CT_collar_auto.rz'), 0, '_angle')
    angleMult >> mod
    # right collar A
    rt.connectSDK('Mathilda_neck_jnt.param', 'RT_collarA_auto.rz',
                    {4.75:0, 3.4:50, 2.5:0})
    mod = modulate.multiplyInput(pm.PyNode('RT_collarA_auto.rz'), 0, '_angle')
    angleMult >> mod
    # right collar B
    rt.connectSDK('Mathilda_neck_jnt.param', 'RT_collarB_auto.rz',
                    {4:0, 3:180, 2:180, 1:0})
    mod = modulate.multiplyInput(pm.PyNode('RT_collarB_auto.rz'), 0, '_angle')
    angleMult >> mod
    # right collar C
    rt.connectSDK('Mathilda_neck_jnt.param', 'RT_collarC_auto.rz',
                    {0:200, 6.6:0, 4:0, 2.5:200, 1.4:280, 8:0})
    mod = modulate.multiplyInput(pm.PyNode('RT_collarC_auto.rz'), 0, '_angle')
    angleMult >> mod
    
    pm.select(pm.PyNode(u'Mathilda_neck_jnt.param').outputs())