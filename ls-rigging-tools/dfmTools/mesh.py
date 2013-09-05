'''
Created on 29/08/2013

@author: Leon
'''
# standard library imports

# third party imports
import maya.cmds as mc

# local imports
import lsDfmTools as dt
reload(dt)

def copyMeshShape():
    src, dest = mc.ls(os=True)[:2]
    dt.copyMeshShape(src, dest)

