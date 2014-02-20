'''
Created on Feb 14, 2014

@author: Leon
'''

import pymel.core as pm

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
        ###bwNd = bwNds[0]
        
        inputAttrs = bwNd.input.inputs(p=True, s=True)
        inputNds = [attr.node() for attr in inputAttrs]
        
        # ITER through each input to remove BTA,
        # and subtract 1
        for attr, nd in zip(inputAttrs, inputNds):
            ###attr = inputAttrs[0]
            ###nd = inputNds[0]
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
    sdkGrp = pm.group(sdkDag, n=sdkDag.name()+'_priDrv')
    sdkHm = pm.group(sdkGrp, n=sdkDag.name()+'_hm')
    bnd.addAttr('sdkMsg', at='message')
    sdkDag.message >> bnd.sdkMsg
    
    cons = pm.parentConstraint(bnd, sdkHm)    
    pm.delete(cons)
    
    # build motion system - weightedConnections
    # we need 9 bw nodes, one for each channel
    channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    bwNodes = {}
    for eachChannel in channels:
        bwNd = pm.createNode('blendWeighted', n=bnd.name().replace('_bnd', '_%s_bw'%eachChannel))
        bwNodes[eachChannel] = bwNd
        bnd.addAttr(eachChannel+'_bwMsg', at='message')
        bwNd.message >> bnd.attr(eachChannel+'_bwMsg')
        # connect bw output to sdk's priDrv
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
        
addMotionSystemToBndGo()

    
def addPrimaryCtlToBnd(bnd):
    # create ctl
    ctl = pm.circle(n=bnd.name().replace('_bnd', '_pri_ctrl'))
    ctg = pm.group(ctl, n=ctl[0].name()+'_ctg')
    cth = pm.group(ctg, n=ctg.name()+'_cth')
    
    # position ctl
    cons = pm.parentConstraint(bnd, cth)
    pm.delete(cons)
    
    # shape ctl
    ctl[1].radius.set(0.05)
    ctl[1].sweep.set(359)
    ctl[1].centerZ.set(0.04)
    pm.delete(ctl, ch=True)
    
addPrimaryCtlToBnd(pm.ls(sl=True)[0])

def connectBndsToPriCtlGo():
    bnds = pm.ls(sl=True)[:-1]
    priCtl = pm.ls(sl=True)[-1]
    for eachBnd in bnds:
        connectBndToPriCtl(eachBnd, priCtl)
    pm.select(priCtl)
    
def connectBndToPriCtl(bnd, priCtl):
    '''
    bnd = pm.PyNode('lf_nostrilf_bnd')
    priCtl = pm.PyNode('nose_pri_ctrl')
    '''
    # bnd's "local" matrix within priCtl
    bnd_wMat = bnd.getMatrix(ws=True)
    priCtl_wMat = priCtl.getMatrix(ws=True)
    bnd_lMat = bnd_wMat * priCtl_wMat.inverse()
    lMatNd = pm.createNode('fourByFourMatrix', n=bnd.replace('_bnd', '_lMat_in_'+priCtl))
    # populate "local" matrix
    for i in range(4):
        for j in range(4):
            lMatNd.attr('in%d%d'%(i,j)).set(bnd_lMat[i][j])
    # bnd's "local-inverse" matrix
    lInvMatNd = pm.createNode('inverseMatrix', n=bnd.replace('_bnd', '_lInvMat_in_'+priCtl))
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
    channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    bwNodes = {}
    for eachChannel in channels:
        bwNodes[eachChannel] = bnd.attr(eachChannel+'_bwMsg').get()
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
    # connect weight to be blended to 0
    bnd.addAttr(priCtl+'_weight', at='double', k=True, min=0, max=1, dv=1)
    for eachChannel in ['tx','ty','tz','rx','ry','rz']:
        bnd.attr(priCtl+'_weight') >> bwNodes[eachChannel].weight[nextIndex]
    # scales need to be blended back to 1 (not 0)
    for eachChannel in ['sx','sy','sz']:
        bta = pm.createNode('blendTwoAttr', n=bnd.replace('_bnd', '_%s_bta'%eachChannel))
        bta.input[0].set(1)
        dmNd.attr('o%s'%eachChannel) >> bta.input[1]
        bnd.attr(priCtl+'_weight') >> bta.attributesBlender
        bta.output >> bwNodes[eachChannel].i[nextIndex]
        
connectBndsToPriCtlGo()

def addSecondaryCtlToBnd(bnd):
    # add secondary control to bnd
    # create ctl
    ctl = pm.circle(n=bnd.name().replace('_bnd', '_ctrl'))
    ctg = pm.group(ctl, n=ctl[0].name()+'_ctg')
    cth = pm.group(ctg, n=ctg.name()+'_cth')
    
    # position ctl
    cons = pm.parentConstraint(bnd, cth)
    pm.delete(cons)
    
    # shape ctl
    ctl[1].radius.set(0.02)
    ctl[1].sweep.set(359)
    ctl[1].centerZ.set(0.02)
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
    
addSecondaryCtls()