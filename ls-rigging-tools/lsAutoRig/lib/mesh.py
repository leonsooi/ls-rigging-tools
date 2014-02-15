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
        
        pm.progressWindow(title='Analyzing edge loops', progress=0, max=loopNum)
        
        # traverse loops outward from selection
        for loopId in range(loopNum):
            previousLoop += nextLoop
            pm.runtime.GrowPolygonSelectionRegion()
            selVertsLoop = pm.ls(sl=True, fl=True)
            nextLoop = [vert for vert in selVertsLoop if vert not in previousLoop]
            self.vertLoops.append(nextLoop)
            # increment progress window
            pm.progressWindow(e=True, step=1, status='\nAnalyzing loop %d' % (loopId+1))
        
        pm.progressWindow(e=True, endProgress=True)
        
    def length(self):
        return len(self.vertLoops)
    
    def __getitem__(self, key):
        return self.vertLoops[key]