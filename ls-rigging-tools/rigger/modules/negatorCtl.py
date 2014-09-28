'''
Created on Sep 27, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()



def addNegatorCtl(ctl):
    '''
    ctl should be a primaryCtl, which is connected to a bnd by message
    bnd is used for WS position
    
    ctl = nt.Transform(u'RT_corner_lip_pri_ctrl_fake')
    '''
    # create control crv
    negCtl = pm.duplicate(ctl, n=ctl+'_negator')[0]
    # set hierarchy
    negCtl.setParent(None)
    ctlMat = negCtl.getMatrix()
    negCtlRev = pm.group(em=True, n=ctl+'_negRev')
    negCtlGrp = pm.group(negCtlRev, n=ctl+'_negGrp')
    negCtlHm = pm.group(negCtlGrp, n=ctl+'_negHm')
    negCtlHm.setMatrix(ctlMat)
    negCtlRev | negCtl
    # connect reverses with mds
    tmd = pm.createNode('multiplyDivide', n=ctl+'_negT_md')
    negCtl.t >> tmd.input1
    tmd.input2.set(-1,-1,-1)
    tmd.output >> negCtlRev.t
    rmd = pm.createNode('multiplyDivide', n=ctl+'_negR_md')
    negCtl.r >> rmd.input1
    rmd.input2.set(-1,-1,-1)
    rmd.output >> negCtlRev.r
    negCtlRev.rotateOrder.set(5)
    # attach home to bnd
    if '_fake' not in ctl.name():
        bnd = ctl.message.outputs(type='joint')[0]
    else:
        realCtl = pm.PyNode(ctl.replace('_fake',''))
        bnd = realCtl.message.outputs(type='joint')[0]
        negCtlHm.s.set(-1,1,1)
    decMat = pm.createNode('decomposeMatrix', n=ctl+'_negHmAttachBnd_dcm')
    bnd.worldMatrix >> decMat.inputMatrix
    decMat.ot >> negCtlHm.t
    decMat.outputRotate >> negCtlHm.r
    