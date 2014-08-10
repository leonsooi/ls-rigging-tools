'''
Created on Aug 8, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import rigger.lib.mesh as mesh
reload(mesh)

def alignVertexLoopWithCurve():
    '''
    select loop of verts
    curve is created to sculpt verts
    '''
    verts = pm.ls(os=True, fl=True)
    sv = mesh.SortedVertices(verts)
    
    # use first and last verts to create 1-span curve
    firstVert = sv.verts[0]
    lastVert = sv.verts[-1]
    firstPos = firstVert.getPosition()
    lastPos = lastVert.getPosition()
    crv = pm.curve(ep=(firstPos, lastPos), d=3)
    endParam = crv.getParamAtPoint(lastPos) * 0.99
    
    # place verts along curve
    totalVerts = len(sv.verts)
    params = [endParam/(totalVerts-1)*vertId for vertId in range(totalVerts)]
    print params
    
    for vert, param in zip(sv.verts, params):
        print vert, param
        pos = crv.getPointAtParam(param)
        vert.setPosition(pos)
        
    # make wire deformer to sculpt verts
    wire = pm.wire(sv.verts, w=crv)