# from http://www.jason-parks.com/artoftech/?p=76

# developerTools.py
# make sure this method is in a module in your pythonpath

def connectToWing():
    """
    SYNOPSIS
     Connects to wingIDE debugger
    
    INPUTS NONE
    
    RETURNS: Nothing
    """
    import wingdbstub
    try:
        wingdbstub.Ensure()
        print 'Connected to wingIDE'
    except ValueError:
        print 'Could NOT connect to wingIDE'
            
