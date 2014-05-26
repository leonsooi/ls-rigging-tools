'''
Created on May 24, 2014

@author: Leon
'''
import pymel.core as pm

def getPriBndWeightsDict(bndGrp):
    # save priCtl weight attrs to dictionary
    bnds = bndGrp.getChildren(ad=True, type='joint')
    weightsTable = {}
    for eachBnd in bnds:
        weightAttrs = [attr for attr in eachBnd.listAttr(ud=True)
                       if '_pri_ctrl_weight_' in attr.name()]
        if weightAttrs:
            for eachAttr in weightAttrs:
                weightsTable[eachAttr.name()] = eachAttr.get()
    return weightsTable


def setPriBndWeights(bndGrp, weightsTable):
    bnds = bndGrp.getChildren(ad=True, type='joint')
    
    for eachBnd in bnds:
        weightAttrs = [attr for attr in eachBnd.listAttr(ud=True)
                       if '_pri_ctrl_weight_' in attr.name()]
        if weightAttrs:
            for eachAttr in weightAttrs:
                if eachAttr.name() in weightsTable.keys():
                    eachAttr.set(weightsTable[eachAttr.name()])
                    
def mirrorPriBndWeights(bndGrp):
    '''
    '''
    leftBnds = [bnd for bnd in bndGrp.getChildren(ad=True, type='joint')
                if 'LT_' in bnd.name()]
    for leftBnd in leftBnds:
        rightBnd = pm.PyNode(leftBnd.replace('LT_', 'RT_'))
        weightAttrNames = [attr.attrName() for attr in leftBnd.listAttr(ud=True)
                           if '_pri_ctrl_weight_' in attr.name()]
        for attrName in weightAttrNames:
            value = leftBnd.attr(attrName).get()
            targetAttr = rightBnd.attr(attrName.replace('LT_', 'RT_'))
            targetAttr.set(value)
                     
    centerBnds = [bnd for bnd in bndGrp.getChildren(ad=True, type='joint')
                  if 'CT_' in bnd.name()]
    
    for centerBnd in centerBnds:
        leftWeightAttrNames = [attr.attrName() for attr in centerBnd.listAttr(ud=True)
                           if '_pri_ctrl_weight_' in attr.name() 
                           and 'LT_' in attr.name()]
        for attrName in leftWeightAttrNames:
            value = centerBnd.attr(attrName).get()
            targetAttr = centerBnd.attr(attrName.replace('LT_', 'RT_'))
            targetAttr.set(value)
        