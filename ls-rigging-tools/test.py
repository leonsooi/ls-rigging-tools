'''
Created on Nov 27, 2013

@author: Leon
'''

if __name__ == '__main__':
    pass

import maya.cmds as mc

mc.xform()

from maya.mel import eval as meval



import pymel.core as pm

test = pm.PyNode('poly1')

import maya.OpenMaya as om

pt = om.MPoint(1,2,3)

