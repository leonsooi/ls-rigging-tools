'''
Created on Aug 26, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import rigger.ui.faceui as fui
reload(fui)

import data as data
reload(data)

def place():
    '''
    '''
    mel.cgmToolbox()
    placerMappings = data.placerMappings
    baseFilePath = data.baseFilePath
    meshNames = {'face':'CT_face_geo',
                 'leftEye':'LT_eyeball_geo',
                 'rightEye':'RT_eyeball_geo'}
    win = fui.newUI(baseFilePath, placerMappings, meshNames)