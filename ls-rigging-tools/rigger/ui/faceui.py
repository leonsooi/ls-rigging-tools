'''
Created on Dec 31, 2013

@author: Leon
'''

import time
import maya.cmds as mc
import pymel.core as pm
from maya.mel import eval as meval

mel = pm.language.mel

import cgm.lib.position as cgmPos

import uitypes
import rigger.modules.eye as eye
reload(uitypes)
reload(eye)
import rigger.modules.face as face
reload(face)
import utils.symmetry as sym
reload(sym)

import rigger.lib.context as context
reload(context)
import rigger.utils.weights as weights
reload(weights)

import rigger.modules.placementGrp as placementGrp
reload(placementGrp)

from ngSkinTools.mllInterface import MllInterface
from ngSkinTools.importExport import XmlImporter

class newUI(pm.uitypes.Window):
    """
    """
    
    # constants 
    _TITLE = 'Face Rig System'
    _WINDOW = 'lsFRS_win'
    
    _LTPREFIX = 'LT_'
    _RTPREFIX = 'RT_'
    '''
    imageRefPath = 'C:/Users/Leon/Pictures/FRS/Images/'
    
    mesh = pm.PyNode('CT_face_geo')
    lf_eye = pm.PyNode('LT_eyeball_geo')
    rt_eye = pm.PyNode('RT_eyeball_geo')
    '''
    def __new__(cls, baseFilePath, placerMapping, indMapping, meshNames):
        '''
        delete old window and create new instance
        '''
        if pm.window(cls._WINDOW, exists=True):
            pm.deleteUI(cls._WINDOW)
            
        self = pm.window(cls._WINDOW, title=cls._TITLE, menuBar=True)

        return pm.uitypes.Window.__new__(cls, self)
    
    def __init__(self, baseFilePath, placerMapping, indMapping, meshNames):
        '''
        create UI and init vars
        '''
        self.imageRefPath = baseFilePath
        self.placerMapping = placerMapping
        self.indMapping = indMapping
        self.mesh = meshNames['face']
        self.lf_eye = meshNames['leftEye']
        self.rt_eye = meshNames['rightEye']
        self.locTweakWidgets = {}
        self.placementGrp = None
        
        with pm.menu(l='Options') as menuOptions:
            pm.menuItem(l='Refresh')
            pm.menuItem(l='Reset')
        
        with pm.menu(l='Help') as menuHelp:
            pm.menuItem(l='Documentation')
            pm.menuItem(l='About')
        
        with pm.tabLayout() as mainTab:
            
            with pm.columnLayout(adj=True) as geoSelectionLayout:
                pass
            
            with pm.columnLayout(adj=True) as jntPlacementLayout:
            
                with pm.verticalLayout(ratios=(1,10,1), spacing=10) as jntPlacementVertLayout:
                    
                    #self.chk_symmetry = pm.checkBox(l='Symmetry', v=True)
                    with pm.horizontalLayout() as startPlacementLayout:
                        self.btn_startJntPlacement = pm.button(l='Start Joint Placement', 
                                                               c=pm.Callback(self.startJointPlacement),
                                                               w=180)
                    
                    self.img_jntReference = pm.image(image=self.imageRefPath+'default.jpg')
                
                    with pm.rowLayout(numberOfColumns=3, adj=2) as jntRowLayout:
                        self.btn_jntScrollLt = pm.button(l='<<', w=40, en=False)
                        self.txt_jntCurrent = pm.text(label='Click "Start Joint Placement" above to begin.', align='center')
                        self.btn_jntScrollRt = pm.button(l='>>', w=40, c=pm.Callback(self.selectNextItem), en=False)
                
                pm.separator(style='in')
                
                with pm.horizontalLayout(ratios=(1,5), spacing=5):
                    
                    with pm.verticalLayout():
                        # left labels
                        self.locTweakWidgets['txt_position'] = pm.text(label='Position', 
                                                                       align='right', en=False)
                        self.locTweakWidgets['txt_orient'] = pm.text(label='Orient', 
                                                                       align='right', en=False)
                        self.locTweakWidgets['txt_scale'] = pm.text(label='Scale', 
                                                                       align='right', en=False)
                        self.locTweakWidgets['txt_mirror'] = pm.text(label='Mirror', 
                                                                       align='right', en=False)
                    with pm.verticalLayout():
                        # right buttons
                        with pm.horizontalLayout():
                            self.locTweakWidgets['btn_prevCV'] = pm.button(l='Prev CV', en=False,
                                                                           c=pm.Callback(self.stepCV, -1))
                            self.locTweakWidgets['btn_nextCV'] = pm.button(l='Next CV', en=False,
                                                                           c=pm.Callback(self.stepCV, 1))
                            self.locTweakWidgets['btn_snapToVtx'] = pm.button(l='Snap to Vtx', en=False)
                            self.locTweakWidgets['btn_user'] = pm.button(l='User', en=False)
                            
                        with pm.horizontalLayout():
                            self.locTweakWidgets['btn_normal'] = pm.button(l='Normal', en=False)
                            self.locTweakWidgets['btn_normal_yup'] = pm.button(l='Normal + Y-up', en=False)
                            self.locTweakWidgets['btn_world'] = pm.button(l='World', en=False)
                            self.locTweakWidgets['btn_orient_user'] = pm.button(l='User', en=False)
                            
                        with pm.horizontalLayout():
                            self.locTweakWidgets['float_scale'] = pm.floatSliderGrp(f=True,
                                                                    min=0.01, max=1.0, v=0.5,
                                                                pre=2, fmx=10.0, en=False,
                                                                dc=pm.Callback(self.editLocScale))
                        with pm.horizontalLayout():
                            self.locTweakWidgets['btn_mirLtToRt'] = pm.button(l='Left to Right', en=False,
                                                                              c=pm.Callback(self.mirrorLocs))
                            self.locTweakWidgets['btn_mirRtToLt'] = pm.button(l='Right to Left', en=False)
                
                pm.separator(style='in')
                
                
                
                with pm.verticalLayout(spacing=5) as buildRigVertLayout:
                    self.btn_updateLocs = pm.button(l='Update All Locators', en=False)
                    self.btn_buildRig = pm.button(l='Build Rig', c=pm.Callback(self.buildRig), en=False)
            
            with pm.columnLayout(adj=True) as deformationLayout:
                pass
            
            with pm.columnLayout(adj=True) as motionLayout:
                pass
            
            with pm.columnLayout(adj=True) as actionsLayout:
                pass
                
        mainTab.setTabLabel((geoSelectionLayout,'Geometry'))
        mainTab.setTabLabel((jntPlacementLayout,'Joints'))
        mainTab.setTabLabel((deformationLayout,'Deformation'))
        mainTab.setTabLabel((motionLayout,'Motion'))
        mainTab.setTabLabel((actionsLayout,'Action Units'))
        mainTab.setSelectTab(jntPlacementLayout)
        
        self.show()
        
        
    def startJointPlacement(self):
        '''
        '''
        self.btn_startJntPlacement.setLabel('Restart Joint Placement')
        self.btn_jntScrollRt.setEnable(True)
        
        self.placementGrp = pm.group(n='CT_placement_grp', em=True)
        self.placementGrp.addAttr('locScale', at='float', dv=0.5)
        self.placementGrp.locScale.set(cb=True)
        
        for btnName, btn in self.locTweakWidgets.items():
            btn.setEnable(True)
        
        jntPlacementContext = context.FaceJointPlacementContext(self.mesh, self, self.placementGrp)
        jntPlacementContext.runContext()
        
    def stepCV(self, stepAmt):
        '''
        '''
        try:
            locs = pm.ls(sl=True)
            for loc in locs:
                attr = loc.cv_id
                currId = attr.get()
                attr.set(currId+stepAmt)
        except:
            mc.warning('No locators on curve selected.')
            
    def mirrorLocs(self):
        placementGrp.mirrorAllPlacements(self.placementGrp)
                    
    def editLocScale(self):
        '''
        '''
        try:
            val = self.locTweakWidgets['float_scale'].getValue()
            self.placementGrp.locScale.set(val)
        except AttributeError as e:
            print e
        
    def selectNextItem(self):
        '''
        '''
        if self.txt_jntCurrent.getLabel() == 'Select mouth lips loop':
            
            self.txt_jntCurrent.setLabel('Select left eyelid loop')
            fullRefPath = self.imageRefPath + "LT_eyeLidLoop.jpg"
            pm.image(self.img_jntReference, image=fullRefPath, e=True)
            
            # assign selection to placement_grp attr
            sel = pm.ls(sl=True, fl=True)
            self.placementGrp.addAttr('mouthLipsLoop', dt='stringArray')
            self.placementGrp.attr('mouthLipsLoop').set(len(sel), *sel, type='stringArray')
            pm.select(cl=True)
            
            placementGrp.addMouthLoopPlacements(self.placementGrp)
            
        elif self.txt_jntCurrent.getLabel() == 'Select left eyelid loop':
            # READY!
            self.txt_jntCurrent.setLabel('Ready to Build!')
            fullRefPath = self.imageRefPath + "default.jpg"
            pm.image(self.img_jntReference, image=fullRefPath, e=True)
            self.btn_jntScrollRt.setEnable(False)
            self.btn_updateLocs.setEnable(True)
            self.btn_buildRig.setEnable(True)
            pm.setToolTo('selectSuperContext')
            
            # assign selection to placement_grp attr
            sel = pm.ls(sl=True, fl=True)
            self.placementGrp.addAttr('leftEyelidLoop', dt='stringArray')
            self.placementGrp.attr('leftEyelidLoop').set(len(sel), *sel, type='stringArray')
            
            placementGrp.addEyeLoopPlacements(self.placementGrp)
            # override for mathilda
            # placementGrp.addEyeLoopPlacements(self.placementGrp, [23,15,9,3])
            # mathilda_override
            # pm.PyNode('LT_innerUpper_eyelid_pLoc').cv_id.set(18)
            
            placementGrp.addIndependentPlacers(self.placementGrp, self.indMapping)
            
            # align jaw pLoc
            cons = mc.aimConstraint('CT__mouthMover_pLoc', 'CT__jaw_pLoc',
                                    aim=[0,0,1], u=[1,0,0], wu=[1,0,0])
            mc.delete(cons)
            
            pm.selectMode(object=True)
            mel.setObjectPickMask("Surface", False)
            
            placementGrp.snapPlacementsToMesh(self.placementGrp)
            placementGrp.mirrorAllPlacements(self.placementGrp)
            placementGrp.orientAllPlacements(self.placementGrp)
            
            
    def buildRig(self):
        '''
        '''
        import rigger.builds.human.build as build
        reload(build)
        
        build.build()


