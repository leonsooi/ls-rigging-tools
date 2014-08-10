'''
Created on Aug 6, 2014

@author: Leon
'''
import pymel.core as pm


def pruneDeltas(baseMesh, targetMesh, tol=0.0001):
    '''
    '''
    for targetVert, baseVert in zip(targetMesh.vtx[:], baseMesh.vtx[:]):
        targetPos = targetVert.getPosition()
        basePos = baseVert.getPosition()
        deltaVec = targetPos - basePos
        if deltaVec.length() < tol:
            targetVert.setPosition(basePos)
            
def getDeltas(baseMesh, targetMesh):
    deltas = []
    for targetVert, baseVert in zip(targetMesh.vtx[:], baseMesh.vtx[:]):
        targetPos = targetVert.getPosition()
        basePos = baseVert.getPosition()
        deltaVec = targetPos - basePos
        deltas.append(deltaVec)
    return deltas
        
def splitXyzDeltas(deltas):
    '''
    split into x/y/z
    return x/y/z deltas
    '''
    xdeltas = [(vec.x,0,0) for vec in deltas]
    ydeltas = [(0,vec.y,0) for vec in deltas]
    zdeltas = [(0,0,vec.z) for vec in deltas]
    return xdeltas, ydeltas, zdeltas

def applyDeltas(mesh, deltas):
    '''
    '''
    for vert, delta in zip(mesh.vtx[:], deltas):
        currPos = vert.getPosition()
        newPos = currPos + delta
        vert.setPosition(newPos)

def createXyzBlendshapes(baseMesh, targetMesh):
    '''
    '''
    deltas = getDeltas(baseMesh, targetMesh)
    xyzDeltas = splitXyzDeltas(deltas)
    xyzNames = 'xDelta', 'yDelta', 'zDelta'
    
    for name, deltas in zip(xyzNames, xyzDeltas):
        newMesh = pm.duplicate(baseMesh, n=targetMesh+'_'+name)[0]
        applyDeltas(newMesh, deltas)