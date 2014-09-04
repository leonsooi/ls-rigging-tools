'''
Created on Aug 28, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import rigger.lib.mesh as mesh
import rigger.lib.datatypes as data

def getAllPLocsOnCurve(crv):
    '''
    crv = nt.Transform(u'CT_placement_grp_mouthLipLoopCrv')
    '''
    pocis = crv.worldSpace.outputs(type='pointOnCurveInfo')
    pLocs = [poci.position.outputs()[0] for poci in pocis]
    return pLocs

def getClosestBndOnCurve(crv, param):
    '''
    crv = nt.Transform(u'CT_placement_grp_mouthLipLoopCrv')
    param=25
    '''
    pLocs = getAllPLocsOnCurve(crv)
    closestPLoc = min(pLocs, key=lambda pLoc: abs(param-pLoc.cv_id.get()))
    bnd = pm.PyNode(closestPLoc.replace('_pLoc', '_bnd'))
    return bnd

def initBndToVertsMap(crv):
    pLocs = getAllPLocsOnCurve(crv)
    bnds = [pm.PyNode(pLoc.replace('_pLoc', '_bnd')) for pLoc in pLocs]
    bndToVertsMap = {}
    for bnd in bnds:
        bndToVertsMap[bnd] = []
    return bndToVertsMap

def populateBndToVertsMap(crv, vertsTree):
    bndToVertsMap = initBndToVertsMap(crv)
    firstVertsTrees = vertsTree.children
    for tree in firstVertsTrees:
        allDesVerts = tree.getAllDescendentsData()
        firstVert = tree.data
        firstVertPos = firstVert.getPosition()
        param = crv.getParamAtPoint(firstVertPos)
        
        closestBnd = getClosestBndOnCurve(crv, param)
        allVertsInTree = [firstVert]
        allVertsInTree += allDesVerts
        
        bndToVertsMap[closestBnd] += allVertsInTree
    return bndToVertsMap

import rigger.modules.eye as eye
reload(eye)

def populateBndToVertsRingMap(crv, vertsTree):
    '''
    use this to get one vert ring per bind
    this is used to get a selection of verts that
    should not be relaxed (to prevent offsets b/t
    controls and deformations)
    '''
    bndToVertsRingMap = initBndToVertsMap(crv)
    firstVertsTrees = vertsTree.children
    for bnd in bndToVertsRingMap.keys():
        closestTree = eye.findClosestVertToJoint(bnd, 
                                                 firstVertsTrees)
        allVertsInTree = [closestTree.data.index()]
        allVertsInTree += [vert.index() for vert in 
                           closestTree.getAllDescendentsData()]
        bndToVertsRingMap[bnd] = allVertsInTree
    return bndToVertsRingMap

def findChildren(root, orphans):
    '''
    Recursive function to find vertex children
    Iterates through orphans list to find verts connected to root
    '''

    currOrphans = orphans[0]
    for eachVert in currOrphans:
        if root.data.isConnectedTo(eachVert):
            child = data.Tree()
            child.data = eachVert
            root.children.append(child)
            
    if len(orphans) > 1:
        for eachChild in root.children:
            findChildren(eachChild, orphans[1:])

def constructVertexLoops(loops):
    '''
    Organize verts into a tree
    This helps us to automatically weights joints later
    
    Select vertex loop round the eyelid
    Set global LOOPNUM
    '''
    
    LOOPNUM = loops
    vertLoops = mesh.VertexLoops(pm.ls(sl=True, fl=True), LOOPNUM)
    
    root = data.Tree()
    
    #pm.progressWindow(title='Analyzing vertices', progress=0, max=len(vertLoops[0]))
    
    # find children for each vert in selection
    for eachVert in vertLoops[0]:
        vertTree = data.Tree()
        vertTree.data = eachVert
        findChildren(vertTree, vertLoops[1:])
        root.children.append(vertTree)
        # increment progress window
        #pm.progressWindow(e=True, step=1, status='\nAnalysing %s' % eachVert)
    
    #pm.progressWindow(e=True, endProgress=True)
    
    return root