'''
Created on Jul 13, 2014

@author: Leon
'''
import pymel.core as pm
import pymel.core.nodetypes as nt

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