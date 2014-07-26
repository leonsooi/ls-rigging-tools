'''
Created on Jul 14, 2014

@author: Leon
'''
import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
import utils.rigging as rt
mel = Mel()

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