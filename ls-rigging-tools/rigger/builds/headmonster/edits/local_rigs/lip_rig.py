'''
Created on Sep 29, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

#===============================================================================
# Add bnds for local rig
#===============================================================================
bnds = [nt.Joint(u'LT_lowerPinch_lip_bnd'),
        nt.Joint(u'LT_upperSide_lip_bnd'),
        nt.Joint(u'CT_lower_lip_bnd'),
        nt.Joint(u'LT_lowerSneer_lip_bnd'),
        nt.Joint(u'LT_corner_lip_bnd'),
        nt.Joint(u'LT_lowerSide_lip_bnd'),
        nt.Joint(u'CT_upper_lip_bnd'),
        nt.Joint(u'LT_upperPinch_lip_bnd'),
        nt.Joint(u'LT_upperSneer_lip_bnd'),
        nt.Joint(u'RT_lowerPinch_lip_bnd'),
        nt.Joint(u'RT_upperSide_lip_bnd'),
        nt.Joint(u'RT_lowerSneer_lip_bnd'),
        nt.Joint(u'RT_corner_lip_bnd'),
        nt.Joint(u'RT_lowerSide_lip_bnd'),
        nt.Joint(u'RT_upperPinch_lip_bnd'),
        nt.Joint(u'RT_upperSneer_lip_bnd')]
        
def addLocalBnd(bnd):
    # add joint in same position
    mat = bnd.getMatrix(ws=True)
    pm.select(cl=True)
    localBnd = pm.joint(n=bnd.replace('_bnd', '_local_bnd'))
    localBnd.radius.set(bnd.radius.get())
    localBndLipCurl = pm.group(localBnd, n=localBnd+'_lipCurl')
    localBndHm = pm.group(localBndLipCurl, n=localBnd+'_hm')
    localBndHm.setMatrix(mat, ws=True)
    
    import rigger.utils.modulate as modulate
    reload(modulate)
    
    # add hierarchy for driving pCtls
    priCtlAttrs = bnd.listAttr(ud=True)
    priCtlAttrs = [attr for attr in priCtlAttrs if 'pri_ctrl_weight_tz' in attr.attrName()]
    groupsList = []
    for attr in priCtlAttrs:
        # add xfo for the attr's driving pCtl
        pCtl = pm.PyNode('_'.join(attr.attrName().split('_')[:5]))
        pCtlMat = pCtl.getMatrix(ws=True)
        pCtlToken = '_'.join(pCtl.split('_')[:3])
        pCtlGrp = pm.group(em=True, n=localBnd+'_'+pCtlToken)
        pCtlHm = pm.group(pCtlGrp, n=pCtlGrp+'_hm')
        pCtlHm.setMatrix(pCtlMat, ws=True)
        if groupsList:
            pCtlHm.setParent(groupsList[-1])
        try:
            # connect TZ from pCtlNegator if it exist
            pCtlNeg = pm.PyNode(pCtl+'_negator')
            pCtlNeg.tz >> pCtlGrp.tz
            # multiply the influence
            pCtlWt = attr.get()
            modAttr = modulate.multiplyInput(pCtlGrp.tz, pCtlWt)
        except:
            print pCtl + ' has no negator in CtlSys'
        groupsList.append(pCtlGrp)
    
    # add localBnd to hierarchy
    groupsList[-1] | localBndHm
    
for bnd in bnds:
    addLocalBnd(bnd)
    
#===============================================================================
# CtlSys negators don't negate TZ - DEPRECATED
#===============================================================================
ctls = [nt.Transform(u'CT__jawDown_pri_ctrl_negator'),
nt.Transform(u'LT_corner_lip_pri_ctrl_negator'),
nt.Transform(u'LT_upperSneer_lip_pri_ctrl_negator'),
nt.Transform(u'LT_lowerSneer_lip_pri_ctrl_negator'),
nt.Transform(u'CT_upper_lip_pri_ctrl_negator'),
nt.Transform(u'CT_lower_lip_pri_ctrl_negator'),
nt.Transform(u'CT__mouthMover_pri_ctrl_negator'),
nt.Transform(u'RT_upperSneer_lip_pri_ctrl_negator'),
nt.Transform(u'RT_lowerSneer_lip_pri_ctrl_negator'),
nt.Transform(u'RT_corner_lip_pri_ctrl_negator'),
nt.Transform(u'CT_upper_lip_ctrl_negator'),
nt.Transform(u'LT_upperSide_lip_ctrl_negator'),
nt.Transform(u'LT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'LT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'LT_corner_lip_ctrl_negator'),
nt.Transform(u'LT_lowerPinch_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSide_lip_ctrl_negator'),
nt.Transform(u'CT_lower_lip_ctrl_negator'),
nt.Transform(u'RT_upperSide_lip_ctrl_negator'),
nt.Transform(u'RT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'RT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'RT_corner_lip_ctrl_negator'),
nt.Transform(u'RT_lowerPinch_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSide_lip_ctrl_negator')]

for ctl in ctls:
    md = pm.PyNode(ctl.replace('_negator', '_negT_md'))
    # md.input2Z.set(0)
    
#===========================================================================
# Calculate offset in local space - to drive CtlSys
#===========================================================================
bnds = [nt.Joint(u'LT_lowerPinch_lip_local_bnd'),
nt.Joint(u'LT_upperSide_lip_local_bnd'),
nt.Joint(u'CT_lower_lip_local_bnd'),
nt.Joint(u'LT_lowerSneer_lip_local_bnd'),
nt.Joint(u'LT_corner_lip_local_bnd'),
nt.Joint(u'LT_lowerSide_lip_local_bnd'),
nt.Joint(u'CT_upper_lip_local_bnd'),
nt.Joint(u'LT_upperPinch_lip_local_bnd'),
nt.Joint(u'LT_upperSneer_lip_local_bnd'),
nt.Joint(u'RT_lowerPinch_lip_local_bnd'),
nt.Joint(u'RT_upperSide_lip_local_bnd'),
nt.Joint(u'RT_lowerSneer_lip_local_bnd'),
nt.Joint(u'RT_corner_lip_local_bnd'),
nt.Joint(u'RT_lowerSide_lip_local_bnd'),
nt.Joint(u'RT_upperPinch_lip_local_bnd'),
nt.Joint(u'RT_upperSneer_lip_local_bnd')]

for bnd in bnds:
    # CtlSys negators to follow localBnd xform in local rig space
    origMat = bnd.getMatrix(ws=True)
    origMat = origMat.inverse()
    bndOrigMat = pm.createNode('fourByFourMatrix', n=bnd+'_origMat')
    bndOrigMat.in00.set(origMat[0][0])
    bndOrigMat.in01.set(origMat[0][1])
    bndOrigMat.in02.set(origMat[0][2])
    bndOrigMat.in10.set(origMat[1][0])
    bndOrigMat.in11.set(origMat[1][1])
    bndOrigMat.in12.set(origMat[1][2])
    bndOrigMat.in20.set(origMat[2][0])
    bndOrigMat.in21.set(origMat[2][1])
    bndOrigMat.in22.set(origMat[2][2])
    bndOrigMat.in30.set(origMat[3][0])
    bndOrigMat.in31.set(origMat[3][1])
    bndOrigMat.in32.set(origMat[3][2])
    offsetMat = pm.createNode('multMatrix', n=bnd+'_offsetMat_mm')
    bnd.worldMatrix >> offsetMat.matrixIn[0]
    bndOrigMat.output >> offsetMat.matrixIn[1]
    decMat = pm.createNode('decomposeMatrix', n=bnd+'_offsetMat_dcm')
    offsetMat.o >> decMat.inputMatrix
    # add attrs to be reused later
    bnd.addAttr('offsetTrans', at='double3', k=True)
    bnd.addAttr('offsetTransX', at='double', p='offsetTrans', k=True)
    bnd.addAttr('offsetTransY', at='double', p='offsetTrans', k=True)
    bnd.addAttr('offsetTransZ', at='double', p='offsetTrans', k=True)
    decMat.ot >> bnd.offsetTrans

#===============================================================================
# connect offsets to controls
#===============================================================================

ctls = [nt.Transform(u'LT_corner_lip_pri_ctrl_negator'),
nt.Transform(u'LT_upperSneer_lip_pri_ctrl_negator'),
nt.Transform(u'LT_lowerSneer_lip_pri_ctrl_negator'),
nt.Transform(u'CT_upper_lip_pri_ctrl_negator'),
nt.Transform(u'CT_lower_lip_pri_ctrl_negator'),
nt.Transform(u'RT_upperSneer_lip_pri_ctrl_negator'),
nt.Transform(u'RT_lowerSneer_lip_pri_ctrl_negator'),
nt.Transform(u'RT_corner_lip_pri_ctrl_negator'),
nt.Transform(u'CT_upper_lip_ctrl_negator'),
nt.Transform(u'LT_upperSide_lip_ctrl_negator'),
nt.Transform(u'LT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'LT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'LT_corner_lip_ctrl_negator'),
nt.Transform(u'LT_lowerPinch_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSide_lip_ctrl_negator'),
nt.Transform(u'CT_lower_lip_ctrl_negator'),
nt.Transform(u'RT_upperSide_lip_ctrl_negator'),
nt.Transform(u'RT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'RT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'RT_corner_lip_ctrl_negator'),
nt.Transform(u'RT_lowerPinch_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSide_lip_ctrl_negator')]

for ctl in ctls:
    ctg = ctl.getParent(2)
    srcBnd = pm.PyNode('_'.join(ctl.split('_')[:3])+'_local_bnd')
    srcBnd.offsetTrans >> ctg.t
    cth = ctl.getParent(3)
    if cth.sx.get() == -1:
        cth.sx.set(1)
        ctg.sx.set(-1)
        
#=======================================================================
# Connect tweak Tzs
#=======================================================================
ctls = [nt.Transform(u'RT_corner_lip_ctrl_negator'),
nt.Transform(u'RT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'RT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'RT_upperSide_lip_ctrl_negator'),
nt.Transform(u'CT_upper_lip_ctrl_negator'),
nt.Transform(u'LT_upperSide_lip_ctrl_negator'),
nt.Transform(u'LT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'LT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'LT_corner_lip_ctrl_negator'),
nt.Transform(u'LT_lowerPinch_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSide_lip_ctrl_negator'),
nt.Transform(u'CT_lower_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSide_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'RT_lowerPinch_lip_ctrl_negator')]

for ctl in ctls:
    localBnd = pm.PyNode('_'.join(ctl.split('_')[:3])+'_local_bnd')
    ctl.tz >> localBnd.tz
    
#===============================================================================
# add lipCurls in local bnds
#===============================================================================
import utils.rigging as rt
#===============================================================================
# add lipCurls in local bnds
#===============================================================================
lipCurlGrps = [nt.Transform(u'LT_upperSide_lip_local_bnd_lipCurl'),
nt.Transform(u'CT_upper_lip_local_bnd_lipCurl'),
nt.Transform(u'LT_upperPinch_lip_local_bnd_lipCurl'),
nt.Transform(u'LT_upperSneer_lip_local_bnd_lipCurl'),
nt.Transform(u'RT_upperSide_lip_local_bnd_lipCurl'),
nt.Transform(u'RT_upperPinch_lip_local_bnd_lipCurl'),
nt.Transform(u'RT_upperSneer_lip_local_bnd_lipCurl')]

grp = lipCurlGrps[0]
for grp in lipCurlGrps:
    grp.addAttr('lipCurlVal', k=True)
    rt.connectSDK(grp.lipCurlVal, grp.ty, {-1:-0.0625, 0:0, 1:0.125})
    rt.connectSDK(grp.lipCurlVal, grp.tz, {-1:-0.25, 0:0, 1:0.5})
    rt.connectSDK(grp.lipCurlVal, grp.rx, {-1:40, 0:0, 1:-40})
    
lipCurlGrps = [nt.Transform(u'LT_lowerPinch_lip_local_bnd_lipCurl'),
nt.Transform(u'CT_lower_lip_local_bnd_lipCurl'),
nt.Transform(u'LT_lowerSneer_lip_local_bnd_lipCurl'),
nt.Transform(u'LT_lowerSide_lip_local_bnd_lipCurl'),
nt.Transform(u'RT_lowerPinch_lip_local_bnd_lipCurl'),
nt.Transform(u'RT_lowerSneer_lip_local_bnd_lipCurl'),
nt.Transform(u'RT_lowerSide_lip_local_bnd_lipCurl')]

for grp in lipCurlGrps:
    grp.addAttr('lipCurlVal', k=True)
    rt.connectSDK(grp.lipCurlVal, grp.ty, {-1:0.0625, 0:0, 1:-0.125})
    rt.connectSDK(grp.lipCurlVal, grp.tz, {-1:-0.25, 0:0, 1:0.5})
    rt.connectSDK(grp.lipCurlVal, grp.rx, {-1:-40, 0:0, 1:40})
    
#===============================================================================
# connect from CtlSys via coeffs
#===============================================================================
# lower lips
coeffs = pm.group(em=True, n='CT_lowerLipCurls_coeffs')
coeffs.addAttr('leftPinch', k=True)
coeffs.addAttr('leftSneer', k=True)
coeffs.addAttr('leftSide', k=True)
coeffs.addAttr('centerMid', k=True)
coeffs.addAttr('rightSide', k=True)
coeffs.addAttr('rightSneer', k=True)
coeffs.addAttr('rightPinch', k=True)
rt.connectSDK('LT_lowerPinch_lip_ctrl_negator.rx',
coeffs.leftPinch, {-40:-1, 0:0, 40:1})
rt.connectSDK('LT_lowerSneer_lip_ctrl_negator.rx',
coeffs.leftSneer, {-40:-1, 0:0, 40:1})
rt.connectSDK('LT_lowerSide_lip_ctrl_negator.rx',
coeffs.leftSide, {-40:-1, 0:0, 40:1})
rt.connectSDK('CT_lower_lip_ctrl_negator.rx',
coeffs.centerMid, {-40:-1, 0:0, 40:1})
rt.connectSDK('RT_lowerSneer_lip_ctrl_negator.rx',
coeffs.rightSneer, {-40:-1, 0:0, 40:1})
rt.connectSDK('RT_lowerSide_lip_ctrl_negator.rx',
coeffs.rightSide, {-40:-1, 0:0, 40:1})
rt.connectSDK('RT_lowerPinch_lip_ctrl_negator.rx',
coeffs.rightPinch, {-40:-1, 0:0, 40:1})

priCtls = [nt.Transform(u'RT_lowerSneer_lip_pri_ctrl_negator'),
            nt.Transform(u'CT_lower_lip_pri_ctrl_negator'),
            nt.Transform(u'LT_lowerSneer_lip_pri_ctrl_negator')]
            
attrs = ['leftPinch',
'leftSneer',
'leftSide',
'centerMid',
'rightSide',
'rightSneer',
'rightPinch']
       
import rigger.utils.modulate as modulate
for pCtl in priCtls:
    token = pCtl.split('_')[0]
    for attr in attrs:
        mod = modulate.addInput(coeffs.attr(attr), 0, token)
        rt.connectSDK(pCtl.rx, mod, {-40:-1, 0:0, 40:1})
        
rt.connectSDK(coeffs.leftPinch, 
'LT_lowerPinch_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.5, 1:0.5})
rt.connectSDK(coeffs.leftSneer, 
'LT_lowerSneer_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.8, 1:0.8})
rt.connectSDK(coeffs.leftSide, 
'LT_lowerSide_lip_local_bnd_lipCurl.lipCurlVal', {-1:-1, 1:1})
rt.connectSDK(coeffs.centerMid, 
'CT_lower_lip_local_bnd_lipCurl.lipCurlVal', {-1:-1, 1:1})
rt.connectSDK(coeffs.rightPinch, 
'RT_lowerPinch_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.5, 1:0.5})
rt.connectSDK(coeffs.rightSneer, 
'RT_lowerSneer_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.8, 1:0.8})
rt.connectSDK(coeffs.rightSide, 
'RT_lowerSide_lip_local_bnd_lipCurl.lipCurlVal', {-1:-1, 1:1})

# upper lips
coeffs = pm.group(em=True, n='CT_upperLipCurls_coeffs')
coeffs.addAttr('leftPinch', k=True)
coeffs.addAttr('leftSneer', k=True)
coeffs.addAttr('leftSide', k=True)
coeffs.addAttr('centerMid', k=True)
coeffs.addAttr('rightSide', k=True)
coeffs.addAttr('rightSneer', k=True)
coeffs.addAttr('rightPinch', k=True)
rt.connectSDK('LT_upperPinch_lip_ctrl_negator.rx',
coeffs.leftPinch, {40:-1, 0:0, -40:1})
rt.connectSDK('LT_upperSneer_lip_ctrl_negator.rx',
coeffs.leftSneer, {40:-1, 0:0, -40:1})
rt.connectSDK('LT_upperSide_lip_ctrl_negator.rx',
coeffs.leftSide, {40:-1, 0:0, -40:1})
rt.connectSDK('CT_upper_lip_ctrl_negator.rx',
coeffs.centerMid, {40:-1, 0:0, -40:1})
rt.connectSDK('RT_upperSneer_lip_ctrl_negator.rx',
coeffs.rightSneer, {40:-1, 0:0, -40:1})
rt.connectSDK('RT_upperSide_lip_ctrl_negator.rx',
coeffs.rightSide, {40:-1, 0:0, -40:1})
rt.connectSDK('RT_upperPinch_lip_ctrl_negator.rx',
coeffs.rightPinch, {40:-1, 0:0, -40:1})

priCtls = [nt.Transform(u'RT_upperSneer_lip_pri_ctrl_negator'),
            nt.Transform(u'CT_upper_lip_pri_ctrl_negator'),
            nt.Transform(u'LT_upperSneer_lip_pri_ctrl_negator')]
            
attrs = ['leftPinch',
'leftSneer',
'leftSide',
'centerMid',
'rightSide',
'rightSneer',
'rightPinch']
       
import rigger.utils.modulate as modulate
for pCtl in priCtls:
    token = pCtl.split('_')[0]
    for attr in attrs:
        mod = modulate.addInput(coeffs.attr(attr), 0, token)
        rt.connectSDK(pCtl.rx, mod, {40:-1, 0:0, -40:1})
        
rt.connectSDK(coeffs.leftPinch, 
'LT_upperPinch_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.5, 1:0.5})
rt.connectSDK(coeffs.leftSneer, 
'LT_upperSneer_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.8, 1:0.8})
rt.connectSDK(coeffs.leftSide, 
'LT_upperSide_lip_local_bnd_lipCurl.lipCurlVal', {-1:-1, 1:1})
rt.connectSDK(coeffs.centerMid, 
'CT_upper_lip_local_bnd_lipCurl.lipCurlVal', {-1:-1, 1:1})
rt.connectSDK(coeffs.rightPinch, 
'RT_upperPinch_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.5, 1:0.5})
rt.connectSDK(coeffs.rightSneer, 
'RT_upperSneer_lip_local_bnd_lipCurl.lipCurlVal', {-1:-0.8, 1:0.8})
rt.connectSDK(coeffs.rightSide, 
'RT_upperSide_lip_local_bnd_lipCurl.lipCurlVal', {-1:-1, 1:1})

#===============================================================================
# connect tweak rotates to localBnds
#===============================================================================
# left and center
ctls = [nt.Transform(u'CT_upper_lip_ctrl_negator'),
nt.Transform(u'LT_upperSide_lip_ctrl_negator'),
nt.Transform(u'LT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'LT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'LT_corner_lip_ctrl_negator'),
nt.Transform(u'LT_lowerPinch_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'LT_lowerSide_lip_ctrl_negator'),
nt.Transform(u'CT_lower_lip_ctrl_negator')]

for ctl in ctls:
    currPlug = ctl.rz.outputs(p=True)[0]
    ctl.rz // currPlug
    localBnd = pm.PyNode('_'.join(ctl.split('_')[:3]) + '_local_bnd')
    ctl.rz >> localBnd.rz
    ctl.ry >> localBnd.ry
    
# right side is more complicated
# because of negative scale md
ctls = [nt.Transform(u'RT_upperSide_lip_ctrl_negator'),
nt.Transform(u'RT_upperSneer_lip_ctrl_negator'),
nt.Transform(u'RT_upperPinch_lip_ctrl_negator'),
nt.Transform(u'RT_corner_lip_ctrl_negator'),
nt.Transform(u'RT_lowerPinch_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSneer_lip_ctrl_negator'),
nt.Transform(u'RT_lowerSide_lip_ctrl_negator')]

for ctl in ctls:
    md = ctl.rz.outputs(scn=True)[0]
    currPlug = md.outputY.outputs(p=True, scn=True)[0]
    md.outputY // currPlug
    localBnd = pm.PyNode('_'.join(ctl.split('_')[:3]) + '_local_bnd')
    md.outputY >> localBnd.rz
    ctl.ry >> md.input1Z
    md.outputZ >> localBnd.ry
