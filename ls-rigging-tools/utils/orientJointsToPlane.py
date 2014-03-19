"""
lsOrientJointsToPlane v0.0.1
Orients the midJnt of a 3-joint chain such that they rotate on a plane
Useful for setting up ikRPsolvers

Example Use: 
import lsOrientJointsToPlane
lsOrientJointsToPlane.lsOrientJointsToPlane([hip, knee, ankle])
"""

import maya.cmds as mc

def lsOrientJointsToPlane(jntList, downVector=[1,0,0], normalVector=[0,0,1]):
    '''
    arguments:
    jntList - [startJnt, midJnt, endJnt]
    downVector (optional) - vector that points to the child joint, defaults to +X
    normalVector (optional) - vector for axis of rotation, defaults to +Z
    
    todo:
    1. options for orienting startJnt and endJnt when necessary
    2. use API for calculating vectors, instead of creating arbitrary polys and constraints... though this should work for now...
    ''' 
    
    # get joint positions
    startJntPos = mc.xform(jntList[0], q=1, ws=1, t=1)
    midJntPos = mc.xform(jntList[1], q=1, ws=1, t=1)
    endJntPos = mc.xform(jntList[2], q=1, ws=1, t=1)
    
    # create poly to act as rotate plane
    tempPoly = mc.polyCreateFacet(ch=0, p=[startJntPos, midJntPos, endJntPos], n="tempPoly_getNormal")
    
    # create locator to get normal vector 
    tempLoc = mc.spaceLocator(n="tempLoc_getNormal")[0]
    mc.xform(tempLoc, ws=1, t=midJntPos)
    normalCons = mc.normalConstraint(tempPoly, tempLoc) # default: X-axis aligns with normal vector
    mc.delete(normalCons)
    
    # orient midJnt (jntList[1])
    mc.move(1,0,0, tempLoc, os=1, r=1)
    mc.parent(jntList[2], w=1)
    aimCons = mc.aimConstraint(jntList[2], jntList[1], aim=downVector, u=normalVector, wuo=tempLoc, wut=2, wu=[1,0,0])
    mc.delete(aimCons)
    mc.makeIdentity(jntList[1], a=1, r=1)
    mc.parent(jntList[2],jntList[1])
        
    # cleanup
    mc.delete(tempPoly, tempLoc)