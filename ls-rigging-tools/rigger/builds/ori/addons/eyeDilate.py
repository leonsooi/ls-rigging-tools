'''
Created on Oct 11, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

#--------------------------------------------------------- PUPIL AND IRIS DILATE
import rigger.modules.dilate as dilate
reload(dilate)

# left iris
geo = nt.Mesh(u'LT_eyeball_geoShape')
pivotGeo = pm.PyNode(u'LT_lens_geoShape.vtx[133]')
tipGeo = geo.vtx[133:144]
ctl = nt.Transform(u'LT_eye_ctl')
name = '_iris'
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:3.75}}
weights = [1, 1, 1, 1, 1, 1, 0.4, 0.15]
addGeos = [nt.Transform(u'LT_pupil_geo')]
dilate.createForRing(ctl, tipGeo, weights, name, keys, pivotGeo, addGeos, True)

# left pupil
geo = nt.Mesh(u'LT_eyeball_geoShape')
tipGeo = geo.vtx[133:144]
ctl = nt.Transform(u'LT_eye_ctl')
name = '_pupil'
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:2}}
weights = [1, .9, .25, 0]
addGeos = [nt.Transform(u'LT_pupil_geo')]
dilate.create(ctl, tipGeo, weights, name, keys, addGeos, True)

# left iris
geo = nt.Mesh(u'RT_eyeball_geoShape')
pivotGeo = pm.PyNode(u'RT_lens_geoShape.vtx[133]')
tipGeo = geo.vtx[133:144]
ctl = nt.Transform(u'RT_eye_ctl')
name = '_iris'
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:3.75}}
weights = [1, 1, 1, 1, 1, 1, 0.4, 0.15]
addGeos = [nt.Transform(u'RT_pupil_geo')]
dilate.createForRing(ctl, tipGeo, weights, name, keys, pivotGeo, addGeos, True)

# left pupil
geo = nt.Mesh(u'RT_eyeball_geoShape')
tipGeo = geo.vtx[133:144]
ctl = nt.Transform(u'RT_eye_ctl')
name = '_pupil'
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:2}}
weights = [1, 0.9, .25, 0]
addGeos = [nt.Transform(u'RT_pupil_geo')]
dilate.create(ctl, tipGeo, weights, name, keys, addGeos, True)
