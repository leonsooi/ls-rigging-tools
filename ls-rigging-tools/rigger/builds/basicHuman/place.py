'''
Created on Aug 26, 2014

@author: Leon
'''
from ngSkinTools.ui.mainwindow import MainWindow

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
    MainWindow.open()
    placerMappings = data.placerMappings
    indMappings = data.independentMappings
    baseFilePath = data.baseFilePath
    meshNames = {'face':'CT_face_geo',
                 'leftEye':'LT_eyeball_geo',
                 'rightEye':'RT_eyeball_geo'}
    win = fui.newUI(baseFilePath, placerMappings, indMappings, meshNames)