'''
Created on Jul 29, 2014

@author: Leon
'''
import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

import assignPriWeightsByBlendshape

def unifyAcsPosGo():
    '''
    '''
    bnds = pm.ls(sl=True)
    unifyAcsPos(bnds)

def unifyAcsPos(bnds):
    '''
    '''
    sdkDags = [pm.PyNode(bnd.replace('_bnd','_sdk'))
               for bnd in bnds]
    sdkNum = float(len(sdkDags)) # cast to float to ensure we can divide later
    
    for channel in ['tx','ty','tz']:
        total = sum([dag.attr(channel).get() for dag in sdkDags])
        avg = total / sdkNum
        [dag.attr(channel).set(avg) for dag in sdkDags]

def setAllAcsPosByDelta():
    '''
    '''
    bndGrp = nt.Transform(u'CT_bnd_grp')
    allBnds = bndGrp.getChildren(ad=True, type='joint')
    # don't change movers
    allBnds = [bnd for bnd in allBnds if 'Mover' not in bnd.name()
               and 'CT__base' not in bnd.name()
               and 'CT__jaw' not in bnd.name()]
    
    bndVertMap = assignPriWeightsByBlendshape.buildBndVertMap()
    
    corrMesh = nt.Mesh(u'RT_lowOutBrow_corrective_bsgShape')
    
    for bnd in allBnds:
        setAcsPosByDelta(bnd, corrMesh, bndVertMap)

def setAcsPosByDelta(bnd, corrMesh, bndVertMap):
    '''
    '''
    bndVertId = bndVertMap[bnd.name()]
    sdkDag = pm.PyNode(bnd.replace('_bnd','_sdk'))
    
    destPos = corrMesh.vtx[bndVertId].getPosition()
    sdkDag.setTranslation(destPos, space='world')

def connectBndsToACS():
    '''
    connect motion system (*_sdk) to acs
    set this up once
    '''
    bndGrp = nt.Transform(u'CT_bnd_grp')
    acsNode = nt.Transform(u'CT_face_acs')
    allBnds = bndGrp.getChildren(ad=True, type='joint')
    
    allSdks = [bnd.replace('_bnd','_sdk') for bnd in allBnds]
    
    for sdk in allSdks:
        for channel in ['tx','ty','tz']:
            mel.DPK_acs_importOutput(acsNode.name(), sdk+'.'+channel)