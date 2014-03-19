'''
Wrapper functions for abAutoRig procedures
Formats syntax and datatypes for use with Python

Original abAutoRig.mel must be in scripts folder
Both Standard and Premium versions will work 
'''

from maya.mel import eval as meval
import maya.cmds as mc
import itertools
meval('source "abAutoRig.mel";')

# Init global variables
meval('abRTInit()')

def setGlobal(name, strVal):
    '''
    sets abAutoRig globals
    '''
    meval('abRTSetGlobal("%(name)s", "%(strVal)s")' % locals())

def getGlobal(name):
    '''
    gets abAutoRig globals
    '''
    return meval('abRTGetGlobal("%(name)s")' % locals())

def formatArray(array):
    '''
    formats numerical lists or tuples with curly braces so that Maya can understand
    returns array as a string
    '''
    return '{' + ','.join(map(str, array)) + '}'

def formatStrArray(array):
    '''
    formats literal lists or tuples with curly braces and double quotes so that Maya can understand
    returns array as a string
    '''
    return '{"' + '","'.join(array) + '"}'


def makeWireController(wireType, facingAxis, aOffset=(0,0,0), size=10):
    '''
    wrapper function for abRTMakeWireController from abAutoRig
    
    string $wireType is the type of controller to build
    int $facingAxis is the direction that the controller will face 0(x+), 1(y+), 2(z+), 3, 4, and 5 are the coresponding negative directions
    float[] $aOffset is used to offset wire from origin
    float $size is how big to make the max dimension on the bounding box (in Maya units which is modified by the global "globalScale")
    
    returns controller name
    '''

    # format the tuple with curly braces for Maya to understand
    # aOffset = '{%d,%d,%d}' % (aOffset[0], aOffset[1], aOffset[2])
    
    aOffset = formatArray(aOffset)
    
    crv = meval('abRTWireController("%(wireType)s", %(facingAxis)d, %(aOffset)s, %(size)f, false, true)' % locals())[0]
    
    return crv


def snapToPosition(sourceObj, targetObj):
    '''
    wrapper function for abRTSnapToPosition
    
    snaps targetObj to sourceObj
    '''
    meval('abRTSnapToPosition("%(sourceObj)s", "%(targetObj)s")' % locals())
    


def groupFreeze(obj, delete=1):
    '''
    wrapper function for abRTGroupFreeze
    
    parents $obj under a group snapped and oriented to its position to zero out transforms
    delete: 0 -- keep created constraints
    delete: 1 -- delete both constraints
    delete: 2 -- keep point constraint
    delete: 3 -- keep orient constraint
    
    returns name of created null
    '''
    return meval('abRTGroupFreeze("%(obj)s", %(delete)d)' % locals())


def getHierarchy(startJnt, endJnt, retEmptyOnFork=1):
    '''
    wrapper function for abRTGetHierarchy
    
    returns all joints in direct hierarchy (including startJnt and endJnt)
    leave $endJnt as "" to crawl return jnts all the way to the bottom of the hierarchy
    if there are downward facing forks or if the joints aren't connected, an empty array will be returned, unless $retEmptyOnFork is false.
    '''
    return meval('abRTGetHierarchy("%(startJnt)s", "%(endJnt)s", %(retEmptyOnFork)d)' % locals())


def duplicateJointHierarchy(aTargets, aNames, grp):
    '''
    will create joint chain based on location of objects in $aTargets, rename them the names in $aNames, and place the result in the existing group $grp
    returns new pathNames
    '''
    
    aTargets = formatStrArray(aTargets)
    aNames = formatStrArray(aNames)
    
    return meval('abRTDuplicateJointHierarchy(%(aTargets)s, %(aNames)s, "%(grp)s")' % locals())


def makeSpineJntsFromCurve(curve, aJntNames, grp, makeLocsInsteadOfJnts=0):
    '''
    wrapper function for abRTMakeSpineJntsFromCurve
    
    makes size($aJntNames) joints (or locs if $makeLocsInsteadOfJnts) following $curve and places them in $grp (if it exists)
    returns new joint paths
    '''
    return meval('abRTMakeSpineJntsFromCurve("%(curve)s", "%(aJntNames)s", "%(grp)s", %(makeLocsInsteadOfJnts)d)' % locals())


def re_getCurvePointInfo(curve, retWS=0):
    '''
    I found this proc online at http://ryane.com and modified it
    if $retWS == true, it returns worldSpace coordinates.  Otherwise it returns them in objectSpace.
    returns {curveCmd, hardnessCmd}
    '''
    return meval('re_getCurvePointInfo("%(curve)s", %(retWS)d)' % locals())


def getRootFromJoint(jnt):
    '''
    returns the root of a skeleton based on the selection of a child joint or "" if unsuccessful
    '''
    return meval('abRTGetRootFromJoint("%(jnt)s")' % locals())

def hideAttr(obj, aAttr):
    '''
    hides $obj's attributes in $aAttr
    '''
    aAttr = formatStrArray(aAttr)
    
    return meval('abRTHideAttr("%(obj)s", %(aAttr)s)' % locals())

def colorObj(obj, indexVal):
    '''
    Note: using indexVal instead of indexKey, unless you have abRTGlobals set up...
    
    sets $obj color to $indexKey (which must be a global key, like "rootCtrlColor" that shows up in globals)
    or to $indexVal if $indexVal > -1
    '''
    return meval('abRTColorObj("%(obj)s", "", %(indexVal)d)' % locals())

def addFkControls(jnts, names, jntsToAlign, jntsToAddSecondaryCtrls, jntsToOrientCtrlsTo, fkChainUpJnt, localAlignParentJnt, wireType, ctrlGrp, limbName):
    '''
    // adds controls to a joints (in a chain) specified in $aJnts, names them using $aRootNames, and places them in $ctrlGrp
    // $aJntsToAlign is joints (by index in $aJnts) to add the align attribute to
    // $aJntsToAddSecondaryCtrl is joints (by index in $aJnts) to which a secondary FK control will be added
    // $aJntsToOrientCtrlsTo is lookup table in form of joint index in $aJnts, object to which that that joint's control will
    be aligned {ind, objName, ind2, objName2}.
    // $fkChainUpJnt is joint to parent $aJnts[0] to
    // $localAlignParentJnt is joint to use as parent space for local align (can be "")
    // $wireType is wire to use for controls ("circle", "sphere") -- it must be a valid type. The orientation of the wire
    can also be specified with "|" to catenate, and then 0-5 for the orientation, in the form of "circle|1".
    // $limbName is name of attribute in charVars to record newly created nodes (for rig removal)
    // first control in $aJnts will have align attribute
    // returns array {joint1, ctrlCurve1, joint2, ctrlCurve2}
    '''
    
    # format data
    jnts = formatStrArray(jnts)
    names = formatStrArray(names)
    jntsToAlign = formatArray(jntsToAlign)
    jntsToAddSecondaryCtrls = formatArray(jntsToAddSecondaryCtrls)
    jntsToOrientCtrlsTo = formatStrArray(jntsToOrientCtrlsTo)
    
    # format syntax
    cmd = 'abRTAddFkControls(%(jnts)s, %(names)s, %(jntsToAlign)s, %(jntsToAddSecondaryCtrls)s, %(jntsToOrientCtrlsTo)s, "%(fkChainUpJnt)s", "%(localAlignParentJnt)s", "%(wireType)s", "%(ctrlGrp)s", "%(limbName)s")' % locals()
    array = meval(cmd)
    
    # format return data as dictionary
    d = dict(itertools.izip_longest(*[iter(array)] * 2, fillvalue=''))
    
    return d
    
def makePvControl(jnts, ikHandle, bindJnt, offsetDir, nameRoot, ctrlGrp):
    '''
    returns string[] {pvControlPath, pvConstraintName, pvControlPathGrp, pvLine(annotation)}
    '''
    jnts = formatStrArray(jnts)
    
    return meval('abRTMakePvControl(%(jnts)s, "%(ikHandle)s", "%(bindJnt)s", %(offsetDir)d, "%(nameRoot)s", "%(ctrlGrp)s")' % locals())
    
def makeIKStretchy(aJnts, aIkJnts, aFkJnts, ikCtrl, statCtrl, stretchTarget, grp, limbName):
    '''
    '''
    
    aJnts = formatStrArray(aJnts)
    aIkJnts = formatStrArray(aIkJnts)
    aFkJnts = formatStrArray(aFkJnts)
    
    meval('abRTMakeIKStretchy(%(aJnts)s, %(aIkJnts)s, %(aFkJnts)s, "%(ikCtrl)s", "%(statCtrl)s", "%(stretchTarget)s", "%(grp)s", "%(limbName)s")' % locals())