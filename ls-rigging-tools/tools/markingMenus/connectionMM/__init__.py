import pymel.core as pm
import maya.cmds as mc

def getRadialPos(posId):
    radialDict = {0:'N', 
                  1:'NE', 
                  2:'E',
                  3:'SE',
                  4:'S',
                  5:'SW',
                  6:'W',
                  7:'NW'}
    
    return radialDict.get(posId, None)

def createMM():
    '''
    '''
    selObjs = pm.ls(sl=True)
    print selObjs
    
    # if no valid objects, create menuItem that says that...
    if len(selObjs) == 0:
        pm.menuItem(l='No valid objects selected', en=False, rp='N')
        return None
    
    # if there are objects, make more menus
    
    # get inputs
    allInputs = []
    for eachObj in selObjs:
        allInputs += [input_ for input_ in eachObj.inputs(p=True, c=True)]
    
    with pm.menuItem(l='Inputs', en=True, rp='W', sm=1) as inputMM:
        if not allInputs:
            inputMM.setEnable(False)
        # submenu for input connections
        for inputId, eachInput in enumerate(allInputs):
            flags = {'l':eachInput[1] + ' >> ' + eachInput[0],
                    'en':True,
                    }
            if getRadialPos(inputId):
                flags['rp'] = getRadialPos(inputId) 
            pm.menuItem(**flags)

    
    # get outputs
    allOutputs = []
    for eachObj in selObjs:
        allOutputs += [output for output in eachObj.outputs(p=True, c=True)]
    
    with pm.menuItem(l='Outputs', en=True, rp='E', sm=1) as outputMM:
        if not allOutputs:
            outputMM.setEnable(False)
        # submenu for output connections
        for outputId, eachOutput in enumerate(allOutputs):
            flags = {'l':eachOutput[0] + ' >> ' + eachOutput[1],
                    'en':True,  
                    }
            if getRadialPos(outputId):
                flags['rp'] = getRadialPos(outputId) 
            pm.menuItem(**flags)

