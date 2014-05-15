'''
Created on May 11, 2014

@author: Leon
'''
import pymel.core as pm
mel = pm.language.Mel()

import utils.rigging as rt

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
    
    for src_attr in all_attrs:
        weight = src_attr.get()
        dest_attr = pm.PyNode(src_attr.name().replace('LT_', 'RT_'))
        dest_attr.set(weight)
        
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