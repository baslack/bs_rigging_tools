import maya.cmds as cmds

#short hand for selected, cmds.ls(sl=1)
sel = lambda: cmds.ls(sl=1)

def clamp(min_val, max_val, val):
    return max(min(val, max_val), min_val)

saturate = lambda x: clamp(0,1,x)

def smootherstep(edge0, edge1, x):
    edge0 = float(edge0)
    edge1 = float(edge1)
    x = float(x)
    x = saturate((x-edge0)/(edge1-edge0))
    return x*x*x*(x*(x*6-15)+10)

def getAttrFromChannel(channel_name):
    #channel_name = channel_name.replace('_', '.', 1)
    channel_name = cmds.listConnections(channel_name, d=1, p=1)[0]
    return channel_name

def connectToEclipse():
    import pydevd
    pydevd.settrace(stdoutToServer=True, stderrToServer=True, suspend=False)

def flagTest(key, flags):
    if key in flags:
        return bool(flags[key])
    else:
        return False

def prepInput(source_flag, destination_flag, **flags):
    '''
    Parses Arguments and Selections into something functions can use.
    '''
    
    #check for flags
    
    if flagTest(source_flag, flags):
        sourceObjs = flags[source_flag]
    else:
        sourceObjs = None
    
    if flagTest(destination_flag, flags):
        destinationObjs = flags[destination_flag]
    else:
        destinationObjs = None
           
    # strings get passed, we map them to lists
    if (type(sourceObjs) == type(str())) or (type(sourceObjs) == type(unicode())):
        sourceObjs = [sourceObjs]
    if (type(destinationObjs) == type(str())) or (type(destinationObjs) == type(unicode())):
        destinationObjs = [destinationObjs]
    
    #defaults to last object as blend
    if not(sourceObjs):
        sourceObjs = cmds.ls(sl=1)[len(cmds.ls(sl=1))-1]
        if type(sourceObjs) != type(list()):
            sourceObjs = [sourceObjs]
    
    #defaults to first to second from last objects as targets    
    if not(destinationObjs):
        destinationObjs = cmds.ls(sl=1)[:len(cmds.ls(sl=1))-1]
        if type(destinationObjs) != type(list()):
            destinationObjs = [destinationObjs]
    
    #remove non-transforms from the lists
    for obj in sourceObjs:
        if cmds.nodeType(obj) != 'transform':
            sourceObjs.remove(obj)
    
    for obj in destinationObjs:
        if cmds.nodeType(obj) != 'transform':
            destinationObjs.remove(obj)
    
    return (sourceObjs, destinationObjs)