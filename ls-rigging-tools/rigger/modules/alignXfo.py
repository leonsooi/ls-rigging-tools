'''
Created on Oct 5, 2014

@author: Leon
'''

import pymel.core as pm
import pymel.core.nodetypes as nt
from pymel.core.language import Mel
mel = Mel()

import secCtl as secCtl
reload(secCtl)


pLoc = nt.Joint(u'LT_upperOuter_eyelid_bnd')
beforeObj = nt.Joint(u'LT_upper_eyelid_bnd')
afterObj = nt.Joint(u'LT_outer_eyelid_bnd')

def alignSecCtlAlongXfos(ctl, prevXfo=None, nextXfo=None):
    '''
    xAxis of ctl will always aim towards nextXfo, or away from prevXfo
    zAxis of ctl is used for upAxis
    '''
    # add offsets
    autoOffset = secCtl.addOffset(ctl, 'child', '_autoAlign')
    manualOffset = secCtl.addOffset(ctl, 'child', '_manualAlign')
    
    # manualOffset uses ctl's rotations
    ctl.r >> manualOffset.r
    
    # autoOffset uses aim constraints
    if prevXfo and nextXfo:
        # have to blend between two xfos
        blendTwoAimConstraints(autoOffset, prevXfo, nextXfo)
    else:
        # direct aim constraint to either
        if prevXfo:
            pm.aimConstraint(prevXfo, autoOffset, 
                             mo=True,
                             aim=(-1,0,0),
                             u=(0,0,1), 
                             wut='objectrotation',
                             wuo=ctl,
                             wu=(0,0,1))
        elif nextXfo:
            pm.aimConstraint(nextXfo, autoOffset, 
                             mo=True,
                             aim=(1,0,0),
                             u=(0,0,1), 
                             wut='objectrotation',
                             wuo=ctl,
                             wu=(0,0,1))
    
def blendTwoAimConstraints(autoOffset, prevXfo, nextXfo):
    '''
    '''
    pass

# align along
def alignAlongXfos(currXfo, upXfo, prevXfo=None, nextXfo=None):
    '''
    there are problems with world-space-local-space matrixs, etc
    don't use yet!
    
    xAxis is always used for alignment
    zAxis is used as upAxis - aligned to upXfo's zAxis
    '''
    # create vectors pmas
    if prevXfo:
        prevPma = getVectorBetweenTwoXfos(prevXfo, currXfo)
        xAxis = prevPma.output3D
    if nextXfo:
        nextPma = getVectorBetweenTwoXfos(currXfo, nextXfo)
        xAxis = nextPma.output3D
        
    # calculate vectors if blend is needed
    if prevXfo and nextXfo:
        # slerp blend between the two vectors
        slerp = pm.createNode('animBlendNodeAdditiveRotation',
                              n=currXfo+'_blendBeforeAndAfterVec_slerp')
        prevPma.output3D >> slerp.inputA
        nextPma.output3D >> slerp.inputB
        xAxis = slerp.output
        
    # upXfo's zAxis will be used for zAxis,
    # but we don't no whether it is perp. to xAxis
    # we'll just use it as upAxis to get the y-axis first
    
    # calculcate up-axis
    upVpd = pm.createNode('vectorProduct', n=currXfo+'_calcUpAxis_vpd')
    upXfo.worldMatrix >> upVpd.matrix
    upVpd.input1.set(0,0,1)
    upVpd.o.set(3)
    up_axis = upVpd.output
    
    # calculate y-axis
    yAxisVpd = pm.createNode('vectorProduct', n=currXfo+'_calcYAxis_vpd')
    xAxis >> yAxisVpd.input1
    up_axis >> yAxisVpd.input2
    yAxisVpd.o.set(2)
    y_axis = yAxisVpd.output
    
    # calculate z-axis
    zAxisVpd = pm.createNode('vectorProduct', n=currXfo+'_calcZAxis_vpd')
    xAxis >> zAxisVpd.input1
    y_axis >> zAxisVpd.input2
    zAxisVpd.o.set(2)
    z_axis = zAxisVpd.output
    
    # construct a matrix in worldSpace
    wsMat = pm.createNode('fourByFourMatrix', n=currXfo+'_wsFbfm')
    # x-vector
    try:
        # try slerp result first
        xAxis.outputX >> wsMat.in00
        xAxis.outputY >> wsMat.in01
        xAxis.outputZ >> wsMat.in02
    except AttributeError:
        # try pma result
        xAxis.output3Dx >> wsMat.in00
        xAxis.output3Dy >> wsMat.in01
        xAxis.output3Dz >> wsMat.in02
    # y-vector
    y_axis.ox >> wsMat.in10
    y_axis.oy >> wsMat.in11
    y_axis.oz >> wsMat.in12
    # z-vector
    z_axis.ox >> wsMat.in20
    z_axis.oy >> wsMat.in21
    z_axis.oz >> wsMat.in22
    
    # decompose
    dcm = pm.createNode('decomposeMatrix', n=currXfo+'_orientMat_dcm')
    wsMat.output >> dcm.inputMatrix
    dcm.outputRotate >> currXfo.r
    
    
    
def getVectorBetweenTwoXfos(xfoA, xfoB):
    '''
    calculates vector using pma
    returns pma
    '''
    # get world space positions for xfos
    pmmA = pm.createNode('pointMatrixMult', n=xfoA+'_wsPos_pmm')
    pmmB = pm.createNode('pointMatrixMult', n=xfoB+'_wsPos_pmm')
    xfoA.worldMatrix >> pmmA.inMatrix
    xfoB.worldMatrix >> pmmB.inMatrix
    # get vector between the two positions
    pma = pm.createNode('plusMinusAverage', n=xfoA+'_to_'+xfoB+'_vec_pma')
    pmmA.output >> pma.input3D[0]
    pmmB.output >> pma.input3D[1]
    pma.operation.set(2)
    return pma