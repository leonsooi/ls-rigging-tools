'''
Created on Sep 17, 2014

@author: Leon
'''

import pymel.core as pm
from pymel.core.language import Mel
mel = Mel()

import pymel.core.nodetypes as nt

import utils.rigging as rt
# coeffs
coeffs = pm.group(em=True, n='CT_lipCurlOut_coeffs')
coeffs.addAttr('leftLower', k=True)
coeffs.addAttr('leftUpper', k=True)
coeffs.addAttr('rightLower', k=True)
coeffs.addAttr('rightUpper', k=True)

# direct drives
rt.connectSDK('LT_lowerSneer_lip_pri_ctrl.rx',
coeffs.leftLower, {0:0, 45:1})
rt.connectSDK('LT_upperSneer_lip_pri_ctrl.rx',
coeffs.leftUpper, {0:0, -45:1})
rt.connectSDK('RT_lowerSneer_lip_pri_ctrl.rx',
coeffs.rightLower, {0:0, 45:1})
rt.connectSDK('RT_upperSneer_lip_pri_ctrl.rx',
coeffs.rightUpper, {0:0, -45:1})

# modulate by centers
import rigger.utils.modulate as modulate
reload(modulate)

priCtls = [nt.Transform(u'CT_upper_lip_pri_ctrl'),
nt.Transform(u'CT_lower_lip_pri_ctrl')]
            
attrs = ['leftLower',
'leftUpper',
'rightLower',
'rightUpper']
       
    
for pCtl in priCtls:
    token = pCtl.split('_')[1]
    for attr in attrs:
        mod = modulate.addInput(coeffs.attr(attr), 0, '_'+token)
        rt.connectSDK(pCtl.rx, mod, {-45:-1, 0:0, 45:1})
        
rt.connectSDK(coeffs.leftLower, 
'blendShapeCt_face_geo.lipCurlOut_lower_Lf', {0:0, 1:1})
rt.connectSDK(coeffs.leftUpper, 
'blendShapeCt_face_geo.lipCurlOut_upper_Lf', {0:0, 1:1})
rt.connectSDK(coeffs.rightLower, 
'blendShapeCt_face_geo.lipCurlOut_lower_Rt', {0:0, 1:1})
rt.connectSDK(coeffs.rightUpper, 
'blendShapeCt_face_geo.lipCurlOut_upper_Rt', {0:0, 1:1})
