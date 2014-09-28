'''
Created on Jul 14, 2014

@author: Leon
'''
import pymel.core as pm

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
import utils.rigging as rt
mel = Mel()

import rigger.utils.modulate as modulate
reload(modulate)

def fixBendyRibbonsGo(prefix='charName_'):
    '''
    '''
    # left arm
    cons = [nt.AimConstraint(prefix+'lf_armRibbon_1_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'lf_armRibbon_2_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'lf_armRibbon_3_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'lf_armRibbon_4_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'lf_armRibbon_5_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'lf_armRibbon_6_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'lf_armRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')
        
    # right arm
    cons = [nt.AimConstraint(prefix+'rt_armRibbon_1_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'rt_armRibbon_2_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'rt_armRibbon_3_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'rt_armRibbon_4_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'rt_armRibbon_5_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'rt_armRibbon_6_loc|rivet1_rivetAimConstraint1'),
            nt.AimConstraint(prefix+'rt_armRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')
        
    # left leg
    
    cons =[nt.AimConstraint(prefix+'lf_legRibbon_1_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'lf_legRibbon_2_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'lf_legRibbon_3_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'lf_legRibbon_4_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'lf_legRibbon_5_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'lf_legRibbon_6_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'lf_legRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')
        
    # right leg
    cons =[nt.AimConstraint(prefix+'rt_legRibbon_1_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'rt_legRibbon_2_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'rt_legRibbon_3_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'rt_legRibbon_4_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'rt_legRibbon_5_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'rt_legRibbon_6_loc|rivet1_rivetAimConstraint1'),
    nt.AimConstraint(prefix+'rt_legRibbon_7_loc|rivet1_rivetAimConstraint1')]
    
    for con in cons:
        setBendyConstraintOnRibbon(con, (0,1,0), (-1,0,0), 'tangentU')

def setBendyConstraintOnRibbon(con, aimVec, upVec, tangent):
    '''
    con - nt.AimConstraint
    aimVector - vector to align to normal
    upVector - vector to align to tangent
    tangent - 'tangentU' or 'tangentV'
    '''
    con.aimVector.set(aimVec)
    con.upVector.set(upVec)
    posi = con.worldUpVector.inputs()[0]
    posi.attr(tangent) >> con.worldUpVector
    
def transferProxyTransforms():
    nodes = pm.ls(sl=True)

    attrsDict = {}
    attrs = ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz')
    
    for n in nodes:
        d = {}
        for a in attrs:
            d[a] = n.attr(a).get()
        attrsDict[n.nodeName()] = d
        
    #--------
    
    # adapt changes
    attrsDict['spine_mid_2_loc'] = attrsDict['spine_mid_loc']
    attrsDict['spine_mid_1_loc'] = attrsDict['spine_low_loc']
    
    nodes = pm.ls(sl=True)
    
    for n in nodes:
        if n.nodeName() in attrsDict.keys():
            for a, val in attrsDict[n.nodeName()].items():
                try:
                    n.attr(a).set(val)
                except:
                    pass
        else:
            print n + ' not found'