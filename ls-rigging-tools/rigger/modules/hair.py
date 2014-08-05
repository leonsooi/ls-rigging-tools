'''
Created on Aug 3, 2014

@author: Leon
'''
import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()
import pymel.core.nodetypes as nt

import rigger.lib.mesh as mesh
reload(mesh)

import rigger.modules.surfOffset as surfOffset
reload(surfOffset)

def addStrandMultAttr():
    '''
    select strand's ctls
    attr will be added to master
    '''
    ctls = pm.ls(sl=True)
    ctgs = [n.getParent() for n in ctls]
    strandName = ctgs[0].split('_')[2]
    grpName = '_'.join(ctgs[0].split('_')[:2])
    grpMaster = pm.PyNode(grpName+'_master_ctl')
    grpMaster.addAttr(strandName+'_Mult', k=True, dv=1)
    multAttr = grpMaster.attr(strandName+'_Mult')
    import rigger.utils.modulate as modulate
    reload(modulate)
    for ctg in ctgs:
        oldMd = ctg.r.inputs(p=True, scn=True)[0]
        newMdName = oldMd.nodeName()+'_'+strandName+'_rotMult'
        newMd = pm.createNode('multiplyDivide', n=newMdName)
        oldMd >> newMd.input1
        multAttr >> newMd.input2X
        multAttr >> newMd.input2Y
        multAttr >> newMd.input2Z
        newMd.output >> ctg.r

def connectPreBindMatrix():
    '''
    used for Mathilda's hair,
    so the controls can move with the lattice w/o double deform
    '''
    jnts = pm.ls(sl=True)
    for jnt in jnts:
        matPlug = jnt.worldMatrix.outputs(p=True)[0]
        preBindPlugName = matPlug.replace('.matrix', '.bindPreMatrix')
        preBindPlug = pm.PyNode(preBindPlugName)
        offsetGrp = jnt.getParent(3)
        offsetGrp.worldInverseMatrix >> preBindPlug

def createControl(name):
    ctl = pm.circle(nr=(1,0,0), sw=359, n=name+'_ctl', ch=False)[0]
    ctg = pm.group(ctl, n=name+'_ctg')
    cth = pm.group(ctg, n=name+'_cth')
    return cth, ctg, ctl

def buildHairRigFromGrp(crvGrp, jntsNum=3):
    '''
    hairGrp is a group with curves
    Z-axis is used for joint chain's up vector
    
    crvGrp = nt.Transform(u'RT_hairGrpE_crv_grp')
    jntsNum = 3
    '''
    headLat = pm.PyNode('CT_headLattice_dfm')
    headSkn = pm.PyNode('NEWGEO:CT_hair_geoShapeDeformed_skn')
    
    crvs = crvGrp.getChildren(ad=True, type='nurbsCurve')
    # create master for the group
    masterCtl = createControl(crvGrp.replace('_crv_grp','_master'))
    wMat = crvGrp.getMatrix(ws=True)
    masterCtl[0].setMatrix(wMat, ws=True)
    # add attrs for joint multipliers
    for jntId in range(jntsNum):
        # defaultMult = 1.0 / pow(2, jntId)
        masterCtl[2].addAttr('jnt_%d_mult'%jntId, dv=1, k=True)
    jntMults = [masterCtl[2].attr('jnt_%d_mult'%jntId) for jntId in range(jntsNum)]
    # multiply for rotations
    mds = []
    for jntId in range(jntsNum):
        md = pm.createNode('multiplyDivide', n=crvGrp.replace('_crv_grp','_master_rotMult%d'%jntId))
        masterCtl[2].r >> md.input1
        jntMults[jntId] >> md.input2X
        jntMults[jntId] >> md.input2Y
        jntMults[jntId] >> md.input2Z
        mds.append(md)
    
    # calculate upvector to orient joints
    upVec = pm.dt.Vector(0,0,1) * wMat
    upVec.normalize()
    
    # build controls for hair strands
    # iter through hair strands
    # store nodes so we can group things later
    wsDagList = []
    wsSurfList = []
    allCtlsList = []
    dcmList = []
    
    for crv in crvs:
        # get points on curve
        totalLen = crv.length()
        sectionLens = [totalLen/jntsNum*jntId for jntId in range(jntsNum+1)]
        params = [crv.findParamFromLength(length) for length in sectionLens]
        points = [crv.getPointAtParam(param) for param in params]
        # create controls
        parentPnts = points[:-1]
        childPnts = points[1:]
        parentCtl = None
        parentWsDag = None
        for ctlId, pPnt, cPnt in zip(range(jntsNum), parentPnts, childPnts):
            # calculate matrrix for control
            xVec = (cPnt - pPnt ).normal()
            yVec = upVec.cross(xVec).normal()
            zVec = xVec.cross(yVec).normal()
            mat = pm.dt.Matrix(xVec, yVec, zVec, pm.dt.Vector(pPnt))
            # this matrix should be affected by the headLattice
            latticeDag = pm.group(em=True, n=crv.replace('_crv','_latDag%d'%ctlId))
            latticeDagHm = pm.group(latticeDag, n=crv.replace('_crv','_latDagHm%d'%ctlId))
            latticeDagHm.setMatrix(mat, ws=True)
            wsDag, surf = surfOffset.addOffset(latticeDag)
            wsDagList.append(wsDag)
            wsSurfList.append(surf)
            # wsDag is the worldSpace transforms after headLattice deformation
            surfOffset.addSurfToDeformer([surf], headLat)
            # add control
            ctlList = createControl(crv.replace('_crv','_ctl%d'%ctlId))
            ctlList[0].setMatrix(mat, ws=True)
            # get transforms from wsDag (from lattice deformations)
            if parentCtl == None:
                # no parent, so just use wsDag directly
                xformPlug = wsDag.worldMatrix
                allCtlsList.append(ctlList[0])
            else:
                # get inversematrix of parent
                # so we can put this in parent space
                mm = pm.createNode('multMatrix', n=crv.replace('_crv','_mm%d'%ctlId))
                wsDag.worldMatrix >> mm.matrixIn[0]
                parentWsDag.worldInverseMatrix >> mm.matrixIn[1]
                xformPlug = mm.matrixSum
            # hierarchy
            ctlList[0].setParent(parentCtl)
            # update for the next iteration
            parentCtl = ctlList[2]
            parentWsDag = wsDag
            # set transforms on cth from xformPlug
            dcm = pm.createNode('decomposeMatrix', n=crv.replace('_crv','_dcm%d'%ctlId))
            dcmList.append(dcm)
            xformPlug >> dcm.inputMatrix
            dcm.outputTranslate >> ctlList[0].t
            dcm.outputRotate >> ctlList[0].r
            # connect master multipliers
            mds[ctlId].output >> ctlList[1].r
            # add joint under control
            pm.select(cl=True)
            jnt = pm.joint(n=crv.replace('_crv','_jnt%d'%ctlId))
            jnt.setParent(ctlList[2])
            jnt.setMatrix(pm.dt.Matrix())
            # bind joint to skin cluster
            headSkn.addInfluence(jnt, lw=True, wt=0)
            bindPostMatrixPlug = jnt.worldMatrix.outputs(p=True)[0]
            bindPreMatrixPlugName = bindPostMatrixPlug.replace('.matrix', '.bindPreMatrix')
            bindPreMatrixPlug = pm.PyNode(bindPreMatrixPlugName)
            wsDag.worldInverseMatrix >> bindPreMatrixPlug
            
    # organize stuff
    wsDagTops = [dag.getParent() for dag in wsDagList]
    wsSurfTops = [dag.getParent(2) for dag in wsSurfList]
    wsDagGrp = pm.group(wsDagTops, n=crvGrp.replace('_crv_grp','_wsDagGrp'))
    wsSurfGrp = pm.group(wsSurfTops, n=crvGrp.replace('_crv_grp','_wsSurfGrp'))
    ctlsGrp = pm.group(masterCtl[0], allCtlsList, n=crvGrp.replace('_crv_grp','_allCtlsGrp'))
    masterGrp = pm.group(wsDagGrp, wsSurfGrp, crvGrp, n=crvGrp.replace('_crv_grp','_rig_grp'))
    
    # move masterCtl with the first wsDag
    origMat = masterCtl[0].getMatrix(ws=True)
    dcmList[0].outputTranslate >> masterCtl[0].t
    dcmList[0].outputRotate >> masterCtl[0].r
    masterCtl[1].setMatrix(origMat, ws=True)
    
    return ctlsGrp, masterGrp 

def createHairCurveFromVertexSelection():
    '''
    select a loop of verts
    creates a curve in the center of mesh
    '''
    verts = pm.ls(os=True, fl=True)
    sv = mesh.SortedVertices(verts)
    edgeRing = getEdgeRingList(sv.verts)
    # iterate through edge ring to get center positions
    posList = [getEdgeLoopCenter(edge) for edge in edgeRing]
    # create curve
    crv = pm.curve(p=posList)

def getEdgeLoopCenter(edge):
    '''
    extend edge to loop
    return center of boundingbox
    '''
    loop = mel.polySelectSp(edge, loop=True)
    bb = pm.exactWorldBoundingBox(loop)
    xpos = (bb[0] + bb[3])/2.0
    ypos = (bb[1] + bb[4])/2.0
    zpos = (bb[2] + bb[5])/2.0
    return xpos, ypos, zpos

def getEdgeRingList(verts):
    # iterate verts from 1 to -1
    edgering = []
    for vert in verts[1:-1]:
        connectedVerts = vert.connectedVertices()
        for adjVert in connectedVerts:
            if adjVert not in verts:
                break
        edgeVerts = [vert, adjVert]
        edge = pm.polyListComponentConversion(edgeVerts, fv=True, 
                                              te=True, internal=True)
        edgering.append(edge)
    return edgering 