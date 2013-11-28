import time

import pymel.core as pm

import lsAutoRig.lib.mesh as mesh
reload(mesh)
import lsAutoRig.lib.datatypes as data
reload(data)

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

def constructVertexLoops():
    '''
    Organize verts into a tree
    This helps us to automatically weights joints later
    
    Select vertex loop round the eyelid
    Set global LOOPNUM
    '''
    
    LOOPNUM = 6
    vertLoops = mesh.VertexLoops(pm.ls(sl=True, fl=True), LOOPNUM)
    
    root = data.Tree()
    
    # find children for each vert in selection
    for eachVert in vertLoops[0]:
        vertTree = data.Tree()
        vertTree.data = eachVert
        findChildren(vertTree, vertLoops[1:])
        root.children.append(vertTree)
        
    return root

def viewVertexLoops(root):
    '''
    '''
    for eachChild in root.children:
    
        for genId in range(9):
            toSel = eachChild.getDescendents(genId)
            pm.select([vert.data for vert in toSel])
            pm.refresh()
            time.sleep(0.1)
            
def test():
    # select vertex loop
    # ...
    root = constructVertexLoops()
    viewVertexLoops(root)