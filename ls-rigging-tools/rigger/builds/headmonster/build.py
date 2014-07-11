'''
Created on Jul 5, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt

import rigger.modules.face as face
# from misc.hacks import priCtlAttrs
from rigger.builds.ori.data import priCtlMappings
reload(face)

import rigger.modules.priCtl as priCtl
reload(priCtl)

import rigger.builds.headmonster.data as data
reload(data)

def build():
    '''
    '''
    mesh = nt.Mesh(u'CT_face_geoShape')   
    placementGrp = nt.Transform(u'CT_placement_grp')
    
    #---------------------------------------------------------------------- bind
    if 'bind' in data.build_actions:
        bindGrp = face.createBndsFromPlacement(placementGrp)
    else:
        bindGrp = nt.Transform(u'CT_bnd_grp')
    
    #--------------------------------------------------------- sec motion system
    if 'sec_motion_system' in data.build_actions:
        face.buildSecondaryControlSystem(placementGrp, bindGrp, mesh)
     
    #------------------------------------------------------------ pri ctl system first
    if 'primary_ctl_system_first' in data.build_actions:
        # run a simple first pass
        # which can be used to block out mappings
        bndsForPriCtls = data.all_bnds_for_priCtls
        priCtl.setupPriCtlFirstPass(bindGrp, bndsForPriCtls)
        priCtl.driveAttachedPriCtlsRun(bindGrp)
            
    #------------------------------------------------------------ pri ctl system second
    if 'primary_ctl_system_second' in data.build_actions:
        if data.priCtlMappings:
            # if priCtlMappings is set up, use the data
            priCtlMappings = data.priCtlMappings
            priCtl.setupPriCtlSecondPass(priCtlMappings)
        else:
            pm.warning('no data for pri ctl system')
            
    #-------------------------------------------------------------- load weights
    if 'load_weights' in data.build_actions:
        priCtlMappings = data.priCtlMappings
        priCtl.setPriCtlFirstPassWeights(priCtlMappings)
            
    #--------------------------------------------------------------------- clean
    if 'clean' in data.build_actions:
        face.cleanFaceRig()


def transferPriCtlWeightsFromOri():
    '''
    '''
    import rigger.builds.ori.data as ori_data
    priCtlMappings = ori_data.priCtlMappings
    
    for pCtl, weightsTable in priCtlMappings.items():
        attrName = pCtl + '_weight_'
        for bndName, weight in weightsTable.items():
            try:
                bnd = pm.PyNode(bndName)
                bnd.attr(attrName).set(weight)
            except pm.MayaNodeError as e:
                pm.warning('Does not exist: ' + bndName)
                
