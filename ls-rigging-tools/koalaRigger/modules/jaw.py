import utils.rigging as rt
import koalaRigger.lib.createNode as cn
import maya.cmds as mc

#===============================================================================
# JAWOPEN rig
#===============================================================================

# LT corner
rt.connectSDK('CT_lips_mod_0.lfCorner', 'LT_mouthCornerHold_bnd_0_parentConstraint1.CT_top_center_locW0', {-1:0, 0:1, 1:1})
rt.connectSDK('CT_lips_mod_0.lfCorner', 'LT_mouthCornerHold_bnd_0_parentConstraint1.CT_bottom_center_locW1', {-1:1, 0:1, 1:0})
# RT corner
rt.connectSDK('CT_lips_mod_0.rtCorner', 'RT_mouthCornerHold_bnd_0_parentConstraint1.CT_top_center_locW0', {-1:0, 0:1, 1:1})
rt.connectSDK('CT_lips_mod_0.rtCorner', 'RT_mouthCornerHold_bnd_0_parentConstraint1.CT_bottom_center_locW1', {-1:1, 0:1, 1:0})

# JawOpen down
rt.connectSDK('CT_lips_mod_0.jawOpen', 'CT_jawOpen_grp.rotateX', {-1:90, 0:0})
# JawOpen up
rt.connectSDK('CT_lips_mod_0.jawOpen', 'CT_jawOpenMouthUp_grp.rotateX', {0:0, 0.5:-7})

# MouthOpen up
rt.connectSDK('CT_lips_mod_0.jawOpen', 'CT_mouthOpen_grp.rx', {0:0, 0.5:-7})

#===============================================================================
# LIPS SEAL rig
#===============================================================================

# LT seal remaps
lfCnrRemap = mc.createNode('remapValue', n='LT_sealCnrRemap')
mc.connectAttr('CT_lips_mod_0.lfSeal', lfCnrRemap+'.inputValue', f=True)
mc.setAttr(lfCnrRemap+'.inputMin', 0)
mc.setAttr(lfCnrRemap+'.inputMax', 0.25)

lfPinchRemap = mc.createNode('remapValue', n='LT_sealPinchRemap')
mc.connectAttr('CT_lips_mod_0.lfSeal', lfPinchRemap+'.inputValue', f=True)
mc.setAttr(lfPinchRemap+'.inputMin', 0.25)
mc.setAttr(lfPinchRemap+'.inputMax', 0.5)

lfSideRemap = mc.createNode('remapValue', n='LT_sealSideRemap')
mc.connectAttr('CT_lips_mod_0.lfSeal', lfSideRemap+'.inputValue', f=True)
mc.setAttr(lfSideRemap+'.inputMin', 0.5)
mc.setAttr(lfSideRemap+'.inputMax', 0.75)

lfMidRemap = mc.createNode('remapValue', n='LT_sealMidRemap')
mc.connectAttr('CT_lips_mod_0.lfSeal', lfMidRemap+'.inputValue', f=True)
mc.setAttr(lfMidRemap+'.inputMin', 0.75)
mc.setAttr(lfMidRemap+'.inputMax', 1)
mc.setAttr(lfMidRemap+'.outputMax', 0.5)

# RT seal remaps
rtCnrRemap = mc.createNode('remapValue', n='RT_sealCnrRemap')
mc.connectAttr('CT_lips_mod_0.rtSeal', rtCnrRemap+'.inputValue', f=True)
mc.setAttr(rtCnrRemap+'.inputMin', 0)
mc.setAttr(rtCnrRemap+'.inputMax', 0.25)

rtPinchRemap = mc.createNode('remapValue', n='RT_sealPinchRemap')
mc.connectAttr('CT_lips_mod_0.rtSeal', rtPinchRemap+'.inputValue', f=True)
mc.setAttr(rtPinchRemap+'.inputMin', 0.25)
mc.setAttr(rtPinchRemap+'.inputMax', 0.5)

rtSideRemap = mc.createNode('remapValue', n='RT_sealSideRemap')
mc.connectAttr('CT_lips_mod_0.rtSeal', rtSideRemap+'.inputValue', f=True)
mc.setAttr(rtSideRemap+'.inputMin', 0.5)
mc.setAttr(rtSideRemap+'.inputMax', 0.75)

rtMidRemap = mc.createNode('remapValue', n='RT_sealMidRemap')
mc.connectAttr('CT_lips_mod_0.rtSeal', rtMidRemap+'.inputValue', f=True)
mc.setAttr(rtMidRemap+'.inputMin', 0.75)
mc.setAttr(rtMidRemap+'.inputMax', 1)
mc.setAttr(rtMidRemap+'.outputMax', 0.5)

# LT seal height
# -1 - jaw0%, mouth100%
# 0 - jaw-50%, mouth50%
# 1 - jaw-100%, mouth0%
rt.connectSDK('CT_lips_mod_0.lfSealHeight', 'CT_lips_mod_0.lfJawSealCoeff', {-1:0, 0:-0.5, 1:-1})
rt.connectSDK('CT_lips_mod_0.lfSealHeight', 'CT_lips_mod_0.lfMouthSealCoeff', {-1:1, 0:0.5, 1:0})
# RT seal height
rt.connectSDK('CT_lips_mod_0.rtSealHeight', 'CT_lips_mod_0.rtJawSealCoeff', {-1:0, 0:-0.5, 1:-1})
rt.connectSDK('CT_lips_mod_0.rtSealHeight', 'CT_lips_mod_0.rtMouthSealCoeff', {-1:1, 0:0.5, 1:0})

#===============================================================================
# NWSF
#===============================================================================
# corner offset
rt.connectSDK('LT_nwsf_ctl.corner', 'LT_nwsfSF_bnd_0.rz', {-30:30, 30:-30})
rt.connectSDK('RT_nwsf_ctl.corner', 'RT_nwsfSF_bnd_0.rz', {30:30, -30:-30})

#===============================================================================
# JawRot, MouthFT
#===============================================================================
# jawRot
rt.connectSDK('CT_jawRot_mod_0.jawRot', 'CT_jawRot_jng.ry', {-1:-12,1:12})
rt.connectSDK('CT_jawRot_mod_0.jawRot', 'CT_jawRotTip_grp.ry', {-1:-3,1:3})
rt.connectSDK('CT_jawRot_mod_0.jawRot', 'CT_jawRotTip_grp.rz', {-1:-5,1:5})
# mouthRot
rt.connectSDK('CT_jawRot_mod_0.mouthRot', 'CT_mouthRot_grp.rz', {-30:-30,30:30})
# mouthSide
rt.connectSDK('CT_jawRot_mod_0.mouthSide', 'CT_jawDownFT_grp.ry', {-1:-30,1:30})
# mouthUp
rt.connectSDK('CT_jawRot_mod_0.mouthUp', 'CT_mouthUpFT_grp.rx', {0:0,1:-10})
rt.connectSDK('CT_jawRot_mod_0.mouthUp', 'CT_jawRotTip_grp.rx', {0:0,1:-15})
# jawDn
rt.connectSDK('CT_jawRot_mod_0.mouthUp', 'CT_jawDownFT_grp.rx', {-1:30,0:0})
rt.connectSDK('CT_jawRot_mod_0.mouthUp', 'CT_mouthRot_grp.rx', {-1:-10,0:0})
