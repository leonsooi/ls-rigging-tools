'''
Created on Jun 28, 2014

@author: Leon

example build for mathilda:

headGeo = nt.Transform(u'CT_face_geo')
import rigger.modules.headLattice as headLattice
reload(headLattice)
latgrp = headLattice.createLattice(headGeo, [])
m = dt.Matrix([[1.08819833575, 0.0, 0.0, 0.0],
         [0.0, 0.800333468787, 0.0, 0.0],
         [0.0, 0.0, 1.08819833575, 0.0],
         [0.0, 23.1879695956, -0.00324741491951, 1.0]])
latgrp.setMatrix(m)
headLattice.createLatticeControls()
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt
import rigger.lib.controls as controls
import rigger.modules.localReader as localReader
reload(localReader)

def createLattice(headGeo, faceGeos):
    '''
    headGeos - list of meshes for head etc (define bounding box for lattice)
    faceGeos - list of meshes for face, headlashes, etc
    '''
    dfm, lat, base = pm.lattice(headGeo, n='CT_headLattice_dfm', objectCentered=True,
                                dv=[2,9,2], ldv=[2,4,2], commonParent=True)
               
    dfm.local.set(True)
    
    for faceGeo in faceGeos:
        dfm.addGeometry(faceGeo)
        
    dfmGrp = lat.getParent()
    dfmGrp.centerPivots()
    pm.select(dfmGrp)
    return dfmGrp

def createLatticeControls():
    '''
    assume lattice is already created and xformed
    
    xform for mathilda:
    dt.Matrix([[1.08819833575, 0.0, 0.0, 0.0],
             [0.0, 0.800333468787, 0.0, 0.0],
             [0.0, 0.0, 1.08819833575, 0.0],
             [0.0, 23.1879695956, -0.00324741491951, 1.0]])
    '''
    lat = nt.Transform(u'CT_headLattice_dfmLattice')
    
    # defining lattice points  
    deformPoints = {'CT_headUpperA': [lat.pt[0:1][8][0:1], []],
                    'CT_headUpperB': [lat.pt[0:1][9][0:1], lat.pt[0:1][10:15][0:1]],
                    'CT_headLowerA': [lat.pt[0:1][7][0:1], []],
                    'CT_headLowerB': [lat.pt[0:1][6][0:1], lat.pt[0:1][0:5][0:1]]}
    
    
    # create clusters
    clusters = {}
    dfg = pm.group(em=True, n='CT_headLatticeClusters_dfg')
    for name, components in deformPoints.items():
        dfm, hdl = pm.cluster(components[0], n=name+'_cluster_dfm', relative=True)
        # above: use relative - the cluster handles will be parented with the face/head control
        # so parentConstraint will only drive offset values to the handles
        # so we'll make sure to only use the local offset values
        for component in components[1]:
            dfm.setGeometry(component)
        dfg | hdl
        clusters[name] = dfm, hdl
    
    # create controls
    controlZOffset = 0
    childEyeShapers = []
    localReadersGrp = pm.group(em=True, n='CT_headLatticeClusters_localReadersGrp')
    for name, (dfm, hdl) in clusters.items():
        pt = hdl.getRotatePivot(space='world')
        pt = dt.Point(pt + (0, 0, controlZOffset))
        ctl = pm.circle(n=name+'_headShaper_ctl')
        ctg = pm.group(ctl, n=name+'_headShaper_ctg')
        cth = pm.group(ctg, n=name+'_headShaper_cth')
        cth.setTranslation(pt)
        # shape ctl
        ctl[1].radius.set(0.5)
        ctl[1].sweep.set(359)
        ctl[1].centerZ.set(0)
        ctl[1].normal.set((0,1,0))
        pm.delete(ctl, ch=True)
        # scale transform
        pm.makeIdentity(ctl[0], s=True, a=True)
        # color shape
        '''
        if 'LT_' in name:
            controls.setColor(ctl[0], 18)
        elif 'RT_' in name:
            controls.setColor(ctl[0], 20)
        else:
            pm.warning('unknown side %s' % name)'''
        # parent constraint cluster (using matrices)
        reader = localReader.create(hdl, localReadersGrp)
        pm.parentConstraint(ctl[0], reader, mo=True)
        childEyeShapers.append(cth)
        
    # group both controls and clusters under the CTG,
    # so cluster will only use local offsets
    headShaperCtg = pm.group(childEyeShapers, localReadersGrp, n='CT_headLatticeControls_ctg')
    # headShaperCtg can then be parented under face_ctrl
    return headShaperCtg