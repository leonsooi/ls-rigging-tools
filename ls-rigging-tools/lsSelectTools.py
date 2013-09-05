import maya.cmds as mc

def selectVertsFromIdList(mesh, idList):
    '''
    '''
    sel = [mesh+'.vtx[%d]'%eachId for eachId in idList]
    mc.select(sel, r=True)
    

def selVertsFromSourceMesh(destMesh, selVerts):
    destVerts = ['%s.%s' % (destMesh, vertName.split('.')[-1]) for vertName in selVerts]
    mc.select(destVerts, r=1)
    
def selVertsFromSourceMeshGo():
    '''
    Select verts on sourceMesh, select destMesh, execute
    '''
    sel = mc.ls(os=1, fl=1)
    destMesh = sel[-1]
    selVerts = sel[:-1]
    selVertsFromSourceMesh(destMesh, selVerts)

# flip selection
def lsFlipSelection(selection, swap=['L_','R_']):
    if selection[:2] == swap[0]:
        newSelection = selection.replace(swap[0], swap[1])
    elif selection[:2] ==swap[1]:
        newSelection = selection.replace(swap[1], swap[0])
    else:
        mc.warning('Prefix not found')
        return
    if mc.objExists(newSelection):
        mc.select(newSelection, r=1)
    else:
        mc.warning('No mirror found')
