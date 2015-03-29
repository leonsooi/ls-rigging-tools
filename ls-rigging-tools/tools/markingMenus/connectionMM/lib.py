'''
Created on Mar 29, 2015

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

def getRadialPos(posId):
    
    radialPos = {0:'N', 
                 1:'NE', 
                 2:'E',
                 3:'SE',
                 4:'S',
                 5:'SW',
                 6:'W',
                 7:'NW'}
    
    return radialPos.get(posId, None)

class MarkingMenu(object):
    
    def __init__(self, menuItems={}):
        """
        menuItems is a dictionary formatted with
        {posId:('commandLabel', pm.Callback),
         posId:('subMenuLabel', moreMenuItems)}
        """
        self.menuItems = menuItems
        self.popupMenu = []
        
    def addMenuItem(self, posId, label, item):
        """
        item can be either pm.Callback or a menuItems dict
        """
        self.menuItems[posId] = (label, item)
        
    def drawPopup(self):
        """
        """
        self.deletePopup()
        
        with pm.popupMenu(parent='viewPanes', ctl=True, alt=True, button=1, mm=True) as mm:
            for posId, (label, item) in self.menuItems.items():
                print posId
                if posId < 8:
                    pm.menuItem(l=label, rp=getRadialPos(posId))
                else:
                    pm.menuItem(l=label)
                    
        self.popupMenu = mm
        
    def deletePopup(self):
        if self.popupMenu:
            pm.deleteUI(self.popupMenu)
            self.popupMenu = None