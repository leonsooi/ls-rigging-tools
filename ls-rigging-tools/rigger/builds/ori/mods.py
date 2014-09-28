'''
Created on Aug 24, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

import rigger.modules.priCtl as priCtl
reload(priCtl)

import utils.rigging as rt
reload(rt)

import rigger.utils.modulate as modulate 

def addUpperLipCurlsSDKs():
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
    rt.connectSDK('LT_upperPinch_lip_ctrl.rx',
    coeffs.leftPinch, {-90:1, 0:0, 90:-1})
    rt.connectSDK('LT_upperSneer_lip_ctrl.rx',
    coeffs.leftSneer, {-90:1, 0:0, 90:-1})
    rt.connectSDK('LT_upperSide_lip_ctrl.rx',
    coeffs.leftSide, {-90:1, 0:0, 90:-1})
    rt.connectSDK('CT_upper_lip_ctrl.rx',
    coeffs.centerMid, {-90:1, 0:0, 90:-1})
    rt.connectSDK('RT_upperSneer_lip_ctrl.rx',
    coeffs.rightSneer, {-90:1, 0:0, 90:-1})
    rt.connectSDK('RT_upperSide_lip_ctrl.rx',
    coeffs.rightSide, {-90:1, 0:0, 90:-1})
    rt.connectSDK('RT_upperPinch_lip_ctrl.rx',
    coeffs.rightPinch, {-90:1, 0:0, 90:-1})
    
    priCtls = [nt.Transform(u'RT_upperSneer_lip_pri_ctrl'),
                nt.Transform(u'CT_upper_lip_pri_ctrl'),
                nt.Transform(u'LT_upperSneer_lip_pri_ctrl')]
                
    attrs = ['leftPinch',
    'leftSneer',
    'leftSide',
    'centerMid',
    'rightSide',
    'rightSneer',
    'rightPinch']
           
        
    for pCtl in priCtls:
        token = pCtl.split('_')[0]
        for attr in attrs:
            mod = modulate.addInput(coeffs.attr(attr), 0, token)
            rt.connectSDK(pCtl.rx, mod, {-90:1, 0:0, 90:-1})
            
    rt.connectSDK(coeffs.leftPinch, 
    'blendShapeCt_face_geo.lipCurlIn_upperPinch_Lf', {0:0, -1:1})
    rt.connectSDK(coeffs.leftSneer, 
    'blendShapeCt_face_geo.lipCurlIn_upperSneer_Lf', {0:0, -1:1})
    rt.connectSDK(coeffs.leftSide, 
    'blendShapeCt_face_geo.lipCurlIn_upperSide_Lf', {0:0, -1:1})
    rt.connectSDK(coeffs.centerMid, 
    'blendShapeCt_face_geo.lipCurlIn_upper_Ct', {0:0, -1:1})
    rt.connectSDK(coeffs.rightPinch, 
    'blendShapeCt_face_geo.lipCurlIn_upperPinch_Rt', {0:0, -1:1})
    rt.connectSDK(coeffs.rightSneer, 
    'blendShapeCt_face_geo.lipCurlIn_upperSneer_Rt', {0:0, -1:1})
    rt.connectSDK(coeffs.rightSide, 
    'blendShapeCt_face_geo.lipCurlIn_upperSide_Rt', {0:0, -1:1})

def addLowerLipCurlsSDKs():
    '''
    '''
    # lower lips
    coeffs = pm.group(em=True, n='CT_lowerLipCurls_coeffs')
    coeffs.addAttr('leftPinch', k=True)
    coeffs.addAttr('leftSneer', k=True)
    coeffs.addAttr('leftSide', k=True)
    coeffs.addAttr('centerMid', k=True)
    coeffs.addAttr('rightSide', k=True)
    coeffs.addAttr('rightSneer', k=True)
    coeffs.addAttr('rightPinch', k=True)
    rt.connectSDK('LT_lowerPinch_lip_ctrl.rx',
    coeffs.leftPinch, {-90:-1, 0:0, 90:1})
    rt.connectSDK('LT_lowerSneer_lip_ctrl.rx',
    coeffs.leftSneer, {-90:-1, 0:0, 90:1})
    rt.connectSDK('LT_lowerSide_lip_ctrl.rx',
    coeffs.leftSide, {-90:-1, 0:0, 90:1})
    rt.connectSDK('CT_lower_lip_ctrl.rx',
    coeffs.centerMid, {-90:-1, 0:0, 90:1})
    rt.connectSDK('RT_lowerSneer_lip_ctrl.rx',
    coeffs.rightSneer, {-90:-1, 0:0, 90:1})
    rt.connectSDK('RT_lowerSide_lip_ctrl.rx',
    coeffs.rightSide, {-90:-1, 0:0, 90:1})
    rt.connectSDK('RT_lowerPinch_lip_ctrl.rx',
    coeffs.rightPinch, {-90:-1, 0:0, 90:1})
    
    priCtls = [nt.Transform(u'RT_lowerSneer_lip_pri_ctrl'),
                nt.Transform(u'CT_lower_lip_pri_ctrl'),
                nt.Transform(u'LT_lowerSneer_lip_pri_ctrl')]
                
    attrs = ['leftPinch',
    'leftSneer',
    'leftSide',
    'centerMid',
    'rightSide',
    'rightSneer',
    'rightPinch']
           
        
    for pCtl in priCtls:
        token = pCtl.split('_')[0]
        for attr in attrs:
            mod = modulate.addInput(coeffs.attr(attr), 0, token)
            rt.connectSDK(pCtl.rx, mod, {-90:-1, 0:0, 90:1})
            
    rt.connectSDK(coeffs.leftPinch, 
    'blendShapeCt_face_geo.lipCurlIn_lowerPinch_Lf', {0:0, -1:1})
    rt.connectSDK(coeffs.leftSneer, 
    'blendShapeCt_face_geo.lipCurlIn_lowerSneer_Lf', {0:0, -1:1})
    rt.connectSDK(coeffs.leftSide, 
    'blendShapeCt_face_geo.lipCurlIn_lowerSide_Lf', {0:0, -1:1})
    rt.connectSDK(coeffs.centerMid, 
    'blendShapeCt_face_geo.lipCurlIn_lower_Ct', {0:0, -1:1})
    rt.connectSDK(coeffs.rightPinch, 
    'blendShapeCt_face_geo.lipCurlIn_lowerPinch_Rt', {0:0, -1:1})
    rt.connectSDK(coeffs.rightSneer, 
    'blendShapeCt_face_geo.lipCurlIn_lowerSneer_Rt', {0:0, -1:1})
    rt.connectSDK(coeffs.rightSide, 
    'blendShapeCt_face_geo.lipCurlIn_lowerSide_Rt', {0:0, -1:1})


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
            
    ctls = [nt.Transform(u'RT_upperSneer_lip_pri_ctrl'),
            nt.Transform(u'CT_upper_lip_pri_ctrl'),
            nt.Transform(u'LT_upperSneer_lip_pri_ctrl'),
            nt.Transform(u'LT_lowerSneer_lip_pri_ctrl'),
            nt.Transform(u'CT_lower_lip_pri_ctrl'),
            nt.Transform(u'RT_lowerSneer_lip_pri_ctrl')]
    for ctl in ctls:
        useSurrogateXfo(ctl, ['rx'])

def flipScaleYOnControl(ctl, ctlGrp):
    '''
    '''
    # create new control
    newCtl = ctl.duplicate(n=ctl+'_new')[0]
    origName = ctl.name()
    ctl.rename(ctl+'_real')
    newCtl.rename(origName)
    # place it under same parent
    # to get the same xforms
    ctlParent = ctl.getParent()
    
    # attribute to switch between real and fake controls
    try:
        realAttr = ctlGrp.realRightControls
        fakeAttr = ctlGrp.fakeRightControls
    except:
        ctlGrp.addAttr('realRightControls', at='bool', dv=0)
        ctlGrp.realRightControls.set(cb=True)
        realAttr = ctlGrp.realRightControls
        ctlGrp.addAttr('fakeRightControls', at='bool', dv=1)
        ctlGrp.fakeRightControls.set(cb=True)
        fakeAttr = ctlGrp.fakeRightControls
        
    def connectShapesVis(ctl, attr):
        for shape in ctl.getChildren(s=True):
            attr >> shape.v
    
    connectShapesVis(ctl, realAttr)
    connectShapesVis(newCtl, fakeAttr)
    realAttr >> ctl.getShape().v
    fakeAttr >> newCtl.getShape().v
    
    # extra xfo to flip scale
    flipXfo = pm.group(em=True, n=origName+'_scaleY')
    ctlParent | flipXfo
    flipXfo.setMatrix(pm.dt.Matrix())
    flipXfo | newCtl
    flipXfo.sy.set(-1)
    '''
    # mirror ctl shape
    leftCtl = pm.PyNode(origName.replace('RT_', 'LT_'))
    pm.select(leftCtl, newCtl)
    try:
        mel.abRTServiceWireReplaceUI("MirrorFromTo")
    except:
        mel.source('abAutoRig')
        mel.abRTWireReplaceUI();
        mel.abRTServiceWireReplaceUI("MirrorFromTo");
    '''
    # connect back to ctl via mds
    tmd = pm.createNode('multiplyDivide', n=ctl+'_revTranslate')
    newCtl.t >> tmd.input1
    tmd.input2.set(1,-1,1)
    tmd.outputX >> ctl.tx
    tmd.outputY >> ctl.ty
    tmd.outputZ >> ctl.tz
    rmd = pm.createNode('multiplyDivide', n=ctl+'_revRotate')
    newCtl.r >> rmd.input1
    rmd.input2.set(-1,1,-1)
    rmd.outputX >> ctl.rx
    rmd.outputY >> ctl.ry
    rmd.outputZ >> ctl.rz
    newCtl.s >> ctl.s


def flipScaleXOnControl(ctl, ctlGrp):
    '''
    '''
    # create new control
    newCtl = ctl.duplicate(n=ctl+'_new')[0]
    origName = ctl.name()
    ctl.rename(ctl+'_real')
    newCtl.rename(origName)
    # place it under same parent
    # to get the same xforms
    ctlParent = ctl.getParent()
    
    # attribute to switch between real and fake controls
    try:
        realAttr = ctlGrp.realRightControls
        fakeAttr = ctlGrp.fakeRightControls
    except:
        ctlGrp.addAttr('realRightControls', at='bool', dv=0)
        ctlGrp.realRightControls.set(cb=True)
        realAttr = ctlGrp.realRightControls
        ctlGrp.addAttr('fakeRightControls', at='bool', dv=1)
        ctlGrp.fakeRightControls.set(cb=True)
        fakeAttr = ctlGrp.fakeRightControls
        
    def connectShapesVis(ctl, attr):
        for shape in ctl.getChildren(s=True):
            attr >> shape.v
    
    connectShapesVis(ctl, realAttr)
    connectShapesVis(newCtl, fakeAttr)
    realAttr >> ctl.getShape().v
    fakeAttr >> newCtl.getShape().v
    
    # extra xfo to flip scale
    flipXfo = pm.group(em=True, n=origName+'_scaleX')
    ctlParent | flipXfo
    flipXfo.setMatrix(pm.dt.Matrix())
    flipXfo | newCtl
    flipXfo.sx.set(-1)
    
    # mirror ctl shape
    leftCtl = pm.PyNode(origName.replace('RT_', 'LT_'))
    pm.select(leftCtl, newCtl)
    try:
        mel.abRTServiceWireReplaceUI("MirrorFromTo")
    except:
        mel.source('abAutoRig')
        mel.abRTWireReplaceUI();
        mel.abRTServiceWireReplaceUI("MirrorFromTo");
    
    # connect back to ctl via mds
    tmd = pm.createNode('multiplyDivide', n=ctl+'_revTranslate')
    newCtl.t >> tmd.input1
    tmd.input2.set(-1,1,1)
    tmd.outputX >> ctl.tx
    tmd.outputY >> ctl.ty
    tmd.outputZ >> ctl.tz
    rmd = pm.createNode('multiplyDivide', n=ctl+'_revRotate')
    newCtl.r >> rmd.input1
    rmd.input2.set(1,-1,-1)
    rmd.outputX >> ctl.rx
    rmd.outputY >> ctl.ry
    rmd.outputZ >> ctl.rz
    newCtl.s >> ctl.s
    

def reverseTxOnControl(ctl):
    '''
    ctl = pm.PyNode('RT_lowerSneer_lip_pri_ctrl')
    reverseTxOnControl(ctl)
    '''
    newCtl = ctl.duplicate(n=ctl+'_new')[0]
    newCtl.setParent(None)
    ctl.v.set(0)
    
    newCth = pm.group(em=True, n=newCtl+'_hm')
    newCth.setMatrix(newCtl.getMatrix())
    newCtg = pm.group(em=True, n=newCtl+'_ctg')
    newCtg.setMatrix(newCth.getMatrix())
    newCth | newCtg | newCtl
    
    # new control to follow old control parent
    decMat = pm.createNode('decomposeMatrix', n=ctl+'_parentMat')
    ctl.parentMatrix >> decMat.inputMatrix
    decMat.outputTranslate >> newCth.t
    decMat.outputRotate >> newCth.r
    decMat.outputScale >> newCth.s
    
    newCtg.ry.set(180)
    leftCtl = pm.PyNode(ctl.replace('RT_', 'LT_'))
    pm.select(leftCtl, newCtl)
    mel.abRTServiceWireReplaceUI("MirrorFromTo");
    
    # connect back to ctl via mds
    tmd = pm.createNode('multiplyDivide', n=ctl+'_revTranslate')
    newCtl.t >> tmd.input1
    tmd.input2.set(-1,1,-1)
    tmd.output >> ctl.t
    rmd = pm.createNode('multiplyDivide', n=ctl+'_revRotate')
    newCtl.r >> rmd.input1
    rmd.input2.set(-1,1,-1)
    rmd.output >> ctl.r
    newCtl.s >> ctl.s

def replaceEyelidAimAtCurve():
    '''
    '''
    # transfer pocis from oldcrv to newcrv
    oldCrv = nt.Transform(u'LT_eye_aimAt_crv_0')
    newCrv = nt.Transform(u'LT_eyelids_aimAt_crv_0')
    
    outPocis = oldCrv.worldSpace.outputs(type='pointOnCurveInfo', p=True)
    for poci in outPocis:
        newCrv.worldSpace >> poci

def connectEyelidLocsToBlinkAttr():
    '''
    '''
    blinkAttr = pm.PyNode('LT_eye_ctl.blink')

    locA, locB = pm.ls(sl=True)[:2]
    
    # get center pt between two locs (from their pocis)
    pociA = locA.t.inputs(type='pointOnCurveInfo', p=True)[0]
    pociB = locB.t.inputs(type='pointOnCurveInfo', p=True)[0]
    pma = pm.createNode('plusMinusAverage', n=locA+'_avgPos_pma')
    pma.operation.set(3)
    pociA >> pma.input3D[0]
    pociB >> pma.input3D[1]
    # blend positions
    blendA = pm.createNode('blendColors', n=locA+'_blendPos_bld')
    pma.output3D >> blendA.color1
    pociA >> blendA.color2
    blinkAttr >> blendA.blender
    blendA.output >> locA.t
    blendB = pm.createNode('blendColors', n=locB+'_blendPos_bld')
    pma.output3D >> blendB.color1
    pociB >> blendB.color2
    blinkAttr >> blendB.blender
    blendB.output >> locB.t

def addInOutEyelidCorners():
    # add primarys for eyelids in/out
    bnd = nt.Joint(u'LT_inner_eyelid_bnd')
    pCtl = priCtl.addPrimaryCtlToBnd(bnd)
    bndsToConnect = [nt.Joint(u'LT_innerUpper_eyelid_bnd'),
                    nt.Joint(u'LT_inner_eyelid_bnd'),
                    nt.Joint(u'LT_innerLower_eyelid_bnd'),
                    nt.Joint(u'LT_inCorner_eyeSocket_bnd')]
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    
    bnd = nt.Joint(u'LT_outer_eyelid_bnd')
    pCtl = priCtl.addPrimaryCtlToBnd(bnd)
    bndsToConnect = [nt.Joint(u'LT_outerUpper_eyelid_bnd'),
                    nt.Joint(u'LT_outer_eyelid_bnd'),
                    nt.Joint(u'LT_outerLower_eyelid_bnd'),
                    nt.Joint(u'LT_outCorner_eyeSocket_bnd')]
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    
    bnd = nt.Joint(u'RT_inner_eyelid_bnd')
    pCtl = priCtl.addPrimaryCtlToBnd(bnd)
    bndsToConnect = [nt.Joint(u'RT_innerUpper_eyelid_bnd'),
                    nt.Joint(u'RT_inner_eyelid_bnd'),
                    nt.Joint(u'RT_innerLower_eyelid_bnd'),
                    nt.Joint(u'RT_inCorner_eyeSocket_bnd')]
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    
    bnd = nt.Joint(u'RT_outer_eyelid_bnd')
    pCtl = priCtl.addPrimaryCtlToBnd(bnd)
    bndsToConnect = [nt.Joint(u'RT_outerUpper_eyelid_bnd'),
                    nt.Joint(u'RT_outer_eyelid_bnd'),
                    nt.Joint(u'RT_outerLower_eyelid_bnd'),
                    nt.Joint(u'RT_outCorner_eyeSocket_bnd')]
    priCtl.connectBndsToPriCtl(bndsToConnect, pCtl)
    
    '''
    # may also need to be driven by eye movers
    import rigger.modules.priCtl as priCtl
    reload(priCtl)
    
    newCtl = nt.Transform(u'LT__eyeMover_pri_ctrl')
    priCtl.driveAttachedPriCtl(nt.Joint(u'LT_outer_eyelid_bnd'), newCtl)
    newCtl = nt.Transform(u'LT__eyeMover_pri_ctrl')
    priCtl.driveAttachedPriCtl(nt.Joint(u'LT_inner_eyelid_bnd'), newCtl)
    
    newCtl = nt.Transform(u'RT__eyeMover_pri_ctrl')
    priCtl.driveAttachedPriCtl(nt.Joint(u'RT_outer_eyelid_bnd'), newCtl)
    newCtl = nt.Transform(u'RT__eyeMover_pri_ctrl')
    priCtl.driveAttachedPriCtl(nt.Joint(u'RT_inner_eyelid_bnd'), newCtl)
    '''