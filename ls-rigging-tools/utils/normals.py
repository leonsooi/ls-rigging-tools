'''
Created on Sep 22, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

def reverseNormalsAndPreserveUVsGo():
    '''
    select meshes
    run reverseNormalsAndPreserveUVs()
    '''
    selObjs = pm.ls(sl=True)
    for obj in selObjs:
        try:
            reverseNormalsAndPreserveUVs(obj)
        except:
            print 'Cannot reverse normals for ' + obj
            
def reverseNormalsAndPreserveUVs(mesh):
    '''
    reverse normals but keep the uvs the same
    (don't change from blue to red, etc) 
    
    this will break uv seams!!!
    '''
    # duplicate the mesh to keep a copy of the correct uvs
    dupMesh = pm.duplicate(mesh)
    
    # reverse normals on the mesh
    pm.polyNormal(mesh, nm=0, ch=0)
    
    # transfer correct uvs back to mesh 
    pm.transferAttributes(dupMesh, mesh, uvs=2, spa=4)
    pm.delete(mesh, ch=True)
    
    # cleanup
    pm.delete(dupMesh)
    