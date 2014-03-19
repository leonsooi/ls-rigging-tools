'''
Class definitions for genes to build bind joints
'''

class Gene():
    '''
    abstract base class that for genes that "generate" bind joints
    '''
    def buildBnd(self):
        '''
        virtual function to be overriden by subclasses
        '''

class DirectGene(Gene):
    '''
    creates a bnd on a pLoc
    '''
    
    def __init__(self, name, pLoc, orient='world', abstract=False):
        '''
        name [string]
        pLoc [nt.Locator] - placement for bnd
        orient [enum] - 'world', 'normal', 'constraint'
        abstract [bool] - whether it creates an actual bnd, or if its just for interpolation
        '''
        
    def buildBnd(self):
        '''
        generate bnd jnt
        '''
        
class LoopGene(Gene):
    '''
    creates a series of bnds from a curve
    '''
    
    def __init__(self, name, pCrv, num, orient='world', cornersDefinition, cornersOverride=None):
        '''
        name [string]
        pCrv [nt.NurbsCurve] - placement for bnds
        num [int] - number of bnds between each corner
        orient [enum] - 'world', 'normal', 'constraint'
        cornersDefinition [dict of lambdas] - lamndas to calculate which cvs are the corners
            e.g. {'in' : ..., 'up' : ..., ...}
        cornersOverride [list of ints] - override cv indices for corners
        '''
        
    def buildBnd(self):
        '''
        '''
        
class InterpolateGene(Gene):
    '''
    create a bnd between other pLocs
    this genes must be built last (after direct and loop genes)
    '''
    
    def __init__(self, name, pLocsWeights, orient='world'):
        '''
        name [string]
        pLocsWeights [dict] - {pLoc: weight, ...}
        orient [enum] - 'world', 'normal', 'constraint'
        '''
        
    def buildBnd(self):
        '''
        '''