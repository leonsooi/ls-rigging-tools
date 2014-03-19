'''
Created on Dec 21, 2013

@author: Leon
'''

import maya.cmds as mc

def getWindowPanels():
    windows = mc.lsUI(wnd=True)
    return windows


