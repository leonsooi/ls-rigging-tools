'''
Created on May 27, 2014

@author: Leon

a local reader is a transform that gets a local offset of another transform...
'''
import pymel.core as pm
def create(xfo, parent, suffix=''):
    '''
    xfo - transform to drive with local offset
    the local reader will have the same world matrix as this
    parent - transform to parent under
    parent should have the same space as xfo
    parent moves in global space, but keeps the same local space for xfo
    to remain constant
    '''
    reader = pm.group(em=True, n=xfo+'_localReader'+suffix)
    readerHm = pm.group(reader, n=xfo+'_localReaderHm'+suffix)
    
    mat = xfo.getMatrix(worldSpace=True)
    readerHm.setMatrix(mat, worldSpace=True)
    
    rp = xfo.getRotatePivot(space='world')
    readerHm.setRotatePivot(rp, space='world')
    reader.setRotatePivot(rp, space='world')
    
    sp = xfo.getScalePivot(space='world')
    readerHm.setScalePivot(sp, space='world')
    reader.setScalePivot(sp, space='world')
    
    parent | readerHm
    
    reader.t >> xfo.t
    reader.r >> xfo.r
    reader.s >> xfo.s
    
    return reader