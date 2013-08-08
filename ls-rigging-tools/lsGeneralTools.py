import maya.cmds as mc
import time

def viewVertexOrder():
    selVert = mc.ls(sl=True, fl=True)
    for eachVert in selVert:
        mc.select(eachVert, r=True)
        mc.refresh()
        time.sleep(0.01)


def deleteLockedNodes(nodes):
    '''
    Unlock nodes and delete
    '''
    mc.lockNode(nodes, l=False)
    mc.delete(nodes)