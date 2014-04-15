'''
Created on Apr 14, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
import rigger.lib.curve as lcrv
reload(lcrv)

def bindSpliceBetweenJoints(startJnt, endJnt, crv, startIndex, endIndex, targetCrv, skn):
    '''
    startJnt = upperBnds[0]
    endJnt = upperBnds[1]
    startIndex = upperBndTable[startJnt]
    endIndex = upperBndTable[endJnt]
    crv = drvCrv
    targetCrv = pm.PyNode('target_crv')
    '''
    startHeight = lcrv.calcHeightFromCurve(startJnt, targetCrv)
    endHeight = lcrv.calcHeightFromCurve(endJnt, targetCrv)
    
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


def setEyelidLoopWeights(prefix):
    # define data
    drvCrv = pm.PyNode(prefix+'_eye_aimAt_crv_0')
    
    upperBnds = [nt.Joint(prefix+'_eyelid_inner_bnd'),
                 nt.Joint(prefix+'_eyelid_inner_upper_bnd'),
                 nt.Joint(prefix+'_eyelid_upper_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_upper_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_bnd')]
    lowerBnds = [nt.Joint(prefix+'_eyelid_inner_bnd'),
                 nt.Joint(prefix+'_eyelid_inner_lower_bnd'),
                 nt.Joint(prefix+'_eyelid_lower_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_lower_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_bnd')]
    
    setEyelidControlsWeights(prefix)
    
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
    targetInPos = upperBnds[0].getTranslation(space='world')
    targetOutPos = upperBnds[-1].getTranslation(space='world')
    targetCrv = pm.curve(ep=(targetInPos, targetOutPos), d=1, n='target_crv')
    lcrv.extendCrv(targetCrv)
    
    bindSpliceBetweenJoints(upperBnds[0], upperBnds[1], drvCrv, upperBndTable[upperBnds[0]], upperBndTable[upperBnds[1]], targetCrv, skn)
    bindSpliceBetweenJoints(upperBnds[1], upperBnds[2], drvCrv, upperBndTable[upperBnds[1]], upperBndTable[upperBnds[2]], targetCrv, skn)
    bindSpliceBetweenJoints(upperBnds[2], upperBnds[3], drvCrv, upperBndTable[upperBnds[2]], upperBndTable[upperBnds[3]], targetCrv, skn)
    bindSpliceBetweenJoints(upperBnds[3], upperBnds[4], drvCrv, upperBndTable[upperBnds[3]], upperBndTable[upperBnds[4]], targetCrv, skn)
    
    bindSpliceBetweenJoints(lowerBnds[0], lowerBnds[1], drvCrv, lowerBndTable[lowerBnds[0]], lowerBndTable[lowerBnds[1]], targetCrv, skn)
    bindSpliceBetweenJoints(lowerBnds[1], lowerBnds[2], drvCrv, lowerBndTable[lowerBnds[1]], lowerBndTable[lowerBnds[2]], targetCrv, skn)
    bindSpliceBetweenJoints(lowerBnds[2], lowerBnds[3], drvCrv, lowerBndTable[lowerBnds[2]], lowerBndTable[lowerBnds[3]], targetCrv, skn)
    bindSpliceBetweenJoints(lowerBnds[3], lowerBnds[4], drvCrv, lowerBndTable[lowerBnds[3]], lowerBndTable[lowerBnds[4]], targetCrv, skn)
    
    pm.delete(targetCrv)

def setEyelidControlsWeights(prefix):
    # define all data - hard coded
    upperBnds = [nt.Joint(prefix+'_eyelid_inner_bnd'),
                 nt.Joint(prefix+'_eyelid_inner_upper_bnd'),
                 nt.Joint(prefix+'_eyelid_upper_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_upper_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_bnd')]
    lowerBnds = [nt.Joint(prefix+'_eyelid_inner_bnd'),
                 nt.Joint(prefix+'_eyelid_inner_lower_bnd'),
                 nt.Joint(prefix+'_eyelid_lower_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_lower_bnd'),
                 nt.Joint(prefix+'_eyelid_outer_bnd')]
    upperCtls = [pm.PyNode(node.name().replace('_bnd', '_ctrl')) for node in upperBnds]
    lowerCtls = [pm.PyNode(node.name().replace('_bnd', '_ctrl')) for node in lowerBnds]
    drvCrv = pm.PyNode(prefix+'_eye_aimAt_crv_0')
    
    targetInPos = upperBnds[0].getTranslation(space='world')
    targetOutPos = upperBnds[-1].getTranslation(space='world')
    targetCrv = pm.curve(ep=(targetInPos, targetOutPos), d=1, n='target_crv')
    
    # weight ctls
    # get Y-height from curve
    upperHeight = lcrv.calcHeightFromCurve(upperBnds[2], targetCrv)
    upperInnerHeight = lcrv.calcHeightFromCurve(upperBnds[1], targetCrv)
    upperOuterHeight = lcrv.calcHeightFromCurve(upperBnds[3], targetCrv)
    upperInnerWeight = upperInnerHeight / upperHeight
    upperOuterWeight = upperOuterHeight / upperHeight
    channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    upperPriCtl = upperCtls[2].name().replace('_ctrl', '_pri_ctrl')
    [upperBnds[1].attr(upperPriCtl+'_weight_'+channel).set(upperInnerWeight) for channel in channels]
    [upperBnds[3].attr(upperPriCtl+'_weight_'+channel).set(upperOuterWeight) for channel in channels]
    
    lowerHeight = lcrv.calcHeightFromCurve(lowerBnds[2], targetCrv)
    lowerInnerHeight = lcrv.calcHeightFromCurve(lowerBnds[1], targetCrv)
    lowerOuterHeight = lcrv.calcHeightFromCurve(lowerBnds[3], targetCrv)
    lowerInnerWeight = lowerInnerHeight / lowerHeight
    lowerOuterWeight = lowerOuterHeight / lowerHeight
    channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    lowerPriCtl = lowerCtls[2].name().replace('_ctrl', '_pri_ctrl')
    [lowerBnds[1].attr(lowerPriCtl+'_weight_'+channel).set(lowerInnerWeight) for channel in channels]
    [lowerBnds[3].attr(lowerPriCtl+'_weight_'+channel).set(lowerOuterWeight) for channel in channels]
    
    # cleanup
    pm.delete(targetCrv)