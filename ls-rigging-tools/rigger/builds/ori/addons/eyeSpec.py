'''
Created on Feb 22, 2015

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

importedNodes = pm.ls('eyeSpec_rig_v003:*')
side = 'LT_'

for n in importedNodes:
    if 'shape' not in n.nodeType(i=True):
        newName = side + n.stripNamespace()
        print newName
        n.rename(newName)

faceCtl = nt.Transform('CT_face_ctrl')
eyeMover = nt.Transform(side + '_eyeMover_pri_ctrl_negator')
eyeCtl = nt.Transform(side + 'eye_ctl')
eyeSpecHm = nt.Transform(side + 'eyeSpec_cth')

eyeCtl| eyeSpecHm
eyeSpecHm.setMatrix(pm.dt.Matrix())
faceCtl| eyeSpecHm
pm.pointConstraint(eyeMover, eyeSpecHm)

eyeSpecGeo = nt.Mesh(side + 'eyeSpec_geoShape')
eyeLensGeo = nt.Mesh(side + 'lens_geoShape')

pm.select(eyeSpecGeo, eyeLensGeo, r=True)