import time

import pymel.core as pm

import cgm.lib.deformers as cgmDeformers

import lsAutoRig.lib.mesh as mesh
reload(mesh)
import lsAutoRig.lib.datatypes as data
reload(data)

def constructEyelidsRig():
    prefix = 'CT_'
    # select edge loop
    # ... [user]
    crv = pm.polyToCurve(form=1, degree=3, ch=False)[0]
    crv = pm.PyNode(crv)
    crv.rename(prefix + 'eyelidAim_crv_0')
    
    # add locators to crv
    for param in range(crv.numSpans()):
        loc = pm.spaceLocator(n=crv.replace('_crv','_loc').replace('_0','_%d'%param))
        poci = pm.createNode('pointOnCurveInfo', n=crv.replace('_crv_','_poci_').replace('_0','_%d'%param))
        crv.worldSpace >> poci.inputCurve
        poci.position >> loc.translate
        poci.parameter.set(param)
        loc.localScale.set(0.2,0.2,0.2)

    # get pivot - center of eye
    pivotgeo = 'pivot_geo'
    pivotgeo = pm.PyNode(pivotgeo)
    eyePivotVec = pivotgeo.rotatePivot.get()
    
    # create joints
    eyeAimJnts = []
    
    for param in range(crv.numSpans()):
        pm.select(cl=True)
        baseJnt = pm.joint(n=crv.replace('_crv_','_jnt_').replace('_0','_%d'%param), p=eyePivotVec)
        endPivotVec = crv.cv[param].getPosition()
        endJnt = pm.joint(n=crv.replace('_crv_','_bnd_').replace('_0','_%d'%param), p=endPivotVec)
        baseJnt.orientJoint('xyz')
        endJnt.jointOrient.set(0,0,0)
        ikHdl, ikEff = pm.ikHandle(n=baseJnt.replace('_jnt_', '_hdl_'), sj=baseJnt, ee=endJnt, solver='ikSCsolver')
        loc = pm.PyNode(baseJnt.replace('_jnt_', '_loc_'))
        loc | ikHdl
    
        eyeAimJnts.append(baseJnt)
        eyeAimJnts.append(endJnt)
    
    [jnt.radius.set(0.3) for jnt in eyeAimJnts]

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