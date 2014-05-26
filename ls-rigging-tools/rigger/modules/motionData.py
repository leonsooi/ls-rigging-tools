'''
Created on Dec 18, 2013

@author: Leon

Tools to manipulate AFS motion data
'''

import pymel.core as pm
import pymel.core.nodetypes as nt

'''
#===============================================================================
# FAT integration
#===============================================================================
# FAT integration test - delete inbetweens
md.clearControlInbetweens(pm.PyNode('JawO_CAU2627'), (1, 99))
md.clearControlInbetweens(pm.PyNode('OSmil_CAU1225'), (1, 99))
md.clearControlInbetweens(pm.PyNode('L_OSmil_LAU1225'), (1, 99))
md.clearControlInbetweens(pm.PyNode('R_OSmil_RAU1225'), (1, 99))

# FAT integration test - remap inbetweens
md.linearizeData(pm.PyNode('JawO_CAU2627.tx'), pm.PyNode('Marker_LLLP'), 0, 100, 0.001)
md.linearizeData(pm.PyNode('OSmil_CAU1225.tx'), pm.PyNode('Marker_LOLP'), 0, 100, 0.001)
'''

#===============================================================================
# Map FAT FeaturePoints to to FRS bnds 
#===============================================================================
def mapFeaturePtsToBnds():
    # TRANSFER FEATURE PT POSITIONS relative to bnds
    bndGrp = pm.PyNode('CT_bnd_grp')
    allBnds = bndGrp.getChildren() # home level
    allBnds = [hm.getChildren()[0] for hm in allBnds] # priDrv level
    allBnds = [pri.getChildren()[0] for pri in allBnds] # secDrv level
    allBnds = [sec.getChildren()[0] for sec in allBnds] # bnd level
    
    markerGrp = pm.PyNode('Marker')
    allMarkerGrps = markerGrp.getChildren()
    
    markerToBndTable = {}
    
    for eachMarker in allMarkerGrps:
        markerPos = eachMarker.getRotatePivot(space='world')
        closestBnd = min(allBnds, key=lambda bnd: (bnd.getTranslation(space='world') - markerPos).length())
        markerToBndTable[eachMarker] = closestBnd
        
    markerToBndTable = {nt.Transform(u'MarkerGroup_CHIN'): nt.Joint(u'CT_mid_chin_bnd'),
                         nt.Transform(u'MarkerGroup_LBCH'): nt.Joint(u'LT_low_crease_bnd'),
                         nt.Transform(u'MarkerGroup_LBLP'): nt.Joint(u'LT_lower_pinch_lip_bnd'),
                         nt.Transform(u'MarkerGroup_LCHIN'): nt.Joint(u'LT_mid_chin_bnd'),
                         nt.Transform(u'MarkerGroup_LCHN'): nt.Joint(u'LT_chin_bnd'),
                         nt.Transform(u'MarkerGroup_LIBR'): nt.Joint(u'LT_in_brow_bnd'),
                         nt.Transform(u'MarkerGroup_LICH'): nt.Joint(u'LT_low_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_LIEY'): nt.Joint(u'LT_squint_bnd'),
                         nt.Transform(u'MarkerGroup_LLACH'): nt.Joint(u'LT_eyelid_lower_bnd'),
                         nt.Transform(u'MarkerGroup_LLID'): nt.Joint(u'LT_eyelid_upper_bnd'),
                         nt.Transform(u'MarkerGroup_LLLP'): nt.Joint(u'LT_lower_sneer_lip_bnd'),
                         nt.Transform(u'MarkerGroup_LMBR'): nt.Joint(u'LT_mid_brow_bnd'),
                         nt.Transform(u'MarkerGroup_LMCH'): nt.Joint(u'LT_low_jaw_bnd'),
                         nt.Transform(u'MarkerGroup_LMEY'): nt.Joint(u'LT_up_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_LMLP'): nt.Joint(u'LT_upper_sneer_lip_bnd'),
                         nt.Transform(u'MarkerGroup_LMOU'): nt.Joint(u'LT_philtrum_bnd'),
                         nt.Transform(u'MarkerGroup_LNOSE'): nt.Joint(u'LT_mid_crease_bnd'),
                         nt.Transform(u'MarkerGroup_LOBR'): nt.Joint(u'LT_temple_bnd'),
                         nt.Transform(u'MarkerGroup_LOCH'): nt.Joint(u'LT_out_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_LOEY'): nt.Joint(u'LT_in_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_LOLP'): nt.Joint(u'LT_corner_lip_bnd'),
                         nt.Transform(u'MarkerGroup_LTCH'): nt.Joint(u'LT_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_LTEMP'): nt.Joint(u'LT_low_temple_bnd'),
                         nt.Transform(u'MarkerGroup_LTFH'): nt.Joint(u'LT_out_low_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_LTFH1'): nt.Joint(u'LT_in_low_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_LTJA'): nt.Joint(u'LT_up_jaw_bnd'),
                         nt.Transform(u'MarkerGroup_LTLP'): nt.Joint(u'LT_upper_pinch_lip_bnd'),
                         nt.Transform(u'MarkerGroup_LUBR'): nt.Joint(u'LT_out_brow_bnd'),
                         nt.Transform(u'MarkerGroup_LUFH'): nt.Joint(u'LT_out_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_LUFH1'): nt.Joint(u'LT_in_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_MNOS'): nt.Joint(u'CT_noseTip_bnd'),
                         nt.Transform(u'MarkerGroup_RBCH'): nt.Joint(u'RT_low_crease_bnd'),
                         nt.Transform(u'MarkerGroup_RBLP'): nt.Joint(u'RT_lower_pinch_lip_bnd'),
                         nt.Transform(u'MarkerGroup_RCHIN'): nt.Joint(u'RT_mid_chin_bnd'),
                         nt.Transform(u'MarkerGroup_RCHN'): nt.Joint(u'RT_chin_bnd'),
                         nt.Transform(u'MarkerGroup_RIBR'): nt.Joint(u'RT_in_brow_bnd'),
                         nt.Transform(u'MarkerGroup_RICH'): nt.Joint(u'RT_low_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_RIEY'): nt.Joint(u'RT_squint_bnd'),
                         nt.Transform(u'MarkerGroup_RLACH'): nt.Joint(u'RT_eyelid_lower_bnd'),
                         nt.Transform(u'MarkerGroup_RLID'): nt.Joint(u'RT_eyelid_upper_bnd'),
                         nt.Transform(u'MarkerGroup_RLLP'): nt.Joint(u'RT_lower_sneer_lip_bnd'),
                         nt.Transform(u'MarkerGroup_RMBR'): nt.Joint(u'RT_mid_brow_bnd'),
                         nt.Transform(u'MarkerGroup_RMCH'): nt.Joint(u'RT_low_jaw_bnd'),
                         nt.Transform(u'MarkerGroup_RMEY'): nt.Joint(u'RT_up_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_RMLP'): nt.Joint(u'RT_upper_sneer_lip_bnd'),
                         nt.Transform(u'MarkerGroup_RMOU'): nt.Joint(u'RT_philtrum_bnd'),
                         nt.Transform(u'MarkerGroup_RNOSE'): nt.Joint(u'RT_mid_crease_bnd'),
                         nt.Transform(u'MarkerGroup_ROBR'): nt.Joint(u'RT_temple_bnd'),
                         nt.Transform(u'MarkerGroup_ROCH'): nt.Joint(u'RT_out_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_ROEY'): nt.Joint(u'RT_in_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_ROLP'): nt.Joint(u'RT_corner_lip_bnd'),
                         nt.Transform(u'MarkerGroup_RTCH'): nt.Joint(u'RT_cheek_bnd'),
                         nt.Transform(u'MarkerGroup_RTEMP'): nt.Joint(u'RT_low_temple_bnd'),
                         nt.Transform(u'MarkerGroup_RTFH'): nt.Joint(u'RT_out_low_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_RTFH1'): nt.Joint(u'RT_in_low_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_RTJA'): nt.Joint(u'RT_up_jaw_bnd'),
                         nt.Transform(u'MarkerGroup_RTLP'): nt.Joint(u'RT_upper_pinch_lip_bnd'),
                         nt.Transform(u'MarkerGroup_RUBR'): nt.Joint(u'RT_out_brow_bnd'),
                         nt.Transform(u'MarkerGroup_RUFH'): nt.Joint(u'RT_out_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_RUFH1'): nt.Joint(u'RT_in_forehead_bnd'),
                         nt.Transform(u'MarkerGroup_TNOS'): nt.Joint(u'CT_brow_bnd'),
                         nt.Transform(u'MarkerGroup_ULLIP'): nt.Joint(u'LT_sneer_bnd'),
                         nt.Transform(u'MarkerGroup_ULLIP1'): nt.Joint(u'LT_in_philtrum_bnd'),
                         nt.Transform(u'MarkerGroup_URLIP'): nt.Joint(u'RT_sneer_bnd'),
                         nt.Transform(u'MarkerGroup_URLIP1'): nt.Joint(u'RT_in_philtrum_bnd')}
    
    # set global positioning first (for scale)
    # place markers at respective bnds
    for eachMarker, eachBnd in markerToBndTable.items():
        bndPosition = eachBnd.getTranslation(space='world')
        newPosition = bndPosition - eachMarker.getRotatePivot(space='world')
        eachMarker.setTranslation(newPosition, space='world')
        pm.makeIdentity(eachMarker, t=True, a=True)
 
#===============================================================================
# Map FRS controls to FeaturePoints
#===============================================================================
def mapControlsToFeaturePts():
    ctlGrp = pm.PyNode('face_ctrls_grp')
    allCtls = [ctl.getChildren()[0] for ctl in ctlGrp.getChildren()] # group level
    allCtls = [grp.getChildren()[0] for grp in allCtls]
    
    priCtlGrp = pm.PyNode('CT_face_primary_ctls_grp')
    allPriCtls = [ctl.getChildren()[0] for ctl in priCtlGrp.getChildren()] # group level
    allPriCtls = [grp.getChildren()[0] for grp in allPriCtls]
    
    ctlToTargetTable = {}
    
    for eachCtl in allCtls:
        cons = eachCtl.getChildren(type='constraint')
        if cons:
            targets = cons[0].getTargetList()
            ctlToTargetTable[eachCtl] = targets
    
    ctlToTargetTable = {nt.Transform(u'CT_brow_ctrl'): [nt.Transform(u'Offset_TNOS')],
                         nt.Transform(u'CT_chin_ctrl'): [nt.Transform(u'Marker_RCHN'),
                                                         nt.Transform(u'Marker_LCHN')],
                         nt.Transform(u'CT_lower_lip_ctrl'): [nt.Transform(u'Offset_RLLP'),
                                                              nt.Transform(u'Offset_LLLP')],
                         nt.Transform(u'CT_mid_chin_ctrl'): [nt.Transform(u'Offset_CHIN')],
                         nt.Transform(u'CT_noseTip_pri_ctrl'): [nt.Transform(u'Offset_MNOS')],
                         nt.Transform(u'CT_upper_lip_ctrl'): [nt.Transform(u'Offset_RMLP'),
                                                              nt.Transform(u'Offset_LMLP')],
                         nt.Transform(u'LT_cheek_pri_ctrl'): [nt.Transform(u'Offset_LTCH')],
                         nt.Transform(u'LT_chin_ctrl'): [nt.Transform(u'Offset_LCHN')],
                         nt.Transform(u'LT_corner_lip_pri_ctrl'): [nt.Transform(u'Offset_LOLP')],
                         nt.Transform(u'LT_eyelid_lower_pri_ctrl'): [nt.Transform(u'Offset_LLACH')],
                         nt.Transform(u'LT_eyelid_upper_pri_ctrl'): [nt.Transform(u'Offset_LLID')],
                         nt.Transform(u'LT_in_brow_ctrl'): [nt.Transform(u'Offset_LIBR')],
                         nt.Transform(u'LT_in_cheek_ctrl'): [nt.Transform(u'Offset_LOEY')],
                         nt.Transform(u'LT_in_forehead_ctrl'): [nt.Transform(u'Offset_LUFH1')],
                         nt.Transform(u'LT_in_low_forehead_ctrl'): [nt.Transform(u'Offset_LTFH1')],
                         nt.Transform(u'LT_in_philtrum_ctrl'): [nt.Transform(u'Offset_ULLIP1')],
                         nt.Transform(u'LT_low_cheek_ctrl'): [nt.Transform(u'Offset_LICH')],
                         nt.Transform(u'LT_low_crease_ctrl'): [nt.Transform(u'Offset_LBCH')],
                         nt.Transform(u'LT_low_jaw_ctrl'): [nt.Transform(u'Offset_LMCH')],
                         nt.Transform(u'LT_low_temple_ctrl'): [nt.Transform(u'Offset_LTEMP')],
                         nt.Transform(u'LT_lower_pinch_lip_ctrl'): [nt.Transform(u'Offset_LBLP'), nt.Transform(u'Offset_LOLP')],
                         nt.Transform(u'LT_lower_sneer_lip_ctrl'): [nt.Transform(u'Offset_LBLP')],
                         nt.Transform(u'LT_lower_side_lip_ctrl'): [nt.Transform(u'Offset_LLLP')],
                         nt.Transform(u'LT_mid_brow_pri_ctrl'): [nt.Transform(u'Offset_LMBR')],
                         nt.Transform(u'LT_mid_chin_ctrl'): [nt.Transform(u'Offset_LCHIN')],
                         nt.Transform(u'LT_mid_crease_ctrl'): [nt.Transform(u'Offset_LNOSE')],
                         nt.Transform(u'LT_out_brow_ctrl'): [nt.Transform(u'Offset_LUBR')],
                         nt.Transform(u'LT_out_cheek_ctrl'): [nt.Transform(u'Offset_LOCH')],
                         nt.Transform(u'LT_out_forehead_ctrl'): [nt.Transform(u'Offset_LUFH')],
                         nt.Transform(u'LT_out_low_forehead_ctrl'): [nt.Transform(u'Offset_LTFH')],
                         nt.Transform(u'LT_philtrum_ctrl'): [nt.Transform(u'Offset_LMOU')],
                         nt.Transform(u'LT_sneer_ctrl'): [nt.Transform(u'Offset_ULLIP')],
                         nt.Transform(u'LT_squint_ctrl'): [nt.Transform(u'Offset_LIEY')],
                         nt.Transform(u'LT_temple_ctrl'): [nt.Transform(u'Offset_LOBR')],
                         nt.Transform(u'LT_up_cheek_ctrl'): [nt.Transform(u'Offset_LMEY')],
                         nt.Transform(u'LT_up_crease_ctrl'): [nt.Transform(u'Offset_LOEY'),
                                                              nt.Transform(u'Offset_LMEY'),
                                                              nt.Transform(u'Offset_LNOSE'),
                                                              nt.Transform(u'Offset_LMOU')],
                         nt.Transform(u'LT_up_jaw_ctrl'): [nt.Transform(u'Offset_LTJA')],
                         nt.Transform(u'LT_upper_pinch_lip_ctrl'): [nt.Transform(u'Offset_LTLP'), nt.Transform(u'Offset_LOLP')],
                         nt.Transform(u'LT_upper_sneer_lip_ctrl'): [nt.Transform(u'Offset_LTLP')],
                         nt.Transform(u'LT_upper_side_lip_ctrl'): [nt.Transform(u'Offset_LMLP')],
                         nt.Transform(u'RT_cheek_pri_ctrl'): [nt.Transform(u'Offset_RTCH')],
                         nt.Transform(u'RT_chin_ctrl'): [nt.Transform(u'Offset_RCHN')],
                         nt.Transform(u'RT_corner_lip_pri_ctrl'): [nt.Transform(u'Offset_ROLP')],
                         nt.Transform(u'RT_eyelid_lower_pri_ctrl'): [nt.Transform(u'Offset_RLACH')],
                         nt.Transform(u'RT_eyelid_upper_pri_ctrl'): [nt.Transform(u'Offset_RLID')],
                         nt.Transform(u'RT_in_brow_ctrl'): [nt.Transform(u'Offset_RIBR')],
                         nt.Transform(u'RT_in_cheek_ctrl'): [nt.Transform(u'Offset_ROEY')],
                         nt.Transform(u'RT_in_forehead_ctrl'): [nt.Transform(u'Offset_RUFH1')],
                         nt.Transform(u'RT_in_low_forehead_ctrl'): [nt.Transform(u'Offset_RTFH1')],
                         nt.Transform(u'RT_in_philtrum_ctrl'): [nt.Transform(u'Offset_URLIP1')],
                         nt.Transform(u'RT_low_cheek_ctrl'): [nt.Transform(u'Offset_RICH')],
                         nt.Transform(u'RT_low_crease_ctrl'): [nt.Transform(u'Offset_RBCH')],
                         nt.Transform(u'RT_low_jaw_ctrl'): [nt.Transform(u'Offset_RMCH')],
                         nt.Transform(u'RT_low_temple_ctrl'): [nt.Transform(u'Offset_RTEMP')],
                         nt.Transform(u'RT_lower_pinch_lip_ctrl'): [nt.Transform(u'Offset_RBLP'), nt.Transform(u'Offset_ROLP')],
                         nt.Transform(u'RT_lower_sneer_lip_ctrl'): [nt.Transform(u'Offset_RBLP')],
                         nt.Transform(u'RT_lower_side_lip_ctrl'): [nt.Transform(u'Offset_RLLP')],
                         nt.Transform(u'RT_mid_brow_pri_ctrl'): [nt.Transform(u'Offset_RMBR')],
                         nt.Transform(u'RT_mid_chin_ctrl'): [nt.Transform(u'Offset_RCHIN')],
                         nt.Transform(u'RT_mid_crease_ctrl'): [nt.Transform(u'Offset_RNOSE')],
                         nt.Transform(u'RT_out_brow_ctrl'): [nt.Transform(u'Offset_RUBR')],
                         nt.Transform(u'RT_out_cheek_ctrl'): [nt.Transform(u'Offset_ROCH')],
                         nt.Transform(u'RT_out_forehead_ctrl'): [nt.Transform(u'Offset_RUFH')],
                         nt.Transform(u'RT_out_low_forehead_ctrl'): [nt.Transform(u'Offset_RTFH')],
                         nt.Transform(u'RT_philtrum_ctrl'): [nt.Transform(u'Offset_RMOU')],
                         nt.Transform(u'RT_sneer_ctrl'): [nt.Transform(u'Offset_URLIP')],
                         nt.Transform(u'RT_squint_ctrl'): [nt.Transform(u'Offset_RIEY')],
                         nt.Transform(u'RT_temple_ctrl'): [nt.Transform(u'Offset_ROBR')],
                         nt.Transform(u'RT_up_cheek_ctrl'): [nt.Transform(u'Offset_RMEY')],
                         nt.Transform(u'RT_up_crease_ctrl'): [nt.Transform(u'Offset_ROEY'),
                                                              nt.Transform(u'Offset_RMEY'),
                                                              nt.Transform(u'Offset_RNOSE'),
                                                              nt.Transform(u'Offset_RMOU')],
                         nt.Transform(u'RT_up_jaw_ctrl'): [nt.Transform(u'Offset_RTJA')],
                         nt.Transform(u'RT_upper_pinch_lip_ctrl'): [nt.Transform(u'Offset_RTLP'), nt.Transform(u'Offset_ROLP')],
                         nt.Transform(u'RT_upper_sneer_lip_ctrl'): [nt.Transform(u'Offset_RTLP')],
                         nt.Transform(u'RT_upper_side_lip_ctrl'): [nt.Transform(u'Offset_RMLP')]
                         }
    
    for eachCtl, targets in ctlToTargetTable.items():
        pm.parentConstraint(targets, eachCtl, mo=True)

#===============================================================================
# TRACK LOCATOR MOTION
#===============================================================================

def trackLocator():
    '''
    
    '''

#===============================================================================
# DELETE INBETWEENS TOOLS
#===============================================================================

def clearControlInbetweens(ctl, deleteRange):
    '''
    ctl = pm.PyNode('JawO_CAU2627')
    deleteRange = (1, 99)
    '''
    allOutputs = ctl.outputs()
    # filter outputs so we only use animCurve nodes
    allAnimOutputs = [output for output in allOutputs if 'animCurve' in output.nodeType(inherited=True)]
    for eachAnimCurve in allAnimOutputs:
        pm.cutKey(eachAnimCurve, float=deleteRange)

def deleteInbetweenRanges(animCurve, deleteRanges):
    '''
    animCurve = pm.PyNode(animCurve) : animCurve to operate on
    deleteRanges = (1,9), (-9,-1) : list of tuples
    '''
    for eachRange in deleteRanges:
        pm.cutKey(animCurve, time=eachRange)

#===============================================================================
# LINEARIZE TOOLS
#===============================================================================

def linearizeData(driver, driven, startVal, endVal, step):
    '''
    '''
    displacements = getCurveDisplacement(driver, driven, startVal, endVal, step)
    
    finalDisp = displacements[-1][1]
    
    remapValToDisp = remapValuesToDisplacements(startVal, endVal, finalDisp)
    
    remapOldValToNewVal = remapOldValuesToNewValues(displacements, remapValToDisp)
    
    timeWarpNd = createAnimCurveUU(startVal, endVal, remapOldValToNewVal, driver)

def getCurveDisplacement(driver, driven, startVal, endVal, step):
    '''
    returns displacement at each input value (from starting position) in a list of tuples
    driver (PyNode Attr) - driving attribute e.g. ctl.tx
    driven (PyNode Transform) - driven transform e.g. locatorN
    startVal (int), endVal (int)
    step (float) - step size - use smaller values (e.g. 0.001) for more accurate results
    '''
    disps = []
    
    val = startVal
    driver.set(val)
    
    prevPos = pm.dt.Point(driven.getTranslation())
    
    totalDisplacement = 0
    
    while val < endVal:
        driver.set(val)
        currPos = pm.dt.Point(driven.getTranslation())
        displacement = (currPos - prevPos).length()
        totalDisplacement += displacement
        prevPos = currPos
        disps.append((val, totalDisplacement))
        val += step
        
    return disps

def createAnimCurveUU(startVal, endVal, remapOldValToNewVal, driver):
    '''
    '''
    animCurveNd = pm.createNode('animCurveUU', name=driver.replace('.','_')+'_timewarp')
    
    pm.setKeyframe(animCurveNd, f=startVal, v=startVal)
    
    for oldVal, newVal in remapOldValToNewVal:
        pm.setKeyframe(animCurveNd, f=oldVal, v=newVal)
        
    pm.setKeyframe(animCurveNd, f=endVal, v=endVal)
    
    # reroute connections
    outgoing = driver.outputs(p=True)
    driver >> animCurveNd.input
    for eachCon in outgoing:
        animCurveNd.output >> eachCon
        
    return animCurveNd
    

def createTimeWarp(startVal, endVal, remapOldValToNewVal, driver):
    '''
    DEPRECATED - USE createAnimCurveUU instead
    Create a timeWarp node that maps oldVals to newVals, from startVal to endVal
    Also inserts the node after driver attribute,
    and reroutes all its outgoing connections
    '''
    timewarpNd = pm.createNode('timeWarp')
    
    origVals = [oldVal for oldVal, newVal in remapOldValToNewVal]
    endVals = [newVal for oldVal, newVal in remapOldValToNewVal]
    origVals += startVal, endVal
    endVals += startVal, endVal
    
    # to set doubleArrays, we need length int at the beginning
    origVals.insert(0, len(origVals))
    endVals.insert(0, len(endVals))
    
    # for some reason, endFrames and origFrames are reversed
    timewarpNd.origFrames.set(endVals, type='doubleArray')
    timewarpNd.endFrames.set(origVals, type='doubleArray')
    
    # reroute connections
    outgoing = driver.outputs(p=True)
    driver >> timewarpNd.input
    for eachCon in outgoing:
        timewarpNd.output >> eachCon
        
    return timewarpNd

def remapOldValuesToNewValues(displacements, remapValToDisp):
    '''
    '''
    remapOldValToNewVal = []
    # remap old value to new value
    for oldVal, oldDisp in remapValToDisp:
        dispIndex = 0
        
        for newVal, newDisp in displacements[dispIndex:]:
            if newDisp > oldDisp:
                # matched (not exactly... but slightly over)
                remapOldValToNewVal.append((oldVal, newVal))
                dispIndex = int(newVal)
                break
            
    return remapOldValToNewVal

def remapValuesToDisplacements(startVal, endVal, finalDisp):
    '''
    '''
    remapValToDisp = []
    # skip first and last values, 
    # since 0 maps to 0,
    # and 100 maps to 100 (assuming startVal=0, endVal=100)
    
    for val in range(startVal+1, endVal):
        remapValToDisp.append((val, float(val)/endVal*finalDisp))
        
    return remapValToDisp

def getCurveVelocity(animCurve, startVal, endVal):
    '''
    DEPRECATED
    returns velocity at each input value in a dictionary
    where velocity = (currPos - prevPos) per unit value (i.e. using backward differences)
    '''
    firstHistory = animCurve.input.inputs(p=True)[0]

    firstHistory // animCurve.input
    
    dispDict = {}
    
    animCurve.input.set(startVal)
    prevDisp = animCurve.output.get()
    
    for val in range(startVal, endVal+1):
        animCurve.input.set(val)
        currDisp = animCurve.output.get()
        diff = currDisp - prevDisp
        prevDisp = currDisp
        dispDict[val] = diff
        
    firstHistory >> animCurve.input
    
    return dispDict


def getTotalDisplacement(velocity):
    '''
    Adds all velocities in the dictionary to get total displacement
    '''
    tDisp = 0.0
    for val, vel in velocity.items():
        tDisp += vel
    return tDisp
    