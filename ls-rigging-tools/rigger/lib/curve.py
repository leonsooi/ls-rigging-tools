'''
Created on Apr 14, 2014

@author: Leon
'''
import pymel.core as pm

def extendCrv(crv, amount=2.0):
    '''
    assume crv has two cvs
    '''
    startPos = crv.cv[0].getPosition()
    endPos = crv.cv[1].getPosition()
    vec = endPos - startPos
    newEndPos = endPos + vec
    newStartPos = startPos - vec
    crv.cv[0].setPosition(newStartPos)
    crv.cv[1].setPosition(newEndPos)
    crv.updateCurve()
    
    

def getClosestCVtoXfo(xfo, crv):
    '''
    return closest CV on curve to xfo
    '''
    cvsPoss = list(enumerate(crv.getCVs(space='world')))
    xfoPos = xfo.getTranslation(space='world')
    closestCV = min(cvsPoss, key=lambda cvPos: (cvPos[1] - xfoPos).length())
    return crv.cv[closestCV[0]]

def calcHeightFromCurve(xfo, crv, scale=10, heightVec=None, intVec=None):
    '''
    xfo = upperBnds[1]
    or xfo could also be a dt.point
    crv = targetCrv
    '''
    if type(xfo) is pm.dt.Point:
        xfoPos = xfo
    else:
        xfoPos = xfo.getTranslation(space='world')
    
    if heightVec:
        intCrv = pm.curve(ep=(xfoPos+heightVec*scale,
                              xfoPos-heightVec*scale), 
                          n='int_curve', d=3)
    else:
        intCrv = pm.curve(ep=((xfoPos[0], xfoPos[1]-scale, xfoPos[2]), 
                              (xfoPos[0], xfoPos[1]+scale, xfoPos[2])), 
                          n='int_curve', d=3)
    
    intNode = pm.createNode('curveIntersect', n='int_node')
    crv.worldSpace >> intNode.inputCurve1    
    intCrv.worldSpace >> intNode.inputCurve2
    intNode.useDirection.set(True)
    
    if intVec:
        intNode.direction.set(intVec)
    else:
        intNode.direction.set(0,0,1)
    
    intParam = intNode.p1.get()[0]
    intPos = crv.getPointAtParam(intParam, space='world')
    # make sure both are points
    intPos = pm.dt.Point(intPos)
    xfoPos = pm.dt.Point(xfoPos)
    height = (xfoPos - intPos).length()
    
    #cleanup
    pm.delete(intNode, intCrv)
    
    return height