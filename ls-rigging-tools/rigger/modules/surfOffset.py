'''
Created on Jun 28, 2014

@author: Leon
'''
import pymel.core as pm

def addOffset(node):
    '''
    - add a grp above node
    - add a nurbs plane under grp's parent (get the same local space)
    - unparent nurbs plane to world space (or whichever deformer space - e.g. headLattice)
    - add pointOnSurfaceInfo to get position and orientation for grp
    - use aimconstraint to convert vectors to orientation
    - return grp as offset
    
    example use for mathilda:
    import rigger.modules.surfOffset as surfOffset
    reload(surfOffset)
    nodes = pm.ls(sl=True)
    offsets = []
    for n in nodes:
        offsetGrp = surfOffset.addOffset(n)
        offsets.append(offsetGrp[1])
    pm.select(offsets)
    '''
    nodeMatrix = node.getMatrix(worldSpace=True)
    offsetGrp = pm.group(em=True, n=node+'_surfOffset_grp')
    offsetGrp.setMatrix(nodeMatrix, worldSpace=True)
    
    # hierarchy
    # also check for sibling nodes, such as scaleX/Y xfos
    siblings = node.getSiblings()
    for sibling in siblings:
        offsetGrp | sibling
    parentNode = node.getParent()
    parentNode | offsetGrp | node
    
    # nurbs plane
    plane = pm.nurbsPlane(n=node+'_surfOffset_srf', ch=False, 
                          degree=1, axis=(0,1,0))[0]
    # parentNode | plane # don't
    # use separate hierachy
    planeGrp = pm.group(plane, n=node+'_surfOffsetSrf_grp')
    planeHm = pm.group(planeGrp, n=node+'_surfOffsetSrf_hm')
    planeHm.setMatrix(nodeMatrix, worldSpace=True)
    
    # point on surface info
    posi = pm.createNode('pointOnSurfaceInfo', n=node+'_surfOffset_posi')
    plane.local >> posi.inputSurface
    posi.parameterU.set(0.5)
    posi.parameterV.set(0.5)
    '''
    # convert vectors to orientation using aim constraint
    aimc = pm.createNode('aimConstraint', n=node+'_surfOffset_aimc')
    offsetGrp | aimc
    posi.normal >> aimc.tg[0].tt
    posi.tangentU >> aimc.worldUpVector
    aimc.aimVector.set((0,1,0))
    aimc.upVector.set((1,0,0))
    '''
    '''
    # use cross products instead of aim constraint
    vpZ = pm.createNode('vectorProduct', n=node+'_surfOffsetZVec_vp')
    posi.normal >> vpZ.input1 # Y
    posi.tangentU >> vpZ.input2
    vpZ.operation.set(2)
    vpX = pm.createNode('vectorProduct', n=node+'_surfOffsetXVec_vp')
    posi.normal >> vpZ.input1 # Y
    posi.tangentU >> vpZ.input2
    vpZ.operation.set(2)'''
    
    # just use vectors from posi to construct matrix!
    mat = pm.createNode('fourByFourMatrix', n=node+'_surfOffset_fbfm')
    # x-vector
    posi.tangentUx >> mat.in00
    posi.tangentUy >> mat.in01
    posi.tangentUz >> mat.in02
    # y-vector
    posi.normalX >> mat.in10
    posi.normalY >> mat.in11
    posi.normalZ >> mat.in12
    # z-vector
    posi.tangentVx >> mat.in20
    posi.tangentVy >> mat.in21
    posi.tangentVz >> mat.in22
    # position
    posi.positionX >> mat.in30
    posi.positionY >> mat.in31
    posi.positionZ >> mat.in32

    # drive grp
    dcm = pm.createNode('decomposeMatrix', n=node+'_surfOffset_dcm')
    mat.output >> dcm.inputMatrix
    dcm.outputTranslate >> offsetGrp.t
    dcm.outputRotate >> offsetGrp.r
    
    return offsetGrp, plane

import maya.cmds as mc
def addSurfToDeformer(surfs, deformer):
    '''
    '''
    membershipSet = pm.listConnections(deformer, type='objectSet')[0]
    #pm.sets(surfs, add=membershipSet)
    surfs = [str(s) for s in surfs]
    memSet = str(membershipSet)
    mc.sets(surfs, add=memSet)