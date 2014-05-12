'''
Created on May 12, 2014

@author: Leon
'''
import pymel.core as pm


def radial_pose_reader(xfo, dir=(0,0,1), targetAxis=(0,0,1)):
    '''
    '''
    xfo.addAttr('vectorAngle', k=True, at='float')
    xfo.addAttr('param', k=True, at='float')
    xfo.addAttr('paramNormalized', k=True, at='float')
    
    # vector product gets xfo's direction vector
    vpd = pm.createNode('vectorProduct', n=xfo+'_radPosReader_vpd')
    vpd.input1.set(dir)
    vpd.operation.set(3)
    xfo.matrix >> vpd.matrix
    
    # angle between direction vector and target axis
    abt = pm.createNode('angleBetween', n=xfo+'_radPosReader_abt')
    vpd.output >> abt.vector1
    abt.vector2.set(dir)
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