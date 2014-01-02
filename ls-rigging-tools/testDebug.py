'''
Created on Dec 29, 2013

@author: Leon
'''

import maya.cmds as mc

for index in range(20):
    cube = mc.polyCube(n='cube_%d' % index)[0]
    if index == 12:
        print '12'
    else:
        mc.xform(cube, t=(index,index,index))
        print mc.xform(cube, q=True, t=True)
        mc.refresh()