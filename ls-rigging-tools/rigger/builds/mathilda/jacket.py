'''
Created on Jun 21, 2014

@author: Leon
'''
import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt
import utils.rigging as rt
import rigger.utils.modulate as modulate
reload(modulate)

def addCtlsToJointChain(jntPrefix, name=''):
    '''
    jntPrefix - string - 'LT_jacketVert_crv_1_crv_jnt_'
    '''
    # create controls 0, 2, 4, 6
    ctlsList = []
    parentJnt = None
    
    for ctlId in (0, 2, 4, 6):
        ctl = addCtl(name+str(ctlId))
        jnt = pm.PyNode(jntPrefix+str(ctlId))
        
        if len(ctlsList) > 0:
            # if there is already ctls in the list,
            # parent under the last ctl
            ctlsList[-1]['ctl'] | ctl['cth']
            # get jnt matrix in parent space
            # to get FK ctl behavior
            ivm = pm.createNode('inverseMatrix', n=name+str(ctlId)+'_ivm')
            parentJnt.worldMatrix >> ivm.inputMatrix
            mm = pm.createNode('multMatrix', n=name+str(ctlId)+'_mm')
            jnt.worldMatrix >> mm.matrixIn[0]
            ivm.outputMatrix >> mm.matrixIn[1]
            xformPlug = mm.matrixSum
        else:
            # this is the first ctl
            # so it is in world space
            # just get the joint matrix
            # for ctl's xforms
            xformPlug = jnt.worldMatrix
                
        dcm = pm.createNode('decomposeMatrix', n=name+str(ctlId)+'_dcm')
        xformPlug >> dcm.inputMatrix
        dcm.outputTranslate >> ctl['cth'].t
        dcm.outputRotate >> ctl['cth'].r
        
        # add bindjnt
        pm.select(cl=True)
        bndJnt = pm.joint(n=name+str(ctlId)+'_bnd')
        bnd_dcm = pm.createNode('decomposeMatrix', n=name+str(ctlId)+'_bnd_dcm')
        ctl['ctl'].worldMatrix >> bnd_dcm.inputMatrix
        bnd_dcm.outputTranslate >> bndJnt.t
        bnd_dcm.outputRotate >> bndJnt.r

        
        
        # store this variables for use in next iteration
        parentJnt = jnt
   
        ctlsList.append(ctl)


def addCtl(name):
    '''
    return dictionary with keys for ctl, cto, ctg, cth
    '''
    ctl = pm.circle(n=name+'_ctl', normal=(0,0,1), sweep=359)[0]
    pm.delete(ctl, ch=True)
    cto = pm.group(ctl, n=name+'_cto')
    ctg = pm.group(cto, n=name+'_ctg')
    cth = pm.group(ctg, n=name+'_cth')
    return {'ctl': ctl,
            'cto': cto,
            'ctg': ctg,
            'cth': cth}
    

def connectAllJacketLocs():
    locGrpParams = {8: '_back',
                   6: '_left',
                   4: '_front',
                   2: '_right',
                   7: '_leftBack',
                   1: '_rightBack',
                   3: '_rightFront',
                   5: '_leftFront'}
    
    for param, grpName in locGrpParams.items():
        for i in range(4,10):
            twistCrv = nt.Transform(u'torsoReader_' + str(i))
            untwistCrv = nt.Transform(u'torsoReader_%d_untwist' % i)
            connectJacketLoc(twistCrv, untwistCrv, param, name=grpName)
        # special case for i=3
        # also connect to additional readers 1 & 2
        twistCrv = nt.Transform(u'torsoReader_3')
        untwistCrv = nt.Transform(u'torsoReader_3_untwist')
        connectJacketLoc(twistCrv, untwistCrv, param, name=grpName, 
                         addCrvs=[nt.Transform(u'torsoReader_2'),
                                  nt.Transform(u'torsoReader_1')])

def addHoriJntChains():
    '''
    '''
    crvs = {nt.Transform(u'LT_jacketHori10_crv_crv'):2.82475264468795,
            nt.Transform(u'RT_jacketHori10_crv_crv'):2.82475264468795,
            nt.Transform(u'LT_jacketHori1_crv_crv'):2.13759073315845,
            nt.Transform(u'RT_jacketHori1_crv_crv'):2.13759073315845,
            nt.Transform(u'LT_jacketHori2_crv_crv'):2.27782543847773,
            nt.Transform(u'RT_jacketHori2_crv_crv'):2.27782543847773,
            nt.Transform(u'LT_jacketHori3_crv_crv'):2.45635390749126,
            nt.Transform(u'RT_jacketHori3_crv_crv'):2.45635390749126,
            nt.Transform(u'LT_jacketHori4_crv_crv'):2.53350803328153,
            nt.Transform(u'RT_jacketHori4_crv_crv'):2.53350803328153,
            nt.Transform(u'LT_jacketHori5_crv_crv'):2.61136289092179,
            nt.Transform(u'RT_jacketHori5_crv_crv'):2.61136289092179,
            nt.Transform(u'LT_jacketHori6_crv_crv'):2.6867108807245,
            nt.Transform(u'RT_jacketHori6_crv_crv'):2.6867108807245,
            nt.Transform(u'LT_jacketHori7_crv_crv'):2.75286616788457,
            nt.Transform(u'RT_jacketHori7_crv_crv'):2.75286616788457,
            nt.Transform(u'LT_jacketHori8_crv_crv'):2.79943068586068,
            nt.Transform(u'RT_jacketHori8_crv_crv'):2.79943068586068,
            nt.Transform(u'LT_jacketHori9_crv_crv'):2.8337879418498,
            nt.Transform(u'RT_jacketHori9_crv_crv'):2.8337879418498}
    for crv, endPt in crvs.items():
        addJointChainToCurvePoints(crv, endPt, 13)
    

def addHoriCrvs():
    '''
    '''
    leftDir = ['_back',
               '_leftBack',
               '_left',
               '_leftFront',
               '_front']
    
    rightDir = ['_back',
               '_rightBack',
               '_right',
               '_rightFront',
               '_front']
    '''
    for jntId in range(5):
        objs = ['jacketVert%s_crv_crv_jnt_%d' % (grpName, jntId)
                 for grpName in leftDir]
        rt.makeCrvThroughObjs(objs, name='LT_jacketHori'+str(jntId)+'_crv', 
                              connect=True, degree=2)
        objs = ['jacketVert%s_crv_crv_jnt_%d' % (grpName, jntId)
                 for grpName in rightDir]
        rt.makeCrvThroughObjs(objs, name='RT_jacketHori'+str(jntId)+'_crv', 
                              connect=True, degree=2)
    '''
    '''
    # start locs
    objs = ['jacketStart%s_loc_offset' % grpName
            for grpName in leftDir]
    rt.makeCrvThroughObjs(objs, name='LT_jacketStartHori_crv', 
                          connect=True, degree=2)
    objs = ['jacketStart%s_loc_offset' % grpName
            for grpName in rightDir]
    rt.makeCrvThroughObjs(objs, name='RT_jacketStartHori_crv', 
                          connect=True, degree=2)
    '''
    # other locs
    for locId in range(1,11):
        objs = ['torsoReader_%d%s_loc_pushOutLoc' % (locId, grpName)
                for grpName in leftDir]
        rt.makeCrvThroughObjs(objs, name='LT_jacketHori'+str(locId)+'_crv', 
                              connect=True, degree=2)
        objs = ['torsoReader_%d%s_loc_pushOutLoc' % (locId, grpName)
                for grpName in rightDir]
        rt.makeCrvThroughObjs(objs, name='RT_jacketHori'+str(locId)+'_crv', 
                              connect=True, degree=2)
    

def addVertJointChains():
    '''
    '''
    crvs = {nt.Transform(u'LT_jacketVert_crv_0_crv'):5.64175573477838,
            nt.Transform(u'LT_jacketVert_crv_1_crv'):5.72573491802788,
            nt.Transform(u'LT_jacketVert_crv_2_crv'):6.03354529902427,
            nt.Transform(u'LT_jacketVert_crv_3_crv'):6.32167583466526,
            nt.Transform(u'LT_jacketVert_crv_4_crv'):6.49099392892804,
            nt.Transform(u'RT_jacketVert_crv_0_crv'):5.64175573477838,
            nt.Transform(u'RT_jacketVert_crv_1_crv'):5.72573491802788,
            nt.Transform(u'RT_jacketVert_crv_2_crv'):6.03354529902427,
            nt.Transform(u'RT_jacketVert_crv_3_crv'):6.32167583466526,
            nt.Transform(u'RT_jacketVert_crv_4_crv'):6.49099392892804}
    for crv, endPt in crvs.items():
        addJointChainToCurvePoints(crv, endPt, 8)

def addJointChainToCurvePoints(crv, endPt, jointNum):
    '''
    add a joint chain on crv.u[0:endPt]
    joints distributed by distance along curve
    '''
    length = findLengthFromParam(crv, endPt)
    lengthBetweenEachJoint = length / (jointNum - 1)
    lengthsAlongCurve = [lengthBetweenEachJoint * i
                         for i in range(jointNum)]
    paramsAlongCurve = [crv.findParamFromLength(length)
                        for length in lengthsAlongCurve]
    pointsAlongCurve = [crv.getPointAtParam(param, space='world')
                        for param in paramsAlongCurve]
    allJnts = []
    pm.select(cl=True)
    for ptId, ptPos in enumerate(pointsAlongCurve):
        jnt = pm.joint(n=crv.name()+'_jnt_%d'%ptId)
        jnt.setTranslation(ptPos, space='world')
        allJnts.append(jnt)
    # orient jnts
    allJnts[0].orientJoint('xyz', ch=True)
    pm.ikHandle(sj=allJnts[0], ee=allJnts[-1], curve=crv,
                sol='ikSplineSolver', createCurve=False,
                n=crv.name()+'ikH')

def setVertJointChainsTwist():
    '''
    '''
    ik_hdls = [nt.IkHandle(u'LT_jacketVert_crv_1_crvikH'),
                nt.IkHandle(u'RT_jacketVert_crv_1_crvikH'),
                nt.IkHandle(u'RT_jacketVert_crv_2_crvikH'),
                nt.IkHandle(u'RT_jacketVert_crv_4_crvikH'),
                nt.IkHandle(u'LT_jacketVert_crv_4_crvikH'),
                nt.IkHandle(u'LT_jacketVert_crv_0_crvikH'),
                nt.IkHandle(u'RT_jacketVert_crv_0_crvikH'),
                nt.IkHandle(u'LT_jacketVert_crv_2_crvikH'),
                nt.IkHandle(u'RT_jacketVert_crv_3_crvikH'),
                nt.IkHandle(u'LT_jacketVert_crv_3_crvikH')]
    
    startObject = pm.PyNode('Mathilda_spine_end_jnt')
    endObject = pm.PyNode('Mathilda_hip_jnt')
    
    for hdl in ik_hdls:
        hdl.dTwistControlEnable.set(1)
        hdl.dWorldUpType.set(2)
        hdl.dWorldUpAxis.set(4)
        startObject.worldMatrix >> hdl.dWorldUpMatrix
        endObject.worldMatrix >> hdl.dWorldUpMatrixEnd

def addCurveLengthRatioGlobalScale(crv, scaleAttr):
    '''
    patches addCurveLengthRatioAttr to globalScale
    '''
    crv.addAttr('globalScale', k=True, dv=1, min=0.001)
    scaleAttr >> crv.attr('globalScale')
    
    # assume lengthRatio attr was already created
    md = crv.attr('lengthRatio').inputs()[0]
    
    # modulate input1X by scale
    currInput = md.input1X.get()
    modScale = modulate.multiplyInput(md.input1X, 1, '_scale')
    scaleAttr >> modScale

def addCurveLengthRatioAttr(crv):
    '''
    crv - transform of a nurbsCurve
    add 'lengthRatio' attribute to crv, where
    lengthRatio = origLength / currLength
    
    e.g.:
    import rigger.builds.mathilda.jacket as jacket
    reload(jacket)
    allCrvs = pm.ls(sl=True)
    for crv in allCrvs:
        jacket.addCurveLengthRatioAttr(crv)
    '''
    origLength = crv.length()
    cif = pm.createNode('curveInfo', n=crv+'_lengthRatio_cif')
    crv.worldSpace[0] >> cif.inputCurve
    md = pm.createNode('multiplyDivide', n=crv+'_lengthRatio_md')
    md.input1X.set(origLength)
    md.operation.set(2)
    cif.arcLength >> md.input2X
    crv.addAttr('lengthRatio', k=True)
    md.outputX >> crv.attr('lengthRatio')
    pm.select(crv)
    
def jacketVertCrvPatch(crv):
    '''
    previously, the vert crvs are driven by pmms
    driven by joints driven by ikSplines driven by hori crvs
    
    this will change it to be driven by motionPaths on the hori crvs,
    which may hopefully be faster than ikSplines
    '''
    for cv in crv.cv[:]:
        pmm = cv.connections()[0]
        # first 4 tokens of the name gives us the hori crv
        horiCrvName = '_'.join(pmm.name().split('_')[:4])
        horiCrv = pm.PyNode(horiCrvName)
        connectVertCrvCVToHoriCrv(cv, horiCrv)
            
def connectVertCrvCVToHoriCrv(cv, horiCrv):
    '''
    get closest pt to cv on horiCrv
    get param, get length, get percentage along length (for motionPath)
    multiply percentage by horiCrv.lengthRatio
    '''
    pt = cv.getPosition()
    param = horiCrv.getParamAtPoint(pt)
    ptLength = findLengthFromParam(horiCrv, param)
    totalLength = horiCrv.length()
    lengthPercent = ptLength / totalLength
    
    # multiply lengthPercent
    mdl = pm.createNode('multDoubleLinear', n=horiCrv+'_cv%d'%cv.index())
    mdl.input1.set(lengthPercent)
    horiCrv.lengthRatio >> mdl.input2
    
    # percentage used for motionPath uVal
    mp = pm.createNode('motionPath', n=horiCrv+'_mp%d'%cv.index())
    horiCrv.worldSpace[0] >> mp.gp
    mdl.output >> mp.uValue
    mp.fractionMode.set(True)
    mp.ac >> cv
    
def jacketCtlPatch():
    '''
    previously ctls were driven matrices by joint's matrix
    joint were driven by ikSplines driven by vert crvs
    
    ctls will still be driven by matrices,
    but will use locator matrices instead
    locators will be driven by motionpaths
    
    DONT PATCH THIS FOR MATHILDA
    the speed improvement is negligible
    possibly because the motion path alignment ends up
    using the same amt of computes as iksplines
    '''
    # set up crvs to calculate lengths
    jacketVertCrvsGrp = nt.Transform(u'CT_jacketVertCrvs_grp')
    allVertCrvs = [n for n in jacketVertCrvsGrp.getChildren()
                    if '_crv' in n.name()]
    for crv in allVertCrvs:
        addCurveLengthRatioAttr(crv)
        addCurveLengthRatioGlobalScale(crv, 
                                       pm.PyNode('Mathilda_root_ctrl.masterScale'))
    
    # set up locators to replace joints
    jacketCtlGrp = nt.Transform(u'CT_jacket_ctls_grp')
    allJacketCths = [n for n in jacketCtlGrp.getChildren(ad=True)
                     if '_cth' in n.name()]
    newLocs = []
    for eachCth in allJacketCths:
        cthId = int(eachCth.name().split('_')[1][-1])
        # get driver jnt (with same id at the end)
        driverJnt = [jnt for jnt in eachCth.listHistory(type='joint')
                     if jnt[-1] == str(cthId)][0]
        # remove last two tokens to get curve name
        vertCrv = '_'.join(driverJnt.split('_')[:-2])
        vertCrv = pm.PyNode(vertCrv)
        newLocs.append(addLocToVertCrv(eachCth, vertCrv, driverJnt))
    locGrp = pm.group(newLocs, n='CT_jacketVertCrvsLoc_grp')
        
    # replace joint matrix with locator matrix
    allVertJntsGrp = pm.PyNode('CT_jacketVertCrvsJoints_grp')
    allVertJnts = allVertJntsGrp.getChildren(ad=True, type='joint')
    for jnt in allVertJnts:
        # find substitute loc
        locName = jnt.replace('_jnt_', '_loc_')
        if pm.objExists(locName):
            loc = pm.PyNode(locName)
            substituteJointWithLoc(jnt, loc)
        else:
            # no loc for this joint
            pass
    
def substituteJointWithLoc(jnt, loc):
    '''
    get all outgoing connections for jnt's worldMatrix
    replace them with loc's worldMatrix
    '''
    outPlugs = jnt.worldMatrix[0].outputs(p=True)
    for plug in outPlugs:
        loc.worldMatrix[0] >> plug

def addLocToVertCrv(cth, vertCrv, driverJnt):
    '''
    get closest pt to ctl on vertCrv
    get param, get length, get percentage along length (for motionPath)
    multiply percentage by vertCrv.lengthRatio
    
    return loc
    '''
    cthId = int(cth.name().split('_')[1][-1])
    
    pt = driverJnt.getTranslation(space='world')
    param = vertCrv.getParamAtPoint(pt)
    ptLength = findLengthFromParam(vertCrv, param)
    totalLength = vertCrv.length()
    lengthPercent = ptLength / totalLength
    
    # multiply lengthPercent
    mdl = pm.createNode('multDoubleLinear', 
                        n=vertCrv+'_md_'+str(cthId))
    mdl.input1.set(lengthPercent)
    vertCrv.lengthRatio >> mdl.input2
    
    # percentage used for motionPath uVal
    mp = pm.createNode('motionPath', 
                       n=vertCrv+'_mp_'+str(cthId))
    vertCrv.worldSpace[0] >> mp.gp
    mdl.output >> mp.uValue
    mp.fractionMode.set(True)
    # aim settings for motionPath
    aimObjects = {0: nt.Joint(u'Mathilda_spine_end_jnt'),
                    2: nt.Joint(u'Mathilda_spine_hi_jnt'),
                    4: nt.Joint(u'Mathilda_spine_mid_jnt'),
                    6: nt.Joint(u'Mathilda_hip_jnt')}
    aimObj = aimObjects[cthId]
    mp.wut.set(1) # object up
    aimObj.worldMatrix >> mp.worldUpMatrix
    mp.frontAxis.set(0) # X
    mp.upAxis.set(2) # Z
    mp.inverseUp.set(True)
    
    # create locator to substitute for joint
    loc = pm.spaceLocator(n=vertCrv+'_loc_'+str(cthId))
    mp.ac >> loc.t
    mp.r >> loc.r
    
    return loc
    
    
def findLengthFromParam(crv, param):
    '''
    MFnNurbsCurve has findParamFromLength, but not the other way!
    workaround is to cut the curve at param,
    then get the whole length of the new curve
    '''
    firstCrv, secondCrv, node = pm.detachCurve(crv.u[param], ch=True, rpo=False)
    try:
        length = firstCrv.length()
        pm.undo()
        return length
    except RuntimeError as e:
        print e
        print 'param may be 0'
        pm.undo()
        return 0
        

def addJointChainToCVs(crv, startCV, endCV):
    '''
    add one joint for each cv in crv.cvs[startCV:endCV]
    '''
    cvsPts = crv.getCVs()
    pm.select(cl=True)
    allJnts = []
    for cvId, cvPt in enumerate(cvsPts[startCV:endCV]):
        closestPt = crv.closestPoint(cvPt)
        
        jnt = pm.joint(n=crv.name()+'_jnt_%d'%cvId)
        jnt.setTranslation(closestPt, space='world')
        allJnts.append(jnt)
    pm.ikHandle(sj=allJnts[0], ee=allJnts[-1], curve=crv,
                sol='ikSplineSolver', createCurve=False,
                n=crv.name()+'ikH')
    

def addVertCrvs():
    '''
    '''
    
    for side in 'LT_', 'RT_':
        for jntId in range(0, 13, 3):
            objs = [side+'jacketHori%s_crv_crv_jnt_%d' % (locId, jntId)
                     for locId in reversed(range(1,11))]
            rt.makeCrvThroughObjs(objs, name=side+'jacketVert_crv_'+str(jntId/3), 
                                  connect=True, degree=2)

def modulatePushOutLocs():
    '''
    add a modulate attr for each row of locs
    add attrs to loc grp
    '''
    locGrpNames = ['_back',
                   '_left',
                   '_front',
                   '_right',
                   '_leftBack',
                   '_rightBack',
                   '_rightFront',
                   '_leftFront']
    master = nt.Transform(u'CT_torsoReader_locs_grp')
    
    for grpName in locGrpNames:
        for rowId in range(1,10):
            master.addAttr('%s_row%d_mod'%(grpName, rowId), k=True, dv=1)
        
            loc = pm.PyNode('torsoReader_%d%s_loc_pushOutLoc' %
                            (rowId, grpName))
            modAttr = modulate.multiplyInput(loc.tz, 1, '_mod')
            master.attr('%s_row%d_mod'%(grpName, rowId)) >> modAttr
    
def addPushOutLoc():
    '''
    '''
    locGrpNames = ['_back',
                   '_left',
                   '_front',
                   '_right',
                   '_leftBack',
                   '_rightBack',
                   '_rightFront',
                   '_leftFront']
    
    for grpName in locGrpNames:
        
        # create orient for consLoc (loc at the top of the chain)
        consLoc = pm.PyNode('jacketStart'+grpName+'_loc')
        
        orientLoc = pm.spaceLocator(n=consLoc.name()+'_orient')
        pm.pointConstraint(consLoc, orientLoc)
        mp = pm.PyNode('CT_jacketLocsAlign%s_mp' % grpName)
        mp.rotate >> orientLoc.r
        
        # add offsetLoc that can be constrained to shoulders later
        offsetLoc = pm.spaceLocator(n=consLoc.name()+'_offset')
        orientLoc | offsetLoc 
        offsetLoc.setMatrix(dt.Matrix.identity)
        
        for locId in range(1,10):
            
            loc = pm.PyNode('torsoReader_%d%s_loc' %
                            (locId, grpName))
            newLoc = pm.spaceLocator(n=loc.name()+'_pushOutLoc')
            newLoc.localScale.set(0.25,0.25,0.25)
            matrix = loc.getMatrix(worldSpace=True)
            newLoc.setMatrix(matrix, worldSpace=True)
            loc | newLoc
            newLoc.setLimit('translateMinZ', 0)  
                
            pm.pointConstraint(offsetLoc, newLoc, skip=('x','y'))
            
            

def connectLocRotate():
    '''
    '''
    locGrpNames = ['_back',
                   '_left',
                   '_front',
                   '_right',
                   '_leftBack',
                   '_rightBack',
                   '_rightFront',
                   '_leftFront']
    
    # create one nurb circle for all groups
    circ = pm.createNode('makeNurbCircle', n='CT_jacketLocsAlign_circle')
    circ.normal.set(0,1,0)
    # use the same root ctrl for all groups
    rootCtl = pm.PyNode('Mathilda_root_ctrl')
    
    # create one motionpath for each group
    for grpName in locGrpNames:
        mp = pm.createNode('motionPath', n='CT_jacketLocsAlign'+grpName+'_mp')
        circ.outputCurve >> mp.gp
        # use paramater from lowest npc
        pm.PyNode('torsoReader_3'+grpName+'_npc').parameter >> mp.uValue
        rootCtl.worldMatrix >> mp.worldUpMatrix
        mp.worldUpType.set(2)
        mp.worldUpVector.set(0,1,0)
        mp.frontAxis.set(0)
        mp.upAxis.set(1)
        # connect to all locs in grp
        for locId in range(1,10):
            mp.rotate >> pm.PyNode('torsoReader_%d%s_loc.r' %
                                   (locId, grpName))

def connectJacketLoc(twistCrv, untwistCrv, param, name='', addCrvs=[]):
    '''
    '''
    mp = pm.createNode('motionPath', n=twistCrv+name+'_mp')
    untwistCrv.worldSpace >> mp.geometryPath
    mp.u.set(param)
    
    npc = pm.createNode('nearestPointOnCurve', n=twistCrv+name+'_npc')
    mp.allCoordinates >> npc.inPosition
    twistCrv.worldSpace >> npc.inputCurve
    
    allLocs = []
    loc = pm.spaceLocator(n=twistCrv+name+'_loc')
    npc.position >> loc.translate
    allLocs.append(loc)
    
    for crv in addCrvs:
        pci = pm.createNode('pointOnCurveInfo', n=crv+name+'_pci')
        npc.parameter >> pci.parameter
        crv.worldSpace >> pci.inputCurve
        loc = pm.spaceLocator(n=crv+name+'_loc')
        pci.position >> loc.translate
        allLocs.append(loc)
    
    pm.select(allLocs)