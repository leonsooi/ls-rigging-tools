'''
Created on Dec 22, 2013

@author: Leon
'''
def replaceBlendshapeTarget(origTarget, newTarget):
    '''
    origTarget = pm.PyNode('Anim_V006_0001|CT_body_geo_0')
    newTarget = pm.PyNode('Anim_V007|CT_body_geo_0')
    
    # example use
    replaceBlendshapeTarget(pm.PyNode('Anim_V006_0001|CT_body_geo_0'), pm.PyNode('Anim_V007|CT_body_geo_0'))        
    replaceBlendshapeTarget(pm.PyNode('Anim_V006_0001|CT_nose_geo_0'), pm.PyNode('Anim_V007|CT_nose_geo_0'))
    replaceBlendshapeTarget(pm.PyNode('Anim_V006_0001|LT_eye_geo_0'), pm.PyNode('Anim_V007|LT_eye_geo_0'))        
    replaceBlendshapeTarget(pm.PyNode('Anim_V006_0001|RT_eye_geo_0'), pm.PyNode('Anim_V007|RT_eye_geo_0'))
    '''
    inPlugs = origTarget.worldMesh.outputs(p=True)
    for eachPlug in inPlugs:
        newTarget.worldMesh >> eachPlug

