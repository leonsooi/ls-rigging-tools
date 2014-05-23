'''
Created on May 23, 2014

@author: Leon
'''
import pymel.core as pm

def mirrorFromTo(fromXfo, toXfo):
    '''
    fromXfo = pm.PyNode('locator1')
    toXfo = pm.PyNode('locator2')
    '''
    worldScaleMat = pm.dt.Matrix([[-1.0, 0.0, 0.0, 0.0],
                                    [0.0, 1.0, 0.0, 0.0],
                                    [0.0, 0.0, 1.0, 0.0],
                                    [0.0, 0.0, 0.0, 1.0]])
    
    fromMat = fromXfo.getMatrix(worldSpace=True)
    fromMatScale = worldScaleMat * fromMat
    fromMat_in_worldScaleMat = fromMatScale * worldScaleMat
    toXfo.setMatrix(fromMat_in_worldScaleMat, worldSpace=True)
    