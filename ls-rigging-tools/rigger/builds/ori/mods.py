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