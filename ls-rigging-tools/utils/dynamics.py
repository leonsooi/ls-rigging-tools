import maya.cmds as mc
from maya.mel import eval as meval
import utils.rigging as rt

def makeDynamicWire(jnts, geo, name, ctl):
    '''
    '''
    # make curve through joints
    startCrv = rt.makeCrvThroughObjs(jnts, name+'_startCrv', True, 2)
    
    # make curve dynamic
    mc.select(startCrv, r=True)
    meval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"};')
    
    # get a handle on new (badly named) nodes
    hairSys = mc.ls(sl=True)[0]
    foll = mc.listConnections(hairSys+'.outputHair[0]', d=True)[0]
    dynCrv = mc.listConnections(foll+'.outCurve', d=True)[0]
    
    # rename nodes properly
    hairSys = mc.rename(hairSys, name+'_hairSysShape')
    foll = mc.rename(foll, name+'_foll')
    dynCrv = mc.rename(dynCrv, name+'_dynCrv')
    
    # rename group and transform nodes as well
    hairSysTransform = mc.listRelatives(hairSys, p=True)[0]
    hairSysTransform = mc.rename(hairSysTransform, name+'_hairSys')
    
    startGrp = mc.listRelatives(foll, p=True)[0]
    startGrp = mc.rename(startGrp, name+'_hairSysFollicles')
    
    outputGrp = mc.listRelatives(dynCrv, p=True)[0]
    outputGrp = mc.rename(outputGrp, name+'_hairSysOutputCrvs')
    
    # since we now have start curve and end curve, we can make the wire deformer
    wireDfm, wireCrv = mc.wire(geo, wire=dynCrv, n=name+'_dyn_wireDfm', dds=(0,50))
    wireBaseUnwanted = wireCrv+'BaseWire'
    # replace base
    mc.connectAttr(startCrv+'.worldSpace[0]', wireDfm+'.baseWire[0]', f=True)
    mc.delete(wireBaseUnwanted)
    
    # group nodes nicely
    masterGrp = mc.group(hairSysTransform, startGrp, outputGrp, n=name+'_hairSysMaster_grp')
    rt.connectVisibilityToggle([startGrp, outputGrp], masterGrp, 'curvesVis', False)
    rt.connectVisibilityToggle(hairSysTransform, masterGrp, 'hairSysVis', False)
    
    # attributes on ctl
    mc.addAttr(ctl, ln='tDynamics', nn='DYNAMICS', at='enum', en='-----', k=True)
    #mc.setAttr(ctl+'.tDynamics', l=True)
    mc.addAttr(ctl, ln='enabled', at='bool', dv=True, k=True)
    mc.addAttr(ctl, ln='weight', at='double', min=0, max=1, dv=1, k=True)
    
    mc.connectAttr(ctl+'.weight', wireDfm+'.envelope', f=True)
    rt.connectSDK(ctl+'.enabled', hairSys+'.simulationMethod', {0:0, 1:3})
    
    # expose follicle attributes to ctl
    mc.addAttr(ctl, ln='pointLock', at='enum', en='No Attach:Base:Tip:Both Ends', k=True, dv=1)
    mc.connectAttr(ctl+'.pointLock', foll+'.pointLock', f=True)
    
    # expose hairSystem attributes to ctl
    mc.addAttr(ctl, ln='startCurveAttract', at='double', min=0, max=1, dv=0.05, k=True)
    mc.addAttr(ctl, ln='mass', at='double', min=0, dv=1, k=True)
    mc.addAttr(ctl, ln='drag', at='double', min=0, dv=0.05, k=True)
    mc.addAttr(ctl, ln='damp', at='double', min=0, dv=0, k=True)
    
    mc.connectAttr(ctl+'.startCurveAttract', hairSys+'.startCurveAttract', f=True)
    mc.connectAttr(ctl+'.mass', hairSys+'.mass', f=True)
    mc.connectAttr(ctl+'.drag', hairSys+'.drag', f=True)
    mc.connectAttr(ctl+'.damp', hairSys+'.damp', f=True)
    