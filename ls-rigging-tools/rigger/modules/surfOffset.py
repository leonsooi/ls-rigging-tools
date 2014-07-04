'''
Created on Jun 28, 2014

@author: Leon
'''
import pymel.core as pm

def addOffset(node):
    '''
    - add a grp above node
    - add a nurbs plane under grp's parent
    - add pointOnSurfaceInfo to get position and orientation for grp
    - use aimconstraint to convert vectors to orientation
    - return grp as offset
    '''
    nodeMatrix = node.getMatrix(worldSpace=True)
    offsetGrp = pm.group(em=True, n=node+'_surfOffset_grp')
    offsetGrp.setMatrix(nodeMatrix, worldSpace=True)
    
    # hierarchy
    parentNode = node.getParent()
    parentNode | offsetGrp | node
    
    # nurbs plane
    plane = pm.nurbsPlane(n=node+'_surfOffset_srf', ch=False, 
                          degree=1, axis=(0,1,0))[0]
    plane.setMatrix(nodeMatrix, worldSpace=True)
    parentNode | plane
    
    # point on surface info
    posi = pm.createNode('pointOnSurfaceInfo', n=node+'_surfOffset_posi')
    plane.local >> posi.inputSurface
    posi.parameterU.set(0.5)
    posi.parameterV.set(0.5)
    
    # convert vectors to orientation using aim constraint
    aimc = pm.createNode('aimConstraint', n=node+'_surfOffset_aimc')
    offsetGrp | aimc
    posi.normal >> aimc.tg[0].tt
    posi.tangentU >> aimc.worldUpVector
    aimc.aimVector.set((0,1,0))
    aimc.upVector.set((1,0,0))
    
    # drive grp
    aimc.constraintRotate >> offsetGrp.r
    posi.position >> offsetGrp.t
    
    return offsetGrp, plane
    
def addSurfToDeformer(surfs, deformer):
    '''
    '''
    membershipSet = pm.listConnections(deformer, type='objectSet')[0]
    pm.sets(surfs, add=membershipSet)