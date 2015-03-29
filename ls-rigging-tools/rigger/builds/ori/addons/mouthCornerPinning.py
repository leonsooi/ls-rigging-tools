'''
Created on Oct 24, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

#===============================================================================
# add mouth corner pinnings
#===============================================================================
# connect corners to bnds (since these were not affected by sticky)
# left
attr = pm.PyNode('CT_stickylips_grp.LT_corner_lip_weight')
bnd = pm.PyNode('LT_corner_lip_bnd')
channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
for channel in channels:
    attr >> bnd.attr('CT__jaw_pri_ctrl_weight_'+channel)
    
# right
attr = pm.PyNode('CT_stickylips_grp.RT_corner_lip_weight')
bnd = pm.PyNode('RT_corner_lip_bnd')
channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
for channel in channels:
    attr >> bnd.attr('CT__jaw_pri_ctrl_weight_'+channel)
    

node = pm.PyNode('CT_stickylips_grp')

# lip_weight is modulated by cornerHeight
node.addAttr('cornerControlLabel', nn='===CORNER CONTROL===', k=True)
node.addAttr('cornerHeightLf', k=True)
node.addAttr('cornerHeightRt', k=True)

def modulateWeightByCornerHeight(weight, origWeight, height):
    '''
    '''
    if weight.get() > 0.5:
        # 1 is the upper limit
        # need to find lower limit
        # get diff from default to upper limit
        pma = pm.createNode('plusMinusAverage', n=weight.attrName()+'_modByCorner_pma')
        pma.op.set(2)
        pma.input1D[0].set(1)
        origWeight >> pma.input1D[1]
        diffAttr = pma.output1D
        # mult by 2 to get full range
        md = pm.createNode('multDoubleLinear', n=weight.attrName()+'_modByCorner_md')
        diffAttr >> md.input1
        md.input2.set(2)
        # subtract from 1 to get lower limit
        pma2 = pm.createNode('plusMinusAverage', n=weight.attrName()+'_modByCorner_pma2')
        pma2.op.set(2)
        pma2.input1D[0].set(1)
        md.output >> pma2.input1D[1]
        lowerLimit = pma2.output1D
        # set range between both limits
        sr = pm.createNode('setRange', n=weight.attrName()+'_modByCorner_sr')
        height >> sr.valueX
        sr.oldMinX.set(-1)
        sr.oldMaxX.set(1)
        sr.minX.set(1)
        lowerLimit >> sr.maxX
        sr.outValueX >> weight
        
    else:
        # 0 is the lower limit
        # mult by 2 to get upper limit
        md = pm.createNode('multDoubleLinear', n=weight.attrName()+'_modByCorner_md')
        origWeight >> md.input1
        md.input2.set(2)
        # set range between both limits
        sr = pm.createNode('setRange', n=weight.attrName()+'_modByCorner_sr')
        height >> sr.valueX
        sr.oldMinX.set(-1)
        sr.oldMaxX.set(1)
        sr.maxX.set(0)
        md.output >> sr.minX
        sr.outValueX >> weight
        

# add attrs to store orig_weights
# add label first
node.addAttr('origWeightsLabel', nn='===ORIG WEIGHTS===', k=True)
weightAttrs = [attr for attr in node.listAttr(ud=True)
                if '_lip_weight' in attr.name()]
for attr in weightAttrs:
    origAttrName = attr.attrName().replace('_lip_', '_lip_orig_')
    attrVal = attr.get()
    node.addAttr(origAttrName, dv=attrVal, k=True)
    origAttr = node.attr(origAttrName)
    if 'LT_' in attr.attrName():
        modulateWeightByCornerHeight(attr, origAttr, node.attr('cornerHeightLf'))
    elif 'RT_' in attr.attrName():
        modulateWeightByCornerHeight(attr, origAttr, node.attr('cornerHeightRt'))
    
# connect jaw control to cornerHeight
jawCtl = nt.Transform(u'CT__jaw_pri_ctrl_negator')
jawCtl.addAttr('leftCornerPinAmount', min=0, k=True, dv=1)
jawCtl.addAttr('rightCornerPinAmount', min=0, k=True, dv=1)
# connect left
md = pm.createNode('multDoubleLinear', n='LT_cornerPinAmt_md')
nt.Transform(u'LT_corner_lip_pri_ctrl_negator').ty >> md.input1
jawCtl.attr('leftCornerPinAmount') >> md.input2
md.output >> node.attr('cornerHeightLf')
# connect right
md = pm.createNode('multDoubleLinear', n='RT_cornerPinAmt_md')
nt.Transform(u'RT_corner_lip_pri_ctrl_negator').ty >> md.input1
jawCtl.attr('rightCornerPinAmount') >> md.input2
md.output >> node.attr('cornerHeightRt')

#===============================================================================
# cheek bnds need to be influences by changing jaw weights too     
#===============================================================================
def connectToCornerWeights(bnd, cornerBnd, weight=0.5):
    channels = ['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    attrName = 'CT__jaw_pri_ctrl_weight_'
    bndAttr = bnd.attr(attrName+channels[0])
    cornerAttr = cornerBnd.attr(attrName+channels[0])
    ratio = bndAttr.get() / cornerAttr.get()
    md = pm.createNode('multDoubleLinear', n=bnd+'_jawInfluence_md')
    cornerAttr >>md.input1
    md.input2.set(ratio)
    bta = pm.createNode('blendTwoAttr', n=bnd+'_jawInfluence_bta')
    bta.input[0].set(bndAttr.get())
    md.output >> bta.input[1]
    bta.ab.set(weight)
    for channel in channels:
        bta.output >> bnd.attr(attrName+channel)
    
# left side
bnds = {nt.Joint(u'LT__sneer_bnd'):1,
        nt.Joint(u'LT_mid_crease_bnd'):1,
        nt.Joint(u'LT_high_cheek_bnd'):0.8,
        nt.Joint(u'LT_low_crease_bnd'):0.8,
        nt.Joint(u'LT_mid_cheek_bnd'):0.7}
cornerBnd = nt.Joint(u'LT_corner_lip_bnd')
for bnd, weight in bnds.items():
    connectToCornerWeights(bnd, cornerBnd, weight)
# right side
bnds = {nt.Joint(u'RT__sneer_bnd'):1,
        nt.Joint(u'RT_mid_crease_bnd'):1,
        nt.Joint(u'RT_high_cheek_bnd'):0.8,
        nt.Joint(u'RT_low_crease_bnd'):0.8,
        nt.Joint(u'RT_mid_cheek_bnd'):0.7}
cornerBnd = nt.Joint(u'RT_corner_lip_bnd')
for bnd, weight in bnds.items():
    connectToCornerWeights(bnd, cornerBnd, weight)