import maya.cmds as mc

def removeOpenWindows():
    '''
    hide open windows, ignore MayaWindow and nexFloatWindow
    '''
    ignore = ['MayaWindow', 'nexFloatWindow']
    windows = mc.lsUI(wnd=True)
    
    toRemove = [win for win in windows if win not in ignore]
    
    for eachWin in toRemove:
        if mc.window(eachWin, q=True, vis=True):
            mc.window(eachWin, e=True, vis=False)
            
    