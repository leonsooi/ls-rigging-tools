'''
Created on Sep 27, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()



def addNegatorCtl(ctl, mirror=None, attach='bnd'):
    '''
    ctl should be a primaryCtl, which is connected to a bnd by message
    bnd is used for WS position
    
    ctl = nt.Transform(u'RT_corner_lip_pri_ctrl_fake')
    
    mirror - None, 'X', 'Y', 'Z'
    attach - 'bnd', 'self'
    'self' will attach to the ctl
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
    if attach == 'bnd':
        bnd = ctl.message.outputs(type='joint')[0]
    elif attach == 'self':
        bnd = ctl

    pmm = pm.createNode('pointMatrixMult', n=ctl+'_negHmAttachBnd_pmm')
    bnd.worldMatrix >> pmm.inMatrix
    pmm.output >> negCtlHm.t
    
    # drive original controls
    # these connections may be overriden manually
    
    # scales are connected directly, regardless of mirror
    negCtl.sx >> ctl.sx
    negCtl.sy >> ctl.sy
    negCtl.sz >> ctl.sz
    
    # translate and rotate depend on mirror
    if mirror is None:
        negCtl.tx >> ctl.tx
        negCtl.ty >> ctl.ty
        negCtl.tz >> ctl.tz
        negCtl.rx >> ctl.rx
        negCtl.ry >> ctl.ry
        negCtl.rz >> ctl.rz
    elif mirror == 'X':
        # flip x for mirroring
        negCtlGrp.s.set(-1,1,1)
        # reverse tx and rz
        md = pm.createNode('multiplyDivide', n=ctl+'_negXfosForMirror_md')
        negCtl.tx >> md.input1X
        negCtl.ry >> md.input1Y
        negCtl.rz >> md.input1Z
        md.input2.set(-1,-1,-1)
        md.outputX >> ctl.tx
        md.outputY >> ctl.ry
        md.outputZ >> ctl.rz
        negCtl.ty >> ctl.ty
        negCtl.tz >> ctl.tz
        negCtl.rx >> ctl.rx
    elif mirror == 'Y':
        # flip y for mirroring
        negCtlGrp.s.set(1,-1,1)
        md = pm.createNode('multiplyDivide', n=ctl+'_negXfosForMirror_md')
        negCtl.ty >> md.input1X
        negCtl.rx >> md.input1Y
        negCtl.rz >> md.input1Z
        md.input2.set(-1,-1,-1)
        md.outputX >> ctl.ty
        md.outputY >> ctl.rx
        md.outputZ >> ctl.rz
        negCtl.tx >> ctl.tx
        negCtl.tz >> ctl.tz
        negCtl.ry >> ctl.ry
    elif mirror == 'XY':
        # flip x & y
        negCtlGrp.s.set(-1,-1,1)
        tmd = pm.createNode('multiplyDivide', n=ctl+'_negXfosForMirror_tmd')
        rmd = pm.createNode('multiplyDivide', n=ctl+'_negXfosForMirror_rmd')
        negCtl.t >> tmd.input1
        tmd.input2.set(-1,-1,1)
        tmd.output >> ctl.t
        negCtl.r >> rmd.input1
        rmd.input2.set(-1,-1,1)
        rmd.output >> ctl.r
        