'''
Created on Jun 21, 2014

@author: Leon
'''
import pymel.core as pm

def connectLocRotate():
    '''
    '''
    locGrpNames = ['_back',
                   '_left',
                   '_front',
                   '_right',
                   '_leftBack',
                   '_rightBack',
                   '_rightFront',
                   '_leftFront']
    
    # create one nurb circle for all groups
    circ = pm.createNode('makeNurbCircle', n='CT_jacketLocsAlign_circle')
    circ.normal.set(0,1,0)
    # use the same root ctrl for all groups
    rootCtl = pm.PyNode('Mathilda_root_ctrl')
    
    # create one motionpath for each group
    for grpName in locGrpNames:
        mp = pm.createNode('motionPath', n='CT_jacketLocsAlign'+grpName+'_mp')
        circ.outputCurve >> mp.gp
        # use paramater from lowest npc
        pm.PyNode('torsoReader_3'+grpName+'_npc').parameter >> mp.uValue
        rootCtl.worldMatrix >> mp.worldUpMatrix
        mp.worldUpType.set(2)
        mp.worldUpVector.set(0,1,0)
        mp.frontAxis.set(0)
        mp.upAxis.set(1)
        # connect to all locs in grp
        for locId in range(1,7):
            mp.rotate >> pm.PyNode('torsoReader_%d%s_loc.r' %
                                   (locId, grpName))

def connectJacketLoc(twistCrv, untwistCrv, param, name='', addCrvs=[]):
    '''
    '''
    mp = pm.createNode('motionPath', n=twistCrv+name+'_mp')
    untwistCrv.worldSpace >> mp.geometryPath
    mp.u.set(param)
    
    npc = pm.createNode('nearestPointOnCurve', n=twistCrv+name+'_npc')
    mp.allCoordinates >> npc.inPosition
    twistCrv.worldSpace >> npc.inputCurve
    
    allLocs = []
    loc = pm.spaceLocator(n=twistCrv+name+'_loc')
    npc.position >> loc.translate
    allLocs.append(loc)
    
    for crv in addCrvs:
        pci = pm.createNode('pointOnCurveInfo', n=crv+name+'_pci')
        npc.parameter >> pci.parameter
        crv.worldSpace >> pci.inputCurve
        loc = pm.spaceLocator(n=crv+name+'_loc')
        pci.position >> loc.translate
        allLocs.append(loc)
    
    pm.select(allLocs)