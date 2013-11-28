import pymel.core as pm

class VertexLoops():
    '''
    Data structure for a list of vertex loops
    '''

    def __init__(self, selVerts, loopNum):
        '''
        Populates the data from an initial loop of verts, 
        and the number of loops around it
        
        selVerts - flattened list of MeshVertex
        loopNum - int
        '''
        
        # initialize lists for the loop
        previousLoop = selVerts
        nextLoop = []
        self.vertLoops = [list(previousLoop)]
        
        pm.select(selVerts, r=True)
        
        # traverse loops outward from selection
        for _ in range(loopNum):
            previousLoop += nextLoop
            pm.runtime.GrowPolygonSelectionRegion()
            selVertsLoop = pm.ls(sl=True, fl=True)
            nextLoop = [vert for vert in selVertsLoop if vert not in previousLoop]
            self.vertLoops.append(nextLoop)
        
    def length(self):
        return len(self.vertLoops)
    
    def __getitem__(self, key):
        return self.vertLoops[key]