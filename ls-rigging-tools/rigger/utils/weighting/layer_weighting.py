'''
Created on Aug 28, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

def initLayers(bndGrp, mesh):
    '''
    first step in setup
    bind bnds in bndGrp to mesh
    and set up ngSkinLayers
    '''
    
def buildLayer(mll, layerInfo):
    '''
    layerInfo should contain information on how to weight layer
    [layerName, influences, maskIn, maskOut]
    e.g.
    ['Base', [u'CT__base_bnd'], None, None]
    or
    ['Lip', [u'CT_upper_lip_bnd',
            u'CT_lower_lip_bnd',
            u'LT_corner_lip_bnd',
            u'LT_upperPinch_lip_bnd',
            u'LT_lowerPinch_lip_bnd',
            u'LT_upperSneer_lip_bnd',
            u'LT_lowerSneer_lip_bnd',
            u'LT_upperSide_lip_bnd',
            u'LT_lowerSide_lip_bnd'], [u'CT_upper_lip_bnd',
                                    u'CT_lower_lip_bnd',
                                    u'LT_corner_lip_bnd',
                                    u'LT_upperPinch_lip_bnd',
                                    u'LT_lowerPinch_lip_bnd',
                                    u'LT_upperSneer_lip_bnd',
                                    u'LT_lowerSneer_lip_bnd',
                                    u'LT_upperSide_lip_bnd',
                                    u'LT_lowerSide_lip_bnd'], [u'LT_in_philtrum_bnd',
                                                                u'LT__philtrum_bnd',
                                                                u'LT_mid_crease_bnd',
                                                                u'LT_low_crease_bnd',
                                                                u'LT_mid_chin_bnd',
                                                                u'CT_mid_chin_bnd'])
    '''