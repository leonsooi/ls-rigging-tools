'''
Created on Oct 2, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

import rigger.utils.modulate as modulate
reload(modulate)

def addSpreadJnts():
    midLoc = addLocatorForPlacement('Ori_lf_', 'middle')
    midLoc.setMatrix(pm.dt.Matrix([[1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [4.15834224221, -4.97379915032e-14, 0.644872211612, 1.0]]))
    midCurl = addCurlJnt('Ori_lf_', 'middle')
    
    indexLoc = addLocatorForPlacement('Ori_lf_', 'index')
    indexLoc.setMatrix(pm.dt.Matrix([[1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [3.98035402327, -1.20792265079e-13, 2.18355008139, 1.0]]))
    indexCurl = addCurlJnt('Ori_lf_', 'index')
    
    midLoc = addLocatorForPlacement('Ori_rt_', 'middle')
    midLoc.setMatrix(pm.dt.Matrix([[1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [4.15834224221, -4.97379915032e-14, 0.644872211612, 1.0]]).inverse())
    midCurl = addCurlJnt('Ori_rt_', 'middle')
    
    indexLoc = addLocatorForPlacement('Ori_rt_', 'index')
    indexLoc.setMatrix(pm.dt.Matrix([[1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [3.98035402327, -1.20792265079e-13, 2.18355008139, 1.0]]).inverse())
    indexCurl = addCurlJnt('Ori_rt_', 'index')

def addLocatorForPlacement(side, finger):
    # add locator for placement
    baseJnt = pm.PyNode(side+finger+'_a_jnt')
    parJnt = baseJnt.getParent()
    loc = pm.spaceLocator(n=side+finger+'Cup_loc')
    parJnt | loc
    loc.setMatrix(pm.dt.Matrix())
    return loc

def addCurlJnt(side, finger):
    # create curl jnt
    baseJnt = pm.PyNode(side+finger+'_a_jnt')
    loc = pm.PyNode(baseJnt.replace('_a_jnt', 'Cup_loc'))
    parJnt = baseJnt.getParent()
    # orient loc so x is aimed to baseJnt
    temp_con = pm.aimConstraint(baseJnt, loc, aim=(1,0,0), u=(0,0,1), wuo=parJnt, wut='objectrotation')
    pm.delete(temp_con)
    # create jnt
    pm.select(cl=True)
    curlJnt = pm.joint(n=side+finger+'Cup_jnt')
    curlJnt.radius.set(baseJnt.radius.get())
    mat = loc.getMatrix(ws=True)
    curlJnt.setMatrix(mat, ws=True)
    parJnt | curlJnt
    pm.makeIdentity(curlJnt, r=True, a=True)
    # find offset matrix for baseJnt
    currMat = baseJnt.getMatrix()
    offMat = currMat * curlJnt.getMatrix().inverse()
    txOffset = offMat.translate[0]
    # change parent for baseJnt
    curlJnt | baseJnt
    txMd = baseJnt.tx.inputs()[0]
    txMd.input2X.set(txOffset)
    return curlJnt





def addCtrlToSpreadJnt(jnt):
    ctl = pm.circle(n=jnt.replace('_jnt', '_ctrl'), normal=(1,0,0), ch=False, sweep=359)[0]
    ctg = pm.group(ctl, n=ctl+'_grp')
    cth = pm.group(ctg, n=ctl+'_cth')
    
    mat = jnt.getMatrix(ws=True)
    cth.setMatrix(mat, ws=True)
    
    par = jnt.getParent()
    par | cth
    
    pm.copyAttr(jnt, ctg, inConnections=True)
    
    ctl | jnt
    
    
    
spreadJnts = [nt.Joint(u'Ori_lf_pinkyCup_jnt'),
nt.Joint(u'Ori_lf_ringCup_jnt'),
nt.Joint(u'Ori_lf_middleCup_jnt'),
nt.Joint(u'Ori_lf_indexCup_jnt'),
nt.Joint(u'Ori_rt_pinkyCup_jnt'),
nt.Joint(u'Ori_rt_ringCup_jnt'),
nt.Joint(u'Ori_rt_middleCup_jnt'),
nt.Joint(u'Ori_rt_indexCup_jnt')]

# add ctl for each spread jnt
for jnt in spreadJnts:
    addCtrlToSpreadJnt(jnt)