'''
Created on May 12, 2014

@author: Leon
'''
import pymel.core as pm

def cone_pose_reader(xfo, name, aimAxis=(1,0,0), defaultAngle=60.0, bspTarget=None):
    '''
    pose xfo, then run this method
    aimAxis - axis of xfo
    '''
    nodename = xfo + '_' + name
    
    # store pose matrix
    pose_xfo = pm.group(em=True, n=nodename+'_pose_xfo')
    xfo | pose_xfo
    pm.makeIdentity(pose_xfo, t=1, r=1, s=1)
    
    xfo_parent = xfo.getParent()
    xfo_parent | pose_xfo
    
    # lock pose so don't accidentally change
    for attr in ('t','r','s'):
        pose_xfo.attr(attr).set(lock=True)
    
    # get vector for xfo
    xfoVP = pm.createNode('vectorProduct', n=nodename+'_xfo_vp')
    xfo.matrix >> xfoVP.matrix
    xfoVP.input1.set(aimAxis)
    xfoVP.operation.set(3)
    
    # get vector for reader
    readerVP = pm.createNode('vectorProduct', n=nodename+'_pose_vp')
    pose_xfo.matrix >> readerVP.matrix
    readerVP.input1.set(aimAxis)
    readerVP.operation.set(3)
    
    # get angle
    angBet = pm.createNode('angleBetween', n=nodename+'_abt')
    xfoVP.output >> angBet.vector1
    readerVP.output >> angBet.vector2
    
    # add attribute to xfo
    xfo.addAttr(name+'_inAngle', k=True, dv=0)
    xfo.addAttr(name+'_outAngle', k=True, dv=defaultAngle)
    xfo.addAttr(name+'_output', k=True)
    
    # set range to 0-1
    str = pm.createNode('setRange', n=nodename+'_str')
    xfo.attr(name+'_inAngle') >> str.oldMinX
    xfo.attr(name+'_outAngle') >> str.oldMaxX
    str.minX.set(1)
    str.maxX.set(0)
    angBet.angle >> str.valueX
    str.outValueX >> xfo.attr(name+'_output')
    
    if bspTarget:
        xfo.attr(name+'_output') >> bspTarget
        
    pm.select(xfo)


def radial_pose_reader(xfo, aimAxis=(0,0,1), targetAxis=(0,0,1)):
    '''
    '''
    xfo.addAttr('vectorAngle', k=True, at='float')
    xfo.addAttr('param', k=True, at='float')
    xfo.addAttr('paramNormalized', k=True, at='float')
    
    # vector product gets xfo's direction vector
    vpd = pm.createNode('vectorProduct', n=xfo+'_radPosReader_vpd')
    vpd.input1.set(aimAxis)
    vpd.operation.set(3)
    xfo.worldMatrix >> vpd.matrix
    
    # angle between direction vector and target axis
    abt = pm.createNode('angleBetween', n=xfo+'_radPosReader_abt')
    vpd.output >> abt.vector1
    abt.vector2.set(aimAxis)
    abt.angle >> xfo.vectorAngle
    
    # make nurbs circle to calculate direction
    mnc = pm.createNode('makeNurbCircle', n=xfo+'_radPosReader_mnc')
    
    # nearest pt on crv
    npc = pm.createNode('nearestPointOnCurve', n=xfo+'radPoseReader_npc')
    vpd.output >> npc.inPosition
    mnc.outputCurve >> npc.inputCurve
    
    # normalize param using md
    mdv = pm.createNode('multiplyDivide', n=xfo+'radPosReader_mdv')
    mdv.operation.set(2)
    npc.parameter >> mdv.input1X
    mnc.sections >> mdv.input2X
    
    # connect back to xfo
    mdv.outputX >> xfo.paramNormalized
    npc.parameter >> xfo.param
    
    pm.select(xfo)