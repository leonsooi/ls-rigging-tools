'''
use for pupil or iris dilation
'''
import pymel.core as pm
import pymel.core.nodetypes as nt
import utils.rigging as rt
import rigger.lib.mesh as mesh

def create(ctl, tipGeo, weights, name, keys, addGeos=[], useScale=False):
    '''
    tipGeo - vtx of the tip of the eye
    weights - list of weights for each loop radiating outwards (including geoTip)
    e.g. [1, 1, 1, 1, 1, .95, 0.75, 0.5, .25, .1]
    addGeo - list of additional geometry for cluster to deform
    name - 'pupil' or 'iris'
    
    e.g.:
    geo = nt.Mesh(u'LT_eyeball_geoShape')
    tipGeo = geo.vtx[381]
    ctl = nt.Transform(u'LT_eye_ctl')
    name = '_iris'
    
    keys = {'sx': {0.01:0.01, 1:1, 2:2},
            'sy': {0.01:0.01, 1:1, 2:2},
            'sz': {0.01:0.01, 1:1, 2:3.75}}
    weights = [1, 1, 1, 1, 1, .95, 0.75, 0.5, .25, .1]
    '''
    geo = tipGeo.node()
    dfm, hdl = pm.cluster(tipGeo, n=ctl+name+'_dfm', foc=True)
    dfg = pm.group(hdl, n=ctl+name+'_dfg')
    rp = hdl.getRotatePivot(space='world')
    sp = hdl.getScalePivot(space='world')
    dfg.setRotatePivot(rp, space='world')
    dfg.setScalePivot(sp, space='world')
    dfh = pm.group(dfg, n=ctl+name+'_dfh')
    
    ctl.addAttr(name, min=0.01, max=2, dv=1, k=True)
    
    for attr, key in keys.items():
        rt.connectSDK(ctl.attr(name), hdl.attr(attr), key)

    loopNums = len(weights) - 1
    vertLoops = mesh.VertexLoops([tipGeo], loopNums)
    
    # add membership
    pm.select(vertLoops[:])
    for vertLoop in vertLoops[:]:
        for eachVert in vertLoop:
            dfm.setGeometry(eachVert)
            
    for loopId, weight in enumerate(weights):
        for eachVert in vertLoops[loopId]:
            print eachVert
            dfm.setWeight(geo, 0, eachVert, weight)
            
    # add additional geometries
    for eachGeo in addGeos:
        dfm.setGeometry(eachGeo, foc=True)
        
    if useScale:
        # modulate cluster scale by control scale
        for eachAttr in ('sx', 'sy', 'sz'):
            scaleInput = hdl.attr(eachAttr).inputs(p=True)[0]
            mdl = pm.createNode('multDoubleLinear', n=hdl+'_'+eachAttr+'_scale_mdl')
            scaleInput >> mdl.input1
            ctl.attr(eachAttr) >> mdl.input2
            mdl.output >> hdl.attr(eachAttr)   
    return dfh