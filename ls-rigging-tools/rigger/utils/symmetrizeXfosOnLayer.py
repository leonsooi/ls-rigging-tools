'''
'''
import pymel.core as pm

def symmetrizeXfosOnLayer():
    '''
    set up animation layer for right_ctrls to mirror left_ctrls
    '''
    # CT_face_ctrl is a top level node for all controls
    # all face controls are curves below this node
    allCtrls = pm.PyNode('CT_face_ctrl').getChildren(ad=True, type='nurbsCurve')
    allCtrls = set([crv.getParent() for crv in allCtrls])
    
    # prefix for left and right sides
    leftPrefix = 'LT_'
    rightPrefix = 'RT_'
    allRightCtrls = [crv for crv in allCtrls if rightPrefix in crv.name()]
    # ASSUME that the controls do not have ANY locked channels!
    
    # new group to hold mirrored locs
    symLocGrp = pm.group(em=True, n='RT_symmetryLoc_grp')
    
    # matrix to scale -1 in x
    symMatrix = pm.createNode('fourByFourMatrix', n='CT_symmetryMatrix_mat')
    symMatrix.in00.set(-1)
    
    for rightCtl in allRightCtrls:
        leftCtl = pm.PyNode(rightCtl.replace(rightPrefix, leftPrefix))
        loc = pm.spaceLocator(n=rightCtl+'_symLoc')
        symLocGrp | loc
        # connect to left side
        mm = pm.createNode('multMatrix', n=rightCtl+'_sym_mm')
        symMatrix.output >> mm.matrixIn[0]
        leftCtl.worldMatrix >> mm.matrixIn[1]
        symMatrix.output >> mm.matrixIn[2]
        dcm = pm.createNode('decomposeMatrix', n=rightCtl+'_sym_dcm')
        mm.matrixSum >> dcm.inputMatrix
        dcm.ot >> loc.t
        dcm.outputRotate >> loc.r
        # constrain on anim layer
        # ASSUME that layer named 'symmetry' already exists!!!
        pm.parentConstraint(loc, rightCtl, l='Symmetry', weight=1)