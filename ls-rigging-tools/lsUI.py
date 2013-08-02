import maya.cmds as mc

#===============================================================================
# get knot data from curve
#===============================================================================

# use a curveInfo node
if not mc.objExists('tempCurveInfo'):
    crvInfoNd = mc.createNode('curveInfo', n='tempCurveInfo')

selCurve = mc.ls(sl=1)[0]
mc.connectAttr('%s.worldSpace'%selCurve, '%s.inputCurve'%crvInfoNd, f=True)
knots = mc.getAttr('%s.knots[*]'%crvInfoNd)

#===============================================================================
# send knot data to curve
#===============================================================================

def rebuildCurveWithKnotData(knots, crvs):
    for crv in crvs:
        cvPositions = mc.getAttr('%s.cv[*]'%crv)
        degree = mc.getAttr('%s.degree'%crv)
        numOfCV = len(cvPositions)
        if numOfCV + degree - 1 == len(knots):
            mc.curve(crv, r=1, os=1, p=cvPositions, k=knots)
        else:
            mc.error('Knot values do not match number of CVs')

rebuildCurveWithKnotData(knots, mc.ls(sl=1))

#===============================================================================
# set limits on transform attrs
#===============================================================================

limitsTbl = {\
            'tx':[-0.5,0.5], \
            'ty':[-1,1], \
            'tz':[-1,1], \
            'rx':[0,0], \
            'ry':[0,0], \
            'rz':[-45,45], \
            }
            
limitsTbl = {'tz':[-1,1]}

def setLimitsOnAttrs(limitsTbl, objs):
    for eachObj in objs:
        for attr, limits in limitsTbl.items():
            kw={}
            kw['e%s'%attr] = (1, 1)
            kw[attr] = limits
            mc.transformLimits(eachObj, **kw)

setLimitsOnAttrs(limitsTbl, mc.ls(sl=1))

#############################################################################

def connectCVToObj(crv, cv, obj):
    objPrefix = '_'.join(obj.split('_')[:2])
    pmm = mc.createNode('pointMatrixMult', n='%sConnectCV_pmm_0'%objPrefix)
    mc.connectAttr('%s.worldMatrix'%obj, '%s.inMatrix'%pmm, f=True)
    mc.connectAttr('%s.output'%pmm, '%s.controlPoints[%d]'%(crv, cv), f=True)


#############################################################################

def mirrorCopyAttr(srcObjs, search, replace, mirrorAttrs, copyAttrs):
    for src in srcObjs:
        dest = src.replace(search, replace)
        for eachAttr in copyAttrs:
            val = mc.getAttr('%s.%s'%(src, eachAttr))
            mc.setAttr('%s.%s'%(dest, eachAttr), val)
        for eachAttr in mirrorAttrs:
            val = mc.getAttr('%s.%s'%(src, eachAttr))
            mc.setAttr('%s.%s'%(dest, eachAttr), -val)
            
mirrorCopyAttr(mc.ls(sl=True), 'L_', 'R_', ['tx', 'sx'], ['ty', 'sy', 'sz'])
mirrorCopyAttr(mc.ls(sl=True), 'L_', 'R_', [], ['sx', 'sy', 'sz'])
mirrorCopyAttr(mc.ls(sl=True), 'lipTop', 'lipBottom', [], ['sx', 'sy', 'sz'])

#############################################################################

# replace names string
def replaceNames(selObjs, search, replace):
    for selId in range(len(selObjs)):
        each = selObjs[selId]
        oldName = each
        newName = mc.rename(each, each.split('|')[-1].replace(search, replace))
        mc.select(newName)
        newLongName = mc.ls(sl=1, l=1)[0]
        selObjs = [each.replace(oldName, newLongName) for each in selObjs]
    mc.select(selObjs)

replaceNames(mc.ls(sl=1, long=1), 'L_', 'R_')

#############################################################################

# add remap node to attribute
def addRemapValueToAttr(attr):
    destPlugs = mc.listConnections(attr, p=1, d=1)
    rmvNode = mc.createNode('remapValue', n=attr.replace('.','_')+'_rmv_0')
    mc.connectAttr(attr, rmvNode+'.inputValue', f=1)
    if destPlugs:
        for eachPlug in destPlugs:
            mc.connectAttr(rmvNode+'.outValue', eachPlug, f=1)
    mc.select(rmvNode)
    mc.setAttr('%s.inputMin'%rmvNode, -1)
    mc.setAttr('%s.inputMax'%rmvNode, 1)
    mc.setAttr('%s.outputMin'%rmvNode, 1)
    mc.setAttr('%s.outputMax'%rmvNode, -1)

# select transforms and run
def doAddRemapValueToAttr(objs, attrs):
    for eachObj in objs:
        for eachAttr in attrs:
            addRemapValueToAttr('%s.%s'%(eachObj, eachAttr))

doAddRemapValueToAttr(mc.ls(sl=1, fl=1), ['tx'])
doAddRemapValueToAttr(mc.ls(sl=1, fl=1), ['rz'])

#############################################################################

# connect blink with clamp
# select top, bottom, topRmv, bottomRmv

def connectBlinkWithClamp():
    topTrans, bottomTrans, rmvNode, bottomRmvNode = mc.ls(os=1)[:4]
    pmaNode = mc.createNode('plusMinusAverage', n=rmvNode+'_pma_0')
    # add the tops
    mc.connectAttr(topTrans+'.ty', pmaNode+'.input2D[0].input2Dx', f=1)
    topParent = mc.listRelatives(topTrans, p=1)[0]
    mc.connectAttr(topParent+'.ty', pmaNode+'.input2D[1].input2Dx', f=1)
    # add the bottoms
    mc.connectAttr(bottomTrans+'.ty', pmaNode+'.input2D[0].input2Dy', f=1)
    bottomParent = mc.listRelatives(bottomTrans, p=1)[0]
    mc.connectAttr(bottomParent+'.ty', pmaNode+'.input2D[1].input2Dy', f=1)
    # clamp
    clpNode = mc.createNode('clamp', n=rmvNode+'_clp_0')
    mc.connectAttr(pmaNode+'.output2Dx', clpNode+'.inputR', f=1)
    mc.connectAttr(pmaNode+'.output2Dy', clpNode+'.inputG', f=1)
    mc.setAttr(clpNode+'.mnr', -1)
    mc.setAttr(clpNode+'.mng', -1)
    mc.setAttr(clpNode+'.mxr', 1)
    mc.setAttr(clpNode+'.mxg', 1)
    # connect to rmv
    mc.connectAttr(clpNode+'.opr', rmvNode+'.inputValue', f=1)
    mc.connectAttr(clpNode+'.opg', bottomRmvNode+'.inputValue', f=1)
    
connectBlinkWithClamp()

###########################
# mirror ctrl transform
# set scaleX, translateX to neg
for eachTransform in mc.ls(sl=1):
    sx = mc.getAttr(eachTransform+'.sx')
    tx = mc.getAttr(eachTransform+'.tx')
    mc.setAttr(eachTransform+'.sx', -sx)
    mc.setAttr(eachTransform+'.tx', -tx)

    
#########################
# Remove double transform from on-mesh controls
selCtls = mc.ls(sl=1)
for eachCtl in selCtls:
    offsetNd = eachCtl.replace('_cluster_controller','_null1')
    mdNd = mc.createNode('multiplyDivide', n=eachCtl.replace('_cluster_controller', '_negate_md'))
    mc.connectAttr(eachCtl+'.t', mdNd+'.input1', f=True)
    mc.setAttr(mdNd+'.input2', -1,-1,-1)
    mc.connectAttr(mdNd+'.output', offsetNd+'.t', f=1)