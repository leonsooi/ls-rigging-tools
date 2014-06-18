'''
Created on Jun 8, 2014

@author: Leon
'''
import pymel.core as pm
import utils.rigging as rt
import pymel.core.nodetypes as nt
reload(rt)
def connectBsp(driverAttr, drivenAttr, geo, bspGeos, scaleTime=100):
    '''
    bspGeos is a dictionary of geos used for this bspTarget at various weights
    {-0.1: nt.mesh,
    0.1: nt.mesh}
    '''
    # get closest vertex on geo for offset calculation
    driverCtl = driverAttr.node()
    driverPt = pm.dt.Point(driverCtl.getRotatePivot(space='world'))
    
    faceId = geo.getClosestPoint(driverPt)[1]
    verts = [geo.vtx[i] for i in geo.f[faceId].getVertices()]
    closestVert = min(verts, key=lambda x:(x.getPosition(space='world') - 
                                           driverPt).length())
    closestVertId = closestVert.index()
    
    # check that we've got the correct vert
    # pm.select(closestVert)
    print closestVertId
    
    # assuming that offsets are only in translation
    attrId = {'tx':0, 'ty':1, 'tz':2}
    driverAttrId = attrId[driverAttr.attrName()]
    
    # position values need to be calculated into ctrl space
    ctlInvMat = driverCtl.getMatrix(worldSpace=True).inverse()
    
    # make sure that ctl is zeroed before calculating offsets
    driverAttr.set(0)
    
    # get offsets for each bspGeo
    # assign to a dictionary for creating sdk later
    sdkKeys = {0:0}
    for weight, bspGeo in bspGeos.items():
        bspVertPt = bspGeo.vtx[closestVertId].getPosition(space='object')
        print bspVertPt
        offset = bspVertPt * ctlInvMat
        print offset
        offset = offset[driverAttrId]
        sdkKeys[offset] = weight
        
    # connect to bsp attr
    rt.connectSDK(driverAttr, drivenAttr, sdkKeys)
    
    # set keys for ctl for preview
    for offset, weight in sdkKeys.items():
        driverAttr.setKey(t=weight*scaleTime, v=offset)
        # save keys as attributes to be used later
        weightStr = str(weight).replace('.','_').replace('-','neg')
        weightAttr = 'bspWeight_' + drivenAttr.getAlias()+ '_' + weightStr
        try:
            driverCtl.addAttr(weightAttr)
        except RuntimeError:
            driverCtl.attr(weightAttr).set(l=False)
        driverCtl.attr(weightAttr).set(offset)
        driverCtl.attr(weightAttr).set(l=True)
        
    pm.select(driverCtl)
    
    return sdkKeys

def connectBspDriver(ctls, bspDriver, geo, weights):
    '''
    ctls = [nt.Transform(u'LT_upper_sneer_lip_pri_ctrl'),
            nt.Transform(u'LT_lower_pinch_lip_ctrl'),
            nt.Transform(u'LT_upper_pinch_lip_ctrl'),
            nt.Transform(u'LT_corner_lip_ctrl'),
            nt.Transform(u'LT_upper_sneer_lip_ctrl'),
            nt.Transform(u'LT_lower_sneer_lip_ctrl'),
            nt.Transform(u'LT_lower_sneer_lip_pri_ctrl'),
            nt.Transform(u'LT_corner_lip_pri_ctrl')]
    
    bspDriver = pm.PyNode('blendShapeCt_face_geo.cheekPuff_Lf')
    geo = nt.Mesh(u'CT_face_geoShape')
    weights = [0, 0.1]
    '''
    bspDriverName = bspDriver.getAlias()
    
    for ctl in ctls:
    
        bspDrvGrp = pm.group(em=True, n=ctl+'_bsgDriverGrp_'+bspDriverName)
        m = ctl.getMatrix(worldSpace=True)
        bspDrvGrp.setMatrix(m, worldSpace=True)
        p = ctl.getParent()
        p | bspDrvGrp | ctl
        
        ctlPos = ctl.getRotatePivot(space='world')
        bspDriver.set(weights[0])
        
        faceId = geo.getClosestPoint(ctlPos)[1]
        verts = [geo.vtx[i] for i in geo.f[faceId].getVertices()]
        closestVert = min(verts, key=lambda x:(x.getPosition(space='world') - 
                                               ctlPos).length())
        closestVertPos = closestVert.getPosition(space='world')
        bspDriver.set(weights[1])
        newPos = closestVert.getPosition(space='world')
        offset = newPos - closestVertPos
        newCtlPos = ctlPos + offset
        bspDrvGrp.setTranslation(newCtlPos, space='world')
        
        tx = bspDrvGrp.tx.get()
        ty = bspDrvGrp.ty.get()
        tz = bspDrvGrp.tz.get()
        
        rt.connectSDK(bspDriver, bspDrvGrp.tx, {weights[0]:0, weights[1]:tx})
        rt.connectSDK(bspDriver, bspDrvGrp.ty, {weights[0]:0, weights[1]:ty})
        rt.connectSDK(bspDriver, bspDrvGrp.tz, {weights[0]:0, weights[1]:tz})
