'''
Created on May 17, 2014

@author: Leon
'''

import pymel.core as pm

def publishForAnimation():
    # run this before publishing a rig for animation
    
    # 1. delete ngSkinTools nodes
    
    # 2. delete keys
    
    # 3. reset controls
    
    # 4. set timeline to 0 - 100
    
    # 5. rename some controls
    pm.PyNode('LT_philtrum_ctrl').rename('LT_noseSneer_ctrl')
    pm.PyNode('RT_philtrum_ctrl').rename('RT_noseSneer_ctrl')
    pm.PyNode('LT_low_crease_ctrl').rename('LT_cheekPuff_ctrl')
    pm.PyNode('RT_low_crease_ctrl').rename('RT_cheekPuff_ctrl')

    
import pymel.core.nodetypes as nt
def connectSmoothGeos():
    # connect smoothGeo
    mainCtl = pm.PyNode('BODY:Main')
    
    allGeos = [nt.Transform(u'DNTEETH:CT_gumBlockGlobal_geo_0'),
                nt.Transform(u'DNTEETH:CT_teethBlockGlobal_geo_0'),
                nt.Transform(u'UPTEETH:CT_teethBlockGlobal_geo_0'),
                nt.Transform(u'UPTEETH:CT_gumBlockGlobal_geo_0'),
                nt.Transform(u'TONGUE:CT_tongueJaw_geo_0'),
                nt.Transform(u'GEO:LT_eye_geo_0'),
                nt.Transform(u'GEO:RT_eye_geo_0'),
                nt.Transform(u'GEO:CT_nose_geo_0'),
                nt.Transform(u'GEO:CT_body_geo_0')]
    
    for eachGeo in allGeos:
        shapes = eachGeo.getChildren(s=True)
        # choose the one that is not intermediate
        shapes = [shape for shape in shapes if shape.intermediateObject.get() == 0]
        targetShape = shapes[0]
        mainCtl.smoothGeo >> targetShape.smoothLevel
        targetShape.displaySmoothMesh.set(2)
        # also set to reference
        targetShape.overrideEnabled.set(1)
        targetShape.overrideDisplayType.set(2)
                
    


