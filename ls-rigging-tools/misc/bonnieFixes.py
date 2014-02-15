'''
Created on Feb 7, 2014

@author: Leon
'''

import pymel.core as pm

# Global scale

# bendy controls need scale constraint
# select each grp and run
grp = pm.ls(sl=True)[0]
# query driver jnt
cons = grp.translateX.inputs()[0]
jnt = pm.parentConstraint(cons, q=True, tl=True)[0]
# add scale constraint
pm.scaleConstraint(jnt, grp)

