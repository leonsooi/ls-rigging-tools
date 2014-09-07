'''
Created on Feb 14, 2014

@author: Leon
'''

from ngSkinTools.mllInterface import MllInterface
import cgm.lib.curves as curves
import cgm.lib.position as cgmPos
import cgm.lib.rigging as cgmrigging
import maya.cmds as mc
import ngSkinToolsPlus.lib.weights as ngWeights
import pymel.core as pm
import pymel.core.nodetypes as nt
import rigger.modules.eye as eye
import utils.rigging as rt
reload(eye)
reload(rt)

reload(ngWeights)



mel = pm.language.Mel()

def selectVertsClosestToBnds(mll):
    infIter = mll.listLayerInfluences(2)
    infs = list(infIter)
    mesh = mll.getTargetInfo()[0]
    mesh = pm.PyNode(mesh)
    vertIds = []
    for inf, infId in infs:
        pos = pm.PyNode(inf).getTranslation(space='world')
        faceId = mesh.getClosestPoint(pos, space='world')[1]
        faceVertIds = mesh.f[faceId].getVertices()
        closestVertId = min(faceVertIds, key=lambda vtxId: (mesh.vtx[vtxId].getPosition() - pos).length())
        vertIds += [closestVertId]
    
    closestVerts = [mesh.vtx[i] for i in vertIds]
    pm.select(closestVerts)

def addPerimeterBndSystem(mesh, perimeterPLocs):
    '''
    depcrecated
    '''
    
    periBnds = []
    
    pLocs = [pm.PyNode(pLoc) for pLoc in perimeterPLocs]
    locScale = pLocs[0].localScaleX.get()
    vecScale = locScale * 2.0
    
    # slice lists for prevLocs, currLocs and nextLocs
    prevLocs = pLocs[:-2]
    currLocs = pLocs[1:-1]
    nextLocs = pLocs[2:]
    
    for prevLoc, currLoc, nextLoc in zip(prevLocs, currLocs, nextLocs):
        if 'LT_' in currLoc.name():
            mirror=True
        else:
            mirror=False
        periBnds += addPerimeterBnd(currLoc, prevLoc, nextLoc, 
                                    mesh, mirror, vecMult=vecScale)
    
    periGrp = pm.group(periBnds, n='CT_perimeterBnds_grp')
    return periGrp


def addPerimeterBnd(currBnd, prevBnd, nextBnd, mesh, mirror, vecMult=1.0):
    """
    DEPRECATED
    make facePerimeterBnd
    currBnd = pm.PyNode('LT_up_jaw_bnd')
    prevBnd = pm.PyNode('LT_out_cheek_bnd')
    nextBnd = pm.PyNode('LT_corner_jaw_bnd')
    mesh = pm.PyNode('body_geo')
    """
    
    currPos = currBnd.getTranslation(space='world')
    prevPos = prevBnd.getTranslation(space='world')
    nextPos = nextBnd.getTranslation(space='world')
    
    prevVec = currPos - prevPos
    prevVec.normalize()
    nextVec = nextPos - currPos
    nextVec.normalize()
    
    tangVec = (prevVec + nextVec) / 2.0
    tangVec.normalize()
    
    normVec = mesh.getClosestNormal(currPos)[0]
    
    outVec = normVec.cross(tangVec)
    outVec.normalize()
    
    outPos = currPos + outVec * vecMult
    
    # snap back to mesh surface
    outPos = mesh.getClosestPoint(outPos)[0]
    
    pm.select(cl=True)
    periJnt = pm.joint(n=currBnd.name() + '_perimeter_bnd')
    periJnt.radius.set(0.1)
    periJnt.setTranslation(outPos, space='world')
    
    
    
    if mirror:
        pm.select(cl=True)
        mirrorOutPos = outPos * (-1, 1, 1)
        mirrorPeriJnt = pm.joint(n=currBnd.name().replace('LT_', 'RT_') + '_perimeter_bnd')
        mirrorPeriJnt.radius.set(0.1)
        mirrorPeriJnt.setTranslation(mirrorOutPos, space='world')
        return [periJnt, mirrorPeriJnt]
    else:
        return [periJnt]

def patchToFixScale(bnd):
    '''
    # PATCH TO PRIMARY DRIVERS BW IN V39
    # patch to fix priDrv scale (through blendweighteds)
    # subtract 1 from the decomposeMatrix node, so that scales are nornmalized to 0
    # blendweighted node blends values at 0
    # add 1 to blended value, then pass to priDrv
    
    e.g.
    bnd = pm.PyNode('lf_low_cheek_bnd')
    '''
    priDrv = bnd.getParent(2)
    channels = ['sx', 'sy', 'sz']
    bwNds = [bnd.attr(ch + '_bwMsg').get() for ch in channels]
    
    # ITER through bwNds to fix each one
    for bwNd in bwNds:
        # ##bwNd = bwNds[0]
        
        inputAttrs = bwNd.input.inputs(p=True, s=True)
        inputNds = [attr.node() for attr in inputAttrs]
        
        # ITER through each input to remove BTA,
        # and subtract 1
        for attr, nd in zip(inputAttrs, inputNds):
            # ##attr = inputAttrs[0]
            # ##nd = inputNds[0]
            adl = pm.createNode('addDoubleLinear', n=nd.replace('_bta', '_adl'))
            # get bta's input
            btaInput = nd.input[1].inputs(s=True, p=True)[0]
            # reroute bta input to adl
            btaInput >> adl.input1
            adl.input2.set(-1)
            # adl connect bw (replace bta)
            inputPlug = attr.outputs(p=True)[0]
            adl.output >> inputPlug
            # get the index, so that we can also connect the weight
            # (assuming they follow the same logical index)
            inputId = inputPlug.index()
            weightPlug = nd.attributesBlender.inputs(p=True)[0]
            weightPlug >> bwNd.weight[inputId]
            # delete BTA
            pm.delete(nd)
            
        # add 1 to the bwNd output
        outPlug = bwNd.output.outputs(p=True)[0]
        adl = pm.createNode('addDoubleLinear', n=bwNd.replace('_bw', '_adl'))
        bwNd.output >> adl.input1
        adl.input2.set(1)
        adl.output >> outPlug

def addMotionSystemToBnd(bnd):
    # msg attr to ctl
    ctl = pm.PyNode(bnd.name().replace('_bnd', '_ctrl'))
    ctg = ctl.getParent()
    bndPriDrv = bnd.getParent(2)
    bnd.addAttr('ctlMsg', at='message')
    ctl.message >> bnd.ctlMsg
    
    # build motion system - SDK
    sdkDag = pm.group(n=bnd.name().replace('_bnd', '_sdk'), em=True)
    sdkGrp = pm.group(sdkDag, n=sdkDag.name() + '_priDrv')
    sdkHm = pm.group(sdkGrp, n=sdkDag.name() + '_hm')
    bnd.addAttr('sdkMsg', at='message')
    sdkDag.message >> bnd.sdkMsg
    
    cons = pm.parentConstraint(bnd, sdkHm)    
    pm.delete(cons)
    
    # build motion system - weightedConnections
    # we need 9 bw nodes, one for each channel
    channels = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    bwNodes = {}
    for eachChannel in channels:
        bwNd = pm.createNode('blendWeighted', n=bnd.name().replace('_bnd', '_%s_bw' % eachChannel))
        bwNodes[eachChannel] = bwNd
        bnd.addAttr(eachChannel + '_bwMsg', at='message')
        bwNd.message >> bnd.attr(eachChannel + '_bwMsg')
        # connect bw output to sdk's priDrv
        # if scale, need to add 1 (normalize to 1)
        if eachChannel in ['sx', 'sy', 'sz']:
            adl = pm.createNode('addDoubleLinear', n=bnd.name().replace('_bnd', '_%s_add1_adl' % eachChannel))
            bwNd.output >> adl.input1
            adl.input2.set(1)
            adl.output >> sdkGrp.attr(eachChannel)
        else:
            bwNd.output >> sdkGrp.attr(eachChannel)
    
    # get finalPrimaryMatrix from multiplying priDrv and sdk
    mmNd = pm.createNode('multMatrix', n=bnd.name().replace('_bnd', '_finalPri_mm'))
    sdkGrp.matrix >> mmNd.matrixIn[0]
    sdkDag.matrix >> mmNd.matrixIn[1]
    dmNd = pm.createNode('decomposeMatrix', n=bnd.name().replace('_bnd', '_finalPri_dm'))
    mmNd.matrixSum >> dmNd.inputMatrix
    dmNd.outputTranslate >> ctg.translate
    dmNd.outputRotate >> ctg.rotate
    dmNd.outputScale >> ctg.scale
    ctg.t >> bndPriDrv.t
    ctg.r >> bndPriDrv.r
    ctg.s >> bndPriDrv.s
    
    return sdkHm

def addMotionSystemToBndGo():
    bnds = pm.ls(sl=True)
    mss = []
    
    for eachBnd in bnds:
        ms = addMotionSystemToBnd(eachBnd)
        mss.append(ms)
    pm.group(mss, n='face_motion_grp')
        
# addMotionSystemToBndGo()

    
def addPrimaryCtlToBnd(bnd):
    # create ctl
    ctl = pm.circle(n=bnd.name().replace('_bnd', '_pri_ctrl'))
    ctg = pm.group(ctl, n=ctl[0].name() + '_ctg')
    cth = pm.group(ctg, n=ctg.name() + '_cth')
    
    # position ctl
    cons = pm.parentConstraint(bnd, cth)
    pm.delete(cons)
    
    # shape ctl
    ctl_radius = bnd.radius.get()
    ctl[1].radius.set(ctl_radius * 2.0)
    ctl[1].sweep.set(359)
    ctl[1].centerZ.set(ctl_radius)
    pm.delete(ctl, ch=True)
    
    # attach message to bnd
    bnd.addAttr('attached_pri_ctl', at='message')
    ctl[0].message >> bnd.attr('attached_pri_ctl')
    
    return ctl[0]
    
# addPrimaryCtlToBnd(pm.ls(sl=True)[0])

def connectBndsToPriCtlGo():
    bnds = pm.ls(sl=True)[:-1]
    priCtl = pm.ls(sl=True)[-1]
    for eachBnd in bnds:
        connectBndToPriCtl(eachBnd, priCtl)
    pm.select(priCtl)
    
def connectBndsToPriCtlCmd(priCtl, bnds):
    for eachBnd in bnds:
        connectBndToPriCtl(eachBnd, priCtl)

def updateBndToPriCtl(bnd, priCtl):
    '''
    update bnd's localMatrix inside priCtl's space
    make sure everything is zeroed out before running
    '''
    # bnd's "local" matrix within priCtl
    bnd_wMat = bnd.getMatrix(ws=True)
    priCtl_wMat = priCtl.getMatrix(ws=True)
    bnd_lMat = bnd_wMat * priCtl_wMat.inverse()
    
    lMatNd = pm.PyNode(bnd.replace('_bnd', '_lMat_in_' + priCtl.stripNamespace().nodeName()))
    for i in range(4):
        for j in range(4):
            lMatNd.attr('in%d%d' % (i, j)).set(bnd_lMat[i][j])

def connectBndToPriCtl(bnd, priCtl, simplify=False):
    '''
    bnd = pm.PyNode('lf_nostrilf_bnd')
    priCtl = pm.PyNode('nose_pri_ctrl')
    '''
    # bnd's "local" matrix within priCtl
    bnd_wMat = bnd.getMatrix(ws=True)
    priCtl_wMat = priCtl.getMatrix(ws=True)
    bnd_lMat = bnd_wMat * priCtl_wMat.inverse()
    lMatNd = pm.createNode('fourByFourMatrix', n=bnd.replace('_bnd', '_lMat_in_' + priCtl.stripNamespace().nodeName()))
    # populate "local" matrix
    for i in range(4):
        for j in range(4):
            lMatNd.attr('in%d%d' % (i, j)).set(bnd_lMat[i][j])
    # bnd's "local-inverse" matrix
    lInvMatNd = pm.createNode('inverseMatrix', n=bnd.replace('_bnd', '_lInvMat_in_' + priCtl.stripNamespace().nodeName()))
    lMatNd.output >> lInvMatNd.inputMatrix
    # for bnd to pivot around priCtl,
    # the matrix is lMat * priCtlMat * lInvMat
    mmNd = pm.createNode('multMatrix', n=bnd.replace('_bnd', '_calc_mm'))
    lMatNd.output >> mmNd.i[0]
    priCtl.matrix >> mmNd.i[1]
    lInvMatNd.outputMatrix >> mmNd.i[2]
    # decompose matrix before passing into bw
    dmNd = pm.createNode('decomposeMatrix', n=bnd.replace('_bnd', '_calc_dm'))
    mmNd.o >> dmNd.inputMatrix
    # get bw nodes to connect to
    channels = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    bwNodes = {}
    for eachChannel in channels:
        bwNodes[eachChannel] = bnd.attr(eachChannel + '_bwMsg').get()
    # get index to connect to
    existingInputs = bwNodes['tx'].i.inputs()
    nextIndex = len(existingInputs)
    # actual connections
    dmNd.otx >> bwNodes['tx'].i[nextIndex]
    dmNd.oty >> bwNodes['ty'].i[nextIndex]
    dmNd.otz >> bwNodes['tz'].i[nextIndex]
    dmNd.orx >> bwNodes['rx'].i[nextIndex]
    dmNd.ory >> bwNodes['ry'].i[nextIndex]
    dmNd.orz >> bwNodes['rz'].i[nextIndex]
    dmNd.osx >> bwNodes['sx'].i[nextIndex]
    dmNd.osy >> bwNodes['sy'].i[nextIndex]
    dmNd.osz >> bwNodes['sz'].i[nextIndex]
    # channel box separator
    bnd.addAttr(priCtl.stripNamespace().nodeName() + '_weights', at='double', k=True, dv=0)
    bnd.setAttr(priCtl.stripNamespace().nodeName() + '_weights', lock=True)
    # connect weight to be blended to 0
    for eachChannel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
        bnd.addAttr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=1)
        bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
    # scales need a minus 1, to be normalized to 0 for blending
    for eachChannel in ['sx', 'sy', 'sz']:
        adl = pm.createNode('addDoubleLinear', n=bnd.replace('_bnd', '_%s_adl' % eachChannel))
        adl.input2.set(-1)
        dmNd.attr('o%s' % eachChannel) >> adl.input1
        adl.output >> bwNodes[eachChannel].i[nextIndex]
        bnd.addAttr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=1)
        bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
        
    # if this bnd already has it's own attached priCtl
    # we need to drive that too
    if bnd.hasAttr('attached_pri_ctl'):
        attachedCtl = bnd.attr('attached_pri_ctl').get()
        
        if attachedCtl != priCtl:
            print 'Bnd: ' + bnd
            print 'Current Pri Ctl: ' + priCtl
            print 'Attached Pri Ctl: ' + attachedCtl
            attachedCtg = attachedCtl.getParent()
            # add zero grp to take in connections
            zeroGrp = pm.PyNode(cgmrigging.groupMeObject(attachedCtg.nodeName(), True, True))
            for eachChannel in channels:
                mdl = pm.createNode('multDoubleLinear', n=bnd.replace('_bnd', '_%s_%s_mdl' % (eachChannel, priCtl)))
                if eachChannel in ['sx', 'sy', 'sz']:
                    adl = pm.createNode('addDoubleLinear', n=bnd.replace('_bnd', '_%s_%s_adl' % (eachChannel, priCtl)))
                    dmNd.attr('o' + eachChannel) >> adl.input1
                    adl.input2.set(-1)
                    adl.output >> mdl.input1
                else:
                    dmNd.attr('o' + eachChannel) >> mdl.input1
                    
                bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel) >> mdl.input2
                
                if eachChannel in ['sx', 'sy', 'sz']:
                    adl = pm.createNode('addDoubleLinear', n=bnd.replace('_bnd', '_%s_%s_adl' % (eachChannel, priCtl)))
                    mdl.output >> adl.input1
                    adl.input2.set(1)
                    adl.output >> zeroGrp.attr(eachChannel)
                else:
                    mdl.output >> zeroGrp.attr(eachChannel)
    
    if simplify:
        # hide the 9 individual attrs
        # add one attr to drive all 9
        bnd.addAttr(priCtl.stripNamespace().nodeName() + '_weight_',
                    at='double', min=-1, max=2, dv=1)
        for eachChannel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            bnd.setAttr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel, 
                        k=False, cb=False)  
            bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_') >> bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel)
    
# connectBndsToPriCtlGo()

def addSecondaryCtlToBnd(bnd):
    # add secondary control to bnd
    # create ctl
    ctl = pm.circle(n=bnd.name().replace('_bnd', '_ctrl'))
    ctg = pm.group(ctl, n=ctl[0].name() + '_ctg')
    cth = pm.group(ctg, n=ctg.name() + '_cth')
    
    # position ctl
    cons = pm.parentConstraint(bnd, cth)
    pm.delete(cons)
    
    # shape ctl
    ctl_radius = bnd.radius.get()
    ctl[1].radius.set(ctl_radius)
    ctl[1].sweep.set(359)
    ctl[1].centerZ.set(ctl_radius)
    pm.delete(ctl, ch=True)
    
    # get secondaryDrv
    secDrv = bnd.getParent(1)
    ctl[0].t >> secDrv.t
    ctl[0].r >> secDrv.r
    ctl[0].s >> secDrv.s
    
    return cth

    
def addSecondaryCtls():
    bnds = pm.ls(sl=True)
    cths = []
    for eachBnd in bnds:
        cth = addSecondaryCtlToBnd(eachBnd)
        cths.append(cth)
    pm.group(cths, n='face_ctrls_grp')
    
# addSecondaryCtls()

def createBndFromPlacementLoc(pLoc, bndGrp):
    '''
    '''
    pm.select(cl=True)
    xfo = pLoc.getMatrix(worldSpace=True)
    jnt = pm.joint(n=pLoc.replace('pLoc', 'bnd'))
    jnt.setMatrix(xfo)
    scale = pLoc.localScaleX.get()
    jnt.radius.set(scale)
    bndGrp | jnt
    return jnt

def createBndsFromPlacement(placementGrp):
    '''
    placementGrp [PyNode.Transform] - parent of placement locs and attrs
    '''
    bndGrp = pm.group(n='CT_bnd_grp', em=True)
    
    #===========================================================================
    # Direct bnds - one bnd jnt for each loc
    #===========================================================================
    directPLoc = placementGrp.getChildren()
    directPLoc = [loc for loc in directPLoc
                  if loc.hasAttr('bindType')]
    
    for eachLoc in directPLoc:
        pm.select(cl=True)
        xfo = eachLoc.getMatrix(worldSpace=True)
        jnt = pm.joint(n=eachLoc.replace('pLoc', 'bnd'))
        jnt.setMatrix(xfo)
        scale = eachLoc.localScaleX.get()
        jnt.radius.set(scale)
        bndGrp | jnt
    
    return bndGrp
    
    
def placeBndBetweenLocs(name, ptWeights, mesh, bndGrp, mirror=False):
    '''
    name [string]
    ptWeights [dict] - {pt: weight}
    mesh [pm.Mesh] - mesh to snap to
    mirror [bool] - mirror from LT to RT
    '''
    totalPt = pm.dt.Point()
    totalWt = sum(ptWeights.values())
    for pt, wt in ptWeights.items():
        totalPt += pt * wt / totalWt
    
    finalPt = mesh.getClosestPoint(totalPt)[0]
    
    pm.select(cl=True)
    jnt = pm.joint(n=name)
    jnt.t.set(finalPt)
    bndGrp | jnt
    
    if mirror:
        finalPt = finalPt * (-1, 1, 1)
        pm.select(cl=True)
        jnt = pm.joint(n=name.replace('LT', 'RT'))
        jnt.t.set(finalPt)
        bndGrp | jnt
    
    
def getParamFromCV(cv):
    crv = cv.node()
    pos = cv.getPosition()
    cPt = crv.closestPoint(pos)
    param = crv.getParamAtPoint(cPt)
    return param

def addSecondaryControlSystemToBnd(bnd):
    '''
    '''
    # add hierarchy for secDrv and priDrv
    bndHm = pm.PyNode(cgmrigging.groupMeObject(str(bnd), parent=True, maintainParent=True))
    bndHm.rename(bnd.replace('_bnd', '_bnd_hm'))
    priDrv = pm.PyNode(cgmrigging.groupMeObject(str(bnd), parent=True, maintainParent=True))
    priDrv.rename(bnd.replace('_bnd', '_priDrv_bnd'))
    secDrv = pm.PyNode(cgmrigging.groupMeObject(str(bnd), parent=True, maintainParent=True))
    secDrv.rename(bnd.replace('_bnd', '_secDrv_bnd'))  
    # reset joint orient
    bnd.r.set(0, 0, 0)
    bnd.jointOrient.set(0, 0, 0)
    # control
    cth = addSecondaryCtlToBnd(bnd)
    # motion
    ms = addMotionSystemToBnd(bnd)
    return cth, ms
    


def buildSecondaryControlSystem(placementGrp, bndGrp, mesh):
    '''
    '''
    bnds = bndGrp.getChildren()

    #===========================================================================
    # Set up hierarchy
    #===========================================================================
    pm.progressWindow(title='Build Motion System', progress=0, max=len(bnds))
    
    cths = []
    mss = []
    for eachBnd in bnds:
        # add hierarchy for secDrv and priDrv
        bndHm = pm.PyNode(cgmrigging.groupMeObject(str(eachBnd), parent=True, maintainParent=True))
        bndHm.rename(eachBnd.replace('_bnd', '_bnd_hm'))
        priDrv = pm.PyNode(cgmrigging.groupMeObject(str(eachBnd), parent=True, maintainParent=True))
        priDrv.rename(eachBnd.replace('_bnd', '_priDrv_bnd'))
        secDrv = pm.PyNode(cgmrigging.groupMeObject(str(eachBnd), parent=True, maintainParent=True))
        secDrv.rename(eachBnd.replace('_bnd', '_secDrv_bnd'))  
        # reset joint orient
        eachBnd.r.set(0, 0, 0)
        eachBnd.jointOrient.set(0, 0, 0)
        
        cth = addSecondaryCtlToBnd(eachBnd)
        cths.append(cth)
        
        ms = addMotionSystemToBnd(eachBnd)
        mss.append(ms)
        
        pm.progressWindow(e=True, step=1, status='Adding %s...' % eachBnd)
    
    pm.progressWindow(e=True, endProgress=True)  
    
    pm.group(cths, n='face_ctrls_grp')
    pm.group(mss, n='face_motion_grp')


def createMover(pLoc):
    '''
    pLoc - [string]
    '''
    pm.select(cl=True)
    jnt = pm.joint(n=pLoc.replace('_pLoc', '_bnd'))
    
    ctl_radius = pm.PyNode(pLoc).localScale.get()
    jnt.radius.set(ctl_radius[0])
    
    cgmPos.moveParentSnap(jnt.name(), pLoc)

    hm = pm.PyNode(cgmrigging.groupMeObject(str(jnt), parent=True, maintainParent=True))
    hm.rename(jnt.replace('_bnd', '_jnt_hm'))
    grp = pm.PyNode(cgmrigging.groupMeObject(str(jnt), parent=True, maintainParent=True))
    grp.rename(jnt.replace('_bnd', '_grp_hm'))
    priCtl = addPrimaryCtlToBnd(jnt)
    priCtl.t >> jnt.t
    priCtl.r >> jnt.r
    priCtl.s >> jnt.s
    return priCtl, hm

def buildPrimaryControlSystem():
    #===========================================================================
    # Add Primary controls
    #===========================================================================
    pm.progressWindow(title='Build Motion System', progress=0, max=17)
    pm.progressWindow(e=True, step=1, status='Create driver for LT_eyelid_upper_bnd')
    
    allPriCtls = []
    # eyes
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_eyelid_upper_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_bnd'),
                                    nt.Joint(u'LT_eyelid_inner_upper_bnd'),
                                    nt.Joint(u'LT_eyelid_upper_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_upper_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_eyelid_lower_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_eyelid_lower_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_bnd'),
                                    nt.Joint(u'LT_eyelid_inner_lower_bnd'),
                                    nt.Joint(u'LT_eyelid_lower_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_lower_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_eyelid_upper_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_eyelid_upper_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_bnd'),
                                    nt.Joint(u'RT_eyelid_inner_upper_bnd'),
                                    nt.Joint(u'RT_eyelid_upper_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_upper_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_eyelid_lower_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_eyelid_lower_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_bnd'),
                                    nt.Joint(u'RT_eyelid_inner_lower_bnd'),
                                    nt.Joint(u'RT_eyelid_lower_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_lower_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for CT_noseTip_bnd')
    # nose
    priCtl = addPrimaryCtlToBnd(pm.PyNode('CT_noseTip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_noseTip_bnd'), nt.Joint(u'LT_nostril_bnd'), nt.Joint(u'RT_nostril_bnd'), nt.Joint(u'LT_up_crease_bnd'), nt.Joint(u'RT_up_crease_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), nt.Joint(u'RT_in_philtrum_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_mid_brow_bnd')
    # brows
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_mid_brow_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_mid_brow_bnd'), nt.Joint(u'LT_in_brow_bnd'), nt.Joint(u'LT_out_brow_bnd'), nt.Joint(u'LT_in_forehead_bnd'), nt.Joint(u'LT_out_forehead_bnd'), nt.Joint(u'LT_in_low_forehead_bnd'), nt.Joint(u'LT_out_low_forehead_bnd'), nt.Joint('CT_brow_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_mid_brow_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_mid_brow_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_mid_brow_bnd'), nt.Joint(u'RT_in_brow_bnd'), nt.Joint(u'RT_in_forehead_bnd'), nt.Joint(u'RT_out_forehead_bnd'), nt.Joint(u'RT_in_low_forehead_bnd'), nt.Joint(u'RT_out_low_forehead_bnd'), nt.Joint(u'RT_out_brow_bnd'), nt.Joint('CT_brow_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_cheek_bnd')
    # cheeks
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_cheek_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_cheek_bnd'), nt.Joint(u'LT_up_cheek_bnd'), nt.Joint(u'LT_mid_crease_bnd'), nt.Joint(u'LT_up_crease_bnd'), nt.Joint(u'LT_in_cheek_bnd'), nt.Joint(u'LT_squint_bnd'), nt.Joint(u'LT_sneer_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_low_crease_bnd'), nt.Joint(u'LT_low_cheek_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_cheek_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_cheek_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_in_cheek_bnd'), nt.Joint(u'RT_up_crease_bnd'), nt.Joint(u'RT_sneer_bnd'), nt.Joint(u'RT_mid_crease_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'RT_up_cheek_bnd'), nt.Joint(u'RT_cheek_bnd'), nt.Joint(u'RT_low_crease_bnd'), nt.Joint(u'RT_low_cheek_bnd'), nt.Joint(u'RT_squint_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_upper_sneer_lip_bnd')
    # sneers
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_upper_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_upper_pinch_lip_bnd'), nt.Joint(u'LT_upper_sneer_lip_bnd'), nt.Joint(u'LT_upper_side_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_sneer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_lower_sneer_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_lower_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'LT_lower_sneer_lip_bnd'), nt.Joint(u'LT_lower_side_lip_bnd'), nt.Joint(u'LT_lower_pinch_lip_bnd'), nt.Joint(u'LT_mid_chin_bnd'), nt.Joint(u'CT_mid_chin_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_upper_sneer_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_upper_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_upper_pinch_lip_bnd'), nt.Joint(u'RT_upper_sneer_lip_bnd'), nt.Joint(u'RT_upper_side_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'RT_in_philtrum_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'RT_sneer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_lower_sneer_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_lower_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'RT_lower_sneer_lip_bnd'), nt.Joint(u'RT_lower_side_lip_bnd'), nt.Joint(u'RT_lower_pinch_lip_bnd'), nt.Joint(u'RT_mid_chin_bnd'), nt.Joint(u'CT_mid_chin_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_corner_lip_bnd')
    # nwsf
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_corner_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_corner_lip_bnd'), nt.Joint(u'LT_upper_pinch_lip_bnd'), nt.Joint(u'LT_upper_sneer_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'LT_lower_sneer_lip_bnd'), nt.Joint(u'LT_lower_pinch_lip_bnd'), nt.Joint(u'CT_mid_chin_bnd'), nt.Joint(u'LT_mid_chin_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_sneer_bnd'), nt.Joint(u'LT_low_crease_bnd'), nt.Joint(u'LT_mid_crease_bnd'), nt.Joint(u'LT_upper_side_lip_bnd'), nt.Joint(u'LT_lower_side_lip_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_corner_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_corner_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_corner_lip_bnd'), nt.Joint(u'RT_upper_pinch_lip_bnd'), nt.Joint(u'RT_upper_sneer_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'RT_lower_sneer_lip_bnd'), nt.Joint(u'RT_lower_pinch_lip_bnd'), nt.Joint(u'CT_mid_chin_bnd'), nt.Joint(u'RT_mid_chin_bnd'), nt.Joint(u'RT_in_philtrum_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'RT_sneer_bnd'), nt.Joint(u'RT_low_crease_bnd'), nt.Joint(u'RT_mid_crease_bnd'), nt.Joint(u'RT_upper_side_lip_bnd'), nt.Joint(u'RT_lower_side_lip_bnd')])
    allPriCtls.append(priCtl)
    
    
    pm.progressWindow(e=True, step=1, status='Create driver for nose_mover')
    # NOSE_MOVER
    priCtl = addPrimaryCtlToBnd(pm.PyNode('CT_noseMover_bnd'))
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_noseMover_bnd'),
                                    nt.Joint(u'CT_noseTip_bnd'),
                                    nt.Joint(u'LT_nostril_bnd'),
                                    nt.Joint(u'CT_philtrum_bnd'),
                                    nt.Joint(u'LT_philtrum_bnd'),
                                    nt.Joint(u'LT_up_crease_bnd'),
                                    nt.Joint(u'LT_in_philtrum_bnd'),
                                    nt.Joint(u'RT_nostril_bnd'),
                                    nt.Joint(u'RT_philtrum_bnd'),
                                    nt.Joint(u'RT_up_crease_bnd'),
                                    nt.Joint(u'RT_in_philtrum_bnd')])
    
    pm.progressWindow(e=True, step=1, status='Create driver for mouth_mover')
    # MOUTH_MOVER
    priCtl = addPrimaryCtlToBnd(pm.PyNode('CT_mouthMover_bnd'))
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_corner_lip_bnd'),
                                     nt.Joint(u'RT_upper_pinch_lip_bnd'),
                                     nt.Joint(u'RT_upper_sneer_lip_bnd'),
                                     nt.Joint(u'CT_upper_lip_bnd'),
                                     nt.Joint(u'LT_upper_sneer_lip_bnd'),
                                     nt.Joint(u'LT_upper_pinch_lip_bnd'),
                                     nt.Joint(u'LT_corner_lip_bnd'),
                                     nt.Joint(u'LT_lower_pinch_lip_bnd'),
                                     nt.Joint(u'LT_lower_sneer_lip_bnd'),
                                     nt.Joint(u'CT_lower_lip_bnd'),
                                     nt.Joint(u'RT_lower_sneer_lip_bnd'),
                                     nt.Joint(u'RT_lower_pinch_lip_bnd'),
                                     nt.Joint(u'RT_low_crease_bnd'),
                                     nt.Joint(u'RT_sneer_bnd'),
                                     nt.Joint(u'RT_philtrum_bnd'),
                                     nt.Joint(u'RT_in_philtrum_bnd'),
                                     nt.Joint(u'LT_in_philtrum_bnd'),
                                     nt.Joint(u'LT_philtrum_bnd'),
                                     nt.Joint(u'LT_sneer_bnd'),
                                     nt.Joint(u'LT_low_crease_bnd'),
                                     nt.Joint(u'LT_mid_chin_bnd'),
                                     nt.Joint(u'CT_mid_chin_bnd'),
                                     nt.Joint(u'RT_mid_chin_bnd'),
                                     nt.Joint(u'LT_upper_side_lip_bnd'),
                                     nt.Joint(u'LT_lower_side_lip_bnd'),
                                     nt.Joint(u'RT_upper_side_lip_bnd'),
                                     nt.Joint(u'RT_lower_side_lip_bnd')])
    
    pm.progressWindow(e=True, step=1, status='Create driver for eye movers')
    # EYE
    '''
    priCtl, lfEyeHm = createMover('LT_eyeMover_pLoc')
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_bnd'),
                                     nt.Joint(u'LT_eyelid_inner_upper_bnd'),
                                     nt.Joint(u'LT_eyelid_upper_bnd'),
                                     nt.Joint(u'LT_eyelid_outer_upper_bnd'),
                                     nt.Joint(u'LT_eyelid_outer_bnd'),
                                     nt.Joint(u'LT_eyelid_outer_lower_bnd'),
                                     nt.Joint(u'LT_eyelid_lower_bnd'),
                                     nt.Joint(u'LT_eyelid_inner_lower_bnd')])
    
    priCtl, rtEyeHm = createMover('RT_eyeMover_pLoc')
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_bnd'),
                                     nt.Joint(u'RT_eyelid_inner_upper_bnd'),
                                     nt.Joint(u'RT_eyelid_upper_bnd'),
                                     nt.Joint(u'RT_eyelid_outer_upper_bnd'),
                                     nt.Joint(u'RT_eyelid_outer_bnd'),
                                     nt.Joint(u'RT_eyelid_outer_lower_bnd'),
                                     nt.Joint(u'RT_eyelid_lower_bnd'),
                                     nt.Joint(u'RT_eyelid_inner_lower_bnd')])
'''
    pm.progressWindow(e=True, step=1, status='Create driver for CT_jaw_bnd')
    # JAW
    priCtl = addPrimaryCtlToBnd(pm.PyNode('CT_jaw_bnd'))
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), 
                                    nt.Joint(u'LT_upper_sneer_lip_bnd'), nt.Joint(u'LT_upper_pinch_lip_bnd'), 
                                    nt.Joint(u'LT_corner_lip_bnd'), nt.Joint(u'LT_lower_pinch_lip_bnd'), 
                                    nt.Joint(u'LT_lower_sneer_lip_bnd'), nt.Joint(u'RT_lower_sneer_lip_bnd'), 
                                    nt.Joint(u'RT_lower_pinch_lip_bnd'), nt.Joint(u'RT_corner_lip_bnd'), 
                                    nt.Joint(u'RT_upper_pinch_lip_bnd'), nt.Joint(u'RT_upper_sneer_lip_bnd'), 
                                    nt.Joint(u'CT_mid_chin_bnd'), nt.Joint(u'RT_mid_chin_bnd'), nt.Joint(u'LT_mid_chin_bnd'), 
                                    nt.Joint(u'LT_chin_bnd'), nt.Joint(u'CT_chin_bnd'), nt.Joint(u'RT_chin_bnd'), 
                                    nt.Joint(u'LT_sneer_bnd'), nt.Joint(u'LT_mid_crease_bnd'), nt.Joint(u'LT_low_crease_bnd'), 
                                    nt.Joint(u'LT_low_jaw_bnd'), nt.Joint(u'LT_cheek_bnd'), nt.Joint(u'LT_low_cheek_bnd'), 
                                    nt.Joint(u'LT_corner_jaw_bnd'), nt.Joint(u'LT_up_jaw_bnd'), nt.Joint(u'RT_philtrum_bnd'), 
                                    nt.Joint(u'RT_in_philtrum_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), 
                                    nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_out_cheek_bnd'), nt.Joint(u'LT_up_cheek_bnd'), 
                                    nt.Joint(u'RT_sneer_bnd'), nt.Joint(u'RT_mid_crease_bnd'), nt.Joint(u'RT_low_crease_bnd'), 
                                    nt.Joint(u'RT_low_jaw_bnd'), nt.Joint(u'RT_corner_jaw_bnd'), nt.Joint(u'RT_low_cheek_bnd'), 
                                    nt.Joint(u'RT_up_jaw_bnd'), nt.Joint(u'RT_cheek_bnd'), nt.Joint(u'RT_up_cheek_bnd'), 
                                    nt.Joint(u'RT_out_cheek_bnd'), nt.Joint(u'LT_neck_bnd'), nt.Joint(u'RT_neck_bnd'),
                                    nt.Joint(u'CT_neck_bnd'),
                                    nt.Joint(u'LT_upper_side_lip_bnd'),
                                    nt.Joint(u'LT_lower_side_lip_bnd'),
                                    nt.Joint(u'RT_upper_side_lip_bnd'),
                                    nt.Joint(u'RT_lower_side_lip_bnd')])
    
    allPriCtlHms = [ctl.getParent(-1) for ctl in allPriCtls]
    pm.group(allPriCtlHms, n='CT_face_primary_ctls_grp') 
    
    pm.progressWindow(e=True, endProgress=True)  
    
    return allPriCtls


"""
# old method using different "mover jnts"
# new method above uses pLocs for everything inc. movers
def buildPrimaryControlSystem():
    #===========================================================================
    # Add Primary controls
    #===========================================================================
    pm.progressWindow(title='Build Motion System', progress=0, max=17)
    pm.progressWindow(e=True, step=1, status='Create driver for LT_eyelid_upper_bnd')
    
    allPriCtls = []
    # eyes
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_eyelid_upper_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_bnd'),
                                    nt.Joint(u'LT_eyelid_inner_upper_bnd'),
                                    nt.Joint(u'LT_eyelid_upper_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_upper_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_eyelid_lower_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_eyelid_lower_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_bnd'),
                                    nt.Joint(u'LT_eyelid_inner_lower_bnd'),
                                    nt.Joint(u'LT_eyelid_lower_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_lower_bnd'),
                                    nt.Joint(u'LT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_eyelid_upper_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_eyelid_upper_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_bnd'),
                                    nt.Joint(u'RT_eyelid_inner_upper_bnd'),
                                    nt.Joint(u'RT_eyelid_upper_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_upper_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_eyelid_lower_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_eyelid_lower_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_bnd'),
                                    nt.Joint(u'RT_eyelid_inner_lower_bnd'),
                                    nt.Joint(u'RT_eyelid_lower_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_lower_bnd'),
                                    nt.Joint(u'RT_eyelid_outer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for CT_noseTip_bnd')
    # nose
    priCtl = addPrimaryCtlToBnd(pm.PyNode('CT_noseTip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_noseTip_bnd'), nt.Joint(u'LT_nostril_bnd'), nt.Joint(u'RT_nostril_bnd'), nt.Joint(u'LT_up_crease_bnd'), nt.Joint(u'RT_up_crease_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), nt.Joint(u'RT_in_philtrum_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_mid_brow_bnd')
    # brows
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_mid_brow_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_mid_brow_bnd'), nt.Joint(u'LT_in_brow_bnd'), nt.Joint(u'LT_out_brow_bnd'), nt.Joint(u'LT_in_forehead_bnd'), nt.Joint(u'LT_out_forehead_bnd'), nt.Joint(u'LT_in_low_forehead_bnd'), nt.Joint(u'LT_out_low_forehead_bnd'), nt.Joint('CT_brow_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_mid_brow_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_mid_brow_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_mid_brow_bnd'), nt.Joint(u'RT_in_brow_bnd'), nt.Joint(u'RT_in_forehead_bnd'), nt.Joint(u'RT_out_forehead_bnd'), nt.Joint(u'RT_in_low_forehead_bnd'), nt.Joint(u'RT_out_low_forehead_bnd'), nt.Joint(u'RT_out_brow_bnd'), nt.Joint('CT_brow_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_cheek_bnd')
    # cheeks
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_cheek_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_cheek_bnd'), nt.Joint(u'LT_up_cheek_bnd'), nt.Joint(u'LT_mid_crease_bnd'), nt.Joint(u'LT_up_crease_bnd'), nt.Joint(u'LT_in_cheek_bnd'), nt.Joint(u'LT_squint_bnd'), nt.Joint(u'LT_sneer_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_low_crease_bnd'), nt.Joint(u'LT_low_cheek_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_cheek_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_cheek_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_in_cheek_bnd'), nt.Joint(u'RT_up_crease_bnd'), nt.Joint(u'RT_sneer_bnd'), nt.Joint(u'RT_mid_crease_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'RT_up_cheek_bnd'), nt.Joint(u'RT_cheek_bnd'), nt.Joint(u'RT_low_crease_bnd'), nt.Joint(u'RT_low_cheek_bnd'), nt.Joint(u'RT_squint_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_upper_sneer_lip_bnd')
    # sneers
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_upper_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_upper_pinch_lip_bnd'), nt.Joint(u'LT_upper_sneer_lip_bnd'), nt.Joint(u'LT_upper_side_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_sneer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_lower_sneer_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_lower_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'LT_lower_sneer_lip_bnd'), nt.Joint(u'LT_lower_side_lip_bnd'), nt.Joint(u'LT_lower_pinch_lip_bnd'), nt.Joint(u'LT_mid_chin_bnd'), nt.Joint(u'CT_mid_chin_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_upper_sneer_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_upper_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_upper_pinch_lip_bnd'), nt.Joint(u'RT_upper_sneer_lip_bnd'), nt.Joint(u'RT_upper_side_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'RT_in_philtrum_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'RT_sneer_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_lower_sneer_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_lower_sneer_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'RT_lower_sneer_lip_bnd'), nt.Joint(u'RT_lower_side_lip_bnd'), nt.Joint(u'RT_lower_pinch_lip_bnd'), nt.Joint(u'RT_mid_chin_bnd'), nt.Joint(u'CT_mid_chin_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_corner_lip_bnd')
    # nwsf
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_corner_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_corner_lip_bnd'), nt.Joint(u'LT_upper_pinch_lip_bnd'), nt.Joint(u'LT_upper_sneer_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'LT_lower_sneer_lip_bnd'), nt.Joint(u'LT_lower_pinch_lip_bnd'), nt.Joint(u'CT_mid_chin_bnd'), nt.Joint(u'LT_mid_chin_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_sneer_bnd'), nt.Joint(u'LT_low_crease_bnd'), nt.Joint(u'LT_mid_crease_bnd'), nt.Joint(u'LT_upper_side_lip_bnd'), nt.Joint(u'LT_lower_side_lip_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_corner_lip_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_corner_lip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_corner_lip_bnd'), nt.Joint(u'RT_upper_pinch_lip_bnd'), nt.Joint(u'RT_upper_sneer_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'RT_lower_sneer_lip_bnd'), nt.Joint(u'RT_lower_pinch_lip_bnd'), nt.Joint(u'CT_mid_chin_bnd'), nt.Joint(u'RT_mid_chin_bnd'), nt.Joint(u'RT_in_philtrum_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'RT_sneer_bnd'), nt.Joint(u'RT_low_crease_bnd'), nt.Joint(u'RT_mid_crease_bnd'), nt.Joint(u'RT_upper_side_lip_bnd'), nt.Joint(u'RT_lower_side_lip_bnd')])
    allPriCtls.append(priCtl)
    
    
    pm.progressWindow(e=True, step=1, status='Create driver for nose_mover')
    # NOSE_MOVER
    priCtl, noseHm = createMover('CT_noseMover_pLoc')
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_nostril_bnd'),
                                     nt.Joint(u'CT_noseTip_bnd'),
                                     nt.Joint(u'LT_nostril_bnd')])
    
    pm.progressWindow(e=True, step=1, status='Create driver for mouth_mover')
    # MOUTH_MOVER
    priCtl, mouthHm = createMover('CT_mouthMover_pLoc')
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_corner_lip_bnd'),
                                     nt.Joint(u'RT_upper_pinch_lip_bnd'),
                                     nt.Joint(u'RT_upper_sneer_lip_bnd'),
                                     nt.Joint(u'CT_upper_lip_bnd'),
                                     nt.Joint(u'LT_upper_sneer_lip_bnd'),
                                     nt.Joint(u'LT_upper_pinch_lip_bnd'),
                                     nt.Joint(u'LT_corner_lip_bnd'),
                                     nt.Joint(u'LT_lower_pinch_lip_bnd'),
                                     nt.Joint(u'LT_lower_sneer_lip_bnd'),
                                     nt.Joint(u'CT_lower_lip_bnd'),
                                     nt.Joint(u'RT_lower_sneer_lip_bnd'),
                                     nt.Joint(u'RT_lower_pinch_lip_bnd'),
                                     nt.Joint(u'RT_low_crease_bnd'),
                                     nt.Joint(u'RT_sneer_bnd'),
                                     nt.Joint(u'RT_philtrum_bnd'),
                                     nt.Joint(u'RT_in_philtrum_bnd'),
                                     nt.Joint(u'LT_in_philtrum_bnd'),
                                     nt.Joint(u'LT_philtrum_bnd'),
                                     nt.Joint(u'LT_sneer_bnd'),
                                     nt.Joint(u'LT_low_crease_bnd'),
                                     nt.Joint(u'LT_mid_chin_bnd'),
                                     nt.Joint(u'CT_mid_chin_bnd'),
                                     nt.Joint(u'RT_mid_chin_bnd'),
                                     nt.Joint(u'LT_upper_side_lip_bnd'),
                                     nt.Joint(u'LT_lower_side_lip_bnd'),
                                     nt.Joint(u'RT_upper_side_lip_bnd'),
                                     nt.Joint(u'RT_lower_side_lip_bnd')])
    
    pm.progressWindow(e=True, step=1, status='Create driver for eye movers')
    # EYE
    priCtl, lfEyeHm = createMover('LT_eyeMover_pLoc')
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_bnd'),
                                     nt.Joint(u'LT_eyelid_inner_upper_bnd'),
                                     nt.Joint(u'LT_eyelid_upper_bnd'),
                                     nt.Joint(u'LT_eyelid_outer_upper_bnd'),
                                     nt.Joint(u'LT_eyelid_outer_bnd'),
                                     nt.Joint(u'LT_eyelid_outer_lower_bnd'),
                                     nt.Joint(u'LT_eyelid_lower_bnd'),
                                     nt.Joint(u'LT_eyelid_inner_lower_bnd')])
    
    priCtl, rtEyeHm = createMover('RT_eyeMover_pLoc')
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_bnd'),
                                     nt.Joint(u'RT_eyelid_inner_upper_bnd'),
                                     nt.Joint(u'RT_eyelid_upper_bnd'),
                                     nt.Joint(u'RT_eyelid_outer_upper_bnd'),
                                     nt.Joint(u'RT_eyelid_outer_bnd'),
                                     nt.Joint(u'RT_eyelid_outer_lower_bnd'),
                                     nt.Joint(u'RT_eyelid_lower_bnd'),
                                     nt.Joint(u'RT_eyelid_inner_lower_bnd')])

    pm.progressWindow(e=True, step=1, status='Create driver for CT_jaw_bnd')
    # JAW
    priCtl, jawHm = createMover('CT_jaw_pLoc')
    allPriCtls.append(priCtl)
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_lower_lip_bnd'), nt.Joint(u'CT_upper_lip_bnd'), 
                                    nt.Joint(u'LT_upper_sneer_lip_bnd'), nt.Joint(u'LT_upper_pinch_lip_bnd'), 
                                    nt.Joint(u'LT_corner_lip_bnd'), nt.Joint(u'LT_lower_pinch_lip_bnd'), 
                                    nt.Joint(u'LT_lower_sneer_lip_bnd'), nt.Joint(u'RT_lower_sneer_lip_bnd'), 
                                    nt.Joint(u'RT_lower_pinch_lip_bnd'), nt.Joint(u'RT_corner_lip_bnd'), 
                                    nt.Joint(u'RT_upper_pinch_lip_bnd'), nt.Joint(u'RT_upper_sneer_lip_bnd'), 
                                    nt.Joint(u'CT_mid_chin_bnd'), nt.Joint(u'RT_mid_chin_bnd'), nt.Joint(u'LT_mid_chin_bnd'), 
                                    nt.Joint(u'LT_chin_bnd'), nt.Joint(u'CT_chin_bnd'), nt.Joint(u'RT_chin_bnd'), 
                                    nt.Joint(u'LT_sneer_bnd'), nt.Joint(u'LT_mid_crease_bnd'), nt.Joint(u'LT_low_crease_bnd'), 
                                    nt.Joint(u'LT_low_jaw_bnd'), nt.Joint(u'LT_cheek_bnd'), nt.Joint(u'LT_low_cheek_bnd'), 
                                    nt.Joint(u'LT_corner_jaw_bnd'), nt.Joint(u'LT_up_jaw_bnd'), nt.Joint(u'RT_philtrum_bnd'), 
                                    nt.Joint(u'RT_in_philtrum_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), 
                                    nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'LT_out_cheek_bnd'), nt.Joint(u'LT_up_cheek_bnd'), 
                                    nt.Joint(u'RT_sneer_bnd'), nt.Joint(u'RT_mid_crease_bnd'), nt.Joint(u'RT_low_crease_bnd'), 
                                    nt.Joint(u'RT_low_jaw_bnd'), nt.Joint(u'RT_corner_jaw_bnd'), nt.Joint(u'RT_low_cheek_bnd'), 
                                    nt.Joint(u'RT_up_jaw_bnd'), nt.Joint(u'RT_cheek_bnd'), nt.Joint(u'RT_up_cheek_bnd'), 
                                    nt.Joint(u'RT_out_cheek_bnd'), nt.Joint(u'LT_neck_bnd'), nt.Joint(u'RT_neck_bnd'),
                                    nt.Joint(u'CT_neck_bnd'),
                                    nt.Joint(u'LT_upper_side_lip_bnd'),
                                    nt.Joint(u'LT_lower_side_lip_bnd'),
                                    nt.Joint(u'RT_upper_side_lip_bnd'),
                                    nt.Joint(u'RT_lower_side_lip_bnd')])
    
    allPriCtlHms = [ctl.getParent(-1) for ctl in allPriCtls]
    pm.group(allPriCtlHms, n='CT_face_primary_ctls_grp') 
    
    pm.group(jawHm, mouthHm, noseHm, lfEyeHm, rtEyeHm, n='CT_jnts_grp')
    
    pm.progressWindow(e=True, endProgress=True)  
    
    return allPriCtls
"""
def cleanFaceRig():
    '''
    '''
    #===========================================================================
    # color
    #===========================================================================
    allCtls = pm.ls('*_ctrl', type='transform')
    for eachCtl in allCtls:
        eachCtl.overrideEnabled.set(True)
        if 'LT_' in eachCtl.name():
            if 'pri_' in eachCtl.name():
                eachCtl.overrideColor.set(6)
            else:
                eachCtl.overrideColor.set(15)
        elif 'CT_' in eachCtl.name():
            if 'pri_' in eachCtl.name():
                eachCtl.overrideColor.set(22)
            else:
                eachCtl.overrideColor.set(25)
        elif 'RT_' in eachCtl.name():
            if 'pri_' in eachCtl.name():
                eachCtl.overrideColor.set(13)
            else:
                eachCtl.overrideColor.set(31)
    #===========================================================================
    # shapes
    #===========================================================================
    # TODO: calculate scale properly
    # right now scale is hard-coded for Mathilda, at around 0.16
    # for is placementGrp.locScale = 1.0,
    # then scale her needs to be 6.25, etc.
    locScale = pm.PyNode('CT_placement_grp.locScale').get()
    ctlScale = 6.25 * locScale
    
    # lips
    replaceControlCurve(pm.PyNode('LT_lowerSneer_lip_pri_ctrl'), 'downArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_lowerSneer_lip_pri_ctrl'), 'downArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('LT_upperSneer_lip_pri_ctrl'), 'upArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_upperSneer_lip_pri_ctrl'), 'upArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('CT_lower_lip_pri_ctrl'), 'downArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('CT_upper_lip_pri_ctrl'), 'upArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('LT_corner_lip_pri_ctrl'), 'rightArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_corner_lip_pri_ctrl'), 'leftArrow', scale=ctlScale)
    # eye
    replaceControlCurve(pm.PyNode('LT_upper_eyelid_pri_ctrl'), 'upArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_upper_eyelid_pri_ctrl'), 'upArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('LT_lower_eyelid_pri_ctrl'), 'downArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_lower_eyelid_pri_ctrl'), 'downArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('LT_inner_eyelid_pri_ctrl'), 'leftArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('LT_outer_eyelid_pri_ctrl'), 'rightArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_outer_eyelid_pri_ctrl'), 'leftArrow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_inner_eyelid_pri_ctrl'), 'rightArrow', scale=ctlScale)
    # jaw
    replaceControlCurve(pm.PyNode('CT__jaw_pri_ctrl'), 'jaw', scale=ctlScale)
    replaceControlCurve(pm.PyNode('CT__mouthMover_pri_ctrl'), 'mouth', scale=ctlScale)
    # face
    faceCtl = pm.group(pm.PyNode('face_ctrls_grp'), pm.PyNode('CT_face_primary_ctls_grp'), n='CT_face_ctrl')
    replaceControlCurve(pm.PyNode(faceCtl), 'head', scale=ctlScale)
    faceCtl.getShape().overrideEnabled.set(True)
    faceCtl.getShape().overrideColor.set(21)
    # brow
    replaceControlCurve(pm.PyNode('LT_mid_brow_pri_ctrl'), 'brow', scale=ctlScale)
    replaceControlCurve(pm.PyNode('RT_mid_brow_pri_ctrl'), 'brow', scale=ctlScale)
    # eye
    upLidPos = pm.PyNode('LT_upper_eyelid_pri_ctrl').getTranslation(space='world')
    lowLidPos = pm.PyNode('LT_lower_eyelid_pri_ctrl').getTranslation(space='world')
    midPos = (upLidPos + lowLidPos) / 2
    eyeCtl = pm.group(em=True, n='LT_eye_ctl')
    eyeCtg = pm.group(eyeCtl, n='LT_eye_ctg')
    eyeCth = pm.group(eyeCtg, n='LT_eye_hm')
    eyeCth.setTranslation(midPos, space='world')
    replaceControlCurve(eyeCtl, 'eye', scale=10*ctlScale)
    eyeCtl.overrideEnabled.set(True)
    eyeCtl.overrideColor.set(6)
    faceCtl | eyeCth
    upLidPos = pm.PyNode('RT_upper_eyelid_pri_ctrl').getTranslation(space='world')
    lowLidPos = pm.PyNode('RT_lower_eyelid_pri_ctrl').getTranslation(space='world')
    midPos = (upLidPos + lowLidPos) / 2
    eyeCtl = pm.group(em=True, n='RT_eye_ctl')
    eyeCtg = pm.group(eyeCtl, n='RT_eye_ctg')
    eyeCth = pm.group(eyeCtg, n='RT_eye_hm')
    eyeCth.setTranslation(midPos, space='world')
    replaceControlCurve(eyeCtl, 'eye', scale=10*ctlScale)
    eyeCtl.overrideEnabled.set(True)
    eyeCtl.overrideColor.set(13)
    faceCtl | eyeCth
    
    # visibilities
    moverCtls = [u'CT__jaw_pri_ctrl',
                u'CT__mouthMover_pri_ctrl',
                u'LT__eyeMover_pri_ctrl',
                u'RT__eyeMover_pri_ctrl',
                u'CT__noseMover_pri_ctrl',
                u'LT__browMover_pri_ctrl',
                u'RT__browMover_pri_ctrl']
    rt.connectVisibilityToggle(moverCtls, faceCtl.name(), 'moverControlsVis', True)
    priCtls = [u'RT_out_browB_pri_ctrl',
            u'RT_mid_browA_pri_ctrl',
            u'RT_in_browA_pri_ctrl',
            u'LT_in_browA_pri_ctrl',
            u'LT_mid_browA_pri_ctrl',
            u'LT_out_browB_pri_ctrl',
            u'LT_upper_eyelid_pri_ctrl',
            u'RT_upper_eyelid_pri_ctrl',
            u'RT_lower_eyelid_pri_ctrl',
            u'CT__noseTip_pri_ctrl',
            u'LT_lower_eyelid_pri_ctrl',
            u'LT__squint_pri_ctrl',
            u'RT__squint_pri_ctrl',
            u'LT_mid_cheek_pri_ctrl',
            u'RT_mid_cheek_pri_ctrl',
            u'CT_upper_lip_pri_ctrl',
            u'CT_lower_lip_pri_ctrl',
            u'LT_upperSneer_lip_pri_ctrl',
            u'LT_lowerSneer_lip_pri_ctrl',
            u'RT_upperSneer_lip_pri_ctrl',
            u'RT_lowerSneer_lip_pri_ctrl',
            u'RT_corner_lip_pri_ctrl',
            u'LT_corner_lip_pri_ctrl',
            u'RT__browCrease_pri_ctrl',
            u'LT__browCrease_pri_ctrl']
    priCtls.append('LT_eye_ctl')
    priCtls.append('RT_eye_ctl')
    rt.connectVisibilityToggle(priCtls, faceCtl.name(), 'primaryControlsVis', True)
    mouthTweakers = [u'CT__mouthMover_ctrl',
                    u'LT_lowerSide_lip_ctrl',
                    u'CT_upper_lip_ctrl',
                    u'LT_lowerPinch_lip_ctrl',
                    u'LT_upperPinch_lip_ctrl',
                    u'CT_lower_lip_ctrl',
                    u'LT_upperSide_lip_ctrl',
                    u'LT_corner_lip_ctrl',
                    u'LT_upperSneer_lip_ctrl',
                    u'LT_lowerSneer_lip_ctrl',
                    u'RT_lowerSide_lip_ctrl',
                    u'RT_lowerPinch_lip_ctrl',
                    u'RT_upperPinch_lip_ctrl',
                    u'RT_upperSide_lip_ctrl',
                    u'RT_corner_lip_ctrl',
                    u'RT_upperSneer_lip_ctrl',
                    u'RT_lowerSneer_lip_ctrl',
                    u'LT_lowerCorner_lip_ctrl',
                    u'LT_upperCorner_lip_ctrl',
                    u'RT_lowerCorner_lip_ctrl',
                    u'RT_upperCorner_lip_ctrl']
    rt.connectVisibilityToggle(mouthTweakers, faceCtl.name(), 'mouthTweakersVis', True)
    browTweakers = [u'CT__brow_ctrl',
                    u'LT__browCrease_ctrl',
                    u'RT__browCrease_ctrl',
                    u'LT_in_browA_ctrl',
                    u'LT_in_browB_ctrl',
                    u'LT_mid_browA_ctrl',
                    u'LT_mid_browB_ctrl',
                    u'LT_out_browA_ctrl',
                    u'RT_in_browA_ctrl',
                    u'RT_in_browB_ctrl',
                    u'RT_mid_browA_ctrl',
                    u'RT_mid_browB_ctrl',
                    u'RT_out_browA_ctrl',
                    u'LT_out_browB_ctrl',
                    u'RT_out_browB_ctrl',
                    u'LT_in_browC_ctrl',
                    u'RT_in_browC_ctrl']
    rt.connectVisibilityToggle(browTweakers, faceCtl.name(), 'browTweakersVis', True)
    eyelidTweakers = [u'LT_inner_eyelid_ctrl',
                    u'LT_innerUpper_eyelid_ctrl',
                    u'LT_upper_eyelid_ctrl',
                    u'LT_outerUpper_eyelid_ctrl',
                    u'LT_outer_eyelid_ctrl',
                    u'LT_outerLower_eyelid_ctrl',
                    u'LT_lower_eyelid_ctrl',
                    u'LT_innerLower_eyelid_ctrl',
                    u'RT_inner_eyelid_ctrl',
                    u'RT_innerUpper_eyelid_ctrl',
                    u'RT_upper_eyelid_ctrl',
                    u'RT_outerUpper_eyelid_ctrl',
                    u'RT_outer_eyelid_ctrl',
                    u'RT_outerLower_eyelid_ctrl',
                    u'RT_lower_eyelid_ctrl',
                    u'RT_innerLower_eyelid_ctrl']
    rt.connectVisibilityToggle(eyelidTweakers, faceCtl.name(), 'eyelidTweakersVis', True)
    eyeSocketTweakers = [u'LT_in_cheek_ctrl',
                        u'LT_in_eyeSocket_ctrl',
                        u'LT_inCorner_eyeSocket_ctrl',
                        u'LT_up_cheek_ctrl',
                        u'LT_out_cheek_ctrl',
                        u'LT_outCorner_eyeSocket_ctrl',
                        u'LT_out_eyeSocket_ctrl',
                        u'LT_mid_eyeSocket_ctrl',
                        u'RT_mid_eyeSocket_ctrl',
                        u'RT_in_eyeSocket_ctrl',
                        u'RT_inCorner_eyeSocket_ctrl',
                        u'RT_in_cheek_ctrl',
                        u'RT_up_cheek_ctrl',
                        u'RT_out_cheek_ctrl',
                        u'RT_outCorner_eyeSocket_ctrl',
                        u'RT_out_eyeSocket_ctrl']
    rt.connectVisibilityToggle(eyeSocketTweakers, faceCtl.name(), 'eyeSocketTweakersVis', True)
    noseTweakers = [u'CT__noseTip_ctrl',
                    u'LT__nostril_ctrl',
                    u'RT__nostril_ctrl']
    rt.connectVisibilityToggle(noseTweakers, faceCtl.name(), 'noseTweakersVis', True)
    extraTweakers = [u'CT__chin_ctrl',
                    u'CT__neck_ctrl',
                    u'LT_corner_jaw_ctrl',
                    u'LT_low_jaw_ctrl',
                    u'LT__chin_ctrl',
                    u'LT__neck_ctrl',
                    u'CT_mid_chin_ctrl',
                    u'LT__philtrum_ctrl',
                    u'LT_up_crease_ctrl',
                    u'LT_in_philtrum_ctrl',
                    u'LT__sneer_ctrl',
                    u'RT__philtrum_ctrl',
                    u'RT_up_crease_ctrl',
                    u'RT_in_philtrum_ctrl',
                    u'RT__sneer_ctrl',
                    u'LT_mid_chin_ctrl',
                    u'LT_low_crease_ctrl',
                    u'LT_mid_cheek_ctrl',
                    u'LT__squint_ctrl',
                    u'LT_up_jaw_ctrl',
                    u'LT_low_cheek_ctrl',
                    u'LT_out_forehead_ctrl',
                    u'LT__temple_ctrl',
                    u'LT_outLow_forehead_ctrl',
                    u'LT_in_forehead_ctrl',
                    u'LT_inLow_forehead_ctrl',
                    u'RT_in_forehead_ctrl',
                    u'RT_out_forehead_ctrl',
                    u'RT__temple_ctrl',
                    u'RT__squint_ctrl',
                    u'RT_low_crease_ctrl',
                    u'RT_up_jaw_ctrl',
                    u'RT_corner_jaw_ctrl',
                    u'RT_low_jaw_ctrl',
                    u'RT__chin_ctrl',
                    u'RT__neck_ctrl',
                    u'RT_inLow_forehead_ctrl',
                    u'RT_outLow_forehead_ctrl',
                    u'RT_low_cheek_ctrl',
                    u'RT_mid_cheek_ctrl',
                    u'RT_mid_chin_ctrl',
                    u'LT__browMover_ctrl',
                    u'RT__browMover_ctrl']
    rt.connectVisibilityToggle(extraTweakers, faceCtl.name(), 'extraTweakersVis', True)
    uselessCtls = [u'CT__noseMover_ctrl',
                    u'LT__eyeMover_ctrl',
                    u'RT__eyeMover_ctrl',
                    u'CT__mouthMover_ctrl',
                    u'CT__jaw_ctrl',
                    'CT__base_ctrl']
    rt.connectVisibilityToggle(uselessCtls, faceCtl.name(), 'uselessControlsVis', False)
    rt.connectVisibilityToggle(['CT_bnd_grp', 'CT_placement_grp'], faceCtl.name(), 'jointsVis', False)
    """
    # lock geometry
    geoGrp = pm.PyNode('CT_geo_grp')
    geoGrp.overrideEnabled.set(True)
    geoGrp.overrideDisplayType.set(2)"""
    
    
def createControlShape(shape=''):
    createdCurves = []
    if shape == 'eye':
        createdCurves.append(mc.curve(d=2, p=[[-0.048, -1.7763568394002505e-15, 0.04], [-0.024, -0.024000000000001777, 0.04], [0.024, -0.024000000000001777, 0.04], [0.048, -1.7763568394002505e-15, 0.04]], k=(0.0, 0.0, 1.0, 2.0, 2.0)))
        createdCurves.append(mc.curve(d=2, p=[[-0.048, -1.7763568394002505e-15, 0.04], [-0.024, 0.023999999999998224, 0.04], [0.024, 0.023999999999998224, 0.04], [0.048, -1.7763568394002505e-15, 0.04]], k=(0.0, 0.0, 1.0, 2.0, 2.0)))
    print createdCurves
    newCurve = curves.combineCurves(createdCurves)
    print newCurve
    return newCurve
    


def replaceControlCurve(ctl, shape='', scale=1.0):
    '''
    '''
    curvesDict = {'rightArrow': lambda: mc.curve( d = 1,p = [[0.0, 0.4, 0.4], [0.0, -0.4, 0.4], [0.4, 0.0, 0.4], [0.0, 0.4, 0.4]],k = (0.0, 1.0, 2.0, 3.0)),
                  'upArrow': lambda: mc.curve( d = 1,p = [[0.4, 0.0, 0.4], [-0.4, 0.0, 0.4], [0.0, 0.4, 0.4], [0.4, 0.0, 0.4]],k = (0.0, 1.0, 2.0, 3.0)),
                  'leftArrow': lambda: mc.curve( d = 1,p = [[0.0, 0.4, 0.4], [0.0, -0.4, 0.4], [-0.4, 0.0, 0.4], [0.0, 0.4, 0.4]],k = (0.0, 1.0, 2.0, 3.0)),
                  'downArrow': lambda: mc.curve( d = 1,p = [[-0.4, 0.0, 0.4], [0.4, 0.0, 0.4], [0.0, -0.4, 0.4], [-0.4, 0.0, 0.4]],k = (0.0, 1.0, 2.0, 3.0)),
                  'brow': lambda: mc.curve( d = 3,p = [[2.868962484439208e-05, 0.3479496286487829, 0.21115284117082092], [-0.2700001800434342, 0.3479496286487829, 0.21115284117082092], [-0.9210889131801816, 0.29182368907698664, 0.10401523499573474], [-1.1745416188051316, 5.430983809615069e-05, -0.008538112900223611], [-0.9260265993953001, -0.2923694497588261, 0.10401523499573474], [-0.010228242729188083, -0.38880745954609164, 0.21115284117082092], [0.9089487328547375, -0.2974686972729315, 0.10401523499573474], [1.1745096115687037, -0.006698680048650013, -0.008538112900223611], [0.9360298063601409, 0.286662906886851, 0.10401523499573474], [0.28853735433138006, 0.34634395982716215, 0.21115284117082092], [0.018549611367866887, 0.34789638519644495, 0.21115284117082092]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 8.0, 8.0)),
                  'mouth': lambda: mc.curve( d = 3,p = [[0.4205541586, -0.020428947890621885, 0.1459612376730961], [0.4205542707, -0.020428857890621543, 0.14596118767309552], [0.420554383, -0.020428767890621202, 0.14596113767309582], [0.4205544952, -0.02042866789062714, 0.14596108767309612], [0.3760259766, 0.015880562109373386, 0.16589323767309594], [0.3307788671, 0.05277566210936868, 0.18042650767309532], [0.2842112107, 0.09074756210937096, 0.1897940176730959], [0.2842112107, 0.07475416210937169, 0.19125550767309552], [0.2842112107, 0.05876066210937836, 0.19271700767309596], [0.2842112107, 0.04276726210937909, 0.19417850767309552], [0.2115939621, 0.04276726210937909, 0.2155809076730959], [0.1387878082, 0.04276726210937909, 0.22902430767309578], [0.06318290227, 0.04276726210937909, 0.23403890767309576], [0.0631841571, 0.11837206210937268, 0.22902450767309546], [0.06318290227, 0.19117826210937494, 0.21558130767309613], [0.06318290227, 0.2637955621093795, 0.19417910767309543], [0.07917618084, 0.2637955621093795, 0.19271760767309587], [0.09516945927, 0.2637955621093795, 0.19125610767309542], [0.1111627377, 0.2637955621093795, 0.18979457767309604], [0.0731908164, 0.3103631621093683, 0.1804272876730959], [0.03629567301, 0.35561026210937996, 0.16589423767309608], [-1.353306672e-05, 0.4001387621093784, 0.14596230767309581], [-0.03632302238, 0.355610362109374, 0.16589438767309606], [-0.07321780799, 0.3103632621093766, 0.18042765767309543], [-0.1111898038, 0.2637955621093795, 0.18979514767309613], [-0.09519817235, 0.2637955621093795, 0.19125650767309565], [-0.07920654098, 0.2637955621093795, 0.19271780767309554], [-0.06321490962, 0.2637955621093795, 0.19417910767309543], [-0.06321490962, 0.19117826210937494, 0.21558130767309613], [-0.06321616445, 0.11837206210937268, 0.22902450767309546], [-0.06321490962, 0.04276726210937909, 0.23403890767309576], [-0.1388198157, 0.04276726210937909, 0.22902430767309578], [-0.2116259695, 0.04276726210937909, 0.2155809076730959], [-0.2842432182, 0.04276726210937909, 0.19417850767309552], [-0.2842432182, 0.05876066210937836, 0.19271700767309596], [-0.2842432182, 0.07475416210937169, 0.19125550767309552], [-0.2842432182, 0.09074756210937096, 0.1897940176730959], [-0.3308108746, 0.05277566210936868, 0.18042650767309532], [-0.3760579841, 0.015880562109373386, 0.16589323767309594], [-0.4205865025, -0.02042866789062714, 0.14596108767309612], [-0.3760579858, -0.05673786789061808, 0.16589325767309582], [-0.3308108755, -0.09363300789063089, 0.18042654767309596], [-0.2842432182, -0.13160494789062227, 0.18979408767309547], [-0.2842432182, -0.11561349789062092, 0.19125540767309612], [-0.2842432182, -0.09962204789061957, 0.1927168076730954], [-0.2842432182, -0.08363059789061822, 0.1941781076730953], [-0.2116259555, -0.08363059789061822, 0.21558050767309567], [-0.1388198121, -0.083631857890623, 0.22902390767309555], [-0.06321490962, -0.08363059789061822, 0.23403850767309553], [-0.06321490962, -0.15923356789062382, 0.22902390767309555], [-0.06321490962, -0.23203795789062553, 0.21558080767309562], [-0.06321490962, -0.30465341789061995, 0.19417910767309543], [-0.07920654098, -0.30465341789061995, 0.19271780767309554], [-0.09519817235, -0.30465341789061995, 0.19125650767309565], [-0.1111898038, -0.30465341789061995, 0.18979514767309613], [-0.07321780799, -0.35122114789062664, 0.18042765767309543], [-0.03632302238, -0.39646827789061945, 0.16589438767309606], [-1.353306672e-05, -0.44099669789062546, 0.14596230767309581], [0.03629567301, -0.39646816789063166, 0.16589423767309608], [0.0731908164, -0.3512210578906263, 0.1804272876730959], [0.1111627377, -0.30465341789061995, 0.18979457767309604], [0.09516945927, -0.30465341789061995, 0.19125610767309542], [0.07917618084, -0.30465341789061995, 0.19271760767309587], [0.06318290227, -0.30465341789061995, 0.19417910767309543], [0.06318290227, -0.23203795789062553, 0.21558080767309562], [0.06318290227, -0.15923356789062382, 0.22902390767309555], [0.06318290227, -0.08363059789061822, 0.23403850767309553], [0.1387878048, -0.083631857890623, 0.22902390767309555], [0.2115939481, -0.08363059789061822, 0.21558050767309567], [0.2842112107, -0.08363059789061822, 0.1941781076730953], [0.2842112107, -0.09962204789061957, 0.1927168076730954], [0.2842112107, -0.11561349789062092, 0.19125540767309612], [0.2842112107, -0.13160494789062227, 0.18979408767309547], [0.3307787499, -0.09363310789062496, 0.18042657767309578], [0.3760257482, -0.05673804789061876, 0.1658933276730954], [0.4205541586, -0.020428947890621885, 0.1459612376730961]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 6.0, 6.0, 6.0, 9.0, 9.0, 9.0, 12.0, 12.0, 12.0, 15.0, 15.0, 15.0, 18.0, 18.0, 18.0, 21.0, 21.0, 21.0, 24.0, 24.0, 24.0, 27.0, 27.0, 27.0, 30.0, 30.0, 30.0, 31.0, 32.0, 33.0, 36.0, 36.0, 36.0, 39.0, 39.0, 39.0, 42.0, 42.0, 42.0, 43.0, 44.0, 45.0, 48.0, 48.0, 48.0, 51.0, 51.0, 51.0, 54.0, 54.0, 54.0, 57.0, 57.0, 57.0, 60.0, 60.0, 60.0, 63.0, 63.0, 63.0, 66.0, 66.0, 66.0, 69.0, 69.0, 69.0, 72.0, 72.0, 72.0, 73.0, 73.0, 73.0)),
                  'head': lambda: mc.curve( d = 2,p = [[0.0, 114.49734953690091, 6.612797333031283], [1.6674884686572777, 114.53004338093189, 6.441343367109859], [3.580017798149398, 114.33570847034616, 5.896028156482873], [5.516548727119685, 113.83613232318154, 4.512163867116608], [6.809507968084384, 112.84804877429715, 3.0678804442605156], [7.615868049855443, 111.24591975093242, 1.1410812808577324], [7.816732059690539, 109.51341676653195, 0.04653833182295575], [7.984960288515327, 107.50658792395498, -0.20212083237656486], [7.786341006592426, 105.46078729789686, -0.10274985828909157], [7.4004546207566335, 103.3630468049505, -0.05069168081345499], [6.798747235979318, 101.28780295938657, 0.07512267782692295], [6.061323333580306, 99.74853060016095, 0.30127010459679315], [5.514498044178216, 98.84369530621169, 0.6380333405319378], [4.2395346481185285, 97.28662911956711, 2.2338041923498766], [3.005126348206007, 96.5939329821601, 3.529399283412688], [1.5770983263800042, 96.031593692638, 4.724914329752706], [0.0, 95.76496959990216, 4.974166937725335], [-3.005126348206007, 96.5939329821601, 3.529399283412688], [-4.2395346481185285, 97.28662911956711, 2.2338041923498766], [-5.514498044178216, 98.84369530621169, 0.6380333405319378], [-6.061323333580306, 99.74853060016095, 0.30127010459679315], [-6.798747235979318, 101.28780295938657, 0.07512267782692295], [-7.4004546207566335, 103.3630468049505, -0.05069168081345499], [-7.786341006592426, 105.46078729789686, -0.10274985828909157], [-7.984960288515327, 107.50658792395498, -0.20212083237656486], [-7.816732059690539, 109.51341676653195, 0.04653833182295575], [-7.615868049855443, 111.24591975093242, 1.1410812808577324], [-6.809507968084384, 112.84804877429715, 3.0678804442605156], [-5.516548727119685, 113.83613232318154, 4.512163867116608], [-3.580017798149398, 114.33570847034616, 5.896028156482873], [-1.6674884686572777, 114.53004338093189, 6.441343367109859], [0.0, 114.49734953690091, 6.612797333031283]],k = (0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 30.0)),
                  'gear': lambda: mc.curve(d=3, p=[[-1.0346866027558053, 13.457507258111141, 0.5293530632957757], [-1.0346865591390677, 13.45976282613017, 0.5293530632957757], [-1.0346658866747478, 13.46738512807856, 0.5293530632957757], [-1.033738502084286, 13.47664930666317, 0.5293530632957757], [-1.0320097820128493, 13.485826153616653, 0.5293530632957757], [-1.0280961757802605, 13.486592296841287, 0.5293530632957757], [-1.0007005800111255, 13.491955368210883, 0.5293530632957757], [-0.9967869737785368, 13.492721511435516, 0.5293530632957757], [-0.9937495944497668, 13.503907631066115, 0.5293530632957757], [-0.989298266433645, 13.51450259476271, 0.5293530632957757], [-0.9836429104539566, 13.524324119675564, 0.5293530632957757], [-0.9858549890119881, 13.527651767458222, 0.5293530632957757], [-1.0013397380341136, 13.550945598329056, 0.5293530632957757], [-1.0035518166287978, 13.554273246130041, 0.5293530632957757], [-0.9983443792352564, 13.561849913791852, 0.5293530632957757], [-0.9924128579988777, 13.569079565736578, 0.5293530632957757], [-0.9856802600314055, 13.575818524912004, 0.5293530632957757], [-0.9788318437184025, 13.58266474737641, 0.5293530632957757], [-0.9714736513054606, 13.58868422895903, 0.5293530632957757], [-0.963762081417692, 13.59395155008437, 0.5293530632957757], [-0.9604511046302086, 13.591724482482363, 0.5293530632957757], [-0.9372739692961425, 13.576134809063827, 0.5293530632957757], [-0.933962992508659, 13.57390774181552, 0.5293530632957757], [-0.9241307189838853, 13.579545768608803, 0.5293530632957757], [-0.9135272007072278, 13.583978013184328, 0.5293530632957757], [-0.9023347199603085, 13.586994115333868, 0.5293530632957757], [-0.9015464223285533, 13.590908915620464, 0.5293530632957757], [-0.8960282680015798, 13.618312871286902, 0.5293530632957757], [-0.8952399703698246, 13.622227671941857, 0.5293530632957757], [-0.8862002187761662, 13.62390265049311, 0.5293530632957757], [-0.8768926373336056, 13.624821739161758, 0.5293530632957757], [-0.8673667997643262, 13.624825906997602, 0.5293530632957757], [-0.8576843442230144, 13.624823713478882, 0.5293530632957757], [-0.8482225576777268, 13.623876986239784, 0.5293530632957757], [-0.8390457105409798, 13.62214826605839, 0.5293530632957757], [-0.8382797867195315, 13.618234416400423, 0.5293530632957757], [-0.8329182507507303, 13.590837114364673, 0.5293530632957757], [-0.832152326929282, 13.58692326433468, 0.5293530632957757], [-0.8209662073719891, 13.583885884958262, 0.5293530632957757], [-0.8103714631885375, 13.579436531369222, 0.5293530632957757], [-0.8005497186159288, 13.573779200944125, 0.5293530632957757], [-0.7997327619286777, 13.574437504020931, 0.5293530632957757], [-0.7700592253931351, 13.594971187404694, 0.5293530632957757], [-0.7705986181375497, 13.593690300498405, 0.5293530632957757], [-0.7630219501092126, 13.588482863500714, 0.5293530632957757], [-0.7557922986409711, 13.58255134193446, 0.5293530632957757], [-0.7490533395388514, 13.575818524912004, 0.5293530632957757], [-0.7422090907318178, 13.568970327763942, 0.5293530632957757], [-0.7361876348430705, 13.561612135314348, 0.5293530632957757], [-0.7309203142528614, 13.55390034584013, 0.5293530632957757], [-0.7331473573470262, 13.550589393866538, 0.5293530632957757], [-0.7487368600463525, 13.527412428967624, 0.5293530632957757], [-0.7509639031405174, 13.524101476627505, 0.5293530632957757], [-0.7453280694627747, 13.51426920295612, 0.5293530632957757], [-0.7408938511199149, 13.503665684752768, 0.5293530632957757], [-0.7378777489337236, 13.49247298456601, 0.5293530632957757], [-0.7372570310960833, 13.491684711399946, 0.5293530632957757], [-0.702890672562298, 13.487214607954368, 0.5293530632957757], [-0.7028598012035626, 13.486942283591253, 0.5293530632957757], [-0.7009692137378295, 13.47633870285836, 0.5293530632957757], [-0.7003011397787526, 13.469573137931175, 0.5293530632957757], [-0.7001175214504842, 13.462692138082572, 0.5293530632957757], [-0.700073975434338, 13.457507258111141, 0.5293530632957757], [-0.7001175214504842, 13.452322378121384, 0.5293530632957757], [-0.7003011397787526, 13.445441377924578, 0.5293530632957757], [-0.7009692137378295, 13.438675812997394, 0.5293530632957757], [-0.7026441922890811, 13.429636061422062, 0.5293530632957757], [-0.7065589926489821, 13.428847788255998, 0.5293530632957757], [-0.7339629485371697, 13.423329804455808, 0.5293530632957757], [-0.7378777489337236, 13.422541531289744, 0.5293530632957757], [-0.7408938511199149, 13.41134883108466, 0.5293530632957757], [-0.7453280694627747, 13.400745312991265, 0.5293530632957757], [-0.7509639031405174, 13.390913039613102, 0.5293530632957757], [-0.7487368600463525, 13.38760208683315, 0.5293530632957757], [-0.7331473573470262, 13.364425121952562, 0.5293530632957757], [-0.7309203142528614, 13.361114170088928, 0.5293530632957757], [-0.7361876348430705, 13.353402380852954, 0.5293530632957757], [-0.7422090907318178, 13.346044188476665, 0.5293530632957757], [-0.7490533395388514, 13.33919599140191, 0.5293530632957757], [-0.7557922986409711, 13.332463173976272, 0.5293530632957757], [-0.7630219501092126, 13.326531652648262, 0.5293530632957757], [-0.7705986181375497, 13.321324215346353, 0.5293530632957757], [-0.773926485030172, 13.323536537644976, 0.5293530632957757], [-0.7972218517233065, 13.33902299294288, 0.5293530632957757], [-0.8005497186159288, 13.341235314874977, 0.5293530632957757], [-0.8103714631885375, 13.335577984853058, 0.5293530632957757], [-0.8209662073719891, 13.331128630824187, 0.5293530632957757], [-0.832152326929282, 13.32809125193525, 0.5293530632957757], [-0.8329182507507303, 13.324177401485583, 0.5293530632957757], [-0.8382797867195315, 13.296780099770544, 0.5293530632957757], [-0.8390457105409798, 13.292866250237196, 0.5293530632957757], [-0.8482225576777268, 13.291137529982496, 0.5293530632957757], [-0.8576843442230144, 13.290190802670093, 0.5293530632957757], [-0.8673667997643262, 13.290188609188027, 0.5293530632957757], [-0.8768926373336056, 13.29019277696889, 0.5293530632957757], [-0.8862002187761662, 13.291111865380971, 0.5293530632957757], [-0.8952399703698246, 13.29278684395055, 0.5293530632957757], [-0.8960282680015798, 13.296701644988525, 0.5293530632957757], [-0.9015464223285533, 13.324105600271944, 0.5293530632957757], [-0.9023347199603085, 13.328020400576865, 0.5293530632957757], [-0.9135272007072278, 13.33103650274473, 0.5293530632957757], [-0.9241307189838853, 13.335468747283604, 0.5293530632957757], [-0.933962992508659, 13.341106773966928, 0.5293530632957757], [-0.9372739692961425, 13.338879706828578, 0.5293530632957757], [-0.9604511046302086, 13.323290033437532, 0.5293530632957757], [-0.963762081417692, 13.32106296611592, 0.5293530632957757], [-0.9714736513054606, 13.326330286816086, 0.5293530632957757], [-0.9788318437184025, 13.33234976844269, 0.5293530632957757], [-0.9856802600314055, 13.33919599140191, 0.5293530632957757], [-0.9924128579988777, 13.345934950540682, 0.5293530632957757], [-0.9983443792352564, 13.353164602008924, 0.5293530632957757], [-1.0035518166287978, 13.360741269707386, 0.5293530632957757], [-1.0013397380341136, 13.364068917435066, 0.5293530632957757], [-0.9858549890119881, 13.387362748782385, 0.5293530632957757], [-0.9836429104539566, 13.390690396510063, 0.5293530632957757], [-0.989298266433645, 13.400511921477896, 0.5293530632957757], [-0.9937495944497668, 13.411106885192819, 0.5293530632957757], [-0.9967869737785368, 13.42229300440191, 0.5293530632957757], [-1.0007005800111255, 13.42305914764487, 0.5293530632957757], [-1.0280961757802605, 13.42842221899614, 0.5293530632957757], [-1.0320097820128493, 13.4291883622391, 0.5293530632957757], [-1.033738502084286, 13.43836520955911, 0.5293530632957757], [-1.0346658866747478, 13.447629388143723, 0.5293530632957757], [-1.0346865591390677, 13.455251689725584, 0.5293530632957757], [-1.0346866027558053, 13.457507258111141, 0.5293530632957757]], k=(0.0, 0.0, 0.0, 1.0, 4.0, 4.0, 4.0, 7.0, 7.0, 7.0, 10.0, 10.0, 10.0, 13.0, 13.0, 13.0, 14.0, 15.0, 16.0, 19.0, 19.0, 19.0, 22.0, 22.0, 22.0, 25.0, 25.0, 25.0, 28.0, 28.0, 28.0, 29.0, 30.0, 31.0, 34.0, 34.0, 34.0, 37.0, 37.0, 37.0, 38.0, 41.0, 41.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 49.0, 49.0, 49.0, 52.0, 52.0, 52.0, 53.0, 56.0, 56.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 66.0, 66.0, 66.0, 69.0, 69.0, 69.0, 72.0, 72.0, 72.0, 75.0, 75.0, 75.0, 76.0, 77.0, 78.0, 81.0, 81.0, 81.0, 84.0, 84.0, 84.0, 87.0, 87.0, 87.0, 90.0, 90.0, 90.0, 91.0, 92.0, 93.0, 96.0, 96.0, 96.0, 99.0, 99.0, 99.0, 102.0, 102.0, 102.0, 105.0, 105.0, 105.0, 106.0, 107.0, 108.0, 111.0, 111.0, 111.0, 114.0, 114.0, 114.0, 117.0, 117.0, 117.0, 120.0, 120.0, 120.0, 121.0, 122.0, 122.0, 122.0)),
                  'eye': lambda: createControlShape('eye'),
                  'jaw': lambda: mc.curve( d = 3,p = [[-2.2980900108794247, -0.7319416624360702, 7.620277407936156], [-2.2393926054492552, -0.9117558586542551, 7.746372526006412], [-2.0852009672903913, -1.172629732436426, 8.057245288909094], [-1.6940330354347068, -1.3985709132517221, 8.489436317006692], [-1.193969928895871, -1.4986057946697926, 8.838933515473705], [-0.6160267190726286, -1.5271941844832866, 9.094313006556687], [-2.8182123918064456e-11, -1.5299153326511656, 9.162476868463806], [0.6160267191659459, -1.5271941842992078, 9.09431300629692], [1.1939699285524892, -1.4986057951777632, 8.838933516635702], [1.694033036644256, -1.3985709110605216, 8.489436313083603], [2.085200962975013, -1.1726297397285859, 8.057245303274142], [2.2393926144193483, -0.9117558430363326, 7.746372496481861], [2.2980900108832407, -0.731941662252195, 7.620277408052782]],k = (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 10.0, 10.0))
                  }
    
    # delete old shape
    shapes = ctl.getChildren(s=True)
    if shapes:
        pm.delete(shapes)
    
    # create new shape
    new = pm.PyNode(curvesDict[shape]())
    
    # scale shape
    new.scale.set(scale,scale,scale)
    pm.makeIdentity(new, s=True, a=True)
    
    # replace shape
    newShapes = new.getChildren()
    # rename new shapes properly
    for eachShape in newShapes:
        eachShape.rename(ctl.name() + 'Shape')
    pm.parent(newShapes, ctl, r=True, s=True)
    
    # delete the new transform since we only wanted the shapes
    pm.delete(new)

def orientLoopTransforms(transforms, secAxis):
    '''
    bnds [list of PyNode.transform]
    '''
    for _ in range(len(transforms) - 1):
        currTransform = transforms[_]
        nextTransform = transforms[_ + 1]
        # orient curr using next as reference
        currPos = currTransform.getRotatePivot(space='world')
        nextPos = nextTransform.getRotatePivot(space='world')
        secVec = nextPos - currPos
        rt.orientToVector(currTransform, (0, 1, 0), (0, 1, 0), secAxis, secVec)

def getBindDict(mesh, skn):
    """
    create a dictionary with influences as keys,
    list of vertIds as values
    * assumes that this is a rigid bind - all weights are either 1 or 0
    mesh = pm.PyNode('body_geo')
    skn = pm.PyNode('skinCluster1')
    """
    bindDict = {}
    
    for infId, inf in enumerate(skn.influenceObjects()):
        print infId, inf
        weightsIter = skn.getWeights(mesh, infId)
        vertsList = list()
        for vertId, vertWeight in enumerate(weightsIter):
            if vertWeight == 1.0:
                vertsList.append(vertId)
        bindDict[inf] = vertsList
        
    return bindDict

def getMaskFromBindDict(bindDict, jnts, mesh):
    """
    returns mask as a list
    jnts = jnts to use in opaque region
    """
    numOfVerts = mesh.numVertices()
    maskList = [0] * numOfVerts
    for eachJnt in jnts:
        for eachVertId in bindDict[eachJnt]:
            maskList[eachVertId] = 1
            
    return maskList



    
def arbitraryWeightsCorrection(char=None):
    '''
    used to correct weights where needed
    '''
    if char is 'sorceress':
        mel.ngAssignWeights('body_geo.vtx[3006]', bnj=True, ij='RT_upper_pinch_lip_bnd', intensity=1.0)
        mel.ngAssignWeights('body_geo.vtx[2984]', bnj=True, ij='LT_upper_pinch_lip_bnd', intensity=1.0)
    elif char is 'pharaoh':
        mel.ngAssignWeights('body_geo.vtx[2681]', bnj=True, ij='RT_upper_pinch_lip_bnd', intensity=1.0)
        mel.ngAssignWeights('body_geo.vtx[1177]', bnj=True, ij='LT_upper_pinch_lip_bnd', intensity=1.0)
    else:
        pm.warning('No correction data for ' + char)
            
    
def createSkinLayers(mesh):
    # select bnd jnts
    jnts = pm.ls('*_bnd', type='joint')
    jnts.remove(pm.PyNode('CT_jaw_bnd'))
    
    # group bind jnts for layering
    # jnts within the same group are smoothed out
    # layers allow distinct creases by masking
    lipJnts = [jnt for jnt in jnts if '_lip_' in jnt.name()]
    eyelidJnts = [jnt for jnt in jnts if '_eyelid_' in jnt.name()]
    noseJnts = [pm.PyNode(jnt) for jnt in ['CT_noseTip_bnd',
                                           'LT_nostril_bnd',
                                           'RT_nostril_bnd',
                                           'CT_noseMover_bnd']]
    neckJnts = [pm.PyNode(jnt) for jnt in ['CT_neck_bnd',
                                           'LT_neck_bnd',
                                           'RT_neck_bnd']]
    centerBrowJnt = [pm.PyNode('CT_brow_bnd')]
    sideBrowJnts = [jnt for jnt in jnts if '_brow_' in jnt.name()
                    and jnt not in centerBrowJnt]
    foreheadJnts = [jnt for jnt in jnts if '_forehead_' in jnt.name()
                    and '_perimeter_' not in jnt.name()] 
    '''
    baseJnts = [jnt for jnt in jnts if jnt not in lipJnts 
                and jnt not in eyelidJnts
                and jnt not in noseJnts]
                '''
    
    pm.select(cl=True)
    
    # rigid bnd to mesh
    skn = pm.skinCluster(jnts, mesh, bindMethod=0, maximumInfluences=1, omi=False)

    # use this data for masking
    bindDict = getBindDict(mesh, skn)
    
    """
    # bnd lowerjaw
    mc.skinCluster('CT_jaw_bnd', 'lowerTeeth_geo')
    mc.skinCluster('CT_jaw_bnd', 'lowerGum_geo')
    mc.skinCluster('CT_jaw_bnd', 'tongue_geo')
    """
    
    # init skin layers
    mll = MllInterface()
    mll.setCurrentMesh(mesh.name())
    mll.initLayers()
    
    #===========================================================================
    # base layer
    #===========================================================================
    # create base layer for CT_base_bnd
    mll.createLayer('Base', False)
    # pm.select(mesh)
    mll.setCurrentLayer(1)
    mel.ngAssignWeights(mesh.name(), bnj=True, ij='CT_base_bnd', intensity=1.0)
    
    #===========================================================================
    # face layer
    #===========================================================================
    # create face layer
    mll.createLayer('Face', False)
    faceJnts = [jnt for jnt in jnts if '_perimeter_' not in jnt.name()
                and jnt not in lipJnts
                and jnt not in noseJnts
                and jnt not in eyelidJnts
                and jnt not in centerBrowJnt
                and jnt not in sideBrowJnts
                and jnt not in foreheadJnts]
    faceJntsName = [jnt.name() for jnt in faceJnts]
    mll.setCurrentLayer(2)
    mel.ngAssignWeights(mesh.name(), bnj=True, ij='/'.join(faceJntsName), intensity=1.0)
    # mask for face layer
    faceMaskJnts = [jnt for jnt in jnts if '_perimeter_' not in jnt.name()
                    and jnt not in centerBrowJnt
                    and jnt not in sideBrowJnts
                    and jnt not in foreheadJnts]
    maskList = getMaskFromBindDict(bindDict, faceMaskJnts, mesh)
    mll.setLayerMask(2, maskList)
    
    #===========================================================================
    # lips layer
    #===========================================================================
    # create lips layer
    mll.createLayer('Lips', False)
    lipJntsName = [jnt.name() for jnt in lipJnts]
    mll.setCurrentLayer(3)
    # skn.addInfluence(lipJnts, lw=True, wt=0)
    mel.ngAssignWeights(mesh.name(), bnj=True, ij='/'.join(lipJntsName), intensity=1.0)
    # arbitraryWeightsCorrection(char='pharaoh')
    """
    # mask for lips layer
    # lists below should be externalized
    innerXfos = [u'CT_upper_lip_bnd',
                 u'LT_upper_sneer_lip_bnd',
                 u'LT_upper_pinch_lip_bnd',
                 u'LT_corner_lip_bnd',
                 u'LT_lower_pinch_lip_bnd',
                 u'LT_lower_sneer_lip_bnd',
                 u'CT_lower_lip_bnd',
                 u'RT_lower_sneer_lip_bnd',
                 u'RT_lower_pinch_lip_bnd',
                 u'RT_corner_lip_bnd',
                 u'RT_upper_pinch_lip_bnd',
                 u'RT_upper_sneer_lip_bnd']
             
    outerXfos = [u'LT_in_philtrum_bnd',
                 u'LT_philtrum_bnd',
                 u'LT_sneer_bnd',
                 u'LT_low_crease_bnd',
                 u'LT_mid_chin_bnd',
                 u'CT_mid_chin_bnd',
                 u'RT_mid_chin_bnd',
                 u'RT_low_crease_bnd',
                 u'RT_sneer_bnd',
                 u'RT_philtrum_bnd',
                 u'RT_in_philtrum_bnd']
    """
    # maskList = ngWeights.createWeightsListByPolyStrip(outerXfos, innerXfos, mesh, 1)
    lipMaskJnts = lipJnts.append(pm.PyNode('CT_mouthMover_bnd'))
    maskList = getMaskFromBindDict(bindDict, lipJnts, mesh)
    mll.setLayerMask(3, maskList)
    
    #===========================================================================
    # nose layer
    #===========================================================================
    mll.createLayer('Nose', False)
    noseJntsName = [jnt.name() for jnt in noseJnts]
    mll.setCurrentLayer(4)
    mel.ngAssignWeights(mesh.name(), bnj=True, ij='/'.join(noseJntsName), intensity=1.0)
    # mask for face layer
    maskList = getMaskFromBindDict(bindDict, noseJnts, mesh)
    mll.setLayerMask(4, maskList)
    
    #===========================================================================
    # brows layer
    #===========================================================================
    mll.createLayer('Brows', False)
    # include forehead in the same layer too
    browsJntsName = [jnt.name() for jnt in sideBrowJnts + foreheadJnts]
    mll.setCurrentLayer(5)
    mel.ngAssignWeights(mesh.name(), bnj=True, ij='/'.join(browsJntsName), intensity=1.0)
    maskList = getMaskFromBindDict(bindDict, centerBrowJnt + sideBrowJnts + foreheadJnts, mesh)
    mll.setLayerMask(5, maskList)
    
    #===========================================================================
    # center brow layer (to get brow furrow crease)
    #===========================================================================
    mll.createLayer('MidBrow', False)
    centerBrowJntName = [jnt.name() for jnt in centerBrowJnt]
    mll.setCurrentLayer(6)
    mel.ngAssignWeights(mesh.name(), bnj=True, ij='/'.join(centerBrowJntName), intensity=1.0)
    maskList = getMaskFromBindDict(bindDict, centerBrowJnt, mesh)
    mll.setLayerMask(6, maskList)
    
    return mll
    
def smoothSkinLayers(mll):
    '''
    '''
    # 2 - face
    ngWeights.relaxLayerWeights(mll, 2)
    ngWeights.smoothLayerMask(mll, 2, 1.0)
    # 3 - lips
    ngWeights.relaxLayerWeights(mll, 3)
    ngWeights.smoothLayerMask(mll, 3, 2.5)
    # 4 - nose
    ngWeights.relaxLayerWeights(mll, 4)
    ngWeights.smoothLayerMask(mll, 4, 1.0)
    # 5 - brows
    ngWeights.relaxLayerWeights(mll, 5)
    ngWeights.smoothLayerMask(mll, 5, 1.5)
    # 6 - midbrows
    ngWeights.relaxLayerWeights(mll, 6)
    ngWeights.smoothLayerMask(mll, 6, 1.0)