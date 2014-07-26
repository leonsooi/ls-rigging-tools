'''
Created on Jul 22, 2014

@author: Leon
'''
import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

def fingerCameraSetup():
    '''
    select startVert, endVert
    create camera on startVert, aims towards endVert
    offset for clipping plane
    '''
    # get data
    offset = 0.2
    startVert, endVert = pm.ls(os=True)[:2]
    
    # get points
    startPt = startVert.getPosition()
    endPt = endVert.getPosition()
    vec = startPt - endPt
    
    # calc points
    camPos = endPt + vec * (1 + offset)
    aimPos = startPt - vec * (1 + offset)
    
    # create camera
    mel.CreateCameraAim()
    aim, cam = pm.ls(os=True)[:2]
    cam.setTranslation(camPos)
    aim.setTranslation(aimPos)
    
    # camera settings
    cam.setOrtho(True)
    length = vec.length()
    cam.setNearClipPlane(0)
    cam.setFarClipPlane(length * (1+offset))
