'''
Created on Nov 27, 2013

@author: Leon
'''

import maya.cmds as mc

def run(num):
    for index in range(num):
        cube = mc.polySphere(n='baba_%d' % index)[0]
        mc.refresh(f=True)
        mc.xform(cube, t=(index,index,index))