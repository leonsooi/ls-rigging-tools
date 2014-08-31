'''
This is a simple script to remove turtle nodes from a scene. 
The "normal" way to remove turtle nodes is to use the 
procedure "ilrClearScene;". Unfortunately, this sometimes 
causes Maya to crash. So here is a brute force solution!

Author: Leon Sooi (www.leonsooi.com)

To use:
Just execute the entire script in your script editor or shelf button

Or:
You can also import and run the nuke function:
import nuke_turtle as nuke_turtle
nuke_turtle.nuke()
'''
import maya.cmds as mc

def nuke():
    ilrNodeTypes = [u'ilrAshikhminShader', 
                    u'ilrBakeLayer', 
                    u'ilrBakeLayerManager', 
                    u'ilrBasicPhotonShader', 
                    u'ilrBssrdfShader', 
                    u'ilrDielectricPhotonShader', 
                    u'ilrDielectricShader', 
                    u'ilrHwBakeVisualizer', 
                    u'ilrLuaNode', 
                    u'ilrNormalMap', 
                    u'ilrOccData', 
                    u'ilrOccSampler', 
                    u'ilrOptionsNode', 
                    u'ilrOrenNayarShader', 
                    u'ilrOutputShaderBackendNode', 
                    u'ilrPhysicPhotonShader', 
                    u'ilrPointCloudShape', 
                    u'ilrPolyColorPerVertex', 
                    u'ilrRaySampler', 
                    u'ilrShadowMask', 
                    u'ilrSurfaceThickness', 
                    u'ilrUIOptionsNode', 
                    u'ilrUVMappingVisualizer']
    nodes = mc.ls(type=ilrNodeTypes)
    if nodes:
        mc.lockNode(nodes, l=False)
        mc.delete(nodes)
        mc.flushUndo()
        mc.unloadPlugin('Turtle.mll')
    else:
        mc.warning('No Turtle nodes found.')
    
if __name__ == "__main__":
    nuke()