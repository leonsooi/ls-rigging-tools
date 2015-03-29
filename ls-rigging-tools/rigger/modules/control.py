'''
Created on Oct 11, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

def addControlsAtSelectedXfos():
    '''
    add controls at the same world matrix as selected xfo
    '''
    selXfos = pm.ls(sl=True, type='transform')
    
    for xfo in selXfos:
        pdResult = pm.promptDialog(title='Add Control',
                                   message='Control: '+xfo.nodeName(),
                                   text=xfo.nodeName()+'_ctl',
                                   button=['OK', 'Cancel'])
        if pdResult =='OK':
            ctlName = pm.promptDialog(q=True, text=True)
            ctl = createControl(ctlName)
            mat = xfo.getMatrix(ws=True)
            cth = ctl.homeGroup.inputs()[0]
            cth.setMatrix(mat, ws=True)
            
        

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
    
    # save home as message
    ctl.addAttr('homeGroup', at='message')
    cth.message >> ctl.homeGroup
    
    return ctl
    