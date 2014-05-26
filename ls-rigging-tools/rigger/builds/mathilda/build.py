import pymel.core as pm
import pymel.core.nodetypes as nt
import maya.cmds as mc
mel = pm.language.Mel()

import rigger.modules.placementGrp as placementGrp
reload(placementGrp)
import rigger.modules.face as face
reload(face)
import rigger.modules.eye as eye
import rigger.modules.sticky as sticky
reload(sticky)
import utils.rigging as rt
import utils.symmetry as sym
reload(placementGrp)
import rigger.builds.mathilda.data as data
reload(data)
import rigger.utils.weights as weights
reload(weights)

#===============================================================================
# PART 1: SET UP PLACEMENT GRP
# start - mathilda_facerigB_v002.0001.ma 
# mathilda_facerigB_v004 (update geometry with seal lips)
#===============================================================================
pGrp = pm.PyNode('CT_placement_grp')
mesh = pm.PyNode(pGrp.mouthLipsLoop.get()[0]).node()

#------------------------------------------------------------------------------ 
# Loop locs
placementGrp.previewLoop(pGrp, 'leftEyelidLoop')

cvMapping = {'LT_eyelid_inner': 19,
            'LT_eyelid_inner_upper': 16,
            'LT_eyelid_upper': 13,
            'LT_eyelid_outer_upper': 10,
            'LT_eyelid_outer': 7,
            'LT_eyelid_outer_lower': 5,
            'LT_eyelid_lower': 2,
            'LT_eyelid_inner_lower': 0}

placementGrp.addLoopPlacements(pGrp, 'leftEyelidLoop', cvMapping)

placementGrp.previewLoop(pGrp, 'mouthLipsLoop')

cvMapping = {'CT_upper_lip': 29,
            'LT_upper_side_lip': 31,
            'LT_upper_sneer_lip': 1,
            'LT_upper_pinch_lip': 3,
            'LT_corner_lip': 5,
            'LT_lower_pinch_lip': 7,
            'LT_lower_sneer_lip': 9,
            'LT_lower_side_lip': 11,
            'CT_lower_lip': 13}
            
placementGrp.addLoopPlacements(pGrp, 'mouthLipsLoop', cvMapping)

#------------------------------------------------------------------------------ 
# Indirect locs
placementGrp.addIndirectPlacements(pGrp)

#------------------------------------------------------------------------------ 
# Align new locs
# Eyelids
face.orientLoopTransforms([nt.Transform(u'LT_eyelid_outer_pLoc'), 
                           nt.Transform(u'LT_eyelid_outer_upper_pLoc'), 
                           nt.Transform(u'LT_eyelid_upper_pLoc')], (-1, 0, 0))

face.orientLoopTransforms([nt.Transform(u'LT_eyelid_inner_pLoc'), 
                           nt.Transform(u'LT_eyelid_inner_upper_pLoc'), 
                           nt.Transform(u'LT_eyelid_upper_pLoc')], (1, 0, 0))

face.orientLoopTransforms([nt.Transform(u'LT_eyelid_outer_pLoc'), 
                           nt.Transform(u'LT_eyelid_outer_lower_pLoc'), 
                           nt.Transform(u'LT_eyelid_lower_pLoc')], (-1, 0, 0))

face.orientLoopTransforms([nt.Transform(u'LT_eyelid_inner_pLoc'), 
                           nt.Transform(u'LT_eyelid_inner_lower_pLoc'), 
                           nt.Transform(u'LT_eyelid_lower_pLoc')], (1, 0, 0))
# Mouth lips
face.orientLoopTransforms([nt.Transform(u'LT_corner_lip_pLoc'), 
                           nt.Transform(u'LT_upper_pinch_lip_pLoc'), 
                           nt.Transform(u'LT_upper_sneer_lip_pLoc'), 
                           nt.Transform(u'LT_upper_side_lip_pLoc'), 
                           nt.Transform(u'CT_upper_lip_pLoc')], (-1, 0, 0))

face.orientLoopTransforms([nt.Transform(u'LT_corner_lip_pLoc'), 
                           nt.Transform(u'LT_lower_pinch_lip_pLoc'), 
                           nt.Transform(u'LT_lower_sneer_lip_pLoc'), 
                           nt.Transform(u'LT_lower_side_lip_pLoc'), 
                           nt.Transform(u'CT_lower_lip_pLoc')], (-1, 0, 0))

# Align for sliding
slidingBnds = [nt.Transform(u'LT_in_forehead_pLoc'),
                 nt.Transform(u'LT_out_forehead_pLoc'),
                 nt.Transform(u'LT_in_low_forehead_pLoc'),
                 nt.Transform(u'LT_out_low_forehead_pLoc'),
                 nt.Transform(u'LT_in_brow_pLoc'),
                 nt.Transform(u'LT_mid_brow_pLoc'),
                 nt.Transform(u'LT_out_brow_pLoc'),
                 nt.Transform(u'LT_temple_pLoc'),
                 nt.Transform(u'CT_brow_pLoc'),
                 nt.Transform(u'LT_up_jaw_pLoc'),
                 nt.Transform(u'LT_low_temple_pLoc'),
                 nt.Transform(u'LT_out_cheek_pLoc'),
                 nt.Transform(u'LT_squint_pLoc'),
                 nt.Transform(u'LT_low_crease_pLoc'),
                 nt.Transform(u'LT_cheek_pLoc'),
                 nt.Transform(u'LT_corner_jaw_pLoc'),
                 nt.Transform(u'LT_low_jaw_pLoc'),
                 nt.Transform(u'LT_mid_crease_pLoc'),
                 nt.Transform(u'LT_up_cheek_pLoc'),
                 nt.Transform(u'LT_sneer_pLoc'),
                 nt.Transform(u'LT_philtrum_pLoc'),
                 nt.Transform(u'LT_in_philtrum_pLoc'),
                 nt.Transform(u'LT_up_crease_pLoc'),
                 nt.Transform(u'LT_in_cheek_pLoc'),
                 nt.Transform(u'LT_chin_pLoc'),
                 nt.Transform(u'CT_chin_pLoc'),
                 nt.Transform(u'CT_mid_chin_pLoc'),
                 nt.Transform(u'LT_mid_chin_pLoc'),
                 nt.Transform(u'CT_neck_pLoc'),
                 nt.Transform(u'LT_neck_pLoc'),
                 nt.Transform(u'LT_corner_jaw_pLoc'),
                 nt.Transform(u'LT_low_jaw_pLoc'),
                 nt.Transform(u'LT_chin_pLoc'),
                 nt.Transform(u'CT_chin_pLoc'),
                 nt.Transform(u'LT_low_cheek_pLoc')]

for eachBnd in slidingBnds:
    rt.alignTransformToMesh(eachBnd, mesh, method='sliding')

# manual orienting and tweaking
# notes:
# cheek locs should have Y-up, so they can translate up and make a bulge, etc
# align jaw locs along jawline
# brow neg-Y should point outwards to maintain brow volume
    
#------------------------------------------------------------------------------ 
# Mirror
placementGrp.snapPlacementsToMesh(pGrp)
placementGrp.mirrorAllPlacements(pGrp)
pDict = data.placeLocXforms
placementGrp.setPlacementGrpFromDict(pGrp, pDict)
#===============================================================================
# BUILD BNDS
# start - mathilda_facerigB_v003.ma
# mathilda_facerigB_v005.ma (update geometry with lips closed)
# mathilda_facerigB_v006.ma (update loc orientations)
#===============================================================================
bndGrp = face.createBndsFromPlacement(pGrp)
face.buildSecondaryControlSystem(pGrp, bndGrp, mesh)
priCtls = face.buildPrimaryControlSystem()
perimeterGrp = face.addPerimeterBndSystem(mesh)
mll = face.createSkinLayers(mesh)

# set primary ctl weights
# all weights from facerigB_v010

allWeights = data.priCtlBndWeights
for attr, val in allWeights.items():
    pm.Attribute(attr).set(val)

# rig cleanup
face.cleanFaceRig()

# smooth necessary layers
face.selectVertsClosestToBnds(mll) # use this as a mask while smoothing

# skin weights cleanup - mathilda_facerigB_v005.0003.ma
# motion weights cleanup

#===============================================================================
# POST-BUILD ADD-ON FEATURES
# mathilda_facerigB_v008.ma
#===============================================================================

# add left eye deformer
edgeLoop = [pm.PyNode(edge) for edge in pGrp.leftEyelidLoop.get()]
eyePivot = pm.PyNode('LT_eyeball_geo')
rigidLoops = 2
falloffLoops = 4
eye.buildEyeRigCmd('LT_eye', eyePivot, edgeLoop, rigidLoops, falloffLoops)

# right eye deformer
symTable = sym.buildSymTable('CT_face_geo')
pm.select(edgeLoop)
mel.ConvertSelectionToVertices()
vertsLoop = mc.ls(sl=True, fl=True)
sym.flipSelection(vertsLoop, symTable)
mel.ConvertSelectionToContainedEdges()
edgeLoop = pm.ls(sl=True)
eyePivot = pm.PyNode('RT_eyeball_geo')
eye.buildEyeRigCmd('RT_eye', eyePivot, edgeLoop, rigidLoops, falloffLoops)

weights.setEyelidLoopWeights('LT')
weights.setEyelidLoopWeights('RT')

# eyeball rig (simple aim constraints)
eye.buildEyeballRig()
eye.addEyeAim(prefix='LT_', distance=25)
eye.addEyeAim(prefix='RT_', distance=25)

# sticky lips
s = sticky.Sticky(up_bnd=pm.PyNode('CT_upper_lip_bnd'), low_bnd=pm.PyNode('CT_lower_lip_bnd'), center=pm.PyNode('CT_jaw_pri_ctrl'))
s = sticky.Sticky(up_bnd=pm.PyNode('LT_upper_side_lip_bnd'), low_bnd=pm.PyNode('LT_lower_side_lip_bnd'), center=pm.PyNode('CT_jaw_pri_ctrl'))
s = sticky.Sticky(up_bnd=pm.PyNode('LT_upper_sneer_lip_bnd'), low_bnd=pm.PyNode('LT_lower_sneer_lip_bnd'), center=pm.PyNode('CT_jaw_pri_ctrl'))
s = sticky.Sticky(up_bnd=pm.PyNode('LT_upper_pinch_lip_bnd'), low_bnd=pm.PyNode('LT_lower_pinch_lip_bnd'), center=pm.PyNode('CT_jaw_pri_ctrl'))
s = sticky.Sticky(up_bnd=pm.PyNode('RT_upper_side_lip_bnd'), low_bnd=pm.PyNode('RT_lower_side_lip_bnd'), center=pm.PyNode('CT_jaw_pri_ctrl'))
s = sticky.Sticky(up_bnd=pm.PyNode('RT_upper_sneer_lip_bnd'), low_bnd=pm.PyNode('RT_lower_sneer_lip_bnd'), center=pm.PyNode('CT_jaw_pri_ctrl'))
s = sticky.Sticky(up_bnd=pm.PyNode('RT_upper_pinch_lip_bnd'), low_bnd=pm.PyNode('RT_lower_pinch_lip_bnd'), center=pm.PyNode('CT_jaw_pri_ctrl'))

sticky.addStickyToFRS()