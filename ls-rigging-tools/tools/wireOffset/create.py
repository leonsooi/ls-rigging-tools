'''
Create a lsWireOffset node
'''
import maya.cmds as mc
import pymel.core as pm
from maya.mel import eval as meval

import utils.wrappers.abRiggingTools as abRT
import utils.rigging as rt
reload(rt)

def createWireOffsetCtl(nodeName, dfmGeo, attachGeo=None, ctlNum=1, size=1, addGrp=1, form=0):
    '''
    
    attachGeo [string] - plug of mesh to attach controls to 
                        e.g. 'abc_wireOffset_wireDfm.outputGeometry[0]' or 'skinCluster1.outputGeometry[0]' 
    '''
    
    #===========================================================================
    # DRIVER SYSTEM
    #===========================================================================
    # check whether selection is edge or vertex
    firstSel = mc.ls(os=True)[0]
    if '.vtx' in firstSel:
        # vertex
        drvSys, drvLocs = createPtDriverSys(nodeName, attachGeo=attachGeo)
    elif '.e' in firstSel:
        # edge
        print 'form: %s' % form
        drvSys, drvLocs = createCrvDriverSys(nodeName, ctlNum, attachGeo=attachGeo, form=form)
    else:
        # invalid selection
        mc.error('invalid selection: %s' % firstSel)
        return 0
    
    #===========================================================================
    # CONTROL SYSTEM
    #===========================================================================
    ctlSys, ctls = createCtlSys(nodeName, drvLocs)
    
    #===========================================================================
    # DEFORMATION SYSTEM
    #===========================================================================
    dfmSys = createDfmSys(nodeName, drvLocs, ctls, dfmGeo)
    
    #===========================================================================
    # MASTER NODE
    #===========================================================================
    masterGrp = mc.group(em=True, n=nodeName+'_wireOffset_mod')
    mc.parent(ctlSys, dfmSys, drvSys, masterGrp)
    
    # add a unique attribute to find it easily
    mc.addAttr(masterGrp, ln='lsWireOffsetNode', at='bool')
    
    # hide unnecessary attrs
    abRT.hideAttr(masterGrp, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
    
    # add attributes for customization
    mc.addAttr(masterGrp, ln='enabled', at='bool', dv=True, k=True)
    mc.addAttr(masterGrp, ln='ctlVis', at='bool', dv=True, k=True)
    mc.addAttr(masterGrp, ln='envelope', at='double', dv=1, min=0, max=1, k=True)
    mc.addAttr(masterGrp, ln='dropoff', at='double', dv=5, min=0, k=True)
    mc.addAttr(masterGrp, ln='rotation', at='double', dv=0, min=0, max=1, k=True)
    
    mc.connectAttr(masterGrp+'.ctlVis', ctlSys+'.ctlVis', f=True)
    mc.connectAttr(masterGrp+'.envelope', dfmSys+'.envelope', f=True)
    mc.connectAttr(masterGrp+'.dropoff', dfmSys+'.dropoff', f=True)
    mc.connectAttr(masterGrp+'.rotation', dfmSys+'.rotation', f=True)
    
    # "enabled" attribute is more tricky
    # first, we'll hide everything
    mc.connectAttr(masterGrp+'.enabled', masterGrp+'.v', f=True)
    # to speed things up, we'll also disable the drvSys and dfmSys
    mc.connectAttr(masterGrp+'.enabled', drvSys+'.enabled', f=True)
    mc.connectAttr(masterGrp+'.enabled', dfmSys+'.enabled', f=True)
    
    mc.select(masterGrp, r=True)
    
    return masterGrp
    

def createCtlSys(nodeName, drvLocs, size=1, addGrp=1):
    '''
    Adds controls under drvLocs, to be used as offset controls
    size - [float] radius of nurbs sphere control
            if size=1, radius will be 0.2 of distance between first 2 locators
    addGrp - [int] number of offset grps above the control
    Returns ctlSysGrp, and a list of controls
    '''
    # calculate size
    pos1 = pm.dt.Point(mc.xform(drvLocs[0], q=True, ws=True, t=True))
    pos2 = pm.dt.Point(mc.xform(drvLocs[1], q=True, ws=True, t=True))
    vec = pos2 - pos1
    dist = vec.length()
    size = dist * 0.2 * size
    
    # create controls
    ctls = []
    for eachLoc in drvLocs:
        
        grp = eachLoc
        # add offset grps
        for grpId in range(addGrp):
            grp = mc.group(em=True, n=eachLoc.replace('_wireOffset_drvLoc', '_wireOffset_offset%d_grp'%grpId).replace('Orig',''), p=grp)
            mc.xform(grp, os=True, a=True, t=(0,0,0), ro=(0,0,0))
            
        # create control
        ctl = mc.sphere(r=size, n=eachLoc.replace('_wireOffset_drvLoc', '_wireOffset_ctl').replace('Orig',''))[0]
        mc.delete(ctl, ch=True)
        rt.parentSnap(ctl, grp)
        
        # assign color
        # first, break connection to shader
        ctlShape = mc.listRelatives(ctl, c=True, s=True)[0]
        shdConn = mc.listConnections(ctlShape+'.instObjGroups', p=True)[0]
        mc.disconnectAttr(ctlShape+'.instObjGroups', shdConn)
        # assign color override
        mc.setAttr(ctlShape+'.overrideEnabled', 1)
        mc.setAttr(ctlShape+'.overrideColor', 6)
        
        ctls.append(ctl)
    
    ctlSysGrp = mc.group(em=True, n=nodeName+'_wireOffset_ctlSys_grp')
    rt.connectVisibilityToggle(ctls, ctlSysGrp, 'ctlVis', True)
    
    return ctlSysGrp, ctls
        

def createDfmSys(nodeName, drvLocs, ctls, geo):
    '''
    drvLocs are used to drive baseCrv
    ctls are used to drive wireCrv
    wire deforms geo
    
    return dfmSysGrp
    '''
    
    # create baseCrv
    baseCrv = rt.makeCrvThroughObjs(drvLocs, nodeName+'_wireOffset_baseCrv', True, 3)
    
    # create wireCrv
    wireCrv = rt.makeCrvThroughObjs(ctls, nodeName+'_wireOffset_wireCrv', True, 3)
    
    # create wireDfm
    wireDfm, wireCrv = mc.wire(geo, wire=wireCrv, n=nodeName+'_wireOffset_wireDfm', dds=(0,5))
    wireBaseUnwanted = wireCrv+'BaseWire'
    # replace base
    mc.connectAttr(baseCrv+'.worldSpace[0]', wireDfm+'.baseWire[0]', f=True)
    mc.delete(wireBaseUnwanted)
    
    # create dfmSysGrp
    dfmSysGrp = mc.group(baseCrv, wireCrv, n=nodeName+'_wireOffset_dfmSys_grp')
    rt.connectVisibilityToggle(wireCrv, dfmSysGrp, 'wireCrvVis', False)
    rt.connectVisibilityToggle(baseCrv, dfmSysGrp, 'baseCrvVis', False)
    
    mc.addAttr(dfmSysGrp, ln='envelope', at='double', k=True, dv=1)
    mc.addAttr(dfmSysGrp, ln='dropoff', at='double', k=True, dv=5)
    mc.addAttr(dfmSysGrp, ln='rotation', at='double', k=True, dv=0)
    
    mc.connectAttr(dfmSysGrp+'.envelope', wireDfm+'.envelope', f=True)
    mc.connectAttr(dfmSysGrp+'.dropoff', wireDfm+'.dds[0]', f=True)
    mc.connectAttr(dfmSysGrp+'.rotation', wireDfm+'.rotation', f=True)
    
    mc.addAttr(dfmSysGrp, ln='enabled', at='bool', k=True, dv=True)
    rt.connectSDK(dfmSysGrp+'.enabled', wireDfm+'.nodeState', {1:0, 0:2})
    
    return dfmSysGrp
    
    

def createPtDriverSys(nodeName, attachGeo=None):
    '''
    Create driver system based on vertex selection in viewport
    Returns drvSysGrp, and a list of locators that can be used to drive offset controls
    '''
    
    # get vertex selections
    selVerts = mc.ls(os=True, fl=True)

    # create control placement locators on each vert
    drvLocs = []
    origLocs = []
    popcNodes = []
    ctlNum = len(selVerts)
    for ctlId in range(ctlNum):
        loc = mc.spaceLocator(n=nodeName+'_wireOffset_drvLoc%d'%ctlId)[0]
        targetVert = selVerts[ctlId]
        mc.select(targetVert, loc, r=True)
        meval('doCreatePointOnPolyConstraintArgList 2 {   "0" ,"0" ,"0" ,"1" ,"" ,"1" ,"0" ,"0" ,"0" ,"0" };')
        meval('CBdeleteConnection "%s.rx";' % loc)
        meval('CBdeleteConnection "%s.ry";' % loc)
        meval('CBdeleteConnection "%s.rz";' % loc)
        mc.setAttr(loc+'.r', 0,0,0)
        drvLocs.append(loc)
        
        # if attachGeo is defined, use attachGeo to drive pointOnPolyConstraint
        popcNode = mc.listRelatives(loc, c=True, type='pointOnPolyConstraint')[0]
        if attachGeo:
            # make origLoc to preserve position
            origLoc = mc.group(n=loc.replace('_drvLoc', '_drvLocOrig'), em=True)
            rt.parentSnap(origLoc, loc)
            mc.parent(origLoc, w=True)
            
            # swap input mesh for popcNode -> this will move drvLoc
            mc.connectAttr(attachGeo, popcNode+'.target[0].targetMesh', f=True)
            
            # parent origLoc back under driverLoc, and use origLoc as driverLoc instead
            mc.parent(origLoc, loc)
            origLocs.append(origLoc)
            
        popcNodes.append(popcNode)
    
    drvLocGrp = mc.group(drvLocs, n=nodeName+'_wireOffset_drvLocs_grp')
    drvSysGrp = mc.group(drvLocGrp, n=nodeName+'_wireOffset_drvSys_grp')
    rt.connectVisibilityToggle(drvLocs, drvSysGrp, 'drvLocsVis', False)
    
    mc.addAttr(drvSysGrp, ln='enabled', at='bool', k=True, dv=True)
    for eachPopc in popcNodes:
        rt.connectSDK(drvSysGrp+'.enabled', eachPopc+'.nodeState', {1:0, 0:2})
    
    if attachGeo:
        return drvSysGrp, origLocs
    
    return drvSysGrp, drvLocs


def createCrvDriverSys(nodeName, ctlNum, form=0, attachGeo=None):
    '''
    Create driver system based on edge loop selection in viewport
    form - [int] 0 = open, 1 = periodic
    Returns drvSysGrp, and a list of locators that can be used to drive offset controls
    '''
    
    # select edge loop in UI
    drvCrv, p2cNode = mc.polyToCurve(form=form, degree=1, n=nodeName+'_wireOffset_crv')
    p2cNode = mc.rename(p2cNode, nodeName+'_wireOffset_p2c')
    crvSpans = mc.getAttr(drvCrv+'.spans')

    
    # create control placement locators on drvCrv
    drvLocs = []
    for ctlId in range(ctlNum):
        loc = mc.spaceLocator(n=nodeName+'_wireOffset_drvLoc%d'%ctlId)[0]
        param = float(ctlId) / ctlNum * crvSpans
        rt.attachToMotionPath(drvCrv, param, loc, False)
        drvLocs.append(loc)
        
    # if curve is open, we will create an extra ctl, where param = crvSpans 
    if mc.getAttr(drvCrv+'.form') != 2:
        loc = mc.spaceLocator(n=nodeName+'_wireOffset_drvLoc%d'%ctlNum)[0]
        param = crvSpans
        rt.attachToMotionPath(drvCrv, param, loc, False)
        drvLocs.append(loc)
        
    
    drvLocGrp = mc.group(drvLocs, n=nodeName+'_wireOffset_drvLocs_grp')
    drvSysGrp = mc.group(drvCrv, drvLocGrp, n=nodeName+'_wireOffset_drvSys_grp')
    
    rt.connectVisibilityToggle(drvLocs, drvSysGrp, 'drvLocsVis', False)
    rt.connectVisibilityToggle(drvCrv, drvSysGrp, 'drvCrvVis', False)
    
    mc.addAttr(drvSysGrp, ln='enabled', at='bool', k=True, dv=True)
    rt.connectSDK(drvSysGrp+'.enabled', p2cNode+'.nodeState', {1:0, 0:2})
    
        
    # if attachGeo is defined, use attachGeo to drive polyToCurve
    if attachGeo:
        # make an origLoc for each driverLoc to preserve orig positions
        origLocs = []
        for eachLoc in drvLocs:
            origLoc = mc.group(n=eachLoc.replace('_drvLoc', '_drvLocOrig'), em=True)
            rt.parentSnap(origLoc, eachLoc)
            mc.parent(origLoc, w=True)
            origLocs.append(origLoc)
            
        # switch the input mesh for polyToCurve -> this will move drvLocs
        mc.connectAttr(attachGeo, p2cNode+'.inputPolymesh', f=True)
        
        # parent orig loc back under driver loc, preserving transforms
        for drv, orig in zip(drvLocs, origLocs):
            mc.parent(orig, drv)
            
        return drvSysGrp, origLocs
    
    return drvSysGrp, drvLocs