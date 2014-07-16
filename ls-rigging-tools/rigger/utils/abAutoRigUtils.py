'''
Created on Jul 14, 2014

@author: Leon
'''
import pymel.core as pm
def transferProxyTransforms():
    nodes = pm.ls(sl=True)

    attrsDict = {}
    attrs = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
    
    for n in nodes:
        d = {}
        for a in attrs:
            d[a] = n.attr(a).get()
        attrsDict[n.nodeName()] = d
        
    #--------
    
    # adapt changes
    attrsDict['spine_mid_2_loc'] = attrsDict['spine_mid_loc']
    attrsDict['spine_mid_1_loc'] = attrsDict['spine_low_loc']
    
    nodes = pm.ls(sl=True)
    
    for n in nodes:
        if n.nodeName() in attrsDict.keys():
            for a, val in attrsDict[n.nodeName()].items():
                try:
                    n.attr(a).set(val)
                except:
                    pass
        else:
            print n + ' not found'