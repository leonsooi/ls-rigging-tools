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
#--------------------------------------------------------------------- LOOP LOCS
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
#----------------------------------------------------------------- INDIRECT LOCS
placementGrp.addIndirectPlacements(pGrp)

#------------------------------------------------------------------------------ 
#---------------------------------------------------------------- ALIGN NEW LOCS
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
slidingBnds = data.slidingBnds
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

#------------------------------------------------------- SET PRIMARY CTL WEIGHTS
# all weights from facerigB_v010

allWeights = data.priCtlBndWeights
for attr, val in allWeights.items():
    pm.Attribute(attr).set(val)

#------------------------------------------------------------------- RIG CLEANUP
face.cleanFaceRig()

# smooth necessary layers
face.selectVertsClosestToBnds(mll) # use this as a mask while smoothing

# skin weights cleanup - mathilda_facerigB_v005.0003.ma
# motion weights cleanup

#===============================================================================
# POST-BUILD ADD-ON FEATURES
# mathilda_facerigB_v008.ma
#===============================================================================

#--------------------------------------------------------- ADD LEFT EYE DEFORMER
edgeLoop = [pm.PyNode(edge) for edge in pGrp.leftEyelidLoop.get()]
eyePivot = pm.PyNode('LT_eyeball_geo')
rigidLoops = 2
falloffLoops = 4
eye.buildEyeRigCmd('LT_eye', eyePivot, edgeLoop, rigidLoops, falloffLoops)

#---------------------------------------------------------- RIGHT EYE DEFORMER
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

#------------------------------------------ EYEBALL RIG (SIMPLE AIM CONSTRAINTS)
eye.buildEyeballRig()
eye.addEyeAim(prefix='LT_', distance=25)
eye.addEyeAim(prefix='RT_', distance=25)

#----------------------------------------------------------------- STICKY LIPS
sticky.Sticky(up_bnd=pm.PyNode('CT_upper_lip_bnd'), 
                  low_bnd=pm.PyNode('CT_lower_lip_bnd'), 
                  center=pm.PyNode('CT_jaw_pri_ctrl'))
sticky.Sticky(up_bnd=pm.PyNode('LT_upper_side_lip_bnd'), 
                  low_bnd=pm.PyNode('LT_lower_side_lip_bnd'), 
                  center=pm.PyNode('CT_jaw_pri_ctrl'))
sticky.Sticky(up_bnd=pm.PyNode('LT_upper_sneer_lip_bnd'), 
                  low_bnd=pm.PyNode('LT_lower_sneer_lip_bnd'), 
                  center=pm.PyNode('CT_jaw_pri_ctrl'))
sticky.Sticky(up_bnd=pm.PyNode('LT_upper_pinch_lip_bnd'), 
                  low_bnd=pm.PyNode('LT_lower_pinch_lip_bnd'), 
                  center=pm.PyNode('CT_jaw_pri_ctrl'))
sticky.Sticky(up_bnd=pm.PyNode('RT_upper_side_lip_bnd'), 
                  low_bnd=pm.PyNode('RT_lower_side_lip_bnd'), 
                  center=pm.PyNode('CT_jaw_pri_ctrl'))
sticky.Sticky(up_bnd=pm.PyNode('RT_upper_sneer_lip_bnd'), 
                  low_bnd=pm.PyNode('RT_lower_sneer_lip_bnd'), 
                  center=pm.PyNode('CT_jaw_pri_ctrl'))
sticky.Sticky(up_bnd=pm.PyNode('RT_upper_pinch_lip_bnd'), 
                  low_bnd=pm.PyNode('RT_lower_pinch_lip_bnd'), 
                  center=pm.PyNode('CT_jaw_pri_ctrl'))

sticky.addStickyToFRS()

#------------------------------------------------------------------ AUTO EYELIDS
# create pose reader on eye joint
import rigger.modules.poseReader as poseReader
reload(poseReader)
xfo = pm.PyNode('LT_eyeball_bnd')
poseReader.radial_pose_reader(xfo)
xfo = pm.PyNode('RT_eyeball_bnd')
poseReader.radial_pose_reader(xfo)
eye.addFleshyEye()
# adjust sdk tangents

#------------------------------------------------------------------- MOUTH MOVER
# create offset for mouth pri control
import rigger.modules.priCtl as priCtl
reload(priCtl)
pCtl = pm.PyNode('CT_mouthMover_pri_ctrl')
offsetGrp = priCtl.addOffset(pCtl, 'child', '_autoRotate')
rt.connectSDK(pCtl.tx, offsetGrp.ry, {-1:-15, 0:0, 1:15})
rt.connectSDK(pCtl.tx, offsetGrp.rz, {-1:-15, 0:0, 1:15})
rt.connectSDK(pCtl.tx, offsetGrp.tz, {-1:0.25, 0:0, 1:0.25})

# create offset for cheek pri ctrl
pCtl = pm.PyNode('LT_cheek_pri_ctrl')
offsetGrp = priCtl.addOffset(pCtl, 'child', '_autoVolume')
rt.connectSDK(pCtl.ty, offsetGrp.tz, {-1:-0.25, 0:0, 1:0.5})

# create offset for cheek pri ctrl
pCtl = pm.PyNode('RT_cheek_pri_ctrl')
offsetGrp = priCtl.addOffset(pCtl, 'child', '_autoVolume')
rt.connectSDK(pCtl.ty, offsetGrp.tz, {-1:-0.25, 0:0, 1:0.5})

#------------------------------------------------------------ EYE SQUASH LATTICE
import rigger.modules.eyeLattice as eyeLattice
reload(eyeLattice)
eyeGeos = [nt.Transform(u'LT_eyeball_geo'), 
           nt.Transform(u'RT_eyeball_geo')]
faceGeos = [nt.Mesh(u'LT_eyeIris_geoShape'),
            nt.Mesh(u'RT_eyeIris_geoShape'),
            nt.Mesh(u'LT_eyeLash_geoShape'),
            nt.Mesh(u'RT_eyeLash_geoShape'),
            nt.Mesh(u'CT_face_geoShape')]
latticeGrp = eyeLattice.createLattice(eyeGeos, faceGeos)

# set latticeGrp xform
from pymel.core.datatypes import Matrix
latticeGrpXform = Matrix([[1.31887392826, 0.0, 0.0, 0.0],
                            [0.0, 2.05176168568, 0.0, 0.0],
                            [0.0, 0.0, 2.44573893765, 0.0],
                            [0.00162200337874, -111.225338771, -5.69868431046, 1.0]])
latticeGrp.setMatrix(latticeGrpXform, worldSpace=True)
eyeShaperCtg = eyeLattice.createLatticeControls()
nt.Transform(u'CT_face_ctrl') | eyeShaperCtg

#--------------------------------------------------------- PUPIL AND IRIS DILATE
import rigger.modules.dilate as dilate
reload(dilate)

# left iris
geo = nt.Mesh(u'LT_eyeball_geoShape')
tipGeo = geo.vtx[381]
ctl = nt.Transform(u'LT_eye_ctl')
name = '_iris'
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:3.75}}
weights = [1, 1, 1, 1, 1, .95, 0.58, 0.3, .15, .06]
addGeos = [nt.Mesh(u'LT_eyeIris_geoShape')]
dilate.create(ctl, tipGeo, weights, name, keys, addGeos, True)

# left pupil
geo = nt.Mesh(u'LT_eyeIris_geoShape')
tipGeo = geo.vtx[40]
ctl = nt.Transform(u'LT_eye_ctl')
name = '_pupil'
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:2}}
weights = [1, 1, 0.25]
dilate.create(ctl, tipGeo, weights, name, keys)

# right iris
geo = nt.Mesh(u'RT_eyeball_geoShape')
tipGeo = geo.vtx[381]
ctl = nt.Transform(u'RT_eye_ctl')
name = '_iris'
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:3.75}}
weights = [1, 1, 1, 1, 1, .95, 0.58, 0.3, .15, .06]
addGeos = [nt.Mesh(u'RT_eyeIris_geoShape')]
dilate.create(ctl, tipGeo, weights, name, keys, addGeos, True)

# right pupil
geo = nt.Mesh(u'RT_eyeIris_geoShape')
tipGeo = geo.vtx[40]
ctl = nt.Transform(u'RT_eye_ctl')
name = '_pupil' 
keys = {'sx': {0.01:0.01, 1:1, 2:2},
        'sy': {0.01:0.01, 1:1, 2:2},
        'sz': {0.01:0.01, 1:1, 2:2}}
weights = [1, 1, 0.25]
dilate.create(ctl, tipGeo, weights, name, keys)