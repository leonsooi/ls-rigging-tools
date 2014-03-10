'''
Created on Mar 8, 2014

@author: Leon
'''

import pymel.core as pm

import spPaint3dContext as spc
import spPaint3dGui as spg


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
        
        self.jointsList = [['Left Inner Brow', 'LT_in_brow'],
                           ['Left Middle Brow', 'LT_mid_brow'],
                           ['Left Outer Brow', 'LT_out_brow'],
                           ['Left Inner Forehead', 'LT_in_forehead'],
                           ['Left Outer Forehead', 'LT_out_forehead'],
                           ['Left Temple', 'LT_temple'],
                           ['Left Squint', 'LT_squint'],
                           ['Center Nose Tip', 'CT_noseTip'],
                           ['Left Nostril', 'LT_nostril'],
                           ['Center Philtrum', 'CT_philtrum'],
                           ['Left Philtrum', 'LT_philtrum'],
                           ['Left Upper Crease', 'LT_up_crease'],
                           ['Left Middle Crease', 'LT_mid_crease'],
                           ['Left Lower Crease', 'LT_low_crease'],
                           ['Left Cheek', 'LT_cheek'],
                           ['Left Upper Jaw', 'LT_up_jaw'],
                           ['Left Jaw Corner', 'LT_corner_jaw'],
                           ['Left Lower Jaw', 'LT_low_jaw'],
                           ['Left Chin', 'LT_chin'],
                           ['Center Chin', 'CT_chin']]
        
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
        
        if 'CT_' in jntName:
            position[0] = 0.0
        
        placementLoc = pm.spaceLocator(n=jntName+'_pLoc')   
        placementLoc.t.set(position)
        placementLoc.localScale.set(0.05, 0.05, 0.05)
        self.grp | placementLoc
        
        # set camera to focus on new placementLoc
        self.camera.tumblePivot.set(position)
        
        if self.jointIndex >= len(self.jointsList):
            # all joints placed
            # exit and start loops selection
            self.exitContext()
        else:
            self.nextJoint()
        
    def nextJoint(self):
        '''
        Calls UI to show the next joint's reference
        '''
        currentJointName, refPath = self.jointsList[self.jointIndex]
        fullRefPath = r"C:\Users\Leon\Pictures\FRS\Images\FRSRef_%s.jpg" % refPath
        pm.image(self.ui.img_jntReference, image=fullRefPath, e=True)
        self.ui.txt_jntCurrent.setLabel(currentJointName)
        
        self.jointIndex += 1
        
    def exitContext(self):
        '''
        '''
        pm.select(cl=True)
        pm.setToolTo('polySelectContext')
        fullRefPath = r"C:\Users\Leon\Pictures\FRS\Images\FRSRef_mouthLoop.jpg"
        pm.image(self.ui.img_jntReference, image=fullRefPath, e=True)
        self.ui.txt_jntCurrent.setLabel('Select mouth lips loop')
        