'''
Created on May 11, 2014

@author: Leon
'''
import pymel.core as pm
mel = pm.language.Mel()

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