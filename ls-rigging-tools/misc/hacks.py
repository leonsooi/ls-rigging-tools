'''
Created on Mar 10, 2014

@author: Leon
'''
import pymel.core as pm

# mirror jnt names
bnds = pm.ls(sl=True)
for each in bnds:
    if 'RT_' in each.nodeName():
        pos = each.getTranslation(space='world') * (-1,1,1)
        print pos
        match = None
        for bnd in bnds:
            p = bnd.getTranslation(space='world')
            distance = (pos - p).length()
            if distance < 0.001:
                match = bnd
        if match:
            each.rename(match.replace('LT_', 'RT_'))
            
# rename parents
bnds = pm.ls(sl=True)
for each in bnds:
    secDrv = each.getParent()
    priDrv = each.getParent(2)
    hm = each.getParent(3)
    secDrv.rename(each.replace('_bnd', '_secDrv_bnd'))
    priDrv.rename(each.replace('_bnd', '_priDrv_bnd'))
    hm.rename(each.replace('_bnd', '_bnd_hm'))
    
# mirror priCtl weights
bnds = pm.ls(sl=True) # select on LT bnds
for eachBnd in bnds:
    rtBnd = pm.PyNode(eachBnd.replace('LT_', 'RT_'))
    allAttrs = eachBnd.listAttr(ud=True)
    priCtlAttrs = [attr for attr in allAttrs if 'pri_ctrl_weight' in attr.name() and not attr.isLocked()]
    priCtlAttrVals = [attr.get() for attr in priCtlAttrs]
    attrNames = [attr.name(False) for attr in priCtlAttrs]
    rtAttrNames = [attr.replace('LT_', 'RT_') for attr in attrNames]
    for eachAttrName, val in zip(rtAttrNames, priCtlAttrVals):
        rtBnd.attr(eachAttrName).set(val)
        
# save priCtl weights
bnds = pm.ls(sl=True)
allWeightDict = {}
for eachBnd in bnds:
    allAttrs = eachBnd.listAttr(ud=True)
    priCtlAttrs = [attr for attr in allAttrs if 'pri_ctrl_weight' in attr.name() and not attr.isLocked()]
    for eachAttr in priCtlAttrs:
        val = eachAttr.get()
        allWeightDict[eachAttr.name()] = val
print allWeightDict