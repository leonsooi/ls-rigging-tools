'''
Created on May 20, 2014

@author: Leon
'''
import pymel.core as pm
def publishRigForAnim():
    '''
    '''
    allCtls = pm.PyNode('CT_allControls_msg_grp.message').outputs()
    resetAttrs(allCtls)
    
    allMeshes = pm.ls(type='mesh')
    
    
    allNodes = pm.ls(exactType='transform')
    allNodes = [node for node in allNodes if node not in allCtls]
    allNodes = [node for node in allNodes if node.nodeName() not in ['top', 'side', 'front', 'persp']]
    

    
    lockAttrs(allNodes)
        
def lockAttrs(nodes):
    '''
    '''
    for node in nodes:
        attrs = node.listAttr(k=True)
        attrs = [attr for attr in attrs if len(attr.inputs())==0]
        for attr in attrs:
            attr.set(l=True)

def resetAttrs(ctls):
    for ctl in ctls:
        attrs = ctl.listAttr(k=True)
        attrs = [attr for attr in attrs if attr.isFreeToChange()==0]
        for attr in attrs:
            dv = pm.attributeQuery(attr.attrName(), n=attr.node(), ld=True)[0]
            attr.set(dv)

