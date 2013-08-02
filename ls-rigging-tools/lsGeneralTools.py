import maya.cmds as mc

def deleteLockedNodes(nodes):
    '''
    Unlock nodes and delete
    '''
    mc.lockNode(nodes, l=False)
    mc.delete(nodes)