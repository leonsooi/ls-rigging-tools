import abRiggingTools as abRT
import maya.cmds as mc
import lsRigTools as rt

class ctlCurve:
    '''
    Control curve object
    '''
    def __init__(self, name, wireType, facingAxis, aOffset=(0,0,0), size=10, colorId=0, snap=None, ctlOffsets=[]):
        '''
        Initializes control curve
        
        snap - transform node (or nodes) to set initial position for home group (if None, set to origin)
        ctlOffsets - list of groups nodes above control
        '''
        
        self.crv = abRT.makeWireController(wireType, facingAxis, aOffset, size)
        self.crv = mc.rename(self.crv, name)
        
        # color control
        abRT.colorObj(self.crv, colorId)
        
        # set pivot to local origin
        mc.setAttr(self.crv+'.rp', 0,0,0)
        mc.setAttr(self.crv+'.sp', 0,0,0)
        
        # snap control to position if snap is defined, otherwise leave it at origin
        if snap:
            abRT.snapToPosition(snap, self.crv)

        # all controls have a home group, to "freeze" the local transforms
        self.home = abRT.groupFreeze(self.crv)
        self.home = mc.rename(self.home, name+'_hm')
        
        # all controls also have a space group, for space-switching
        self.space = abRT.groupFreeze(self.crv)
        self.space = mc.rename(self.space, name+'_space')
        
        # add optional offset groups between space and actual control
        self.grp = {}
        
        for offsetGrp in ctlOffsets:
            self.grp[offsetGrp] = abRT.groupFreeze(self.crv)
            self.grp[offsetGrp] = mc.rename(self.grp[offsetGrp], name+'_'+offsetGrp)
    
    def setSpaces(self, spaces, niceNames=None):
        '''
        If spaces is just a string, it will parentConstraint space grp to the space
        If spaces is a list, it will also create attributes on self to switch spaces
        Default space is first in list
        '''
        if niceNames is None:
            niceNames=spaces
        rt.spaceSwitchSetup(spaces, self.space, self.crv, 'parentConstraint', niceNames)
