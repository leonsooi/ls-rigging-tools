'''
Created on Aug 12, 2014

@author: Leon
'''

import Red9.core.Red9_Meta as r9Meta
import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()


def setupAttributesOnBsg(baseMesh, targetMesh, 
                         driverAttrs, driverVals=None,
                         unifyBnds=[]):
    '''
    baseMesh - mesh shape in default pose
    targetMesh - mesh shape (bsg) to add attrs to
    driverAttrs - attr to drive this bsg e.g. 'ctl.ty'
    unifyBnds - list of tuples of bnds that should have 
                datapoint values unified
    
    Assume:
    - that baseMesh is in default pose
    - bndVertIds are already set up on bnds
    - driverVals can only be calculated for drivertranslation
    (so driverVals must be given for other attr types (e.g. rotations, scale or user defined)
    - driverAttrs are from pri_ctrls, to avoid cycles if driving sec_ctrls
    
    Creates attributes on the targetMesh
    driverAttrs - dictionary: {attr: value to trigger shape}
    unifyBnds - list of tuples [(bnd, bnd, ...), (bnd, bnd), ...]
    
    TODO: calculate driverVals for ws-translate attrs
    '''
    
    driverVertIdMap = {}
    # get bndVertId for each driver
    for driverAttr in driverAttrs:
        drvCtl = driverAttr.node()
        possibleBndsAttrs = drvCtl.message.outputs(type='joint', p=True)
        bnd = [bnd.node() for bnd in possibleBndsAttrs
               if 'attached_pri_ctl' in bnd.attrName()][0]
        vertId = bnd.bndVertId.get()
        driverVertIdMap[driverAttr] = vertId
        
    # get range for each driver
    # this only works for translations
    # ranges for other attr types must be specified in driverVals
    for driverAttr in driverAttrs:
        # get delta for corresponding vertex
        pass