'''
Created on Sep 27, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()



def addNegatorCtl(ctl, mirror=False):
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
    # attach home to bnd
    if '_fake' not in ctl.name():
        bnd = ctl.message.outputs(type='joint')[0]
    else:
        realCtl = pm.PyNode(ctl.replace('_fake',''))
        bnd = realCtl.message.outputs(type='joint')[0]
        negCtlHm.s.set(-1,1,1)
    pmm = pm.createNode('pointMatrixMult', n=ctl+'_negHmAttachBnd_pmm')
    bnd.worldMatrix >> pmm.inMatrix
    pmm.output >> negCtlHm.t
    
    # drive original controls
    # these connections may be overriden manually
    negCtl.tx >> ctl.tx
    negCtl.ty >> ctl.ty
    negCtl.rz >> ctl.rz
    negCtl.sx >> ctl.sx
    negCtl.sy >> ctl.sy
    
    # flip x for mirroring
    if mirror:
        negCtlHm.s.set(-1,1,1)
        # reverse tx and rz
        md = pm.createNode('multiplyDivide', n=ctl+'_negTxRzForMirror_md')
        negCtl.tx >> md.input1X
        negCtl.rz >> md.input1Y
        md.input2.set(-1,-1,-1)
        md.outputX >> ctl.tx
        md.outputY >> ctl.rz