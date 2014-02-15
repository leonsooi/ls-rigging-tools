'''
Created on Dec 31, 2013

@author: Leon
'''

import time

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
            
        self = pm.window(cls._WINDOW, title=cls._TITLE, menuBar=True)
        return pm.uitypes.Window.__new__(cls, self)
    
    def __init__(self):
        '''
        create UI
        '''
        with pm.menu(l='Options') as menuOptions:
            pm.menuItem(l='Symmetry', checkBox=True)
            pm.menuItem(divider=True)
            pm.menuItem(l='Refresh')
            pm.menuItem(l='Reset')
        
        with pm.menu(l='Help') as menuHelp:
            pm.menuItem(l='Documentation')
            pm.menuItem(l='About')
        
        with pm.tabLayout() as mainTab:

            with pm.columnLayout(adj=True) as jawLayout:
                pass
            
            with pm.columnLayout(adj=True) as lipsLayout:
                pass
            
            with pm.columnLayout(adj=True) as eyeLayout:
                
                with pm.frameLayout(label='Geometry', cll=True) as geoFrame:
                    with pm.verticalLayout() as geoLayout:
                        self.sel_eyeball = uitypes.Selector(l='Eyeball')
                        self.sel_edgeloop = uitypes.Selector(l='Edge loop', bc=pm.Callback(self.initJointPlacement))
                        
                with pm.frameLayout(label='Joint Placement', cll=True, visible=False) as jntFrame:
                    with pm.verticalLayout() as jntLayout:
                        self.sel_innerVtx = uitypes.Selector(l='Inner Vtx')
                        self.sel_upperVtx = uitypes.Selector(l='Upper Vtx')
                        self.sel_outerVtx = uitypes.Selector(l='Outer Vtx')
                        self.sel_lowerVtx = uitypes.Selector(l='Lower Vtx')
                        
                with pm.frameLayout(label='Deformation', cll=True) as skinFrame:
                    with pm.verticalLayout() as skinLayout:
                        self.float_blinkHeight = pm.floatSliderGrp(l='Blink height', field=True, cw3=(60,40,140), 
                                                                   min=0, max=1, v=0.25, precision=2)
                        self.int_rigidLoops = pm.intSliderGrp(l='Rigid loops', field=True, cw3=(60,40,140),
                                                                 min=1, max=12, fieldMaxValue=99, v=4)
                        self.int_falloffLoops = pm.intSliderGrp(l='Falloff loops', field=True, cw3=(60,40,140),
                                                                 min=1, max=12, fieldMaxValue=99, v=4)
                        self.btn_updateEyelidCrv = pm.button(l='Show Eyelid Curve', en=False)
                        self.btn_updateMidCrv = pm.button(l='Show Mid Curve', en=False)
                        self.btn_updateWeights = pm.button(l='Update Skin Weights', en=False)
                        self.chk_useSkinLayers = pm.checkBox(l='Use ngSkinLayers', v=True)
                        
                with pm.frameLayout(label='Rig', cll=True) as rigFrame:
                    with pm.verticalLayout() as rigLayout:
                        self.btn_namePrefix = pm.textFieldGrp(l='Name Prefix', adj=2, cw2=(60,60))
                        self.btn_createRig = pm.button(l='Build Rig', c=pm.Callback(self.createEyeRigCmd))
            
            with pm.columnLayout(adj=True) as browsLayout:
                pass
        
        mainTab.setTabLabel((jawLayout,'Jaw'))
        mainTab.setTabLabel((lipsLayout,'Lips'))
        mainTab.setTabLabel((eyeLayout,'Eyes'))
        mainTab.setTabLabel((browsLayout,'Brows'))
        mainTab.setSelectTab(eyeLayout)
        
        self.show()
    
    def initJointPlacement(self):
        '''
        '''
        edgeLoop = self.sel_edgeloop.getSelection()
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
        # pm.select(innerVtx, upperVtx, outerVtx, lowerVtx)
        # reselect edge loop, so it looks like nothing happened
        pm.select(edgeLoop, r=True)
        
        # update display
        self.sel_innerVtx.setSelection(innerVtx)
        self.sel_upperVtx.setSelection(upperVtx)
        self.sel_outerVtx.setSelection(outerVtx)
        self.sel_lowerVtx.setSelection(lowerVtx)
    
    def getClosestCV(self, crv, pt):
        '''
        crv - nt.nurbsCurve
        pt - pm.dt.Point
        returns nt.nurbsCurveCV closest to pt
        '''
        allCVPts = crv.getCVs()
        cvId = allCVPts.index(min(allCVPts, key=lambda p: (pt-p).length()))
        return crv.cv[cvId]
    
    def createEyeRigCmd(self):
        
        # hard code name for now
        name = self.btn_namePrefix.getText()
        if name == '':
            name = 'LT_eye'
        # get data from ui
        eyePivot = self.sel_eyeball.getSelection()[0]
        edgeLoop = self.sel_edgeloop.getSelection()
        blinkLine = self.float_blinkHeight.getValue()
        rigidLoops = self.int_rigidLoops.getValue()
        falloffLoops = self.int_falloffLoops.getValue()
        influenceLoops = rigidLoops + falloffLoops
        
        pm.progressWindow(title='Rigging eyelid', max=3, status='\nCreate bind joints...')
        # first run will mess up UI, refresh to redraw window properly
        pm.refresh()
        
        aimLocs, aimJnts, drvCrv = eye.constructEyelidsDeformer(name, eyePivot, edgeLoop)
        
        pm.progressWindow(e=True, step=1, status='\nCreate driver joints...')
        
        # get cv selections for inner, upper, outer, lower
        innerPos = self.sel_innerVtx.getSelection().getPosition()
        innerCV = self.getClosestCV(drvCrv, innerPos)
        upperPos = self.sel_upperVtx.getSelection().getPosition()
        upperCV = self.getClosestCV(drvCrv, upperPos)
        outerPos = self.sel_outerVtx.getSelection().getPosition()
        outerCV = self.getClosestCV(drvCrv, outerPos)
        lowerPos = self.sel_lowerVtx.getSelection().getPosition()
        lowerCV = self.getClosestCV(drvCrv, lowerPos)
        
        # select cvs for inner upper outer lower
        cornerCVs = [innerCV, upperCV, outerCV, lowerCV]
        eyePivotVec, sections, targetCrv, drvJnts, drvSkn = eye.constructEyelidsRig(name, eyePivot, cornerCVs)
        # returned variables above need to be connected to masterGrp
        # so that we can reweight later
        
        pm.progressWindow(e=True, step=1, status='\nWeight driver joints...')
        
        # reweighting (just to get the angles)
        # though it would be better to get the angles from the previous function
        # but that was not done properly
        up, lw, drvSkn = eye.reweightAimCurve(eyePivotVec, sections, targetCrv, drvJnts, drvSkn)
        upperAngle = max(up) * 1.05
        lowerAngle = max(lw) * 1.05
        
        pm.progressWindow(e=True, endProgress=True)
        
        # get vertex loops
        pm.select(edgeLoop, r=True)
        meval('ConvertSelectionToVertices')
        root = eye.constructVertexLoops(influenceLoops)
        pm.select(cl=True)
        
        # calculate generation weights (for layer mask)
        generationWeights = [1] * rigidLoops
        linearFalloff = [float(index)/(falloffLoops+1) for index in range(falloffLoops,0,-1)]
        smoothFalloff = pm.dt.smoothmap(0, 1, linearFalloff)
        generationWeights += smoothFalloff
        
        # assume that skn weights are already set up
        eye.setMeshWeights(root, aimJnts, generationWeights)
        
        masterGrp = eye.rigCleanup(name, aimJnts, drvJnts, aimLocs, drvSkn, targetCrv)
        
        # build eyeball rig
        grp_eye, grp_aimEyeTgt = eye.buildEyeballRig(name, eyePivot, masterGrp, cornerCVs)
        
        eye.setConnections(masterGrp, drvJnts, upperAngle, lowerAngle, blinkLine)
        
        eye.addAutoEyelids(name, masterGrp)
        
        eye.createGUI(name, masterGrp)

        # update UI buttons
        self.btn_updateWeights.setEnable(True)
        self.btn_updateMidCrv.setEnable(True)
        self.btn_updateEyelidCrv.setEnable(True)
        self.btn_createRig.setLabel('Rebuild Rig')
        