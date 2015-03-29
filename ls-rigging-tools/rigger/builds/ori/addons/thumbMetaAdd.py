'''
Created on Dec 21, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

# thumb meta add
import rigger.builds.ori.addons.fixFingerRotates as fingerFixes

# left thumb
thumbLoc = fingerFixes.addLocatorForPlacement('Ori_lf_', 'thumb')
thumbLoc.t.set(2.865, -0.454, 0.701)
midCurl = fingerFixes.addCurlJnt('Ori_lf_', 'thumb')
fingerFixes.addCtrlToSpreadJnt(midCurl)

# right thumb
thumbLoc = fingerFixes.addLocatorForPlacement('Ori_rt_', 'thumb')
thumbLoc.t.set(-2.865, 0.454, -0.701)
midCurl = fingerFixes.addCurlJnt('Ori_rt_', 'thumb')
fingerFixes.addCtrlToSpreadJnt(midCurl)