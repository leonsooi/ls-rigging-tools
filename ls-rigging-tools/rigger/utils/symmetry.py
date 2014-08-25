'''
Created on May 11, 2014

@author: Leon
'''
import pymel.core as pm
mel = pm.language.Mel()
import pymel.core.nodetypes as nt

import utils.rigging as rt

def mirror_eyeCurve_weights():
    '''
    mirror LT_eye_aimAt_crv_0 to RT_eye_aimAt_crv_0
    '''
    lf_crv = nt.Transform(u'LT_eyelidsIn_aimAt_crv_0')
    rt_crv = nt.Transform(u'RT_eyelidsIn_aimAt_crv_0')
    lf_skn = pm.PyNode(mel.findRelatedSkinCluster(lf_crv))
    rt_skn = pm.PyNode(mel.findRelatedSkinCluster(rt_crv))
    
    def setEyeJointsLabels(joints):
        for jnt in joints:
            ### change the label
            
            label = '_'.join(jnt.name().split('_')[1:3])
            #label = '_'.join(jnt.name().split('_')[1:4])
            jnt.attr('type').set('Other')
            jnt.otherType.set(label)
    
    lf_infs = pm.skinCluster(lf_crv, q=True, inf=True)
    setEyeJointsLabels(lf_infs)
    
    rt_infs = pm.skinCluster(rt_crv, q=True, inf=True)
    setEyeJointsLabels(rt_infs)
    
    lf_crv.sx.setLocked(False)
    lf_crv.sx.set(-1)
    
    pm.copySkinWeights(ss=lf_skn, ds=rt_skn, sa='closestPoint', ia='label', nm=True)
    
    lf_crv.sx.set(1)

def mirror_PyNodes(*args, **kwargs):
    '''
    pass in as many nodes or list of nodes as you want
    '''
    search = kwargs.get('search', 'LT_')
    replace = kwargs.get('replace', 'RT_')
    
    retList = []
    for arg in args:
        if isinstance(arg, pm.PyNode):
            mirrored = pm.PyNode(arg.replace(search, replace))
            retList.append(mirrored)
        elif isinstance(arg, list):
            mirrored = [pm.PyNode(a.replace(search, replace)) for a in arg]
            retList.append(mirrored)
        else:
            # don't know what this is, so just return it unchanged
            retList.append(arg)
    
    if len(retList) > 1:        
        return retList
    else:
        return retList[0]
            

def mirror_bnd_driver(bndLf):
    '''
    '''
    # mirror SDKs on bnd from left to right
    bndRt = pm.PyNode(bndLf.replace('LT_', 'RT_'))
    
    bwNodesLf = {}
    for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
        bwNodesLf[attr] = bndLf.attr(attr+'_bwMsg').inputs()[0]
        
    bwNodesRt = {}
    for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
        bwNodesRt[attr] = bndRt.attr(attr+'_bwMsg').inputs()[0]
        
    for attr, bwLf in bwNodesLf.items():
        bwRt = bwNodesRt[attr]
        # compare inputs to see which needs mirroring
        inputsLf = bwLf.input.inputs(p=True)
        inputsRt = bwRt.input.inputs(p=True)
        
        if len(inputsLf) > len(inputsRt):
            # we have new stuff to mirror
            for inputId in range(len(inputsRt), len(inputsLf)):
                # mirror inputId
                print 'mirror %d for %s' % (inputId, bwLf)
                mirror_animCurve(inputsLf[inputId].node())
                
def mirror_animCurve(acrv):
    '''
    '''
    # mirror acrv from LT to RT
    # time & values remain the same
    indices = acrv.ktv.get(mi=True)
    ktvs = [acrv.ktv[i].get() for i in indices]
    ktvs_tbl = {}
    for t,v in ktvs:
        ktvs_tbl[t] = v
    # swap names for input and output
    inPlugLf = acrv.input.inputs(p=True)[0]
    inPlugRt = pm.PyNode(inPlugLf.replace('LT_', 'RT_'))
    outPlugLf = acrv.output.outputs(p=True)[0]
    outPlugRt = pm.PyNode(outPlugLf.replace('LT_', 'RT_'))
    # make new sdk
    rt.connectSDK(inPlugRt, outPlugRt, ktvs_tbl, acrv+'_mirrorToRt')

def mirror_bnd_weights(src_bnd):
    '''
    mirror from LT to RT
    '''
    all_attrs = src_bnd.listAttr(ud=True, u=True)
    all_attrs = [attr for attr in all_attrs if 'pri_ctrl_weight' in attr.name()]
    all_attrs = [attr for attr in all_attrs if attr.isFreeToChange() == 0]
    
    for src_attr in all_attrs:
        weight = src_attr.get()
        # mirror nodeName first
        src_nodeName = src_attr.nodeName()
        print 'source attr: ' + src_attr
        dest_nodeName = src_nodeName.replace('LT_', 'RT_') # CT_ will remain as CT_
        dest_node = pm.PyNode(dest_nodeName)
        # then mirror attrName
        src_attrName = src_attr.attrName()
        if 'LT_' in src_attrName:
            dest_attrName = src_attrName.replace('LT_', 'RT_')
        elif 'RT_' in src_attrName:
            dest_attrName = src_attrName.replace('RT_', 'LT_')
        else:
            # CT remains as CT
            dest_attrName = src_attrName
        dest_attr = dest_node.attr(dest_attrName)
        try:
            print 'dest attr: ' + dest_attr
            print weight
            dest_attr.set(weight)
        except RuntimeError as e:
            pass
            print e
        
def mirror_bnd_weights_run():
    '''
    UI access for mirror_bnd_weights
    '''
    sel = pm.ls(sl=True)
    for each in sel:
        mirror_bnd_weights(each)
    
def get_cv_map(src_crv, dest_crv):
    '''
    return cv mapping from src to dest crvs
    '''
    map_tbl = {}
    dest_cvs = dest_crv.cv[:]
    for cv in src_crv.cv[:]:
        src_pt = cv.getPosition()
        dest_pt = pm.dt.Point(src_pt * (-1,1,1))
        dest_cv = min(dest_cvs, key=lambda x: (x.getPosition() - dest_pt).length())
        map_tbl[cv] = dest_cv
        
    return map_tbl

def mirror_crv_weights(map_tbl):

    src_cv, dest_cv = map_tbl.items()[0]
    pm.select(map_tbl.items()[0])
    src_skn = pm.PyNode(mel.findRelatedSkinCluster(src_cv.node()))
    dest_skn = pm.PyNode(mel.findRelatedSkinCluster(dest_cv.node()))
    
    for src_cv, dest_cv in map_tbl.items():
        infs = pm.skinCluster(src_skn, q=True, inf=True)
        dest_infs = [pm.PyNode(inf.name().replace('LT_', 'RT_')) for inf in infs]
        weights = pm.skinPercent(src_skn, src_cv, q=True, v=True)
        weights_list = zip(dest_infs, weights)
        pm.skinPercent(dest_skn, dest_cv, tv=weights_list)
        
def mirror_crv_weights_run():
    '''
    UI access for mirror_crv_weights
    '''
    src_crv, dest_crv = pm.ls(sl=True)[:2]
    map_tbl = get_cv_map(src_crv, dest_crv)
    mirror_crv_weights(map_tbl)