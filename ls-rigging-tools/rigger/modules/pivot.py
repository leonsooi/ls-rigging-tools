'''
Created on May 12, 2014

@author: Leon

Pivot allows for a bnd to be rotated or scaled from a different pivot point
Pivots behave like pri_ctls, but are represented as locators
'''
import pymel.core as pm
import pymel.core.nodetypes as nt
import face

def addInnerLipsPivots():
    bnds = [nt.Joint(u'CT_upper_lip_bnd'),
            nt.Joint(u'LT_upper_sneer_lip_bnd'),
            nt.Joint(u'LT_upper_pinch_lip_bnd'),
            nt.Joint(u'LT_corner_lip_bnd'),
            nt.Joint(u'LT_lower_pinch_lip_bnd'),
            nt.Joint(u'LT_lower_sneer_lip_bnd'),
            nt.Joint(u'CT_lower_lip_bnd'),
            nt.Joint(u'RT_lower_sneer_lip_bnd'),
            nt.Joint(u'RT_lower_pinch_lip_bnd'),
            nt.Joint(u'RT_corner_lip_bnd'),
            nt.Joint(u'RT_upper_pinch_lip_bnd'),
            nt.Joint(u'RT_upper_sneer_lip_bnd')]
    for eachBnd in bnds:
        addPivotToBnd(eachBnd, 'innerPivot')
        
def addRollLipsPivots():
    bnds = [nt.Joint(u'CT_upper_lip_bnd'),
            nt.Joint(u'LT_upper_sneer_lip_bnd'),
            nt.Joint(u'LT_upper_pinch_lip_bnd'),
            nt.Joint(u'LT_lower_pinch_lip_bnd'),
            nt.Joint(u'LT_lower_sneer_lip_bnd'),
            nt.Joint(u'CT_lower_lip_bnd'),
            nt.Joint(u'RT_lower_sneer_lip_bnd'),
            nt.Joint(u'RT_lower_pinch_lip_bnd'),
            nt.Joint(u'RT_upper_pinch_lip_bnd'),
            nt.Joint(u'RT_upper_sneer_lip_bnd')]
    for eachBnd in bnds:
        addPivotToBnd(eachBnd, 'rollPivot')

def addPivotToBnd(bnd, name='_Pivot'):
    '''
    '''
    # create loc
    loc = pm.spaceLocator(n=bnd+'_'+name+'_loc')
    loc_grp = pm.group(loc, n=bnd+'_'+name+'_grp')
    loc_hm = pm.group(loc_grp, n=bnd+'_'+name+'_hm')
    
    # size
    radius = bnd.radius.get()
    loc.localScale.set(3*[radius])
    
    bnd | loc_hm
    pm.makeIdentity(loc_hm, t=1, r=1, s=1, a=0)
    loc_hm.setParent(world=True)
    
    bnd.addAttr('pivot_'+name, at='message')
    loc.message >> bnd.attr('pivot_'+name)
    
    return loc



def connectBndToPivot(bnd, pivot):
    '''
    basically the same at face.connectBndToPriCtl
    but don't drive primary controls
    '''
    
    # bnd's "local" matrix within pivot
    bnd_wMat = bnd.getMatrix(ws=True)
    pivot_wMat = pivot.getMatrix(ws=True)
    bnd_lMat = bnd_wMat * pivot_wMat.inverse()
    lMatNd = pm.createNode('fourByFourMatrix', n=bnd.replace('_bnd', '_lMat_in_' + pivot.nodeName()))
    # populate "local" matrix
    for i in range(4):
        for j in range(4):
            lMatNd.attr('in%d%d' % (i, j)).set(bnd_lMat[i][j])
    # bnd's "local-inverse" matrix
    lInvMatNd = pm.createNode('inverseMatrix', n=bnd.replace('_bnd', '_lInvMat_in_' + pivot.nodeName()))
    lMatNd.output >> lInvMatNd.inputMatrix
    # for bnd to pivot around pivot,
    # the matrix is lMat * pivotMat * lInvMat
    mmNd = pm.createNode('multMatrix', n=bnd.replace('_bnd', '_calc_mm'))
    lMatNd.output >> mmNd.i[0]
    pivot.matrix >> mmNd.i[1]
    lInvMatNd.outputMatrix >> mmNd.i[2]
    # decompose matrix before passing into bw
    dmNd = pm.createNode('decomposeMatrix', n=bnd.replace('_bnd', '_calc_dm'))
    mmNd.o >> dmNd.inputMatrix
    # get bw nodes to connect to
    channels = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']
    bwNodes = {}
    for eachChannel in channels:
        bwNodes[eachChannel] = bnd.attr(eachChannel + '_bwMsg').get()
    # get index to connect to
    existingInputs = bwNodes['tx'].i.inputs()
    nextIndex = len(existingInputs)
    # actual connections
    dmNd.otx >> bwNodes['tx'].i[nextIndex]
    dmNd.oty >> bwNodes['ty'].i[nextIndex]
    dmNd.otz >> bwNodes['tz'].i[nextIndex]
    dmNd.orx >> bwNodes['rx'].i[nextIndex]
    dmNd.ory >> bwNodes['ry'].i[nextIndex]
    dmNd.orz >> bwNodes['rz'].i[nextIndex]
    dmNd.osx >> bwNodes['sx'].i[nextIndex]
    dmNd.osy >> bwNodes['sy'].i[nextIndex]
    dmNd.osz >> bwNodes['sz'].i[nextIndex]
    # channel box separator
    bnd.addAttr(pivot.nodeName() + '_weights', at='double', k=True, dv=0)
    bnd.setAttr(pivot.nodeName() + '_weights', lock=True)
    # connect weight to be blended to 0
    for eachChannel in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
        bnd.addAttr(pivot.nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=1)
        bnd.attr(pivot.nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
    # scales need a minus 1, to be normalized to 0 for blending
    for eachChannel in ['sx', 'sy', 'sz']:
        adl = pm.createNode('addDoubleLinear', n=bnd.replace('_bnd', '_%s_adl' % eachChannel))
        adl.input2.set(-1)
        dmNd.attr('o%s' % eachChannel) >> adl.input1
        adl.output >> bwNodes[eachChannel].i[nextIndex]
        bnd.addAttr(pivot.nodeName() + '_weight_' + eachChannel, at='double', k=True, min=-1, max=2, dv=1)
        bnd.attr(pivot.nodeName() + '_weight_' + eachChannel) >> bwNodes[eachChannel].weight[nextIndex]
    