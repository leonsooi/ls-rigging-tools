import glob
import os

def removeFineIncrements():
    '''
    '''
    path = r'G:\BACKUP\Documents\maya\projects\Sylph\scenes'

    incrementsTable = {} # {'basename.ext': [basename.####.ext, basename.####.ext]}
    allFineIncrements = glob.glob(path+'/*.[0-9][0-9][0-9][0-9].*')
    allFineIncrements = [os.path.basename(f) for f in allFineIncrements]
    allMainIncrements = ['.'.join(f.split('.')[:-2] + [f.split('.')[-1]]) for f in allFineIncrements]
    allUniqueMainIncrements = list(set(allMainIncrements))
    
    for eachUniqueMainInc in allUniqueMainIncrements:
        fineIncs = [f for f in allFineIncrements if f.split('.')[:-2] == eachUniqueMainInc.split('.')[:-1] and f.split('.')[-1] == eachUniqueMainInc.split('.')[-1]]
        incrementsTable[eachUniqueMainInc] = fineIncs
    
    # in each list, just keep the latest file
    # preview deletion
    for main, fines in incrementsTable.items():
        print main
        for f in fines[:-1]:
            print '--- ' + f + ' -delete'
        print '--- ' + fines[-1] + ' -keep'        
        
    # actual deletion
    for main, fines in incrementsTable.items():
        print main
        for f in fines[:-1]:
            print '--- ' + f + ' -delete'
            fullpath = path.replace('\\', '/') + '/' + f
            print fullpath
            if os.path.isfile(fullpath):
                print 'file exists'
                os.remove(fullpath)
            else:
                print 'no file found'
        print '--- ' + fines[-1] + ' -keep'  
        


def removeFilesBetweenInterval():
    '''
    '''
    # remove files between intervals (in seconds)
    interval = 28800
    path = r'G:\BACKUP\Documents\maya\projects\ANIM350\scenes'
    rpath = path.replace('\\', '/') + '/'
    
    incrementsTable = {} # {'basename.ext': [basename.####.ext, basename.####.ext]}
    allFineIncrements = glob.glob(path+'/*.*')
    allFineIncrements = [os.path.basename(f) for f in allFineIncrements]
    allMainIncrements = [os.path.splitext(f)[0].rstrip('1234567890') + os.path.splitext(f)[1] for f in allFineIncrements]
    allUniqueMainIncrements = list(set(allMainIncrements))
    
    for eachUniqueMainInc in allUniqueMainIncrements:
        fineIncs = [f for f in allFineIncrements if os.path.splitext(f)[0].rstrip('1234567890') == os.path.splitext(eachUniqueMainInc)[0] and f.split('.')[-1] == eachUniqueMainInc.split('.')[-1]]
        incrementsTable[eachUniqueMainInc] = fineIncs
    
    # in each list, just keep the latest file
    # preview deletion
    for main, fines in incrementsTable.items():
        print main
        currTime = os.stat(rpath+fines[0]).st_mtime
        for f in fines[1:-1]:
            nextTime = os.stat(rpath+f).st_mtime
            if nextTime - currTime < interval:
                print '--- ' + f + ' -delete'
            else:
                print '--- ' + f + ' -keep'
                currTime = nextTime
        print '--- ' + fines[-1] + ' -keep\n'        
        
    # actual deletion
    for main, fines in incrementsTable.items():
        print main
        currTime = os.stat(rpath+fines[0]).st_mtime
        for f in fines[1:-1]:
            nextTime = os.stat(rpath+f).st_mtime
            if nextTime - currTime < interval:
                print '--- ' + f + ' -delete'
                fullpath = rpath + f
                if os.path.isfile(fullpath):
                    print 'file exists'
                    os.remove(fullpath)
            else:
                print '--- ' + f + ' -keep'
                currTime = nextTime
        print '--- ' + fines[-1] + ' -keep\n'  