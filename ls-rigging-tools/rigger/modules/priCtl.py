'''
Created on May 26, 2014

@author: Leon
'''
import pymel.core as pm
def addOffset(pCtl, hierarchy, order='secondLast', suffix='_offset'):
    '''
    hierarchy - 'parent', 'child', 'sibling', 'world'
    order - 'secondLast', 'second'
    secondLast will make offset pivot from original position
    second will make offset pivot from offset's post-transform position
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
        
    if order == 'secondLast':

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
    
    elif order == 'second':
        for outMM in outMMs:
            # move elements up by 1
            # (keep element 0 at 0, since we're going to insert at 1)
            nextIndex = outMM.matrixIn.numElements()
            plugsToMove = [outMM.matrixIn.elementByLogicalIndex(i).inputs(p=True)[0]
                           for i in range(1, nextIndex)]
            # move plugs
            for plugId, plug in enumerate(plugsToMove):
                plug >> outMM.matrixIn.elementByLogicalIndex(plugId+2)
                
            # connect offsetGrp to second plug
            offsetGrp.matrix >> outMM.matrixIn[1]
    
    else:
        pm.warning('Unknown order method %s' % order)
    return offsetGrp