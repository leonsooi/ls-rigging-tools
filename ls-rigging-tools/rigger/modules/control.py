'''
Created on Oct 11, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

def createControl(name, groups=[]):
    '''
    name - name of control
    groups - list of strings - ['_hello', '_up', '_auto']
    hierarchy would be: cth, ctg, groups..., ctl
    '''
    ctl = pm.circle(n=name, normal=(1,0,0), ch=False, sweep=359)[0]
    hierarchyStack = [ctl]
    for grp in groups:
        lastNode = hierarchyStack[-1]
        newNode = pm.group(lastNode, n=ctl+grp)
        newNode.setPivots(pm.dt.Point())
        hierarchyStack.append(newNode)
    ctg = pm.group(hierarchyStack[-1], n=ctl+'_grp')
    ctg.setPivots(pm.dt.Point())
    cth = pm.group(ctg, n=ctl+'_cth')
    cth.setPivots(pm.dt.Point())
    return ctl
    