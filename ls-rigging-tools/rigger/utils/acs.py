'''
Created on Aug 8, 2014

@author: Leon
'''
import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

def setDataPointValues(acs, dpId, valsDict, absolute=False):
    '''
    use dictionary to set values
    assume using name for keys
    '''
    outIds = []
    outVals = []
    for outName, outVal in valsDict.items():
        outId = mel.DPK_acs_getOutputOfName(acs, outName)
        outIds.append(outId)
        outVals.append(outVal)
        
    mel.DPK_acs_setDataPointValues(acs, dpId, absolute, outIds, outVals)
    
def setSelectedDataPointValues(acs, valsDict, absolute=False):
    '''
    '''
    dpId = mel.DPK_acs_getDataPoints_selected(False)[0]
    setDataPointValues(acs, dpId, valsDict)
    
def getSelectedDataPointValues(acs, absolute=False, key='name'):
    '''
    only select one data point!
    '''
    dpIds = mel.DPK_acs_getDataPoints_selected(False)
    dpId = dpIds[0]
    retDict = getDataPointValues(acs, dpId, absolute, key)
    if len(dpIds) > 1:
        pm.warning('only first data point returned')
    return retDict
    
def getDataPointValues(acs, dpId, absolute=False, key='name'):
    '''
    return dictionary with output values
    key - 'name' or 'id'
    '''
    retDict = {}
    allOutIds = mel.DPK_acs_getDataPoint_outputs(acs, dpId, absolute)
    allOutVals = mel.DPK_acs_getDataPoint_values(acs, dpId, absolute, allOutIds)
    if key == 'name':
        # swap ids for names
        allOutIds = [mel.DPK_acs_getOutputName(acs, outId)
                     for outId in allOutIds]
    for outId, outVal in zip(allOutIds, allOutVals):
        retDict[outId] = outVal
    return retDict

def mirrorMouthOutputsFromLeftToRight():
    '''
    '''
    acsnode = 'ACSnode2'
    # mirrorMouthSide outputs from left to right
    # first, import the right attrs
    currAttrs = mel.DPK_acs_getAllOutputAttrs(acsnode)
    newAttrs = [attr.replace('LT_','RT_') for attr in currAttrs]
    for attr in newAttrs:
        mel.DPK_acs_importOutput(acsnode, attr)
    # next, get values from left side
    # store in dictionary
    leftDpId = 2
    rightDpId = 1
    leftAttrValsDict = {}
    leftOutsIds = mel.DPK_acs_getDataPoint_outputs(acsnode, leftDpId, False)
    leftVals = mel.DPK_acs_getDataPoint_values(acsnode, leftDpId, False, leftOutsIds)
    for outId, val in zip(leftOutsIds, leftVals):
        outName = mel.DPK_acs_getOutputName(acsnode, outId)
        leftAttrValsDict[outName] = val
    # create dictionary for right side
    rightAttrValsDict = {}
    for outName, val in leftAttrValsDict.items():
        newName = outName.replace('LT_','RT_')
        rightAttrValsDict[newName] = val
    # assign dictionary to output on right side
    outNames = rightAttrValsDict.keys()
    outIds = [mel.DPK_acs_getOutputOfName(acsnode, outName) for outName in outNames]
    outVals = rightAttrValsDict.values()
    mel.DPK_acs_setDataPointValues(acsnode, rightDpId, False, outIds, outVals)

def importOutputAttrOnNodes(acs, nodes, attrName):
    '''
    nodes = pm.ls(sl=True)
    attrName = 'CT__mouthMover_pri_ctrl_weight_tx'
    acs.importOutputAttrOnNodes(acsnode, nodes, attrName)
    '''
    for node in nodes:
        nodeAttr = node+'.'+attrName
        mel.DPK_acs_importOutput(acs, nodeAttr)

def renameInputsByAttrName(acs):
    '''
    import rigger.utils.acs as acs
    reload(acs)
    acs.renameInputsByAttrName('ACSnode1')
    '''
    # get all inputs to acs
    inputsInts = mel.DPK_acs_getAllInputs(acs)
    # get new names by attrName
    newNames = []
    for inputInt in inputsInts:
        inputStr = mel.DPK_acs_getInputAttr(acs, inputInt)
        attr = inputStr.split('.')[1]
        newNames.append(attr)
    # rename
    mel.DPK_acs_renameInputs(acs, inputsInts, newNames)
    
def getInputId(node, data):
    '''
    get inputId from possible data
    data could be the inputName, inputAttr, or inputId
    validate data before return
    '''
    if isinstance(data, (int, long)):
        # this may be an inputId
        # check that inputId is valid
        pass
    
    # todo

def createAttrDataForInput(node, inputName, data):
    '''
    data = [{0: [-1.0, 0, u'linear'], 1: [1.0, 0, u'linear'], 11: [-0.5, 1, u'linear']},
             {4: [-1.0, 0, u'linear'], 7: [1.0, 0, u'linear']}]
    assume input does not have these attrs
    just create the attrs
    (if attrs already exists, use updateAttrDataForInput)
    
    example:
    import rigger.utils.acs as acs    
    reload(acs)
    attrData = acs.getAttrDataFromInput(node, 'lfSmile')
    acs.createAttrDataForInput(node, 'rtSmile', attrData)
    '''
    inputId = mel.DPK_acs_getInputOfName(node, inputName)
    for grpId, posGrpData in enumerate(data):
        for _srcAttrId, attrData in posGrpData.items():
            pos, layer, tt = attrData[:]
            print grpId, pos, layer, tt 
            attrId = mel.DPK_acs_createPosAttr(node, 
                                      inputId,
                                      grpId, 
                                      pos,
                                      tt)
            if layer:
                mel.DPK_acs_setPosAttr_layer(node, attrId, layer)

def mirrorSelectedDataPointGo():
    dpIds = mel.DPK_acs_getDataPoints_selected(False)
    for dpId in dpIds:
        node = mel.DPK_acs_getACSnode()
        mirrorDataPoint(node, dpId)
        mel.DPK_acs_refreshUI()

def mirrorDataPoint(node, dpId):
    outputIds = mel.DPK_acs_getDataPoint_outputs(node, dpId, True)
    outputValues = mel.DPK_acs_getDataPoint_values(node, dpId, True, outputIds)
    posIds = mel.DPK_acs_getDataPoint_posAttrs(node, dpId)
    mirPosIds = [mirrorPosIdByInputName(node, posId) for posId in posIds]
    mirDpId = mel.DPK_acs_createDataPoint(node,
                                                mirPosIds,
                                                False)
    mirOutIds = [mirrorOutIdByName(node, outId)
                      for outId in outputIds]
    mirOutValues = mirrorValuesByOutNames(node, outputIds, 
                                          outputValues)
    mel.DPK_acs_setDataPointValues(node, mirDpId, True, 
                                   mirOutIds, mirOutValues)
    
def mirrorValuesByOutNames(node, outIds, values, mirAttrs=['_tx', '_rz']):
    '''
    '''
    mirValues = []
    for outId, val in zip(outIds, values):
        outName = mel.DPK_acs_getOutputName(node, outId)
        if any(attr in outName for attr in mirAttrs):
            newVal = -val
            mirValues.append(newVal)
        else:
            mirValues.append(val)
    return mirValues
    
def mirrorOutIdByName(node, outId, search='LT', replace='RT'):
    '''
    '''
    outName = mel.DPK_acs_getOutputName(node, outId)
    mirOutName = outName.replace(search, replace)
    mirOutId = mel.DPK_acs_getOutputOfName(node, mirOutName)
    return mirOutId

def mirrorPosIdByInputName(node, posId, search='lf', replace='rt'):
    inputId = mel.DPK_acs_getPosAttr_input(node, posId)
    inputName = mel.DPK_acs_getInputName(node, inputId)
    targetInputName = inputName.replace(search, replace)
    targetInputId = mel.DPK_acs_getInputOfName(node, targetInputName)
    inputPos = mel.DPK_acs_getPosAttr_pos(node, posId)
    inputPosGrp = mel.DPK_acs_getPosAttr_group(node, posId)
    # get targetPos
    targetPosId = mel.DPK_acs_getPosAttr(node, 
                                         targetInputId, 
                                         inputPosGrp, 
                                         inputPos)
    return targetPosId

def getAttrDataFromInput(node, inputName):
    '''
    get data on pos, layer and tangent
    store in data in dictionary per positionGroup
    return list of positionGroups' dictionaries
    '''
    inputId = mel.DPK_acs_getInputOfName(node, inputName)
    grpNum = mel.DPK_acs_getPositionGroups(node, inputId)
    
    srcAttrsData = []
    for grpId in range(grpNum):
        attrIds = mel.DPK_acs_getPosAttrs(node, inputId, grpId)
        attrData = {}
        for attrId in attrIds:
            pos = mel.DPK_acs_getPosAttr_pos(node, attrId)
            layer = mel.DPK_acs_getPosAttr_layer(node, attrId)
            tt = mel.DPK_acs_getPosAttr_tt(node, attrId)
            attrData[attrId] = [pos, layer, tt]
        srcAttrsData.append(attrData)
        
    return srcAttrsData