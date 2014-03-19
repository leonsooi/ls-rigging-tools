'''
Created on Dec 30, 2013

@author: Leon
'''

import pymel.core as pm

class Selector(pm.uitypes.TextFieldButtonGrp):
    '''
    class for selector elements
    '''
    __all__ = set()
    __displayMode__ = 2 # 0:longName, 1:shortName, 2:nodeName
    __componentMode__ = True # only show componentIds for component selections
    
    def __new__(cls, name=None, lw=60, **kwargs):
        '''
        lw (int): width of the label column
        '''
        # label defaults to ''
        label = kwargs.pop('l', '')
        label = kwargs.pop('label', label)
        
        # kwargs to always override internally
        # use long names here, because they seem to override short names
        kwargs['adjustableColumn'] = 2
        kwargs['columnWidth3'] = lw, 100, 20
        kwargs['buttonLabel'] = '<<'
        kwargs['editable'] = False

        # create instance
        self = pm.uitypes.TextFieldButtonGrp.__new__(cls, name=None, label=label, **kwargs)
        
        return self
    
    
    def __init__(self, name=None, lw=60, **kwargs):
        '''
        '''
        # add to all, to keep track of all instances
        self.__class__.__all__.add(self)
        
        # initialize variables
        self.selection = list()
        
        # if buttonCommand is defined,
        # assign to additionalCmd
        self.additionalCmd = kwargs.pop('bc', None)
        self.additionalCmd = kwargs.pop('buttonCommand', self.additionalCmd)
        # button will call loadSelection
        # loadSelection will call additionCmd if defined
        self.buttonCommand(pm.Callback(self.loadSelection))

    def loadSelection(self):
        '''
        loads selected objects into selection list,
        and display in textField
        '''
        self.selection = pm.ls(sl=True)
        
        self.refreshDisplay()
        
        if self.additionalCmd:
            self.additionalCmd()
        
    def refreshDisplay(self):
        '''
        refresh display selection in textField
        '''
        text = ', '.join([sel.name() for sel in self.selection])
        self.setText(text)
        
    def getSelection(self):
        return self.selection
    
    def setSelection(self, sel):
        '''
        sel (list of pyNodes)
        '''
        self.selection = sel
        self.refreshDisplay()
        