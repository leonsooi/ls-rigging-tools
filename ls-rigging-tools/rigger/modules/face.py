'''
Created on Feb 14, 2014

@author: Leon
'''

import cgm.lib.curves as curves
import cgm.lib.rigging as cgmrigging
import cgm.lib.position as cgmPos
import maya.cmds as mc
import pymel.core as pm
import pymel.core.nodetypes as nt
import rigger.modules.eye as eye
import utils.rigging as rt
reload(eye)
reload(rt)

import ngSkinToolsPlus.lib.weights as ngWeights
reload(ngWeights)

from ngSkinTools.mllInterface import MllInterface


mel = pm.language.Mel()

def addPerimeterBndSystem(mesh):
    '''
    '''
    
    periBnds = []

    periBnds += addPerimeterBnd(nt.Joint('LT_in_forehead_bnd'), nt.Joint('RT_in_forehead_bnd'), nt.Joint('LT_out_forehead_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('LT_out_forehead_bnd'), nt.Joint('LT_in_forehead_bnd'), nt.Joint('LT_temple_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('LT_temple_bnd'), nt.Joint('LT_out_forehead_bnd'), nt.Joint('LT_low_temple_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('LT_low_temple_bnd'), nt.Joint('LT_temple_bnd'), nt.Joint('LT_out_cheek_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('LT_out_cheek_bnd'), nt.Joint('LT_low_temple_bnd'), nt.Joint('LT_up_jaw_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('LT_up_jaw_bnd'), nt.Joint('LT_out_cheek_bnd'), nt.Joint('LT_corner_jaw_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('LT_corner_jaw_bnd'), nt.Joint('LT_up_jaw_bnd'), nt.Joint('LT_neck_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('LT_neck_bnd'), nt.Joint('LT_corner_jaw_bnd'), nt.Joint('CT_neck_bnd'), mesh, True, vecMult=1)
    periBnds += addPerimeterBnd(nt.Joint('CT_neck_bnd'), nt.Joint('LT_neck_bnd'), nt.Joint('RT_neck_bnd'), mesh, False, vecMult=1)
    
    periGrp = pm.group(periBnds, n='CT_perimeterBnds_grp')
    return periGrp

def addPerimeterBnd(currBnd, prevBnd, nextBnd, mesh, mirror, vecMult=1.0):
    """
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
    
def connectBndToPriCtl(bnd, priCtl):
    '''
    bnd = pm.PyNode('lf_nostrilf_bnd')
    priCtl = pm.PyNode('nose_pri_ctrl')
    '''
    # bnd's "local" matrix within priCtl
    bnd_wMat = bnd.getMatrix(ws=True)
    priCtl_wMat = priCtl.getMatrix(ws=True)
    bnd_lMat = bnd_wMat * priCtl_wMat.inverse()
    lMatNd = pm.createNode('fourByFourMatrix', n=bnd.replace('_bnd', '_lMat_in_' + priCtl.nodeName()))
    # populate "local" matrix
    for i in range(4):
        for j in range(4):
            lMatNd.attr('in%d%d' % (i, j)).set(bnd_lMat[i][j])
    # bnd's "local-inverse" matrix
    lInvMatNd = pm.createNode('inverseMatrix', n=bnd.replace('_bnd', '_lInvMat_in_' + priCtl.nodeName()))
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
    bnd.addAttr(priCtl.nodeName() + '_weights', at='double', k=True, dv=0)
    bnd.setAttr(priCtl.nodeName() + '_weights', lock=True)
    # connect weight to be blended to 0
    for eachChannel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
        bnd.addAttr(priCtl.nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=1)
        bnd.attr(priCtl.nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
    # scales need a minus 1, to be normalized to 0 for blending
    for eachChannel in ['sx', 'sy', 'sz']:
        adl = pm.createNode('addDoubleLinear', n=bnd.replace('_bnd', '_%s_adl' % eachChannel))
        adl.input2.set(-1)
        dmNd.attr('o%s' % eachChannel) >> adl.input1
        adl.output >> bwNodes[eachChannel].i[nextIndex]
        bnd.addAttr(priCtl.nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=1)
        bnd.attr(priCtl.nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
        
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
                    
                bnd.attr(priCtl.nodeName() + '_weight_' + eachChannel) >> mdl.input2
                
                if eachChannel in ['sx', 'sy', 'sz']:
                    adl = pm.createNode('addDoubleLinear', n=bnd.replace('_bnd', '_%s_%s_adl' % (eachChannel, priCtl)))
                    mdl.output >> adl.input1
                    adl.input2.set(1)
                    adl.output >> zeroGrp.attr(eachChannel)
                else:
                    mdl.output >> zeroGrp.attr(eachChannel)
    
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

def createBndsFromPlacement(placementGrp):
    '''
    placementGrp [PyNode.Transform] - parent of placement locs and attrs
    '''
    bndGrp = pm.group(n='CT_bnd_grp', em=True)
    
    #===========================================================================
    # Direct bnds - one bnd jnt for each loc
    #===========================================================================
    directPLoc = placementGrp.getChildren()
    # not needed for CT_philtrum
    directPLoc = [loc for loc in directPLoc if 
                  loc.bindType.get() != 2 and
                  'CT_philtrum' not in loc.name() ]
    
    for eachLoc in directPLoc:
        pm.select(cl=True)
        xfo = eachLoc.getMatrix(worldSpace=True)
        jnt = pm.joint(n=eachLoc.replace('pLoc', 'bnd'))
        jnt.setMatrix(xfo)
        scale = eachLoc.localScaleX.get()
        jnt.radius.set(scale)
        bndGrp | jnt
                   
    #===========================================================================
    # Special bnds
    #===========================================================================
    # base bnd - to hold all weights not affected by face
    pm.select(cl=True)
    baseBnd = pm.joint(n='CT_base_bnd')
    bndGrp | baseBnd
    
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

def buildSecondaryControlSystem(placementGrp, bndGrp, mesh):
    '''
    '''
    bnds = bndGrp.getChildren()

    #===========================================================================
    # Set up hierarchy
    #===========================================================================
    pm.progressWindow(title='Build Control System', progress=0, max=len(bnds))
    
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
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_upper_bnd'), nt.Joint(u'LT_eyelid_upper_bnd'), nt.Joint(u'LT_eyelid_outer_upper_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_eyelid_lower_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_eyelid_lower_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_eyelid_inner_lower_bnd'), nt.Joint(u'LT_eyelid_lower_bnd'), nt.Joint(u'LT_eyelid_outer_lower_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_eyelid_upper_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_eyelid_upper_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_upper_bnd'), nt.Joint(u'RT_eyelid_upper_bnd'), nt.Joint(u'RT_eyelid_outer_upper_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_eyelid_lower_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_eyelid_lower_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_eyelid_inner_lower_bnd'), nt.Joint(u'RT_eyelid_lower_bnd'), nt.Joint(u'RT_eyelid_outer_lower_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for CT_noseTip_bnd')
    # nose
    priCtl = addPrimaryCtlToBnd(pm.PyNode('CT_noseTip_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'CT_noseTip_bnd'), nt.Joint(u'LT_nostril_bnd'), nt.Joint(u'RT_nostril_bnd'), nt.Joint(u'LT_up_crease_bnd'), nt.Joint(u'RT_up_crease_bnd'), nt.Joint(u'LT_philtrum_bnd'), nt.Joint(u'RT_philtrum_bnd'), nt.Joint(u'LT_in_philtrum_bnd'), nt.Joint(u'RT_in_philtrum_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for LT_mid_brow_bnd')
    # brows
    priCtl = addPrimaryCtlToBnd(pm.PyNode('LT_mid_brow_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'LT_mid_brow_bnd'), nt.Joint(u'LT_in_brow_bnd'), nt.Joint(u'LT_out_brow_bnd'), nt.Joint(u'LT_in_forehead_bnd'), nt.Joint(u'LT_out_forehead_bnd'), nt.Joint(u'LT_in_low_forehead_bnd'), nt.Joint(u'LT_out_low_forehead_bnd')])
    allPriCtls.append(priCtl)
    
    pm.progressWindow(e=True, step=1, status='Create driver for RT_mid_brow_bnd')
    priCtl = addPrimaryCtlToBnd(pm.PyNode('RT_mid_brow_bnd'))
    connectBndsToPriCtlCmd(priCtl, [nt.Joint(u'RT_mid_brow_bnd'), nt.Joint(u'RT_in_brow_bnd'), nt.Joint(u'RT_in_forehead_bnd'), nt.Joint(u'RT_out_forehead_bnd'), nt.Joint(u'RT_in_low_forehead_bnd'), nt.Joint(u'RT_out_low_forehead_bnd'), nt.Joint(u'RT_out_brow_bnd')])
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
    # lips
    replaceControlCurve(pm.PyNode('LT_lower_sneer_lip_pri_ctrl'), 'downArrow')
    replaceControlCurve(pm.PyNode('RT_lower_sneer_lip_pri_ctrl'), 'downArrow')
    replaceControlCurve(pm.PyNode('LT_upper_sneer_lip_pri_ctrl'), 'upArrow')
    replaceControlCurve(pm.PyNode('RT_upper_sneer_lip_pri_ctrl'), 'upArrow')
    replaceControlCurve(pm.PyNode('LT_corner_lip_pri_ctrl'), 'rightArrow')
    replaceControlCurve(pm.PyNode('RT_corner_lip_pri_ctrl'), 'leftArrow')
    # eye
    replaceControlCurve(pm.PyNode('LT_eyelid_upper_pri_ctrl'), 'upArrow')
    replaceControlCurve(pm.PyNode('RT_eyelid_upper_pri_ctrl'), 'upArrow')
    replaceControlCurve(pm.PyNode('LT_eyelid_lower_pri_ctrl'), 'downArrow')
    replaceControlCurve(pm.PyNode('RT_eyelid_lower_pri_ctrl'), 'downArrow')
    # jaw
    replaceControlCurve(pm.PyNode('CT_jaw_pri_ctrl'), 'mouth')
    # face
    faceCtl = pm.group(pm.PyNode('face_ctrls_grp'), pm.PyNode('CT_face_primary_ctls_grp'), n='CT_face_ctrl')
    replaceControlCurve(pm.PyNode(faceCtl), 'head')
    faceCtl.getShape().overrideEnabled.set(True)
    faceCtl.getShape().overrideColor.set(21)
    # eye
    upLidPos = pm.PyNode('LT_eyelid_upper_pri_ctrl').getTranslation(space='world')
    lowLidPos = pm.PyNode('LT_eyelid_lower_pri_ctrl').getTranslation(space='world')
    midPos = (upLidPos + lowLidPos) / 2
    eyeCtl = pm.group(em=True, n='LT_eye_ctl')
    eyeCtg = pm.group(eyeCtl, n='LT_eye_ctg')
    eyeCth = pm.group(eyeCtg, n='LT_eye_hm')
    eyeCth.setTranslation(midPos, space='world')
    replaceControlCurve(eyeCtl, 'eye')
    eyeCtl.overrideEnabled.set(True)
    eyeCtl.overrideColor.set(6)
    faceCtl | eyeCth
    upLidPos = pm.PyNode('RT_eyelid_upper_pri_ctrl').getTranslation(space='world')
    lowLidPos = pm.PyNode('RT_eyelid_lower_pri_ctrl').getTranslation(space='world')
    midPos = (upLidPos + lowLidPos) / 2
    eyeCtl = pm.group(em=True, n='RT_eye_ctl')
    eyeCtg = pm.group(eyeCtl, n='RT_eye_ctg')
    eyeCth = pm.group(eyeCtg, n='RT_eye_hm')
    eyeCth.setTranslation(midPos, space='world')
    replaceControlCurve(eyeCtl, 'eye')
    eyeCtl.overrideEnabled.set(True)
    eyeCtl.overrideColor.set(13)
    faceCtl | eyeCth
    
    # visibilities
    moverCtls = [u'CT_mouthMover_pri_ctrl',
                 u'CT_noseMover_pri_ctrl',
                 u'LT_eyeMover_pri_ctrl',
                 u'RT_eyeMover_pri_ctrl']
    rt.connectVisibilityToggle(moverCtls, faceCtl.name(), 'moverControlsVis', True)
    priCtls = [u'RT_mid_brow_pri_ctrl', u'RT_eyelid_upper_pri_ctrl', u'RT_eyelid_lower_pri_ctrl', u'LT_mid_brow_pri_ctrl', u'LT_eyelid_upper_pri_ctrl', u'LT_eyelid_lower_pri_ctrl', u'CT_noseTip_pri_ctrl', u'CT_jaw_pri_ctrl', u'RT_cheek_pri_ctrl', u'LT_cheek_pri_ctrl', u'LT_upper_sneer_lip_pri_ctrl', u'RT_upper_sneer_lip_pri_ctrl', u'RT_lower_sneer_lip_pri_ctrl', u'LT_lower_sneer_lip_pri_ctrl', u'LT_corner_lip_pri_ctrl', u'RT_corner_lip_pri_ctrl']
    priCtls.append('LT_eye_ctl')
    priCtls.append('RT_eye_ctl')
    rt.connectVisibilityToggle(priCtls, faceCtl.name(), 'primaryControlsVis', True)
    secCtls = [u'LT_eyelid_inner_ctrl', u'LT_eyelid_upper_ctrl', u'LT_eyelid_outer_ctrl', u'LT_eyelid_lower_ctrl', u'LT_eyelid_inner_upper_ctrl', u'LT_eyelid_inner_lower_ctrl', u'LT_eyelid_outer_upper_ctrl', u'LT_eyelid_outer_lower_ctrl', u'RT_eyelid_inner_ctrl', u'RT_eyelid_upper_ctrl', u'RT_eyelid_outer_ctrl', u'RT_eyelid_lower_ctrl', u'RT_eyelid_inner_upper_ctrl', u'RT_eyelid_inner_lower_ctrl', u'RT_eyelid_outer_upper_ctrl', u'RT_eyelid_outer_lower_ctrl', u'RT_nostril_ctrl', u'CT_noseTip_ctrl', u'LT_nostril_ctrl', u'CT_upper_lip_ctrl', u'CT_lower_lip_ctrl', u'LT_upper_sneer_lip_ctrl', u'LT_lower_sneer_lip_ctrl', u'RT_upper_sneer_lip_ctrl', u'RT_lower_sneer_lip_ctrl', u'LT_corner_lip_ctrl', u'LT_upper_pinch_lip_ctrl', u'RT_corner_lip_ctrl', u'RT_upper_pinch_lip_ctrl', u'RT_lower_pinch_lip_ctrl', u'LT_lower_pinch_lip_ctrl', u'LT_in_brow_ctrl', u'LT_mid_brow_ctrl', u'LT_out_brow_ctrl', u'RT_in_brow_ctrl', u'CT_brow_ctrl', u'RT_mid_brow_ctrl', u'RT_out_brow_ctrl']
    rt.connectVisibilityToggle(secCtls, faceCtl.name(), 'secondaryControlsVis', False)
    terCtls = [u'LT_in_forehead_ctrl', u'RT_in_forehead_ctrl', u'LT_out_forehead_ctrl', u'RT_out_forehead_ctrl', u'LT_temple_ctrl', u'RT_temple_ctrl', u'LT_squint_ctrl', u'RT_squint_ctrl', u'LT_philtrum_ctrl', u'RT_philtrum_ctrl', u'LT_up_crease_ctrl', u'RT_up_crease_ctrl', u'LT_mid_crease_ctrl', u'RT_mid_crease_ctrl', u'LT_low_crease_ctrl', u'RT_low_crease_ctrl', u'LT_cheek_ctrl', u'RT_cheek_ctrl', u'LT_up_jaw_ctrl', u'RT_up_jaw_ctrl', u'LT_corner_jaw_ctrl', u'RT_corner_jaw_ctrl', u'LT_low_jaw_ctrl', u'RT_low_jaw_ctrl', u'LT_chin_ctrl', u'RT_chin_ctrl', u'CT_chin_ctrl', u'LT_in_low_forehead_ctrl', u'RT_in_low_forehead_ctrl', u'LT_out_low_forehead_ctrl', u'RT_out_low_forehead_ctrl', u'LT_low_temple_ctrl', u'RT_low_temple_ctrl', u'LT_out_cheek_ctrl', u'RT_out_cheek_ctrl', u'LT_in_philtrum_ctrl', u'RT_in_philtrum_ctrl', u'LT_low_cheek_ctrl', u'RT_low_cheek_ctrl', u'LT_in_cheek_ctrl', u'RT_in_cheek_ctrl', u'LT_up_cheek_ctrl', u'RT_up_cheek_ctrl', u'LT_sneer_ctrl', u'RT_sneer_ctrl', u'CT_mid_chin_ctrl', u'LT_mid_chin_ctrl', u'RT_mid_chin_ctrl']
    terCtls += ['LT_neck_ctrl', 'CT_neck_ctrl', 'RT_neck_ctrl']
    rt.connectVisibilityToggle(terCtls, faceCtl.name(), 'tertiaryControlsVis', False)
    rt.connectVisibilityToggle(['CT_bnd_grp', 'CT_jnts_grp', 'CT_placement_grp'], faceCtl.name(), 'jointsVis', False)
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
    


def replaceControlCurve(ctl, shape='', scale=10.0):
    '''
    '''
    curvesDict = {'rightArrow': lambda: mc.curve(d=1, p=[[0.0, 0.04, 0.04], [0.0, -0.04, 0.04], [0.04, 0.0, 0.04], [0.0, 0.04, 0.04]], k=(0.0, 1.0, 2.0, 3.0)),
                  'upArrow': lambda: mc.curve(d=1, p=[[0.04, 0.0, 0.04], [-0.04, 0.0, 0.04], [0.0, 0.04, 0.04], [0.04, 0.0, 0.04]], k=(0.0, 1.0, 2.0, 3.0)),
                  'leftArrow': lambda: mc.curve(d=1, p=[[-0.04, 0.04, 0.04], [-0.04, -0.04, 0.04], [-0.08, 0.0, 0.04], [-0.04, 0.04, 0.04]], k=(0.0, 1.0, 2.0, 3.0)),
                  'downArrow': lambda: mc.curve(d=1, p=[[-0.04, 0.0, 0.04], [0.04, 0.0, 0.04], [0.0, -0.04, 0.04], [-0.04, 0.0, 0.04]], k=(0.0, 1.0, 2.0, 3.0)),
                  'mouth': lambda: mc.curve(d=3, p=[[-0.22980900108794244, -0.04759124309943556, 0.8429444356540107], [-0.22393926054492552, -0.045358199737086075, 0.8647067285245191], [-0.20852009672903912, -0.04176876798173142, 0.899687807001127], [-0.1694033035434707, -0.036679282264361804, 0.9492877747432129], [-0.11939699288958709, -0.03296208453991381, 0.9855140061233637], [-0.06160267190726286, -0.030623318742626176, 1.0083066249634127], [-2.8182109062622687e-12, -0.029838670626822782, 1.0159534724654171], [0.06160267191659459, -0.030623318741553832, 1.0083066249315928], [0.1193969928552489, -0.032962084518374, 0.9855140062483384], [0.1694033036644256, -0.03667928229732598, 0.9492877742950683], [0.20852009629750132, -0.041768767799972184, 0.8996878086018357], [0.22393926144193482, -0.04535820005803114, 0.864706725199887], [0.22980900108832408, -0.04759124307766545, 0.8429444356536281]], k=(0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 10.0, 10.0)),
                  'head': lambda: mc.curve(d=2, p=[[0.0, 14.358673055621011, 1.10344962833128], [0.15379506219426828, 14.362009719493294, 1.0863042317391376], [0.3301906251659591, 14.342176313710215, 1.0317727106764392], [0.5087998930920709, 14.291190639461561, 0.8933862817398125], [0.628051540474641, 14.190348943476284, 0.7489579394542033], [0.7024233884711769, 14.02683907825714, 0.556278023113925], [0.7209493893796295, 13.850023525115141, 0.44682372821044736], [0.7364653413044864, 13.645210860977455, 0.4219578117904953], [0.7181463751524083, 13.436420819879839, 0.43189490919924256], [0.6825554719317545, 13.22232990693574, 0.43710072694680624], [0.6270590613694109, 13.01053495376001, 0.44968216281084405], [0.5590453047139784, 12.853440105391334, 0.4722969054878311], [0.5086107554059927, 12.761094548447085, 0.5059732290813456], [0.3910188928665723, 12.602183700068066, 0.6655503142631394], [0.2771674900973296, 12.531488612210927, 0.7951098233694205], [0.14545823839333608, 12.47409746574503, 0.9146613280034224], [0.0, 12.446886380475599, 0.9395865888006854], [-0.2771674900973296, 12.531488612210927, 0.7951098233694205], [-0.3910188928665723, 12.602183700068066, 0.6655503142631394], [-0.5086107554059927, 12.761094548447085, 0.5059732290813456], [-0.5590453047139784, 12.853440105391334, 0.4722969054878311], [-0.6270590613694109, 13.01053495376001, 0.44968216281084405], [-0.6825554719317545, 13.22232990693574, 0.43710072694680624], [-0.7181463751524083, 13.436420819879839, 0.43189490919924256], [-0.7364653413044864, 13.645210860977455, 0.4219578117904953], [-0.7209493893796295, 13.850023525115141, 0.44682372821044736], [-0.7024233884711769, 14.02683907825714, 0.556278023113925], [-0.628051540474641, 14.190348943476284, 0.7489579394542033], [-0.5087998930920709, 14.291190639461561, 0.8933862817398125], [-0.3301906251659591, 14.342176313710215, 1.0317727106764392], [-0.15379506219426828, 14.362009719493294, 1.0863042317391376], [0.0, 14.358673055621011, 1.10344962833128]], k=(0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 30.0)),
                  'gear': lambda: mc.curve(d=3, p=[[-1.0346866027558053, 13.457507258111141, 0.5293530632957757], [-1.0346865591390677, 13.45976282613017, 0.5293530632957757], [-1.0346658866747478, 13.46738512807856, 0.5293530632957757], [-1.033738502084286, 13.47664930666317, 0.5293530632957757], [-1.0320097820128493, 13.485826153616653, 0.5293530632957757], [-1.0280961757802605, 13.486592296841287, 0.5293530632957757], [-1.0007005800111255, 13.491955368210883, 0.5293530632957757], [-0.9967869737785368, 13.492721511435516, 0.5293530632957757], [-0.9937495944497668, 13.503907631066115, 0.5293530632957757], [-0.989298266433645, 13.51450259476271, 0.5293530632957757], [-0.9836429104539566, 13.524324119675564, 0.5293530632957757], [-0.9858549890119881, 13.527651767458222, 0.5293530632957757], [-1.0013397380341136, 13.550945598329056, 0.5293530632957757], [-1.0035518166287978, 13.554273246130041, 0.5293530632957757], [-0.9983443792352564, 13.561849913791852, 0.5293530632957757], [-0.9924128579988777, 13.569079565736578, 0.5293530632957757], [-0.9856802600314055, 13.575818524912004, 0.5293530632957757], [-0.9788318437184025, 13.58266474737641, 0.5293530632957757], [-0.9714736513054606, 13.58868422895903, 0.5293530632957757], [-0.963762081417692, 13.59395155008437, 0.5293530632957757], [-0.9604511046302086, 13.591724482482363, 0.5293530632957757], [-0.9372739692961425, 13.576134809063827, 0.5293530632957757], [-0.933962992508659, 13.57390774181552, 0.5293530632957757], [-0.9241307189838853, 13.579545768608803, 0.5293530632957757], [-0.9135272007072278, 13.583978013184328, 0.5293530632957757], [-0.9023347199603085, 13.586994115333868, 0.5293530632957757], [-0.9015464223285533, 13.590908915620464, 0.5293530632957757], [-0.8960282680015798, 13.618312871286902, 0.5293530632957757], [-0.8952399703698246, 13.622227671941857, 0.5293530632957757], [-0.8862002187761662, 13.62390265049311, 0.5293530632957757], [-0.8768926373336056, 13.624821739161758, 0.5293530632957757], [-0.8673667997643262, 13.624825906997602, 0.5293530632957757], [-0.8576843442230144, 13.624823713478882, 0.5293530632957757], [-0.8482225576777268, 13.623876986239784, 0.5293530632957757], [-0.8390457105409798, 13.62214826605839, 0.5293530632957757], [-0.8382797867195315, 13.618234416400423, 0.5293530632957757], [-0.8329182507507303, 13.590837114364673, 0.5293530632957757], [-0.832152326929282, 13.58692326433468, 0.5293530632957757], [-0.8209662073719891, 13.583885884958262, 0.5293530632957757], [-0.8103714631885375, 13.579436531369222, 0.5293530632957757], [-0.8005497186159288, 13.573779200944125, 0.5293530632957757], [-0.7997327619286777, 13.574437504020931, 0.5293530632957757], [-0.7700592253931351, 13.594971187404694, 0.5293530632957757], [-0.7705986181375497, 13.593690300498405, 0.5293530632957757], [-0.7630219501092126, 13.588482863500714, 0.5293530632957757], [-0.7557922986409711, 13.58255134193446, 0.5293530632957757], [-0.7490533395388514, 13.575818524912004, 0.5293530632957757], [-0.7422090907318178, 13.568970327763942, 0.5293530632957757], [-0.7361876348430705, 13.561612135314348, 0.5293530632957757], [-0.7309203142528614, 13.55390034584013, 0.5293530632957757], [-0.7331473573470262, 13.550589393866538, 0.5293530632957757], [-0.7487368600463525, 13.527412428967624, 0.5293530632957757], [-0.7509639031405174, 13.524101476627505, 0.5293530632957757], [-0.7453280694627747, 13.51426920295612, 0.5293530632957757], [-0.7408938511199149, 13.503665684752768, 0.5293530632957757], [-0.7378777489337236, 13.49247298456601, 0.5293530632957757], [-0.7372570310960833, 13.491684711399946, 0.5293530632957757], [-0.702890672562298, 13.487214607954368, 0.5293530632957757], [-0.7028598012035626, 13.486942283591253, 0.5293530632957757], [-0.7009692137378295, 13.47633870285836, 0.5293530632957757], [-0.7003011397787526, 13.469573137931175, 0.5293530632957757], [-0.7001175214504842, 13.462692138082572, 0.5293530632957757], [-0.700073975434338, 13.457507258111141, 0.5293530632957757], [-0.7001175214504842, 13.452322378121384, 0.5293530632957757], [-0.7003011397787526, 13.445441377924578, 0.5293530632957757], [-0.7009692137378295, 13.438675812997394, 0.5293530632957757], [-0.7026441922890811, 13.429636061422062, 0.5293530632957757], [-0.7065589926489821, 13.428847788255998, 0.5293530632957757], [-0.7339629485371697, 13.423329804455808, 0.5293530632957757], [-0.7378777489337236, 13.422541531289744, 0.5293530632957757], [-0.7408938511199149, 13.41134883108466, 0.5293530632957757], [-0.7453280694627747, 13.400745312991265, 0.5293530632957757], [-0.7509639031405174, 13.390913039613102, 0.5293530632957757], [-0.7487368600463525, 13.38760208683315, 0.5293530632957757], [-0.7331473573470262, 13.364425121952562, 0.5293530632957757], [-0.7309203142528614, 13.361114170088928, 0.5293530632957757], [-0.7361876348430705, 13.353402380852954, 0.5293530632957757], [-0.7422090907318178, 13.346044188476665, 0.5293530632957757], [-0.7490533395388514, 13.33919599140191, 0.5293530632957757], [-0.7557922986409711, 13.332463173976272, 0.5293530632957757], [-0.7630219501092126, 13.326531652648262, 0.5293530632957757], [-0.7705986181375497, 13.321324215346353, 0.5293530632957757], [-0.773926485030172, 13.323536537644976, 0.5293530632957757], [-0.7972218517233065, 13.33902299294288, 0.5293530632957757], [-0.8005497186159288, 13.341235314874977, 0.5293530632957757], [-0.8103714631885375, 13.335577984853058, 0.5293530632957757], [-0.8209662073719891, 13.331128630824187, 0.5293530632957757], [-0.832152326929282, 13.32809125193525, 0.5293530632957757], [-0.8329182507507303, 13.324177401485583, 0.5293530632957757], [-0.8382797867195315, 13.296780099770544, 0.5293530632957757], [-0.8390457105409798, 13.292866250237196, 0.5293530632957757], [-0.8482225576777268, 13.291137529982496, 0.5293530632957757], [-0.8576843442230144, 13.290190802670093, 0.5293530632957757], [-0.8673667997643262, 13.290188609188027, 0.5293530632957757], [-0.8768926373336056, 13.29019277696889, 0.5293530632957757], [-0.8862002187761662, 13.291111865380971, 0.5293530632957757], [-0.8952399703698246, 13.29278684395055, 0.5293530632957757], [-0.8960282680015798, 13.296701644988525, 0.5293530632957757], [-0.9015464223285533, 13.324105600271944, 0.5293530632957757], [-0.9023347199603085, 13.328020400576865, 0.5293530632957757], [-0.9135272007072278, 13.33103650274473, 0.5293530632957757], [-0.9241307189838853, 13.335468747283604, 0.5293530632957757], [-0.933962992508659, 13.341106773966928, 0.5293530632957757], [-0.9372739692961425, 13.338879706828578, 0.5293530632957757], [-0.9604511046302086, 13.323290033437532, 0.5293530632957757], [-0.963762081417692, 13.32106296611592, 0.5293530632957757], [-0.9714736513054606, 13.326330286816086, 0.5293530632957757], [-0.9788318437184025, 13.33234976844269, 0.5293530632957757], [-0.9856802600314055, 13.33919599140191, 0.5293530632957757], [-0.9924128579988777, 13.345934950540682, 0.5293530632957757], [-0.9983443792352564, 13.353164602008924, 0.5293530632957757], [-1.0035518166287978, 13.360741269707386, 0.5293530632957757], [-1.0013397380341136, 13.364068917435066, 0.5293530632957757], [-0.9858549890119881, 13.387362748782385, 0.5293530632957757], [-0.9836429104539566, 13.390690396510063, 0.5293530632957757], [-0.989298266433645, 13.400511921477896, 0.5293530632957757], [-0.9937495944497668, 13.411106885192819, 0.5293530632957757], [-0.9967869737785368, 13.42229300440191, 0.5293530632957757], [-1.0007005800111255, 13.42305914764487, 0.5293530632957757], [-1.0280961757802605, 13.42842221899614, 0.5293530632957757], [-1.0320097820128493, 13.4291883622391, 0.5293530632957757], [-1.033738502084286, 13.43836520955911, 0.5293530632957757], [-1.0346658866747478, 13.447629388143723, 0.5293530632957757], [-1.0346865591390677, 13.455251689725584, 0.5293530632957757], [-1.0346866027558053, 13.457507258111141, 0.5293530632957757]], k=(0.0, 0.0, 0.0, 1.0, 4.0, 4.0, 4.0, 7.0, 7.0, 7.0, 10.0, 10.0, 10.0, 13.0, 13.0, 13.0, 14.0, 15.0, 16.0, 19.0, 19.0, 19.0, 22.0, 22.0, 22.0, 25.0, 25.0, 25.0, 28.0, 28.0, 28.0, 29.0, 30.0, 31.0, 34.0, 34.0, 34.0, 37.0, 37.0, 37.0, 38.0, 41.0, 41.0, 41.0, 42.0, 43.0, 44.0, 45.0, 46.0, 49.0, 49.0, 49.0, 52.0, 52.0, 52.0, 53.0, 56.0, 56.0, 56.0, 57.0, 58.0, 59.0, 60.0, 61.0, 62.0, 63.0, 66.0, 66.0, 66.0, 69.0, 69.0, 69.0, 72.0, 72.0, 72.0, 75.0, 75.0, 75.0, 76.0, 77.0, 78.0, 81.0, 81.0, 81.0, 84.0, 84.0, 84.0, 87.0, 87.0, 87.0, 90.0, 90.0, 90.0, 91.0, 92.0, 93.0, 96.0, 96.0, 96.0, 99.0, 99.0, 99.0, 102.0, 102.0, 102.0, 105.0, 105.0, 105.0, 106.0, 107.0, 108.0, 111.0, 111.0, 111.0, 114.0, 114.0, 114.0, 117.0, 117.0, 117.0, 120.0, 120.0, 120.0, 121.0, 122.0, 122.0, 122.0)),
                  'eye': lambda: createControlShape('eye')
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