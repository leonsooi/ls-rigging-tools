'''
Created on Jul 5, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt

import rigger.modules.face as face
reload(face)

import rigger.modules.priCtl as priCtl
reload(priCtl)

import rigger.builds.ori.data as data
reload(data)

def build():
    '''
    '''
#     mesh = nt.Mesh(u'CT_face_geoShape')
#      
#     placementGrp = nt.Transform(u'CT_placement_grp')
#     bindGrp = face.createBndsFromPlacement(placementGrp)
#     face.buildSecondaryControlSystem(placementGrp, bindGrp, mesh)
#     
    bindGrp = nt.Transform(u'CT_bnd_grp')
    if data.priCtlMappings:
        # if priCtlMappings is setup, use the data
        priCtlMappings = data.priCtlMappings
        priCtl.setupPriCtlSecondPass(priCtlMappings)
    else:
        # run a simple first pass
        # which can be used to block out mappings
        bndsForPriCtls = data.all_bnds_for_priCtls
        priCtl.setupPriCtlFirstPass(bindGrp, bndsForPriCtls)
    #face.cleanFaceRig()
