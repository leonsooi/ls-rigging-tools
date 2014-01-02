'''
Created on Dec 31, 2013

@author: Leon
'''

import pymel.core as pm
from maya.mel import eval as meval

import uitypes
import lsAutoRig.modules.eye as eye
reload(uitypes)
reload(eye)

class UI(pm.uitypes.Window):
    """
    """
    
    # constants 
    _TITLE = 'lsFaceRig Modules'
    _WINDOW = 'lsFR_win'
    
    _LTPREFIX = 'LT_'
    _RTPREFIX = 'RT_'
    
    def __new__(cls):
        '''
        delete old window and create new instance
        '''
        if pm.window(cls._WINDOW, exists=True):
            pm.deleteUI(cls._WINDOW)
            
        self = pm.window(cls._WINDOW, title=cls._TITLE)
        return pm.uitypes.Window.__new__(cls, self)
    
    def __init__(self):
        '''
        create UI
        '''
        with pm.tabLayout() as mainTab:
            
            with pm.columnLayout(adj=True) as settingsLayout:
                pass
            
            with pm.columnLayout(adj=True) as jawLayout:
                pass
            
            with pm.columnLayout(adj=True) as lipsLayout:
                pass
            
            with pm.columnLayout(adj=True) as eyeLayout:
                
                with pm.frameLayout(label='Geometry', cll=True) as geoFrame:
                    with pm.verticalLayout() as geoLayout:
                        self.eyeballSel = uitypes.Selector(l='Eyeball')
                        self.edgeloopSel = uitypes.Selector(l='Edge loop', bc=pm.Callback(self.initJointPlacement))
                        
                with pm.frameLayout(label='Joint Placement', cll=True) as jntFrame:
                    with pm.verticalLayout() as jntLayout:
                        self.innerVtxSel = uitypes.Selector(l='Inner Vtx')
                        self.upperVtxSel = uitypes.Selector(l='Upper Vtx')
                        self.outerVtxSel = uitypes.Selector(l='Outer Vtx')
                        self.lowerVtxSel = uitypes.Selector(l='Lower Vtx')
                        
                with pm.frameLayout(label='Rig', cll=True) as rigFrame:
                    with pm.verticalLayout() as rigLayout:
                        self.createRig = pm.button(l='Create Rig', c=pm.Callback(self.createRigCmd))
            
            with pm.columnLayout(adj=True) as browsLayout:
                pass
        
        mainTab.setTabLabel((settingsLayout,'Settings'))
        mainTab.setTabLabel((jawLayout,'Jaw'))
        mainTab.setTabLabel((lipsLayout,'Lips'))
        mainTab.setTabLabel((eyeLayout,'Eyes'))
        mainTab.setTabLabel((browsLayout,'Brows'))
        mainTab.setSelectTab(eyeLayout)
        
        self.show()
    
    def initJointPlacement(self):
        '''
        '''
        edgeLoop = self.edgeloopSel.getSelection()
        pm.select(edgeLoop, r=True)
        meval('ConvertSelectionToVertices')
        vertLoop = pm.ls(sl=True, fl=True)
        
        # determine inner, upper, outer and lower verts
        # find upper, outer, lower first
        upperVtx = max(vertLoop, key=lambda vtx: vtx.getPosition()[1])
        outerVtx = min(vertLoop, key=lambda vtx: vtx.getPosition()[2])
        lowerVtx = min(vertLoop, key=lambda vtx: vtx.getPosition()[1])

        # find out which side is outer on
        if outerVtx.getPosition().x > upperVtx.getPosition().x:
            # inner should be on min x
            innerVtx = min(vertLoop, key=lambda vtx: vtx.getPosition()[0])
        else:
            # inner should be on max x
            innerVtx = max(vertLoop, key=lambda vtx: vtx.getPosition()[0])
            
        # select/display verts
        pm.select(innerVtx, upperVtx, outerVtx, lowerVtx)
        
        # update display
        self.innerVtxSel.setSelection(innerVtx)
        self.upperVtxSel.setSelection(upperVtx)
        self.outerVtxSel.setSelection(outerVtx)
        self.lowerVtxSel.setSelection(lowerVtx)
    
    def getClosestCV(self, crv, pt):
        '''
        crv - nt.nurbsCurve
        pt - pm.dt.Point
        returns nt.nurbsCurveCV closest to pt
        '''
        allCVPts = crv.getCVs()
        cvId = allCVPts.index(min(allCVPts, key=lambda p: (pt-p).length()))
        return crv.cv[cvId]
    
    def createRigCmd(self):
        # hard code name for now
        name = self._LTPREFIX + 'eyelid'
        eyePivot = self.eyeballSel.getSelection()[0]
        edgeLoop = self.edgeloopSel.getSelection()
        
        aimLocs, aimJnts, drvCrv = eye.constructEyelidsDeformer(name, eyePivot, edgeLoop)
        
        # get cv selections for inner, upper, outer, lower
        print self.innerVtxSel.getSelection()
        innerPos = self.innerVtxSel.getSelection().getPosition()
        innerCV = self.getClosestCV(drvCrv, innerPos)
        upperPos = self.upperVtxSel.getSelection().getPosition()
        upperCV = self.getClosestCV(drvCrv, upperPos)
        outerPos = self.outerVtxSel.getSelection().getPosition()
        outerCV = self.getClosestCV(drvCrv, outerPos)
        lowerPos = self.lowerVtxSel.getSelection().getPosition()
        lowerCV = self.getClosestCV(drvCrv, lowerPos)
        
        pm.select(innerCV, upperCV, outerCV, lowerCV, r=True)
        """
        # select 4 cvs on drvCrv
        eyePivotVec, sections, targetCrv, drvJnts, drvSkn = eye.constructEyelidsRig(name, eyePivot)
        # returned variables above need to be connected to masterGrp
        # so that we can reweight later
        
        # reweighting (just to get the angles)
        # though it would be better to get the angles from the previous function
        # but that was not done properly
        up, lw, drvSkn = reweightAimCurve(eyePivotVec, sections, targetCrv, drvJnts, drvSkn)
        upperAngle = max(up) * 1.2 # over rotate by 20%
        lowerAngle = max(lw)
        
        # get vertex loops
        pm.select(edgeLoop, r=True)
        meval('ConvertSelectionToVertices')
        root = constructVertexLoops(loops)
        pm.select(cl=True)
        
        # assume that skn weights are already set up
        setMeshWeights(root, aimJnts)
        
        masterGrp = rigCleanup(name, aimJnts, drvJnts, aimLocs, drvSkn, targetCrv)
        setConnections(masterGrp, drvJnts, upperAngle, lowerAngle)
        """