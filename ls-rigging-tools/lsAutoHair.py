import maya.cmds as mc
from maya.mel import eval as meval
import lsLib as ll

def lsSnap(target, object, operation=0):
    constraints = {
    0:mc.parentConstraint,
    1:mc.pointConstraint,
    2:mc.orientConstraint}
    tempCons = constraints[operation](target, object)
    mc.delete(tempCons)

def lsZeroOut(object, suffix='zeroOut'):
    grp = mc.group(em=1, n='%s_%s'%(object, suffix))
    lsSnap(object, grp)
    parents = mc.listRelatives(object, parent=1, fullPath=1)
    if parents:
        mc.parent(grp, parents[0])
    mc.parent(object, grp)
    return grp

# rig settings
CREATE_IK = True
CREATE_FK = True
CREATE_PROC = True
CREATE_DYN = True
CENTER_CRV = True
EDGE_STEP = 7


# select startEdge, then endEdge
selEdges = mc.ls(sl=1)[0:2]
endEdgeUndo = mc.undoInfo(q=1, un=1)
prefix = selEdges[0].split('[')[0]
endEdgeIndex = int(endEdgeUndo.split('[')[1][:-2])
selEdgesIndex = [int(edgeName.split('[')[1][:-1]) for edgeName in selEdges]

for eachEdge in selEdgesIndex:
    if eachEdge != endEdgeIndex:
        startEdgeIndex = eachEdge
        break
        
edgeLoopIndices = mc.polySelect(elp=[startEdgeIndex, endEdgeIndex], ns=1)
edgeLoop = ['%s[%d]'%(prefix, edgeIndex) for edgeIndex in edgeLoopIndices]
if edgeLoopIndices[-1] == startEdgeIndex:
    edgeLoop.reverse()
    edgeLoopIndices.reverse()

centerPositions = []

# loop through edges to store center positions
for i in range(len(edgeLoop)-1):
    currEdge = edgeLoop[i]
    currEdgeIndex = edgeLoopIndices[i]
    nextEdge = edgeLoop[i+1]
    nextEdgeIndex = edgeLoopIndices[i+1]
    
    currRing = mc.polySelect(er=currEdgeIndex, ns=1, ass=1)
    nextRing = mc.polySelect(er=nextEdgeIndex, ns=1, ass=1)
    
    currVerts = mc.filterExpand(mc.polyListComponentConversion(currRing, toVertex=1), sm=31)
    nextVerts = mc.filterExpand(mc.polyListComponentConversion(nextRing, toVertex=1), sm=31)
    
    selVerts = list(set(currVerts) - set(nextVerts))
    mc.select(selVerts, r=1)
    boundingBox = mc.polyEvaluate(selVerts, boundingBoxComponent=1)
    ctrPos = [(axis[0]+axis[1])/2 for axis in boundingBox]
    centerPositions.append(ctrPos)
    
# get center positions for the last 2 rings
currEdge = edgeLoop[-1]
currEdgeIndex = edgeLoopIndices[-1]
prevEdge = edgeLoop[-2]
prevEdgeIndex = edgeLoopIndices[-2]

currRing = mc.polySelect(er=currEdgeIndex, ns=1, ass=1)
prevRing = mc.polySelect(er=prevEdgeIndex, ns=1, ass=1)

currVerts = mc.filterExpand(mc.polyListComponentConversion(currRing, toVertex=1), sm=31)
prevVerts = mc.filterExpand(mc.polyListComponentConversion(prevRing, toVertex=1), sm=31)

selVerts = list(set(currVerts) & set(prevVerts))
mc.select(selVerts, r=1)
boundingBox = mc.polyEvaluate(selVerts, boundingBoxComponent=1)
ctrPos = [(axis[0]+axis[1])/2 for axis in boundingBox]
centerPositions.append(ctrPos)

selVerts = list(set(currVerts) - set(prevVerts))
mc.select(selVerts, r=1)
boundingBox = mc.polyEvaluate(selVerts, boundingBoxComponent=1)
ctrPos = [(axis[0]+axis[1])/2 for axis in boundingBox]
centerPositions.append(ctrPos)

# filter down centerPositions list to every EDGE_STEPth edge
centerPositionsFiltered = centerPositions[::EDGE_STEP]
if not centerPositionsFiltered[-1] == centerPositions[-1]:
    centerPositionsFiltered.append(centerPositions[-1])

# create joint chain
mc.select(cl=1)
jntList = []
jntName = prefix.replace('.','_') + '%d_'%(startEdgeIndex)
for eachPos in centerPositionsFiltered:
    jntList.append(mc.joint(p=[eachPos[0], eachPos[1], eachPos[2]], n='%sjnt%d'%(jntName, len(jntList))))

mc.joint(jntList, edit=1, orientJoint='xyz', secondaryAxisOrient='yup', children=1, zeroScaleOrient=1)

# make FK and IK chains
FKjntList = mc.duplicate(jntList, n='%sFKjnt0'%jntName)
IKjntList = mc.duplicate(jntList, n='%sIKjnt0'%jntName)

# create hair master ctrl
mc.select(jntList[0])
meval('wireShape("plus")')
masterCtrl = mc.rename('%smasterctrl'%jntName)
masterCtrlZero = lsZeroOut(masterCtrl)
mc.addAttr(masterCtrl, ln='FK', at='float', dv=1, min=0, max=1, k=1)
mc.addAttr(masterCtrl, ln='IK', at='float', dv=0, min=0, max=1, k=1)
mc.addAttr(masterCtrl, ln='DY', at='float', dv=0, min=0, max=1, k=1)
mc.addAttr(masterCtrl, ln='FkMaster', at='bool', k=1)
mc.setAttr(masterCtrl+'.FkMaster', l=1)
mc.addAttr(masterCtrl, ln='Curl', at='float', k=1)
mc.addAttr(masterCtrl, ln='Twist', at='float', k=1)
mc.addAttr(masterCtrl, ln='Wave', at='float', k=1)

# constraints for IK and FK chains to drive bnJnts
for i in range(len(jntList)):
    cons = mc.parentConstraint(FKjntList[i], IKjntList[i], jntList[i])[0]
    weightList = mc.parentConstraint(cons, q=1, wal=1)
    mc.connectAttr(masterCtrl+'.FK', cons+'.'+weightList[0], f=1)
    mc.connectAttr(masterCtrl+'.IK', cons+'.'+weightList[1], f=1)
    cons = mc.scaleConstraint(FKjntList[i], IKjntList[i], jntList[i])[0]
    weightList = mc.scaleConstraint(cons, q=1, wal=1)
    mc.connectAttr(masterCtrl+'.FK', cons+'.'+weightList[0], f=1)
    mc.connectAttr(masterCtrl+'.IK', cons+'.'+weightList[1], f=1)

jntGrp = mc.group(em=1, n=jntName+'jntGrp')
lsZeroOut(jntGrp)
mc.parentConstraint(masterCtrl, jntGrp, mo=1)
mc.parent(jntList[0], FKjntList[0],IKjntList[0], jntGrp)


# create circle FK controls on joint chain
def createFKCtrlsOnJnts(jntChain, parentCtrl, radius=1):  
    prev = parentCtrl
    for jnt in jntChain:    
        ctrl = mc.circle(r=radius, nr=(1,0,0), n=jnt.replace('FKjnt', 'FKctrl'), ch=0)[0]
        lsSnap(jnt, ctrl)
        ctrlParent = lsZeroOut(ctrl)
        ctrlOffset = lsZeroOut(ctrl, 'offset')
        mc.parentConstraint(ctrl, jnt, mo=1)
        mc.parent(ctrlParent, prev)
        mc.connectAttr(parentCtrl+'.Curl', ctrlOffset+'.rotateZ', f=1)
        mc.connectAttr(parentCtrl+'.Wave', ctrlOffset+'.rotateY', f=1)
        mc.connectAttr(parentCtrl+'.Twist', ctrlOffset+'.rotateX', f=1)
        prev = ctrl
createFKCtrlsOnJnts(FKjntList, masterCtrl, 0.5)

# create IK spline ctrls
ikH, eff, ikCrv = mc.ikHandle(n=jntName+'ikH', sj=IKjntList[0], ee=IKjntList[-1], solver='ikSplineSolver', ccv=1, scv=0)
eff = mc.rename(eff, jntName+'eff')
ikCrv = mc.rename(ikCrv, jntName+'ikCrv')
mc.parent(ikCrv, masterCtrlZero)
mc.parent(ikH, jntGrp)

# constraint first CV to masterCtrl
clus = mc.cluster(ikCrv+'.cv[0]', n=masterCtrl.replace('masterctrl','ikClus0'))
mc.parentConstraint(masterCtrl, clus)

def createIKCtrlsOnJnts(ikCrv, parentCtrl, size=1):
    ikCVNum = ll.getCurveCVCount(ikCrv)
    prev=parentCtrl
    for i in range(1, ikCVNum):
        clus = mc.cluster('%s.cv[%d]'%(ikCrv, i), n=parentCtrl.replace('masterctrl','ikClus%d')%i)
        cvPos = mc.xform('%s.cv[%d]'%(ikCrv, i), q=1, ws=1, t=1)
        mc.select(parentCtrl)
        meval('wireShape("plus")')
        ikCtrl = mc.rename(masterCtrl.replace('masterctrl','ikCtrl%d'%i))
        mc.xform(ikCtrl, t=cvPos, ws=1)
        mc.scale(size, size, size, ikCtrl, ocp=1)
        mc.makeIdentity(ikCtrl, a=1, s=1)
        mc.parent(ikCtrl, parentCtrl)
        lsZeroOut(ikCtrl)
        ctrlPR = lsZeroOut(ikCtrl, 'PR')
        mc.addAttr(ikCtrl, ln='SPACE', at='bool', k=1)
        mc.setAttr(ikCtrl+'.SPACE', l=1)
        mc.addAttr(ikCtrl, ln='parent', at='float', dv=0, min=0, max=1, k=1)
        mc.addAttr(ikCtrl, ln='master', at='float', dv=1, min=0, max=1, k=1)
        mc.addAttr(ikCtrl, ln='world', at='float', dv=0, min=0, max=1, k=1)
        mc.parentConstraint(ikCtrl, clus)
        cons = mc.parentConstraint(prev, parentCtrl, ctrlPR, mo=1)[0]
        wal = mc.parentConstraint(cons, q=1, wal=1)
        if len(wal) > 1:
            mc.connectAttr(ikCtrl+'.parent', '%s.%s'%(cons, wal[0]), f=1)
            mc.connectAttr(ikCtrl+'.master', '%s.%s'%(cons, wal[1]), f=1)
        prev=ikCtrl
        
createIKCtrlsOnJnts(ikCrv, masterCtrl, 0.5)

# stretchy ik joints
ikCrvInfo = mc.shadingNode('curveInfo', asUtility=1, n=masterCtrl.replace('masterctrl', 'crvInfo'))
mc.connectAttr(ikCrv+'Shape.worldSpace[0]', ikCrvInfo+'.inputCurve', f=1)
baseLen = mc.getAttr(ikCrvInfo+'.arcLength')
scaleMd = mc.shadingNode('multiplyDivide', asUtility=1, n=masterCtrl.replace('masterctrl','md_scale'))
mc.setAttr(scaleMd+'.input2X', baseLen)
mc.connectAttr(ikCrvInfo+'.arcLength', scaleMd+'.input1X', f=1)
mc.setAttr(scaleMd+'.operation', 2)
[mc.connectAttr(scaleMd+'.outputX', jnt+'.scaleX', f=1) for jnt in IKjntList]