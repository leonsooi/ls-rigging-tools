'''
Created on Apr 14, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
import rigger.lib.curve as lcrv
reload(lcrv)

def setMatrixWeightsFromDict(wdict):
    '''
    pass in a dictionary
    {bndName: (attr: val)}
    '''
    pm.select(cl=True)
    for bndName, attrsAndVals in wdict.items():
        try:
            bnd = pm.PyNode(bndName)
            for attr, val in attrsAndVals:
                try:
                    attr = pm.PyNode(attr)
                    if attr.isFreeToChange() == 0:
                        attr.set(val)
                except pm.MayaObjectError as e:
                    print e
            pm.select(bnd, add=True)
        except pm.MayaObjectError as e:
            print e 

def getAllMatrixWeightsOnSelectedBnds():
    '''
    returns a dictionary
    {bndName: (attr: val)}
    '''
    selBnds = pm.ls(sl=True)
    retDict = {}
    for bnd in selBnds:
        attrs = getAllMatrixWeightsAttrsOnBnd(bnd)
        attrsAndVals = [(attr.name(), attr.get()) for attr in attrs]
        retDict[bnd.name()] = attrsAndVals
    return retDict 

def getAllMatrixWeightsAttrsOnBnd(bnd):
    all_attrs = bnd.listAttr(ud=True, u=True)
    all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weight' in attr.name()]
    all_attrs = [attr for attr in all_attrs if attr.isFreeToChange() == 0]
    return all_attrs

def zeroAllMatrixScaleWeights():
    '''
    do this is using DQ skinning
    '''
    bndGrp = pm.PyNode('CT_bnd_grp')
    allBnds = bndGrp.getChildren(ad=True, type='joint')
    
    for bnd in allBnds:
        all_attrs = getAllMatrixWeightsAttrsOnBnd(bnd)
        scale_attrs = [attr for attr in all_attrs if 'weight_s' in attr.name(0)]
        for attr in scale_attrs:
            attr.set(0)
            
def getUpperLowerEyeCurves(crv, cornerCvIds):
    '''
    cornerCvIds = ids for in, up, out, low cvs
    '''
    # get a continuous slice of cvs first
    lowCvId = min(cornerCvIds[0], cornerCvIds[2])
    highCvId = max(cornerCvIds[0], cornerCvIds[2])
    
    # is this the upper slice or lower slice?
    if lowCvId < cornerCvIds[1] < highCvId:
        # upCV is inbetween, so must be upper slice
        sliceName = ['upper', 'lower']
    else:
        sliceName = ['lower', 'upper']
        
    # get the first slice
    firstSlice = range(lowCvId, highCvId+1)
    
    # get the second slice
    maxCvId = crv.numCVs()
    secondSlice = range(highCvId, maxCvId) + range(0, lowCvId+1)
    
    crvMap = {}
    for name, sliceCrv in zip(sliceName, [firstSlice, secondSlice]):
        # create the crv
        print sliceCrv
        cvPoss = [crv.cv[i].getPosition(space='world') for i in sliceCrv]
        newCrv = pm.curve(p=cvPoss, d=1, n=name+'_crv')
        crvMap[name] = newCrv
    
    return crvMap
    

def bindSpliceBetweenJoints(startJnt, endJnt, crv, startIndex, endIndex, 
                            targetCrv, skn, heightVec, intVec):
    '''
    startJnt = upperBnds[0]
    endJnt = upperBnds[1]
    startIndex = upperBndTable[startJnt]
    endIndex = upperBndTable[endJnt]
    crv = drvCrv
    targetCrv = pm.PyNode('target_crv')
    '''
    startHeight = lcrv.calcHeightFromCurve(startJnt, targetCrv,
                                           heightVec=heightVec, intVec=intVec)
    endHeight = lcrv.calcHeightFromCurve(endJnt, targetCrv,
                                           heightVec=heightVec, intVec=intVec)
    
    # figure out which splice to work on
    sectionBetween = crv.cv[min(startIndex, endIndex)+1:max(startIndex, endIndex)-1]
    sectionOutside = [cv for cv in crv.cv if cv not in sectionBetween and cv.index() not in (startIndex, endIndex)]
    # use the shorter section
    section = min((sectionBetween, sectionOutside), key=lambda sec: len(sec))
    
    for eachCV in section:
        pos = eachCV.getPosition(space='world')
        height = lcrv.calcHeightFromCurve(pos, targetCrv)
        startSeg = height - startHeight
        endSeg = endHeight - height
        weight = startSeg / (startSeg + endSeg)
        pm.skinPercent(skn, eachCV, tv=((startJnt, 1-weight),(endJnt, weight)))


def setEyelidLoopWeights(prefix, upperBnds=None, lowerBnds=None):
    # define data
    drvCrv = pm.PyNode(prefix+'_eye_aimAt_crv_0')
    
    if not upperBnds:
        upperBnds = [nt.Joint(prefix+'_inner_eyelid_bnd'),
                     nt.Joint(prefix+'_innerUpper_eyelid_bnd'),
                     nt.Joint(prefix+'_upper_eyelid_bnd'),
                     nt.Joint(prefix+'_outerUpper_eyelid_bnd'),
                     nt.Joint(prefix+'_outer_eyelid_bnd')]
    if not lowerBnds:
        lowerBnds = [nt.Joint(prefix+'_inner_eyelid_bnd'),
                     nt.Joint(prefix+'_innerLower_eyelid_bnd'),
                     nt.Joint(prefix+'_lower_eyelid_bnd'),
                     nt.Joint(prefix+'_outerLower_eyelid_bnd'),
                     nt.Joint(prefix+'_outer_eyelid_bnd')]
        
    cornerBnds = upperBnds[0], upperBnds[2], upperBnds[4], lowerBnds[2]
    '''
    cornerPLocs = [pm.PyNode(bnd.replace('_bnd','_pLoc')) for bnd in cornerBnds]
    cornerCvIds = [pLoc.cv_id.get() for pLoc in cornerPLocs]
    print cornerCvIds
    '''
    cornerCvIds = [lcrv.getClosestCVtoXfo(eachBnd, drvCrv).index()
                   for eachBnd in cornerBnds]
    print cornerCvIds
    
    targetCrvs = getUpperLowerEyeCurves(drvCrv, cornerCvIds)
    
    setEyelidControlsWeights(prefix, upperBnds, lowerBnds, targetCrvs)
    
    # map bnds to CV index
    upperBndTable = {}
    for eachBnd in upperBnds:
        #  get CV index closest to eachBnd
        cv = lcrv.getClosestCVtoXfo(eachBnd, drvCrv)
        upperBndTable[eachBnd] = cv.index()
    
    lowerBndTable = {}
    for eachBnd in lowerBnds:
        #  get CV index closest to eachBnd
        cv = lcrv.getClosestCVtoXfo(eachBnd, drvCrv)
        lowerBndTable[eachBnd] = cv.index()
           
    # initial bind
    skn = pm.skinCluster(upperBnds+lowerBnds, drvCrv)
    
    # make sure each bnd has 100% weight to its closest cv
    for eachBnd in upperBnds:
        bindCV = upperBndTable[eachBnd]
        pm.skinPercent(skn, drvCrv.cv[bindCV], tv=(eachBnd, 1.0))
        
    for eachBnd in lowerBnds:
        bindCV = lowerBndTable[eachBnd]
        pm.skinPercent(skn, drvCrv.cv[bindCV], tv=(eachBnd, 1.0))
        
    # bind splices between each bind jnt
    
    # get vector from upper control
    heightVec = pm.dt.Vector(0,-1,0) * upperBnds[2].getMatrix(ws=True)
    intVec = pm.dt.Vector(0,0,-1) * upperBnds[2].getMatrix(ws=True)
    
    bindSpliceBetweenJoints(upperBnds[0], upperBnds[1], drvCrv, upperBndTable[upperBnds[0]], upperBndTable[upperBnds[1]], targetCrvs['lower'], skn, heightVec, intVec)
    bindSpliceBetweenJoints(upperBnds[1], upperBnds[2], drvCrv, upperBndTable[upperBnds[1]], upperBndTable[upperBnds[2]], targetCrvs['lower'], skn, heightVec, intVec)
    bindSpliceBetweenJoints(upperBnds[2], upperBnds[3], drvCrv, upperBndTable[upperBnds[2]], upperBndTable[upperBnds[3]], targetCrvs['lower'], skn, heightVec, intVec)
    bindSpliceBetweenJoints(upperBnds[3], upperBnds[4], drvCrv, upperBndTable[upperBnds[3]], upperBndTable[upperBnds[4]], targetCrvs['lower'], skn, heightVec, intVec)
    
    # get vector from lower control
    heightVec = pm.dt.Vector(0,-1,0) * lowerBnds[2].getMatrix(ws=True)
    intVec = pm.dt.Vector(0,0,-1) * lowerBnds[2].getMatrix(ws=True)
    
    bindSpliceBetweenJoints(lowerBnds[0], lowerBnds[1], drvCrv, lowerBndTable[lowerBnds[0]], lowerBndTable[lowerBnds[1]], targetCrvs['upper'], skn, heightVec, intVec)
    bindSpliceBetweenJoints(lowerBnds[1], lowerBnds[2], drvCrv, lowerBndTable[lowerBnds[1]], lowerBndTable[lowerBnds[2]], targetCrvs['upper'], skn, heightVec, intVec)
    bindSpliceBetweenJoints(lowerBnds[2], lowerBnds[3], drvCrv, lowerBndTable[lowerBnds[2]], lowerBndTable[lowerBnds[3]], targetCrvs['upper'], skn, heightVec, intVec)
    bindSpliceBetweenJoints(lowerBnds[3], lowerBnds[4], drvCrv, lowerBndTable[lowerBnds[3]], lowerBndTable[lowerBnds[4]], targetCrvs['upper'], skn, heightVec, intVec)
    
    pm.delete(targetCrvs.values())

def setEyelidControlsWeights(prefix, upperBnds, lowerBnds, targetCrvs):
    # define all data - hard coded
    if not upperBnds:
        upperBnds = [nt.Joint(prefix+'_inner_eyelid_bnd'),
                     nt.Joint(prefix+'_innerUpper_eyelid_bnd'),
                     nt.Joint(prefix+'_upper_eyelid_bnd'),
                     nt.Joint(prefix+'_outerUpper_eyelid_bnd'),
                     nt.Joint(prefix+'_outer_eyelid_bnd')]
    if not lowerBnds:
        lowerBnds = [nt.Joint(prefix+'_inner_eyelid_bnd'),
                     nt.Joint(prefix+'_innerLower_eyelid_bnd'),
                     nt.Joint(prefix+'_lower_eyelid_bnd'),
                     nt.Joint(prefix+'_outerLower_eyelid_bnd'),
                     nt.Joint(prefix+'_outer_eyelid_bnd')]
    upperCtls = [pm.PyNode(node.name().replace('_bnd', '_ctrl')) for node in upperBnds]
    lowerCtls = [pm.PyNode(node.name().replace('_bnd', '_ctrl')) for node in lowerBnds]
    
    # weight ctls
    # UPPER controls
    # get vector from upper control
    heightVec = pm.dt.Vector(0,-1,0) * upperBnds[2].getMatrix(ws=True)
    intVec = pm.dt.Vector(0,0,-1) * upperBnds[2].getMatrix(ws=True)
    # get Y-height from lower curve
    upperHeight = lcrv.calcHeightFromCurve(upperBnds[2], targetCrvs['lower'],
                                           heightVec=heightVec, intVec=intVec)
    upperInnerHeight = lcrv.calcHeightFromCurve(upperBnds[1], targetCrvs['lower'],
                                           heightVec=heightVec, intVec=intVec)
    upperOuterHeight = lcrv.calcHeightFromCurve(upperBnds[3], targetCrvs['lower'],
                                           heightVec=heightVec, intVec=intVec)
    upperInnerWeight = upperInnerHeight / upperHeight
    upperOuterWeight = upperOuterHeight / upperHeight
    channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    upperPriCtl = upperCtls[2].name().replace('_ctrl', '_pri_ctrl')
    [upperBnds[1].attr(upperPriCtl+'_weight_'+channel).set(upperInnerWeight) for channel in channels]
    [upperBnds[3].attr(upperPriCtl+'_weight_'+channel).set(upperOuterWeight) for channel in channels]
    
    # LOWER controls
    # get vector from lower control
    heightVec = pm.dt.Vector(0,1,0) * lowerBnds[2].getMatrix(ws=True)
    intVec = pm.dt.Vector(0,0,-1) * lowerBnds[2].getMatrix(ws=True)
    # get y-height from upper crv
    lowerHeight = lcrv.calcHeightFromCurve(lowerBnds[2], targetCrvs['upper'],
                                           heightVec=heightVec, intVec=intVec)
    lowerInnerHeight = lcrv.calcHeightFromCurve(lowerBnds[1], targetCrvs['upper'],
                                           heightVec=heightVec, intVec=intVec)
    lowerOuterHeight = lcrv.calcHeightFromCurve(lowerBnds[3], targetCrvs['upper'],
                                           heightVec=heightVec, intVec=intVec)
    lowerInnerWeight = lowerInnerHeight / lowerHeight
    lowerOuterWeight = lowerOuterHeight / lowerHeight
    channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    lowerPriCtl = lowerCtls[2].name().replace('_ctrl', '_pri_ctrl')
    [lowerBnds[1].attr(lowerPriCtl+'_weight_'+channel).set(lowerInnerWeight) for channel in channels]
    [lowerBnds[3].attr(lowerPriCtl+'_weight_'+channel).set(lowerOuterWeight) for channel in channels]
