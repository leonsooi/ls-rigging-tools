'''
Created on May 26, 2014

@author: Leon
'''
import pymel.core as pm
def addOffset(pCtl, hierarchy, suffix='_offset'):
    '''
    hierarchy - 'parent', 'child', 'sibling', 'world'
    '''
    offsetGrp = pm.group(em=True, n=pCtl+suffix)
    wMat = pCtl.getMatrix(worldSpace=True)
    offsetGrp.setMatrix(wMat, worldSpace=True)
    
    parent = pCtl.getParent()
    
    if hierarchy == 'parent':    
        parent | offsetGrp | pCtl
    elif hierarchy == 'child':
        pCtl | offsetGrp
    elif hierarchy == 'sibling':
        parent | offsetGrp
    elif hierarchy == 'world':
        pass
    else:
        pm.warning('Unknown hierarchy method: %s' % hierarchy)
        
    # connect matrices to drive children
    outMMs = pCtl.matrix.outputs(type='multMatrix')
    for outMM in outMMs:
        # be sure to use the next plugIndex
        nextIndex = outMM.matrixIn.numElements()
        nextPlug = outMM.matrixIn.elementByLogicalIndex(nextIndex)
        lastPlug = outMM.matrixIn.elementByLogicalIndex(nextIndex-1)
        invMat = lastPlug.inputs(p=True)[0]
        if not nextPlug.isConnected():
            # offsetGrp matrix should be inserted at second-last plug (invMat)
            offsetGrp.matrix >> lastPlug
            invMat >> nextPlug
        else:
            pm.warning('Overriding plug %s. Check logical indices.' % nextPlug)
            
    return offsetGrp