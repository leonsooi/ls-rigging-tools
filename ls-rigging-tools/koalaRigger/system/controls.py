import utils.wrappers.abRiggingTools as abRT
import maya.cmds as mc
import utils.rigging as rt
import utils.general as gt
reload(gt)

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
        

class FKChain():
    """
    FK Chain control system
    """

    def __init__(self, name, pivots):
        """
        Creates group name_fkChainCS_0
        pivots (list) - list of pivots in a hierarchy
        """
        self.ctlOptions = {}
        self.ctlOptions['wireSize'] = 10.0
        self.ctlOptions['downAxis'] = 0
        
        self.root = mc.group(em=True, n=name+'_fkChainCS_0')
        
        for opt, val in self.ctlOptions.items():
            attrType = gt.getMayaType(val)
            mc.addAttr(self.root, ln=opt, at=attrType)
            mc.setAttr(self.root+'.'+opt, e=True, cb=True)
            mc.setAttr(self.root+'.'+opt, val)
        
        self.pivots = pivots
    
    def updateOptions(self):
        self.ctlOptions['wireSize'] = mc.getAttr(self.root+'.wireSize')
        self.ctlOptions['downAxis'] = mc.getAttr(self.root+'.downAxis')
    
    def build(self):
        
        self.updateOptions()
        
        ctls = []
        parentCtl = None
        counter = 0
        
        for eachPivot in self.pivots:
            ctl = ctlCurve(self.root+'_ctl_%d'%counter, 'circle', 0, size=self.ctlOptions['wireSize'], snap=eachPivot)
            mc.parentConstraint(ctl.crv, eachPivot)
            if parentCtl:
                mc.parentConstraint(parentCtl.crv, ctl.home, mo=True)
            counter += 1
            ctls.append(ctl.home)
            parentCtl = ctl
            
        self.ctlGrp = mc.group(ctls, n=self.root+'_ctlGrp', p=self.root)
        
        
        