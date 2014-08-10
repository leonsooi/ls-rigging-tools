'''

'''
import pymel.core as pm

def symmetrizeXfosOnLayer():
    '''
    set up layer where right_ctrls mirror left_ctrls
    '''
    allCtrls = pm.PyNode('CT_face_ctrl').getChildren(ad=True, type='nurbsCurve')
    allCtrls = set([crv.getParent() for crv in allCtrls])
    
    # new group to hold mirrored locs
    symLocGrp = pm.group(em=True, n='RT_symmetryLoc_grp')
    
    allRightCtrls = [crv for crv in allCtrls if 'RT_' in crv.name()]
    symMatrix = pm.createNode('fourByFourMatrix', n='CT_symmetryMatrix_mat')
    symMatrix.in00.set(-1)
    
    for rightCtl in allRightCtrls:
        leftCtl = pm.PyNode(rightCtl.replace('RT_', 'LT_'))
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
        pm.parentConstraint(loc, rightCtl, l='Symmetry', weight=1)