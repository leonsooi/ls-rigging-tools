'''
Created on Dec 18, 2013

@author: Leon

Tools to manipulate AFS motion data
'''

import pymel.core as pm

def linearizeData(driver, driven, startVal, endVal, step):
    '''
    '''
    displacements = getCurveDisplacement(driver, driven, startVal, endVal, step)
    
    finalDisp = displacements[-1][1]
    
    remapValToDisp = remapValuesToDisplacements(startVal, endVal, finalDisp)
    
    remapOldValToNewVal = remapOldValuesToNewValues(displacements, remapValToDisp)
    
    timeWarpNd = createTimeWarp(startVal, endVal, remapOldValToNewVal, driver)

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

def createTimeWarp(startVal, endVal, remapOldValToNewVal, driver):
    '''
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
    