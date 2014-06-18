
import pymel.core as pm
def addOffset(secCtl, hierarchy, suffix='_offset'):
    '''
    hierarchy - 'parent', 'child', 'sibling', 'world'
    '''
    offsetGrp = pm.group(em=True, n=secCtl+suffix)
    wMat = secCtl.getMatrix(worldSpace=True)
    offsetGrp.setMatrix(wMat, worldSpace=True)
    
    parent = secCtl.getParent()
    
    if hierarchy == 'parent':    
        parent | offsetGrp | secCtl
    elif hierarchy == 'child':
        secCtl | offsetGrp
    elif hierarchy == 'sibling':
        parent | offsetGrp
    elif hierarchy == 'world':
        pass
    else:
        pm.warning('Unknown hierarchy method: %s' % hierarchy)
        
    # connect matrices to drive children
    outMMs = secCtl.matrix.outputs(type='multMatrix')
    
    if not outMMs:
        # get secDrvs and create a new MM for each secDrv
        secDrvs = secCtl.translate.outputs(type='transform')
        for eachSecDrv in secDrvs:
            mat = pm.createNode('multMatrix', n=secCtl+'_'+eachSecDrv+'_'+suffix+'_mm')
            secCtl.matrix >> mat.matrixIn[0]
            dm = pm.createNode('decomposeMatrix', n=secCtl+'_'+eachSecDrv+'_'+suffix+'_dm')
            mat.matrixSum >> dm.inputMatrix
            dm.outputTranslate >> eachSecDrv.t
            dm.outputRotate >> eachSecDrv.r
            dm.outputScale >> eachSecDrv.s
            outMMs.append(mat)
        
        
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