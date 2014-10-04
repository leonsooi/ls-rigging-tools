'''
Created on Oct 3, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

import rigger.modules.priCtl as priCtl
reload(priCtl)
import rigger.modules.face as face
reload(face)

import rigger.builds.hat.data as data
reload(data)

mel = pm.language.Mel()
import maya.cmds as mc
import rigger.modules.eye as eye
reload(eye)
import utils.symmetry as sym
import rigger.utils.weights as weights
reload(weights)



def build():
    '''
    '''
    mesh = nt.Mesh(u'CT_hat_simplegeoShape')   
    placementGrp = nt.Transform(u'CT_placement_grp')
    
    #---------------------------------------------------------------------- bind
    if 'bind' in data.build_actions:
        bindGrp = face.createBndsFromPlacement(placementGrp)
        pm.refresh()
    else:
        bindGrp = nt.Transform(u'CT_bnd_grp')
    
    #--------------------------------------------------------- sec motion system
    if 'sec_motion_system' in data.build_actions:
        face.buildSecondaryControlSystem(placementGrp, bindGrp, mesh)
        pm.refresh()
     
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
            priCtl.driveAttachedPriCtlsRun(bindGrp)
            pm.refresh()
        else:
            pm.warning('no data for pri ctl system')
            
    #-------------------------------------------------------------- load weights
    if 'load_weights' in data.build_actions:
        priCtlWeights = data.priCtlWeights
        priCtl.setPriCtlSecondPassWeights(priCtlWeights)
        pm.refresh()
            
    #--------------------------------------------------------------------- clean
    if 'clean' in data.build_actions:
        print 'clean'
        face.cleanFaceRig()
        pm.select(cl=True)
        pm.refresh()