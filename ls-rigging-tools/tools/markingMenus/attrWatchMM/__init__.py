import maya.cmds as mc
import pymel.core as pm

import Red9.core.Red9_Meta as r9Meta
import Red9.core.Red9_CoreUtils as r9Core

def deleteHUD():
    r9Meta.monitorHUDManagement('delete')
    
def refreshHUD():
    r9Meta.monitorHUDManagement('refreshHeadsUp')

def addAttrWithPromptDialog():
    try:
        node, attr = getNodeAttrFromPromptDialog()
        addAttrToHUD(node, attr)
    except:
        pass

def removeAttrWithPromptDialog():
    try:
        node, attr = getNodeAttrFromPromptDialog()
        removeAttrFromHUD(node, attr)
    except:
        pass

def getNodeAttrFromPromptDialog():
    """
    Show a prompt dialog where node.attr can be entered.
    To be used with a hotkey or shelf button.
    If a node is selected, nodeName will be added to text.
    """
    selNode = pm.ls(os=True)[0]
    
    pdResult = pm.promptDialog(title='Add Attribute to HUD',
                               message='Attribute: '+selNode.nodeName(),
                               text=selNode.nodeName()+'.',
                               button=['OK', 'Cancel'])
    
    if pdResult =='OK':
        nodeAttr = pm.promptDialog(q=True, text=True)
        node = nodeAttr.split('.')[0]
        attr = '.'.join(nodeAttr.split('.')[1:])
        return node, attr
        
def removeAttrFromHUD(node, attr):
    """
    remove attrs from the MetaHUD
    """
    currentHUDs = r9Meta.getMetaNodes(mTypes=r9Meta.MetaHUDNode,
                                      mAttrs='mNodeID=CBMonitorHUD')
    if currentHUDs:
        metaHUD=currentHUDs[0]
        if attr:
            metaHUD.killHud()
            monitoredAttr='%s_%s' % (r9Core.nodeNameStrip(node), attr)
            print 'removing attr :', attr, monitoredAttr
            try:
                metaHUD.removeMonitoredAttr(monitoredAttr)
            except:
                pass
        metaHUD.refreshHud()
    
def addAttrToHUD(node, attr):
    """
    adds node.attr to the HUD using Red9_Meta.MetaHUDNode
    """
    currentHUDs = r9Meta.getMetaNodes(mTypes=r9Meta.MetaHUDNode,
                                      mAttrs='mNodeID=CBMonitorHUD')
    
    if not currentHUDs:
        metaHUD = r9Meta.MetaHUDNode(name='CBMonitorHUD')
    else:
        metaHUD = currentHUDs[0]
    
    monitoredAttr='%s_%s' % (r9Core.nodeNameStrip(node), attr)
    metaHUD.addMonitoredAttr(monitoredAttr,
                             value=mc.getAttr('%s.%s' % (node, attr)),
                             refresh=False)
    mc.connectAttr('%s.%s' % (node, attr), '%s.%s' % (metaHUD.mNode, monitoredAttr))
    metaHUD.refreshHud()