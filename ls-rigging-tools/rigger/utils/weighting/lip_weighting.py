'''
Created on Aug 28, 2014

@author: Leon

Weighting utility for mouth lip loop

'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import maya.cmds as mc

import loop_weighting as loop
reload(loop)

def getLipVertexLoops(pGrp, loopNum=10):
    '''
    '''
    mouthLipsLoop = pGrp.mouthLipsLoop.get()
    mc.select(mouthLipsLoop, r=True)
    mel.ConvertSelectionToVertices()
    treeRoot = loop.constructVertexLoops(loopNum)
    return treeRoot

def getBndToVertsMap(treeRoot):
    crv = pm.nt.Transform(u'CT_placement_grp_mouthLipLoopCrv')
    bndToVertsMap = loop.populateBndToVertsMap(crv, treeRoot)
    return bndToVertsMap

def getBndToVertsIdsMap(treeRoot):
    bndToVertsMap = getBndToVertsMap(treeRoot)
    bndToVertsIdsMap = {}
    for bnd, vertsList in bndToVertsMap.items():
        bndName = bnd.name()
        vertIds = [vert.index() for vert in vertsList]
        bndToVertsIdsMap[bndName] = vertIds
    return bndToVertsIdsMap

