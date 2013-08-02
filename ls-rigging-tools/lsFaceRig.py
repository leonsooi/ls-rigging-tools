import maya.cmds as mc

#===============================================================================
# EYELIDS
#===============================================================================

# names are currently hard-coded...
# add locators to curve
targetCurve = 'RT_eyeLidsShaper_crv_0'
startParam = 0
endParam = 19

for param in range(startParam, endParam+1):
    loc = mc.spaceLocator(n=targetCurve.replace('_crv_','_loc_').replace('_0','_%d'%param))[0]
    poci = mc.createNode('pointOnCurveInfo', n=targetCurve.replace('_crv_','_poci_').replace('_0','_%d'%param))
    mc.connectAttr(targetCurve+'.worldSpace', poci+'.inputCurve', f=True)
    mc.connectAttr(poci+'.result.position', loc+'.translate', f=True)
    mc.setAttr(poci+'.parameter', param)
    mc.setAttr(loc+'.localScale', 0.02, 0.02, 0.02)
    
# create joints from eyePivot to crvLocs
targetCurve = 'RT_eyeLidsShaper_crv_0'
startParam = 0
endParam = 19
eyePivot = mc.xform('RT_eyeRot_pivot_loc_0', q=1, ws=1, t=1)

jnts = []
for param in range(startParam, endParam+1):
    mc.select(cl=True)
    baseJnt = mc.joint(n=targetCurve.replace('_crv_','_jnt_').replace('_0','_%d'%param), p=eyePivot)
    endPivot = mc.xform(targetCurve.replace('_crv_','_loc_').replace('_0','_%d'%param), q=1, ws=1, t=1)
    endJnt = mc.joint(n=targetCurve.replace('_crv_','_endJnt_').replace('_0','_%d'%param), p=endPivot)
    jnts.append(baseJnt)
    jnts.append(endJnt)

mc.select(jnts)
mc.setAttr('.radius', *[0.1] * len(jnts))

# create ikHandle on crvLocs
selBaseJnts = mc.ls(sl=True)

for eachJnt in selBaseJnts:
    endJnt = eachJnt.replace('_jnt_', '_endJnt_')
    targetLoc = eachJnt.replace('_jnt_', '_loc_')
    ikhandle = mc.ikHandle(n=eachJnt.replace('_jnt_', '_hdl_'), sj=eachJnt, ee=endJnt, solver='ikSCsolver')
    mc.parent(ikhandle[0], targetLoc)
    
