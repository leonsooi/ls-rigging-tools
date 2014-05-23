import pymel.core as pm
import pymel.core.nodetypes as nt

import rigger.modules.placementGrp as placementGrp
import rigger.modules.face as face
import utils.rigging as rt
reload(placementGrp)

#===============================================================================
# PART 1: SET UP PLACEMENT GRP
#===============================================================================
pGrp = pm.PyNode('CT_placement_grp')

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

cvMapping = {'CT_lip_upper_mid': 29,
            'LT_lip_upper_side': 31,
            'LT_lip_upper_sneer': 1,
            'LT_lip_upper_pinch': 3,
            'LT_lip_corner': 5,
            'LT_lip_lower_pinch': 7,
            'LT_lip_lower_sneer': 9,
            'LT_lip_lower_side': 11,
            'CT_lip_lower_mid': 13}
            
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
face.orientLoopTransforms([nt.Transform(u'LT_lip_corner_pLoc'), 
                           nt.Transform(u'LT_lip_upper_pinch_pLoc'), 
                           nt.Transform(u'LT_lip_upper_sneer_pLoc'), 
                           nt.Transform(u'LT_lip_upper_side_pLoc'), 
                           nt.Transform(u'CT_lip_upper_mid_pLoc')], (-1, 0, 0))

face.orientLoopTransforms([nt.Transform(u'LT_lip_corner_pLoc'), 
                           nt.Transform(u'LT_lip_lower_pinch_pLoc'), 
                           nt.Transform(u'LT_lip_lower_sneer_pLoc'), 
                           nt.Transform(u'LT_lip_lower_side_pLoc'), 
                           nt.Transform(u'CT_lip_lower_mid_pLoc')], (-1, 0, 0))

# Align for sliding
mesh = pm.PyNode(pGrp.mouthLipsLoop.get()[0]).node()
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
    
#------------------------------------------------------------------------------ 
# Mirror
placementGrp.snapPlacementsToMesh(pGrp)
placementGrp.mirrorAllPlacements(pGrp)

#===============================================================================
# BUILD BNDS
#===============================================================================
