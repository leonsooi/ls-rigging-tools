'''
Created on May 12, 2014

@author: Leon

Pivot allows for a bnd to be rotated or scaled from a different pivot point
Pivots behave like pri_ctls, but are represented as locators
'''
import pymel.core as pm

import face

def addPivotToBnd(bnd, name='_Pivot'):
    '''
    '''
    # create loc
    loc = pm.spaceLocator(n=bnd+'_'+name+'_loc')
    loc_grp = pm.group(loc, n=bnd+'_'+name+'_grp')
    loc_hm = pm.group(loc_grp, n=bnd+'_'+name+'_hm')
    
    # size
    radius = bnd.radius.get()
    loc.localScale.set(3*[radius])
    
    bnd | loc_hm
    pm.makeIdentity(loc_hm, t=1, r=1, s=1, a=0)
    loc_hm.setParent(world=True)
    
    bnd.addAttr('pivot_'+name, at='message')
    loc.message >> bnd.attr('pivot_'+name)
    
    return loc

def connectBndToPivot(bnd, pivot):
    '''
    basically the same at face.connectBndToPriCtl
    '''
    face.connectBndToPriCtl(bnd, pivot)