import maya.cmds as mc

def create_distanceBetween(transA, transB, globalCompensate=''):
    '''
    returns outputPlug that gives distance between transforms A and B
    '''
    # distance node
    dist = mc.createNode('distanceBetween', n=transA+'_dist')
    mc.connectAttr(transA+'.worldMatrix', dist+'.inMatrix1', f=True)
    mc.connectAttr(transB+'.worldMatrix', dist+'.inMatrix2', f=True)
    
    if globalCompensate:
        # compensate global scale
        md = mc.createNode('multiplyDivide', n=transA+'_globalScale_compensate_md')
        mc.connectAttr(dist+'.distance', md+'.input1X', f=True)
        mc.connectAttr(globalCompensate+'.sx', md+'.input2X', f=True)
        mc.setAttr(md+'.op', 2)
        return md+'.outputX'
    else:
        return dist+'.distance'
    

def create_multDoubleLinear(plug1, plug2):
    '''
    return outputPlug that gives plug1 * plug2
    plug2 can also be a constant double
    '''
    name = plug1.split('.')[0]
    mdl = mc.createNode('multDoubleLinear', n=name+'_mdl')
    mc.connectAttr(plug1, mdl+'.input1', f=True)
    
    # check whether plug2 is a plug or constant
    if isinstance(plug2, basestring):
        # this is a string, so should be a plug
        # (since mdl does not accept string as inputs anyway)
        mc.connectAttr(plug2, mdl+'.input2', f=True)
    else:
        mc.setAttr(mdl+'.input2', plug2)
    
    return mdl+'.output'