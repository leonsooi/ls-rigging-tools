'''
Created on May 26, 2014

@author: Leon
'''
import pymel.core as pm

import cgm.lib.rigging as cgmrigging

def addPriCtlDrivers(priBnd):
    '''
    find all priCtl drivers that are driving this bind
    connect to this bind's priCtl so it moves together
    '''
    # get all priCtls driving this bnd
    attachedCtl = priBnd.attr('attached_pri_ctl').get()
    all_attrs = priBnd.listAttr(ud=True, l=True)
    all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weights' in attr.name()]
    all_priCtls = [attr.attrName().replace('_weights','') for attr in all_attrs]
    
    # let other priCtl drive the new priCtl
    for ctl in all_priCtls:
        if ctl != attachedCtl:
            driveAttachedPriCtl(priBnd, pm.PyNode(ctl))
        else:
            # don't drive an attached ctl
            pass

def setPriCtlFirstPassWeights(priCtlMappings):
    '''
    '''
    for pCtl, weightsTable in priCtlMappings.items():
        attrName = pCtl + '_weight_'
        for bndName, weight in weightsTable.items():
            try:
                bnd = pm.PyNode(bndName)
                bnd.attr(attrName).set(weight)
            except pm.MayaNodeError as e:
                pm.warning('Does not exist: ' + bndName)
                
def setPriCtlSecondPassWeights(priCtlWeights):
    '''
    '''
    for attr, weight in priCtlWeights:
        try:
            targetAttr = pm.PyNode(attr)
            targetAttr.set(weight)
        except pm.MayaAttributeError as e:
            print e
                
def getPriCtlSecondPassWeights(bndGrp):
    '''
    '''
    allBnds = bndGrp.getChildren(type='joint', ad=True)
    
    allWeightsList = []
    
    for bnd in allBnds:
        weightsList = getPriCtlWeights(bnd)
        allWeightsList += weightsList
        
    return allWeightsList
    
def getPriCtlWeights(bnd):
    '''
    '''
    weightsList = []
    
    all_attrs = bnd.listAttr(ud=True, u=True)
    all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weight' in attr.name()]
    all_attrs = [attr for attr in all_attrs if attr.isFreeToChange() == 0]
    
    for src_attr in all_attrs:
        weight = src_attr.get()
        weightsList.append((src_attr.name(), weight))
        
    return weightsList

def getPriCtlFirstPassWeights(bndGrp):
    '''
    traverse all 'LT' and 'CT' bnds
    store only weights that are not 0
    
    # format to save priCtlMappings
    # {bnd_for_priCtl: {bnd: weight,
    #                   bnd: weight,
    #                   bnd: weight}}
    '''
    allBnds = bndGrp.getChildren(type='joint', ad=True)
    
    priCtlMappings = {}
    
    for bnd in allBnds:
        all_attrs = bnd.listAttr(ud=True, u=True)
        # filter to only attrs for simplified pri ctrl weights
        all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weight' in attr.name()]
        all_attrs = [attr for attr in all_attrs if attr.isFreeToChange() == 0]
        for attr in all_attrs:
            weight = attr.get()
            if weight:
                priCtlName = '_'.join(attr.attrName().split('_')[:5])
                if priCtlName not in priCtlMappings.keys():
                    priCtlMappings[priCtlName] = {}
                priCtlMappings[priCtlName][bnd.name()] = round(weight, 4)
                
            else:
                # weight is 0, remove for optimization
                pass
            
    return priCtlMappings

def setupPriCtlSecondPass(priCtlMappings):
    '''
    add binds to priCtl based on mappings generated from firstpass
    '''
    allPriCtls = []
    
    ### Start Progress
    progressAmt = 0
    pm.progressWindow(title='Build Control System',
                      status='Initialize controls...',
                      max=len(priCtlMappings.items()),
                      progress=progressAmt)
    ###
    
    for priCtlName, bndMappings in priCtlMappings.items():
        
        ### Progress
        progressAmt += 1
        pm.progressWindow(e=True,
                          progress=progressAmt,
                          status='Setup control "%s"...'%priCtlName)
        ###
        
        # change to bndName
        bndName = priCtlName.replace('_pri_ctrl', '_bnd')
        priCtlBnd = pm.PyNode(bndName)
        priCtl = addPrimaryCtlToBnd(priCtlBnd)
        for secBndName, weight in bndMappings.items():
            secBnd = pm.PyNode(secBndName)
            connectBndToPriCtl(secBnd, priCtl, False, dv=weight)
        allPriCtls.append(priCtl)
    
    ### End Progress
    pm.progressWindow(endProgress=True)
    ###
        
    allPriCtlHms = [ctl.getParent(-1) for ctl in allPriCtls]
    pm.group(allPriCtlHms, n='CT_face_primary_ctls_grp') 
    return allPriCtls    
    
def setupPriCtlFirstPass(bndGrp, bndsForPriCtls):
    '''
    the first pass will add all binds to every priCtl
    this is to allow maximum controls in adjusting weights
    
    only one attr is exposed (which control other 9)
    this is to simplify as we are just blocking out weights
    
    the weights can be export out, pruned and rebuilt for second pass
    
    bndGrp - grp with all the binds
    bndsForPriCtls - list of strings (names)
    
    also mirrors LT to RT
    '''
    allBnds = bndGrp.getChildren(type='joint', ad=True)
    
    # cast to pynodes
    bndsForPriCtls = [pm.PyNode(n.replace('_pLoc', '_bnd')) for n in bndsForPriCtls]
    
    for priCtlBnd in bndsForPriCtls:
        print priCtlBnd
        newCtl = addPrimaryCtlToBnd(priCtlBnd)
        for secBnd in allBnds:
            # print secBnd
            connectBndToPriCtl(secBnd, newCtl, True)
        
def driveAttachedPriCtlsRun(bndGrp):
    '''
    '''
    allBnds = bndGrp.getChildren(type='joint', ad=True)
    
    for eachBnd in allBnds:
        if eachBnd.hasAttr('attached_pri_ctl'):
            attachedCtl = eachBnd.attr('attached_pri_ctl').get()
            
            # get all priCtls driving this bnd
            all_attrs = eachBnd.listAttr(ud=True, l=True)
            all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weights' in attr.name()]
            all_priCtls = [attr.attrName().replace('_weights','') for attr in all_attrs]
            
            for priCtl in all_priCtls:
                if priCtl != attachedCtl:
                    driveAttachedPriCtl(eachBnd, pm.PyNode(priCtl))
                else:
                    # don't drive an attached ctl
                    pass
    

def driveAttachedPriCtl(bnd, priCtl):
    # find dmNd
    all_mms = priCtl.matrix.outputs(type='multMatrix')
    bndName = '_'.join(bnd.name().split('_')[:3])
    mm = [m for m in all_mms if bndName in m.name()][0]
    dmNd = mm.matrixSum.outputs(type='decomposeMatrix')[0]
    
    channels = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    
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
    
    return eachChannel

def connectBndsToPriCtl(bnds, priCtl, simplify=False, dv=1):
    '''
    bnds - list of bnds to connect to pCtl
    '''
    for bnd in bnds:
        connectBndToPriCtl(bnd, priCtl, simplify, dv)

def connectBndToPriCtl(bnd, priCtl, simplify=False, dv=1):
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
        bnd.addAttr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=dv)
        bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
    # scales need a minus 1, to be normalized to 0 for blending
    for eachChannel in ['sx', 'sy', 'sz']:
        adl = pm.createNode('addDoubleLinear', n=bnd.replace('_bnd', '_%s_adl' % eachChannel))
        adl.input2.set(-1)
        dmNd.attr('o%s' % eachChannel) >> adl.input1
        adl.output >> bwNodes[eachChannel].i[nextIndex]
        bnd.addAttr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=dv)
        bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
        
    # if this bnd already has it's own attached priCtl
    # we need to drive that too
    # drivePriCtlOffset(bnd, priCtl, dmNd, channels, adl)
    
    if simplify:
        # hide the 9 individual attrs
        # add one attr to drive all 9
        bnd.addAttr(priCtl.stripNamespace().nodeName() + '_weight_',
                    at='double', min=-1, max=2, dv=0, k=True)
        for eachChannel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            bnd.setAttr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel, 
                        k=False, cb=False)  
            bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_') >> bnd.attr(priCtl.stripNamespace().nodeName() + '_weight_' + eachChannel)
        
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

def updateOffset(pCtl, offsetGrp, order='secondLast'):
    '''
    if you add additional binds to a priCtl,
    use this to also add them to the offsetgrps
    '''
    # get matrixMults connected to priCtl
    priCtl_outMMs = pCtl.matrix.outputs(type='multMatrix')
    
    # get matrixMults connected to offsetGrp
    offset_outMMs = offsetGrp.matrix.outputs(type='multMatrix')
    
    # matrixMults to update
    update_outMMs = [mm for mm in priCtl_outMMs
                     if mm not in offset_outMMs]
    
    connectOffsetToMatrices(order, offsetGrp, update_outMMs)


def connectOffsetToMatrices(order, offsetGrp, outMMs):
    if order == 'secondLast':
        for outMM in outMMs:
            # be sure to use the next plugIndex
            nextIndex = outMM.matrixIn.numElements()
            nextPlug = outMM.matrixIn.elementByLogicalIndex(nextIndex)
            lastPlug = outMM.matrixIn.elementByLogicalIndex(nextIndex - 1)
            invMat = lastPlug.inputs(p=True)[0]
            if not nextPlug.isConnected():
                # offsetGrp matrix should be inserted at second-last plug (invMat)
                offsetGrp.matrix >> lastPlug
                invMat >> nextPlug
            else:
                pm.warning('Overriding plug %s. Check logical indices.' % nextPlug)
    
    elif order == 'second':
        for outMM in outMMs:
            # move elements up by 1
            # (keep element 0 at 0, since we're going to insert at 1)
            nextIndex = outMM.matrixIn.numElements()
            plugsToMove = [outMM.matrixIn.elementByLogicalIndex(i).inputs(p=True)[0] for 
                i in range(1, nextIndex)]
            # move plugs
            for plugId, plug in enumerate(plugsToMove):
                plug >> outMM.matrixIn.elementByLogicalIndex(plugId + 2)
            
            # connect offsetGrp to second plug
            offsetGrp.matrix >> outMM.matrixIn[1]
    
    else:
        pm.warning('Unknown order method %s' % order)

def addOffset(pCtl, hierarchy, order='secondLast', suffix='_offset'):
    '''
    hierarchy - 'parent', 'child', 'sibling', 'world'
    order - 'secondLast', 'second'
    secondLast will make offset pivot from original position
    second will make offset pivot from offset's post-transform position
    '''
    offsetGrp = pm.group(em=True, n=pCtl+suffix)
    wMat = pCtl.getMatrix(worldSpace=True)
    offsetGrp.setMatrix(wMat, worldSpace=True)
    
    parent = pCtl.getParent()
    
    if hierarchy == 'parent':    
        parent | offsetGrp | pCtl
    elif hierarchy == 'child':
        pCtl | offsetGrp
    elif hierarchy == 'sibling':
        parent | offsetGrp
    elif hierarchy == 'world':
        pass
    else:
        pm.warning('Unknown hierarchy method: %s' % hierarchy)
    
    # get matrices that drive children
    outMMs = pCtl.matrix.outputs(type='multMatrix')
        
    connectOffsetToMatrices(order, offsetGrp, outMMs)
    
    return offsetGrp