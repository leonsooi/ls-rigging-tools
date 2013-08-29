import maya.cmds as mc
from maya.mel import eval as meval
import lsRigTools as rt

def makeDynamicWire(jnts, mesh, name):
    '''
    '''
    startCrv = rt.makeCrvThroughObjs(jnts, name+'_startCrv', True, 1)
    
    mc.select(startCrv, r=True)
    meval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"};')
    
    hairSys = mc.ls(sl=True)[0]
    foll = mc.listConnections(hairSys+'.outputHair[0]', d=True)[0]
    dynCrv = mc.listConnections(foll+'.outCurve', d=True)[0]
    
    hairSys = mc.rename(hairSys, name+'_hairSys')
    foll = mc.rename(foll, name+'_foll')
    dynCrv = mc.rename(dynCrv, name+'_dynCrv')
    

