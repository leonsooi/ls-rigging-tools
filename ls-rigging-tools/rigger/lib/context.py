'''
Created on Mar 8, 2014

@author: Leon
'''

import pymel.core as pm

import spPaint3dContext as spc
import spPaint3dGui as spg

import rigger.modules.placementGrp as placementGrp
reload(placementGrp)


class FaceJointPlacementContext():
    """
    This context is based on spPaint3dContext
    """
    def __init__(self, mesh, ui, grp):
        """
        mesh [PyNode.mesh] - mesh to place joints on
        mesh will be converted added to sp3dObjectList to be used for intersections
        """
        
        self.meshList = spg.sp3dObjectList('target')
        self.meshList.addObj(str(mesh))
        
        # create dragger context
        if pm.draggerContext('FaceJointPlacementContext', exists=True):
            pm.deleteUI('FaceJointPlacementContext')
            
        self.context = pm.draggerContext('FaceJointPlacementContext', pressCommand=self.onPress, name='FaceJointPlacementContext', cursor='crossHair')
        
        self.jointsList = ui.placerMapping
        
        self.targetMesh = mesh
        self.jointIndex = 0
        self.ui = ui
        self.grp = grp
        
        self.camera = pm.PyNode('persp')
        
    def runContext(self):
        """
        Set maya tool to this context
        """
        if pm.draggerContext(self.context, exists=True):
            pm.setToolTo(self.context)

        self.nextJoint()
        
    def onPress(self):
        """
        
        """
        pressPosition = pm.draggerContext(self.context, q=True, anchorPoint=True)
        worldPos, worldDir = spc.getViewportClick(pressPosition[0], pressPosition[1])
        intersected = spc.targetSurfaceLoopIntersect(self.meshList, worldPos, worldDir)
        self.addJoint(pm.dt.Point(intersected.hitPoint.x, intersected.hitPoint.y, intersected.hitPoint.z))
        
    def addJoint(self, position):
        """
        position [pm.dt.Point] - position to place joint
        """
        pm.select(cl=True)
        
        jntName = self.jointsList[self.jointIndex-1][1]
        bindType = self.jointsList[self.jointIndex-1][2]
        orientType = self.jointsList[self.jointIndex-1][3]
        loc = placementGrp.addPlacementLoc(self.grp, jntName, 
                                     position, bindType, orientType)
        placementGrp.snapPLocToVert(loc, self.targetMesh)
        placementGrp.snapOrientPLocOnMesh(loc, self.targetMesh)
        '''
        if 'CT_' in jntName:
            position[0] = 0.0
        
        placementLoc = pm.spaceLocator(n=jntName+'_pLoc')   
        placementLoc.t.set(position)
        # placementLoc.localScale.set(0.05, 0.05, 0.05)
        # create attribute to tell FRS what type of bind this will be
        placementLoc.addAttr('bindType', k=True, at='enum', en='direct=0:indirect=1:independent=2', dv=0)
        placementLoc.addAttr('orientType', k=True, at='enum', en='user=0:sliding=1:normal=2', dv=1)
        self.grp | placementLoc
        '''
        # set camera to focus on new placementLoc
        self.camera.tumblePivot.set(position)
        
        if self.jointIndex >= len(self.jointsList):
            # all joints placed
            # exit and start loops selection
            self.exitContext()
        else:
            self.nextJoint()
        
        if not self.ui.btn_jntScrollLt.getEnable():
            self.ui.btn_jntScrollLt.setEnable(True)
        
    def nextJoint(self):
        '''
        Calls UI to show the next joint's reference
        '''
        currentJointName, refPath = self.jointsList[self.jointIndex][:2]
        fullRefPath = self.ui.imageRefPath + r"%s.jpg" % refPath
        pm.image(self.ui.img_jntReference, image=fullRefPath, e=True)
        self.ui.txt_jntCurrent.setLabel(currentJointName)
        
        self.jointIndex += 1
        
    def exitContext(self):
        '''
        '''
        pm.select(cl=True)
        pm.setToolTo('polySelectContext')
        fullRefPath = self.ui.imageRefPath + "CT__mouthLipLoop.jpg"
        pm.image(self.ui.img_jntReference, image=fullRefPath, e=True)
        self.ui.txt_jntCurrent.setLabel('Select mouth lips loop')
        