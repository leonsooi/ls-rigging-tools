class Tree():

    def __init__(self):
        '''
        Constructor
        '''
        self.data = None
        self.children = []
        
    def isLeaf(self):
        return self.children == []
    
    def getDescendents(self, generation=1):
        if generation == 1:
            return self.children
        else:
            descendents = []
            for eachChild in self.children:
                descendents += eachChild.getDescendents(generation-1)
            return descendents