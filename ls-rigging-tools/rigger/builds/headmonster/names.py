'''
Created on Jul 25, 2014

@author: Leon
'''
import pymel.core as pm

# mouth locs
mouthCols = ['upper',
            'upperSide',
            'upperSneer',
            'upperPinch',
            'upperCorner',
            'corner',
            'lowerCorner',
            'lowerPinch',
            'lowerSneer',
            'lowerSide',
            'lower']

mouthRows = ['lip',
            'inCrease',
            'midCrease',
            'outCrease',
            'cheek']

locs = pm.ls(os=True)
row = mouthRows[3]
for loc, col in zip(locs, mouthCols):
    loc.rename('LT_'+col+'_'+row+'_pLoc')

# eye locs
eyeCols = ['upper',
            'upperOuter',
            'outer',
            'lowerOuter',
            'lower',
            'lowerInner',
            'inner',
            'upperInner']

eyeRows = ['eyelid',
            'eyeSocket']

locs = pm.ls(os=True)
row = eyeRows[1]
for loc, col in zip(locs, eyeCols):
    loc.rename('LT_'+col+'_'+row+'_pLoc')
    
# grid locs
gridCols = ['mid',
            'side',
            'outerA',
            'outerB',
            'outerC']

gridRows = ['forehead',
            'temple',
            'squint',
            'cheekA',
            'cheekB',
            'cheekC',
            'cheekD']

locs = pm.ls(os=True)
col = gridCols[4]
for loc, row in zip(locs, gridRows):
    loc.rename('LT_'+col+'_'+row+'_pLoc')