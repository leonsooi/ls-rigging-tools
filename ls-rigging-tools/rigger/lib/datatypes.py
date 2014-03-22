class Tree():
	'''
	A very simple tree data structure
	'''
	def __init__(self):
		'''
		Init data and children
		'''
		self.data = None
		self.children = []
	
	def isLeaf(self):
		return self.children == []
	
	def getDescendents(self, generation=1):
		'''
		Recursive function to traverse and return descendents
		There is probably a better way to do this without recursion???
		Returns list of descendents
		'''
		if generation == 1:
			return self.children
		else:
			descendents = []
			for eachChild in self.children:
				descendents += eachChild.getDescendents(generation-1)
			return descendents
	
	def getDescendentsData(self, generation=1):
		return [tree.data for tree in self.getDescendents(generation)]
	
	def getAllDescendents(self):
		allDescendents = []
		generation = 1
		while self.getDescendents(generation):
			allDescendents += self.getDescendents(generation)
			generation += 1
		return allDescendents
	
	def getAllDescendentsData(self):
		return [tree.data for tree in self.getAllDescendents()]