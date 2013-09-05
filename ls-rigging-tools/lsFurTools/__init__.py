import maya.cmds as mc
import glob
import os

def printFurAttrs():
    # get dictionary of mapped fur attributes
    '''
    { furDescription : { surface : [map1, map2, map3...]}}
    '''
    furMapsPath = r'S:\Leon.Sooi\Private\maya\projects\Rigs\renderData\fur\furAttrMap'.replace('\\', '/')
    fileName = os.path.splitext(mc.file(q=1, sn=1, shn=1))[0]
    mapList = glob.glob('%s/%s_*' % (furMapsPath, fileName))
    mapList = [os.path.splitext(os.path.basename(path))[0].replace(fileName+'_', '') for path in mapList]
    surfaceList = [map_.split('_')[0] for map_ in mapList]
    furList = [map_.split('_')[1] for map_ in mapList]
    attrList = [map_.split('_')[2] for map_ in mapList]
    
    furDict = {}
    
    for eachFur, eachSurface, eachAttr in zip(furList,surfaceList,attrList):
        if eachFur in furDict:
            # add to furDict[eachFur]
            if eachSurface in furDict[eachFur]:
                # add to furDict[eachFur][eachSurface]
                furDict[eachFur][eachSurface].append(eachAttr)
            else:
                # create list and append to furDict[eachFur]
                furDict[eachFur][eachSurface] = [eachAttr]
        else:
            # create surfaceDict and append to furDict
            surfaceDict = {}
            surfaceDict[eachSurface] = [eachAttr]
            furDict[eachFur] = surfaceDict
            
    # print fur attrs
    print "\n------------------------------------------------------------"
    for eachFur, surfaceDict in furDict.items():
        print "FUR: %s" % eachFur.upper()
        for eachSurface, attrList in surfaceDict.items():
            print '%s - %s' % (eachSurface, ', '.join(attrList))
        print '\n'