'''
Created on Jun 27, 2012

@author: Benjamin Slack
e-mail: iam@nimajneb.com

description: This package consists of various methods and 
techniques derived from AnimationRigs.com and implemented
by me using python and pymel.
'''
import pymel.core as pm
import maya.cmds as cmds
import re
import pickle
import collections
from _abcoll import Iterable

if __name__ == '__main__':
    pass

#master parameter synonyms list
syn = {'w':'w',
       'world':'w',
       'n':'n',
       'name':'n'}

string_type = "<type 'str'>"
transform_type = "<class 'pymel.core.nodetypes.Transform'>"
list_type = "<type 'list'>"

class MyError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def extractNodes (*args):
    if args == ():
        args = pm.selected()
    
    list_nodes = list()
    
    for arg in args:
        
        if (isinstance(arg, collections.Iterable)) and (repr(type(arg)) != string_type):
            iterated = extractNodes(*arg)
            for item in iterated:
                list_nodes.append(item)
        elif repr(type(arg)) == string_type:
            iterated = pm.ls(arg)
            for item in iterated:
                list_nodes.append(item)
        else:
            list_nodes.append(pm.PyNode(arg))

    return list(set(list_nodes))

eN = extractNodes

def rename (*args, **flags):
    '''
    created by Benjamin Slack, iam@nimajneb.com
    07.22.12
    
    usage:
    module.rename(name1, name2 ... name_n, keyword_arg1, keyword_arg2 ... keyword_arg_n)
    or
    module.rn(n1,n2...nN, k1, k2...kN)
    
    description:    
    Master renaming function. Can be used several ways. It operates on a list of objects,
    passed to it with the "list" parameter.
    
    -list    (list)
        default: pm.selected()
        
    -all    (bool)
        overrides 'list' to pm.ls(dag=1)
    
    The default operation of the function simply over writes the names of the listed 
    objects. It concatenates the non-keyword suppled string arguments into a "basename."
    
    -basename or -n (string)
        default: ''
    
    In addition to this <basename>, there are several named parameters which can add
    and modify the renaming.
    
    -master or -m    (string)
        default: ''
    
    -function or -f    (string)
        default: ''
        
    -location or -l    (string)
        default: ''
        
    -prefix or -p    (string)
        default: ''
    
    -suffix or -s    (string)
        default: ''
        
    The ordering of these modifications is controlled by the structure parameter.
    By changing this parameter, the caller can re-arrange how the keyword matching 
    letter the letter from the structure string
    
    -structure or -x (string)
        default: 'mflpns'

    The rename utility can use the namespace system Maya uses for referenced files.
    This is experimental, so use at own risk. (See Maya documentation: Namespaces.)
    
    -useNamespace or -ns (bool)
        default: False
        
    The second method of use is "replace." This option takes the first argument as
    a search pattern and the second as a replacement pattern. The search pattern can
    use regular expression syntax (see Python documentation) for pattern matching.
    Syntax Example: rename(<search_string>, <replacement_string>, r=1)
    
    -replace or -r (bool)
        default: True
        
    By default, the renaming utility checks children of the objects it renames.
    It carries those modifications down the branches, should it find appropriate
    matching. E.g. xxx_foot with the child xxx_foot_pointconstraint, renamed to
    xxx_hand, will result in xxx_hand_pointconstraint. If this behavior is not
    desired, it can be disabled.
    
    -checkChildren or -cc (bool)
        default: True
        
    '''
    
    defaults = {
               'm':'', 'master':'',
               'f':'', 'function':'',
               'l':'', 'location':'',
               'p':'', 'prefix':'',
               'n':'', 'basename':'',
               's':'', 'suffix':'',
               'x':'mflpns', 'structure':'mflpns',
               'r':False, 'replace':False,
               'ns':False, 'useNamespace':False,
               'cc':True, 'checkChildren':True,
               'list':pm.selected(),
               'all':False
               }
    
    #set states for function's switches
    for item in defaults.keys():
        try:
            defaults[item] = flags[item]
        except:
            pass
        
    #if the all flag is set, set the list to all objects
    if defaults['all']:
        defaults['list'] = pm.ls(dag=1)
    
    #setup the appropriate name separator
    if (defaults['ns'] or defaults['useNamespace']):
        separator = ':'
    else:
        separator = "_"
    
    if (defaults['r'] or defaults['replace']):
        #search and replace
        
        #error check input
        try:
            len_args = len(args)
        except:        
            raise MyError('Replacement selected without arguments')
            return
        
        if len_args == 0:
            raise MyError('Replacement selected without arguments')
            return
        elif len_args > 2:
            raise MyError('Too many arguments, expected: <search>, <replacement>')
            return
        elif len_args == 1:
            raise MyError('Too few arguments, expected: <search>, <replacement>')
            return
        
        #take first arg as search string
        search_str = args[0]

        #take second arg as replacement string
        replace_str = args[1]
        
        for obj in defaults['list']:
            #check for att parent
            try:
                att_is_parent = (obj.name()+'_att') == obj.getParent().name()
            except:
                att_is_parent = False
            
            # try inserted to protect from exception if empty gets passed in recursion
            try:
                pm.rename(obj, re.sub(search_str, replace_str, obj.name()))
            except:
                pass
            
            #rename parent att
            if att_is_parent:
                pm.rename(obj.getParent(), re.sub(search_str, replace_str, obj.getParent().name()))
            
            #search children for the rename pattern as well
            children_sans_shapes = list(set(obj.getChildren()).difference(set(obj.getChildren(s=1))))
            if defaults['cc'] and defaults['checkChildren']:   
                try:
                    for child in children_sans_shapes:
                        rename(search_str, replace_str, r=True, list=[child])
                except:
                    pass

    else:
        #simple rename

        #assemble a list of alpha numeric suffixes to be auto added on duplicates
        suffix_ords = range(ord('a'),ord('z')+1)
        suffix_chars = []
        for i in suffix_ords:
            suffix_chars.append(chr(i))
        for i in suffix_ords:
            for j in suffix_ords:
                suffix_chars.append(chr(i)+chr(j))
        
        #assemble from the unnamed parameters
        r_str = ''
        for i,arg in enumerate(args):
            r_str += arg
            if ((i+1) < len(args)):
                r_str += separator     
        defaults['n'] += r_str
        defaults['basename'] += r_str
        
        no_basename = (defaults['n'] == '') and (defaults['basename'] == '')
                    
        #do the simple rename
        for i, obj in enumerate(defaults['list']):
            r_str = ''

            if no_basename:
                defaults['n'] = obj.name()
    
            #assemble from the named parameters
            for j, x in enumerate(list(defaults['x'])):
                if not(defaults[x]==''):
                    r_str += defaults[x]
                    r_str += separator
            r_str = r_str[0:len(r_str)-1]
            
            #check to see if direct parent is a att node, if so flag for rename
            try:
                att_is_parent = (obj.name()+'_att') == obj.getParent().name()
            except:
                att_is_parent = False
            
            #if its a single rename, no suffix, multiple, append alpha suffix    
            add_suffix = ''
            if len(defaults['list']) == 1:
                add_suffix = ''
            elif no_basename:
                add_suffix = ''
            else:
                add_suffix = '_'+suffix_chars[i]
          
            # workaround to deal with the oddness of shape node auto renaming
            children_sans_shapes = list(set(obj.getChildren()).difference(set(obj.getChildren(s=1))))

            # if useNamespace add the root colon for the rename
            
            if (defaults['ns'] or defaults['useNamespace']):
                if defaults['cc'] and defaults['checkChildren']:
                    rename(obj.name(), ':'+r_str+add_suffix, r=True, list=children_sans_shapes)
                pm.rename(obj, ':'+r_str+add_suffix)
                if att_is_parent:
                    pm.rename(obj.getParent(), ':'+r_str+add_suffix+'_att')
            else:
                if defaults['cc'] and defaults['checkChildren']:
                    rename(obj.name(), r_str+add_suffix, r=True, list=children_sans_shapes)
                pm.rename(obj, r_str+add_suffix)
                if att_is_parent:
                    pm.rename(obj.getParent(), r_str+add_suffix+'_att')
    
    #namespace cleanup
    ns_stack = []
    for ns in pm.listNamespaces(recursive=1):
        #print '{0}, {1}\n'.format(repr(ns), repr(ns.listNodes(recursive=1)==[]))
        if ns.listNodes(recursive=1)==[]:
            ns_stack.append(ns)
    #print 'stack: {0}\n'.format(repr(ns_stack))
    while len(ns_stack) > 0:
        popped = ns_stack.pop()
        #print 'stack pop: {0}\n'.format(repr(popped))
        pm.namespace(rm=popped)   
    
rn = rename #alias for rename

def createAtt (*args):
    '''
    This function creates an "att" or attachment node. AKA zeroing 
    node. It takes an arbitrary number of string or nodes in and 
    returns the created nodes as an iterable list.
    '''
    if args == ():
        args == pm.selected()
    
    list_att_nodes = []
    list_nodes = extractNodes(*args)
    for a_node in list_nodes:
        att_node = pm.createNode('transform', n=a_node.name()+'_att', p=a_node)
        parent_of_the_node = a_node.getParent()
        if  parent_of_the_node == None:
            pm.parent(att_node, w=True)
        else:
            pm.parent(att_node, parent_of_the_node)
        pm.parent(a_node, att_node)
        list_att_nodes.append(att_node)
    return list_att_nodes

cAtt = createAtt #alias for createAtt

def createSpaces (obj2bind, *list_spaces, **flags):
    '''
    This function takes an object and binds it to an arbitrary number of parent
    spaces. It then sets up a "controller" object to house the switches for
    blending between those parent spaces. If no controller object is sent, one
    is created on the fly.
    '''
    
    #init flags
    defaults = {'w':False}
    
    #populate synonyms
    for item in flags.keys():
        try:
            flags[syn[item]] = flags[item]
        except:
            pass
    
    #override settings against flags    
    for item in defaults.keys():
        try:
            defaults[item] = flags[item]
        except:
            pass
    
    list_att = list() # init att capture list
    
    #init list_spaces
    try:
        list_spaces = extractNodes(*list_spaces)
    except:
        raise MyError('List of Spaces Is Invalid: Must Decompose to Transforms')
    
    #world space add flag actions

    if defaults['w']:
        if not(pm.ls('worldSpace')):
            world_space = pm.createNode('transform',n='worldSpace')
        else:
            world_space = pm.ls('worldSpace')[0]

            
        list_spaces = [world_space] + list_spaces
        
    #init object to bind
    try:
        obj2bind = extractNodes(obj2bind)[0]
    except:
        raise MyError('Binding Object Is Invalid: Must Decompose to Transform')
    
    obj2bind_att = createAtt(obj2bind)[0]
  
    #setup attachments
    for space in list_spaces: 
        this_name = '{0}_{1}_att'.format(space.name(),obj2bind.name())
        bind_att = pm.createNode('transform', n=this_name,p=obj2bind_att)
        pm.parent(bind_att, w=True)
        pm.parent(bind_att, space)
        list_att.append(bind_att)
       
    #setup binds
    pc = pm.pointConstraint(list_att,obj2bind_att,n=(obj2bind_att.name()+'_pc'))
    oc = pm.orientConstraint(list_att,obj2bind_att,n=(obj2bind_att.name()+'_oc'))

    #setup controller
    enum_list = str() #enum values for the controller switch
    for space in list_spaces:
        enum_list += space.name()+':'
    emum_list = enum_list[0:len(enum_list)-1]
    pm.addAttr(obj2bind, sn='spaceSwitch', at='enum', en=enum_list, h=False, k=True, r=True, w=True)
    
    #format expression string
    exp_string = str()
    for i, state in enumerate(list_spaces): #for every state of switch     
        exp_string += 'if ({0}.spaceSwitch == {1})'.format(obj2bind.name(),i)+ '{ \n'
        for j, weight in enumerate(pc.getWeightAliasList()): #for every weight in constraint list
            if i == j :
                weight_value = 1
            else:
                weight_value = 0
            exp_string += '    {0} = {1};\n'.format(weight,weight_value)
        for k, weight in enumerate(oc.getWeightAliasList()): #for every weight in constraint list
            if i == k :
                weight_value = 1
            else:
                weight_value = 0
            exp_string += '    {0} = {1};\n'.format(weight,weight_value)
        exp_string += '}\n'
    
    #create expression for controlling space weight
    exp = pm.expression(n=obj2bind.name()+'_exp',s=exp_string)

    pm.select(obj2bind) #dummy entry, remains to implement
    print obj2bind.name()+' bound to '+repr(list_spaces)+' control spaces'
    return(obj2bind)

#holding varible for quickAlign's transforms
qAback = []

def quickAlign(*args, **flags):
    '''
    07.26.12, Benjamin Slack, iam@nimajneb.com
    
    quickAlign orients an arbitrary number of transforms nodes to a target node.
    Parameters should be passed as a list of the form [<target>, <obj1>, <obj2> ... <objN>]
    In addition, two parameters modify quickAlign's functioning.
    
    -holdPositions or -h (bool)
    This flag will counter transform rotations of the aligned objects so that their
    position remains fixed. However, these operations are not undoable. So to allow
    them to be undone, a second parameter was introduced.
    
    -restore or -r (bool)
    This flag will restore the transform matricies of each obj to the state previous
    to the last quickAlign call. Note, the order passed to quick align must match
    exactly if the restoration is to be accomplished properly.
    
    If no arguments are passed to quickAlign, it will assumed it should operate on
    the currently selected objects.
    '''
    #access the last call of qA's stored transforms
    global qAback
    
    defaults = {'holdPositions':False, 'h':False,
                'restore':False, 'r':False}
    
    for item in defaults.keys():
        try:
            defaults[item] = flags[item]
        except:
            pass

    # if nothing gets passed, grab the selection
    if args == ():
        args = pm.selected()

    # if there's less that two items, throw error    
    if len(args) < 2:
        try:
            raise MyError('quickOrient Error: requires two or more nodes to be selected or passed\n')
        except MyError as e:
            print e.value
            return -1

    #if not a restore call, store the TM's of all the passed nodes
    if not(defaults['restore'] or defaults['r']):
        qAback = []
        for each_node in args:
            qAback.append(each_node.getMatrix(worldSpace=True))
            
    #else, on a restore call, copy all stored TM's back to the passed nodes
    else:
        for i, each_node in enumerate(args):
            each_node.setMatrix(qAback[i], worldSpace=True)
        pm.refresh()
        print 'quickAlign: Restored Transforms\n'
        return 1
        
    target = args[0]
    list_nodes = args[1:len(args)]
    
    #sort list_nodes by parents to children get aligned after parents
    stack = []
    leaves = []
    branches = []
    roots = []
    
    for this_node in list_nodes:
        #print 'this_node:{0} children:{1}\n'.format(repr(this_node),repr(this_node.getChildren(ad=1,typ='transform')))
        this_node_is_leaf = this_node.listRelatives(ad=1, typ='transform') == []
        if this_node_is_leaf :
            leaves.append(this_node)
            #print 'leaf: {0}\n'.format(repr(this_node))
        this_node_is_branch = (this_node.listRelatives(ap=1, typ='transform') != []) and (this_node.listRelatives(ad=1, typ='transform') != [])
        if this_node_is_branch :
            branches.append(this_node)
            #print 'branch: {0}\n'.format(repr(this_node))
        this_node_is_root = (this_node.listRelatives(ap=1, typ='transform') == []) and (this_node.listRelatives(ad=1, typ='transform') != [])
        if this_node_is_root :
            roots.append(this_node)
            #print 'root: {0}\n'.format(repr(this_node))
    
    stack = leaves + branches + roots
    
    #print 'stack: {0}\n'.format(stack)  
    
    pm.undoInfo(ock=True)
        
    if (defaults['holdPositions'] or defaults['h']) :
        #hold positions
        while len(stack) > 0:
            acting_node = stack.pop()
            cached_translations = []
            for this_node in acting_node.listRelatives(ad=1, typ='transform'):
                cached_translations.append(this_node.getTranslation(space='world'))
            acting_node.setRotation(target.getRotation(space='world'), space='world')
            for i,this_node in enumerate(acting_node.listRelatives(ad=1, typ='transform')):
                this_node.setTranslation(cached_translations[i], space='world')
    
    else:
        #respect parenting
        while len(stack) > 0:
            this_constraint = pm.orientConstraint(target, stack.pop())
            pm.delete(this_constraint)
    
    pm.undoInfo(cck=True)
    
    return 0

qA = quickAlign

def quickLookAt(*args, **flags):
    defaults = {
                'aim': (1,0,0),
                'sk': 'none',
                'u': (0,1,0),
                'wuo': None,
                'wut': 'scene',
                'wu': (0,1,0)
                }
    
    setDefaults(defaults, flags)
       
    args = empty_args_use_selected(args)

    if not(validateParameters(args, 'quickLookAt', 2)):
        return False
    
    target = args[0]
    
    bound = args[1:]
    
    for this_bound in bound:
        if defaults['wuo'] == None:
            aim_com = pm.aimConstraint(target, this_bound, aim = defaults['aim'], sk = defaults['sk'], u = defaults['u'], wut = defaults['wut'], wu = defaults['wu'])
        else:
            aim_com = pm.aimConstraint(target, this_bound, aim = defaults['aim'], sk = defaults['sk'], u = defaults['u'], wuo = defaults['wuo'], wut = defaults['wut'], wu = defaults['wu'])
        pm.delete(aim_com)
    
    return True

qL = quickLookAt

def quickMoveTo(*args, **flags):
    
    # if nothing gets passed, grab the selection
    if args == ():
        args = pm.selected()

    # if there's less that two items, throw error    
    if len(args) < 2:
        try:
            raise MyError('quickMoveTo Error: requires two or more nodes to be selected or passed\n')
        except MyError as e:
            print e.value
            return -1

    target = args[0]
    list_nodes = args[1:len(args)]
    
    for this_node in list_nodes:
        this_constraint = pm.pointConstraint(target, this_node)
        pm.delete(this_constraint)
        
    return 0

qM = quickMoveTo

def validateParameters(params, funcName, *args, **flags):
      
    if len(args) > 0:
        minP = args[0]
    else:
        minP = 0
    if len(args) > 1:
        maxP = args[1]
    else:
        maxP = float('inf')
    if len(args) > 2:
        try:
            raise MyError('checkParameters: too many parameters passed')
        except MyError as e:
            print e.value
            return False
       
    if len(params) == 0:
        try:
            raise MyError(funcName+': zero parameters.\n')
        except MyError as e:
            print e.value
            return False
    elif len(params) < minP:
        try:
            raise MyError(funcName+': less than required number of parameters.\n')
        except MyError as e:
            print e.value
            return False
    elif len(params) > maxP:
        try:
            raise MyError(funcName+': more than required number of parameters.\n')
        except MyError as e:
            print e.value
            return False
    else:
        return True
        
vP = validateParameters        

def setDefaults(defaults, flags):
    for item in defaults.keys():
        try:
            defaults[item] = flags[item]
        except:
            pass
    return defaults

def empty_args_use_selected(args):
    if args == ():
        args = pm.selected()
    return args
       
def attachHandle(*args, **flags):
    defaults = {
                'd':True, 'deleteHandle':True
                }   

    defaults = setDefaults(defaults, flags)
    
    args = empty_args_use_selected(args)
    
    #validate parameters
    args_are_valid = vp(args, 'attachHandle', 2)
    if args_are_valid:
        handle = list(args[0:len(args)-1])
        target = args[len(args)-1]
        
    #Error Checking
    this_item_had_type_error = False
    handle_not_transform = False
    for this_item in handle:           
        try:
            handle_type = repr(type(this_item))
        except MyError as e:
            this_item_had_type_error = True
            raise MyError("attachHandleError: item, {0} of 'handle' parameter gave error on type check.".format(repr(this_item)))
            print e.value
        if handle_type == string_type:
            this_item = pm.ls(this_item, tr=1)
        elif handle_type == transform_type:
            this_item = this_item
        else:
            handle_not_transform = True
            try:
                raise MyError('attachHandleError: object, {0} passed to \'handle\' parameter doesn\'t decompose to transform node.'.format(repr(this_item)))
            except MyError as e:
                print e.value

    target_not_transform = False
    try:
        target_type = repr(type(target))
    except:
        raise MyError("attachHandleError: object, {0}, of 'target' parameter gave error on type check.".format(repr(target)))    
    if target_type == string_type:
        target_node = pm.ls(target, tr=1)
    elif target_type == transform_type:
        target_node = target
    else:
        target_not_transform = True
        try:
            raise MyError('attachHandleError: object, {0}, of \'target\' parameter doesn\'t decompose to transform node.'.format(repr(target)))
        except MyError as e:
            print e.value

    if handle_not_transform or target_not_transform or (not(args_are_valid)) or this_item_had_type_error:
        return False
    
    #remove the shapes from the target    
    target_shape_nodes = target_node.listRelatives(s=1)
    for shape_node in target_shape_nodes:
        pm.delete(shape_node)
    
    #parent the new shapes onto the target
    for this_node in handle:
        pm.makeIdentity(this_node, a=True)
        this_node_shape_nodes = this_node.listRelatives(s=1)
        for shape_node in this_node_shape_nodes:
            pm.delete(shape_node, ch=True)
            pm.parent(shape_node, target_node, r=True, s=True)
        if defaults['d'] and defaults['deleteHandle']:
            pm.delete(this_node)
    
    for this_node in target_node.listRelatives(s=True):
        pm.rename(this_node, target_node.name()+'Shape#' )
    
    return True

aH = attachHandle

class RigContainer:
    def __init__(self,name='rig'):
        self.name = name
        if pm.objExists(self.name):
            is_script_node = repr(type(pm.ls(self.name))) == "<class 'pymel.core.nodetypes.Script'>"
            if is_script_node:   
                #don't create script node, it exists
                pass
            else:
                #create script node
                pass    
        else:
            #create script node
            pass
        
def parameterEcho(*args, **flags):
    print 'args: {0}, flags: {1}\n'.format(repr(args), repr(flags))
    
pE = parameterEcho       

class SimpleBlend:
    
    def __init__(self, *args, **flags):
        #flags for position and orientation
        self.defaults = {
                         'o': True, #orient
                         'p': True #position
                         }
        
        self.defaults = setDefaults(self.defaults, flags)
        
        # init object lists
        self.bindings = list()
        self.targets = list()
        
        #defaults
        self.pc_ext = '_pc'
        self.oc_ext = '_oc'
        self.exp_ext = '_exp'
        self.bound = None
        self.controller = None
        self.controller_attr = None
        self.controller_attr_name = 'simpleBlend'
        self.use_enum = False

        args = extractNodes(*args)
        if not(validateParameters(args, 'SimpleBlend', 2)):
            print 'SimpleBlend Exited: Nothing done.'
            return None
        else:
            pass
        
        self.setBound(args[len(args)-1])
        self.setTargets(*args[0:len(args)-1])
        
        try:
            self.controller = extractNodes(flags['controller'])[0]
        except:
            self.controller = self.bound
        try:
            self.controller_attr_name = flags['attr']
        except:
            pass
        try:
            self.use_enum = flags['use_enum']
        except:
            pass
        
        #print 'SimpleBlend __init__, targets: {0}, bound: {1}, controller{2}\n'.format(repr(self.targets), repr(self.bound), repr(self.controller))
        self.createBindings()
        
    #def __call__(self, *args, **flags):
    #    self.__init__(*args, **flags)
      
    def getController(self):
        return self.controller
    
    def setController(self, new_controller):
        self.removeBindings()
        self.controller = extractNodes(new_controller)[0]
        self.createBindings()
    
    def getControllerType(self):
        return self.controller_type
    
    def setControllerType(self, new_controller_type):
        self.removeBindings()
        self.controller_type = new_controller_type
        self.createBindings()
    
    def createBindings(self):
        if (self.bound == None) or (self.targets == []) or (self.controller == None) :
            return
            
        # set constraints
        if self.defaults['p']:
            pc = pm.pointConstraint(self.targets, self.bound, n=(self.bound.name()+self.pc_ext))
        if self.defaults['o']:
            oc = pm.orientConstraint(self.targets, self.bound, n=(self.bound.name()+self.oc_ext))

        if self.use_enum == True:
            #setup controller, currently only enum
            enum_list = str() #enum values for the controller switch
            for this_target in self.targets:
                enum_list += this_target.name()+':'
            emum_list = enum_list[0:len(enum_list)-1]
            pm.addAttr(self.controller, sn=self.controller_attr_name, at='enum', en=enum_list, h=False, k=True, r=True, w=True)
            self.controller_attr = self.controller.attr(self.controller_attr_name)
            
            #format expression string
            exp_string = str()
            for i, state in enumerate(self.targets): #for every state of switch     
                exp_string += 'if ({0} == {1})'.format((self.controller.name()+'.'+self.controller_attr_name),i)+ '{ \n'
                if self.defaults['p']:
                    for j, weight in enumerate(pc.getWeightAliasList()): #for every weight in constraint list
                        if i == j :
                            weight_value = 1
                        else:
                            weight_value = 0
                        exp_string += '    {0} = {1};\n'.format(weight,weight_value)
                if self.defaults['o']:
                    for k, weight in enumerate(oc.getWeightAliasList()): #for every weight in constraint list
                        if i == k :
                            weight_value = 1
                        else:
                            weight_value = 0
                        exp_string += '    {0} = {1};\n'.format(weight,weight_value)
                exp_string += '}\n'

            #create expression for controlling space weight
            exp = pm.expression(n=(self.bound.name()+self.exp_ext),s=exp_string)
            
            if self.defaults['p']:
                self.bindings.append(pc)
            if self.defaults['o']:
                self.bindings.append(oc)
            self.bindings.append(self.controller_attr)
            self.bindings.append(exp)
            
        else:
            #print 'trace: line 852, self.controller: {0}\n'.format(repr(self.controller))
            self.controller.addAttr(self.controller_attr_name, at='compound', nc=len(self.targets))
            for this_target in self.targets:
                #print 'trace: line 855, this_target: {0}\n'.format(repr(this_target))
                self.controller.addAttr(this_target.name(), at='float', p=self.controller_attr_name, min=0.0, max=1.0, k=1, h=0, r=1, w=1)
            self.controller_attr = self.controller.attr(self.controller_attr_name)
            if self.defaults['p']:
                pc_weights = pc.getWeightAliasList()
            if self.defaults['o']:
                oc_weights = oc.getWeightAliasList()
            for i, this_attr in enumerate(self.controller.attr(self.controller_attr_name).children()):
                if self.defaults['p']:
                    this_attr.connect(pc_weights[i])
                if self.defaults['o']:
                    this_attr.connect(oc_weights[i])
            
            #bindings
            if self.defaults['p']:
                self.bindings.append(pc)
            if self.defaults['o']:
                self.bindings.append(oc)
            self.bindings.append(self.controller_attr)
            
            #print 'SimpleBlend createBindings, bindings: {0}\n'.format(repr(self.bindings))
        
        
    def removeBindings(self):
        while self.bindings != []:
            binding = self.bindings.pop()
            if repr(type(binding)) == "<class 'pymel.core.general.Attribute'>":
                binding.delete()
            else:
                pm.delete(binding)
            
    def getBound(self):
        return self.bound
    
    def setBound(self, new_bound):
        self.removeBindings()
        self.bound = extractNodes(new_bound)[0]
        self.createBindings()
    
    def getTargets(self):
        return self.targets
    
    def setTargets(self, *new_targets):
        self.removeBindings()
        self.targets = extractNodes(*new_targets)
        self.createBindings()  

def jointFromLocator(loc=None, suffix='_loc', repl='_jnt', ss=True):
    joints = list()
    store_selected = pm.selected()
    if loc == None:
        loc = pm.selected()
    if not(isinstance(loc, collections.Iterable)):
        loc = list(loc)
    for this_loc in loc:
        this_loc = pm.PyNode(this_loc)
        joint_name = re.sub(suffix, repl, this_loc.name())
        if joint_name == this_loc.name():
            joint_name = joint_name + repl
        pm.select(this_loc)
        this_joint = pm.nodetypes.Joint(n=joint_name)
        pm.parent(this_joint, w=1)
        joints.append(this_joint)
    if ss:
        pm.select(store_selected)
    else:
        pm.select(joints)
    return joints

jFL = jointFromLocator

def locatorFromJoint(jnt=None, suffix='_jnt', repl='_loc', ss=True):
    locators = list()
    store_selected = pm.selected()
    if jnt == None:
        jnt = pm.selected()
    if not(isinstance(jnt, collections.Iterable)):
        loc = list(loc)
    for this_jnt in jnt:
        this_jnt = pm.PyNode(this_jnt)            
        loc_name = re.sub(suffix, repl, this_jnt.name())
        if loc_name == this_jnt.name():
            loc_name = loc_name + repl
        pm.select(cl=1)
        new_loc = pm.PyNode(cmds.spaceLocator(n=loc_name)[0])
        pm.parent(new_loc, this_jnt, r=1)
        pm.parent(new_loc, w=1)
        locators.append(new_loc)
    if ss:
        pm.select(store_selected)
    else:
        pm.select(locators)
    return locators

lFJ = locatorFromJoint

class IKFKLimb:
    '''
    To do list 10.19.12:
    
    1. Change Controller to be IK controller only
        a. Remove IK/FK switch from IK controller
    2. Hide IK and FK bones
    3. Create FK controllers
    4. Auto hide FK or IK controls based on IK/FK blend
    5. Implement Reorientation on setBaseJoints?
    6. Setup hand/foot attachment object
        a. follows base wrist for position always
        b. orients self to IK or FK control based on blend
    7. Share IK/FK Blend attribute between two controllers?
    8. Snap IK to FK
    9. Snap FK to IK
    10. Implement Stretch.
        a. IK Stretch (automatic)
        b. FK Stretch (manual)
        c. Blend Stretch
    11. Implement Bend/Bow
        a. linked to twist?
    12. Implement Twist Bones
        b. linked to bend/bow?
    
    
    
    '''
        
    def __init__(self, name='limb', character='', side='', base_joints=[]):
        #init from parameters
        self.name = name
        self.character = character
        self.side = side
        self.base_joints = base_joints
        
        #init primary objects
        self.att = None
        self.locators = list()
        self.ik_joints = list()
        self.fk_joints = list()
        self.bindings = list()
        self.base_joints_blends = list()
        self.att = None
        self.controller = None
        self.controller_spaces = list()
        self.controller_att = None
        self.controller_spaces_att = list()
        self.end_effector = None
        self.ikhd = None
        self.pv = None
        self.pvo = None
        self.controller_attr = None
        
        #default string attributes
        self.controller_attr_name = 'IK_FK'
        self.start_ext = '_srt'
        self.hinge_ext = '_hng'
        self.end_ext = '_end'
        self.loc_ext = '_loc'
        self.jnt_ext = '_jnt'
        self.base_ext = '_base'
        self.ik_ext = '_ik'
        self.fk_ext = '_fk'
        self.ef_ext = '_ef'
        self.ikhd_ext = '_ikhd'
        self.con_ext = '_ctrl'
        self.pv_ext = '_pv'
        self.pvo_ext = '_pvo'
        self.controller_spaces_att_ext = '_cs_att'
        self.rv_ext = '_rv'
          
    def prefix(self):
        return self.character + self.side + self.name

    def createLocators(self):
        start_name = self.prefix()+self.start_ext+self.loc_ext
        start = pm.PyNode(cmds.spaceLocator(n=start_name)[0])
        hinge_name = self.prefix()+self.hinge_ext+self.loc_ext
        hinge = pm.PyNode(cmds.spaceLocator(n=hinge_name)[0])
        end_name = self.prefix()+self.end_ext+self.loc_ext
        end = pm.PyNode(cmds.spaceLocator(n=end_name)[0])
        self.locators.append(start)
        self.locators.append(hinge)
        self.locators.append(end)
        return self.locators
            
    def destroyLocators(self):
        while not(self.locators == []):
            pm.delete(self.locators.pop())
        return None
   
    def createBaseJoints(self):
        self.removeBindings()
        self.base_joints = jointFromLocator(self.locators, self.loc_ext, self.jnt_ext)
        start = self.base_joints[0]
        hinge = self.base_joints[1]
        end = self.base_joints[2]
        quickLookAt(end, hinge, u=(0,0,1), wuo=start, wut='object')
        quickAlign(hinge, end)
        quickLookAt(hinge, start, u=(0,1,0), wuo=hinge, wut='objectrotation')
        for this_joint in self.base_joints:
            this_orient = pm.datatypes.Quaternion(this_joint.getTransformation().getRotationQuaternion())
            this_joint.setOrientation(this_orient)
            pm.makeIdentity(this_joint)
        pm.parent(end, hinge)
        pm.parent(hinge, start)
        self.att = createAtt(start)
        self.cleanupBlendJoints()
        self.createBindings()
        return self.base_joints

    def getBaseJoints(self):
        return self.base_joints
    
    def setBaseJoints(self, base_joints = []):
        self.removeBindings()
        if base_joints == []:
            base_joints = pm.selected()
        if len(base_joints) != 3:
            raise MyError('IKFKLimb.setBaseJoints requires a 3 joint chain.')
        
        ordered_base_joints = []
        base_joints_set = set(base_joints)
        root = None
        leaf = None
        branch = None
        for this_joint in base_joints:
            this_joint_is_not_leaf = False
            this_joint_is_not_root = False
            these_parents = this_joint.listRelatives(p=1)
            these_children = this_joint.listRelatives(c=1)
            for this_parent in these_parents:
                if (this_parent in base_joints_set):
                    this_joint_is_not_root = True
            for this_child in these_children:
                if (this_child in base_joints_set):
                    this_joint_is_not_leaf = True
            #print 'base_joints_set: {0}\n'.format(repr(base_joints_set))
            #print 'this_joint: {0}, these_children: {1}, these_parents: {2}\n'.format(repr(this_joint), repr(these_children), repr(these_parents))
            #print 'this_joint_is_not_leaf: {0}, this_joint_is_not_root: {1}\n'.format(this_joint_is_not_leaf, this_joint_is_not_root)
            if this_joint_is_not_root and this_joint_is_not_leaf:
                branch = this_joint
            elif this_joint_is_not_leaf and not(this_joint_is_not_root):
                root = this_joint
            elif not(this_joint_is_not_leaf) and this_joint_is_not_root:
                leaf = this_joint
        ordered_base_joints.append(root)
        ordered_base_joints.append(branch)
        ordered_base_joints.append(leaf)
        self.base_joints = ordered_base_joints
        #rename pieces
        root.rename(self.prefix()+self.start_ext)
        branch.rename(self.prefix()+self.hinge_ext)
        leaf.rename(self.prefix()+self.end_ext)
        
        self.att = createAtt(root)
        
        self.cleanupBlendJoints()
        
        self.createBindings()
        
        return self.base_joints
    
    def cleanupBlendJoints(self):
        if self.ik_joints != []:
            self.destroyIKJoints()
        self.createIKJoints()
        if self.fk_joints != []:
            self.destroyFKJoints()
        self.createFKJoints()

    def createIKJoints(self):
        pm.select(cl=1)
        start = pm.duplicate(self.base_joints[0], n=(self.prefix()+self.start_ext+self.ik_ext), po=1)[0]
        self.ik_joints.append(start)
        hinge = pm.duplicate(self.base_joints[1], n=(self.prefix()+self.hinge_ext+self.ik_ext), po=1)[0]
        self.ik_joints.append(hinge)
        end = pm.duplicate(self.base_joints[2], n=(self.prefix()+self.end_ext+self.ik_ext), po=1)[0]
        self.ik_joints.append(end)
        pm.parent(end, hinge)
        pm.parent(hinge, start)
        self.ikhd = pm.nodetypes.IkHandle(sj=start, ee=end, sol='ikRPsolver', n=(self.prefix()+self.ikhd_ext))
        self.end_effector = self.ikhd.getEndEffector()
        rename(self.prefix()+self.ef_ext, list = [self.end_effector])
        self.pvo = pm.PyNode(cmds.spaceLocator(n = self.prefix()+self.pvo_ext)[0])
        quickMoveTo(hinge, self.pvo)
        self.pv =  pm.animation.poleVectorConstraint(self.pvo, self.ikhd, n=(self.prefix()+self.pv_ext))
        return self.ik_joints
    
    def destroyIKJoints(self):
        completed_without_error = True
        try:
            pm.delete(self.pv)
        except:
            raise MyError('IKFKLimb.destroyIKJoints: Unable to delete Pole Vector Object.')
            completed_without_error = False
        try:
            pm.delete(self.pvo)
        except:
            raise MyError('IKFKLimb.destroyIKJoints: Unable to delete Pole Vector  Constraint.')
            completed_without_error = True
        try:
            pm.delete(self.ikhd)
        except:
            raise MyError('IKFKLimb.destroyIKJoints: Unable to delete IK Handle.')
            completed_without_error = True
        try:
            pm.delete(self.ik_joints[0])
        except:
            raise MyError('IKFKLimb.destroyIKJoints: Unable to delete IK Joints.')        
            completed_without_error = True
        self.ik_joints = []
        return completed_without_error
    
    def createFKJoints(self):
        pm.select(cl=1)
        start = pm.duplicate(self.base_joints[0], n=(self.prefix()+self.start_ext+self.fk_ext), po=1)[0]
        self.fk_joints.append(start)
        hinge = pm.duplicate(self.base_joints[1], n=(self.prefix()+self.hinge_ext+self.fk_ext), po=1)[0]
        self.fk_joints.append(hinge)
        end = pm.duplicate(self.base_joints[2], n=(self.prefix()+self.end_ext+self.fk_ext), po=1)[0]
        self.fk_joints.append(end)
        pm.parent(end, hinge)
        pm.parent(hinge, start)
        return self.fk_joints
    
    def destroyFKJoints(self):
        completed_without_error = True
        try:
            pm.delete(self.fk_joints[0])
        except:
            raise MyError('IKFKLimb.destroyIKJoints: Unable to delete FK Joints.')        
            completed_without_error = False
        self.fk_joints = []
        return completed_without_error
    
    def destroyAllJoints(self):
        while not(self.base_joints == []):
            pm.delete(self.base_joints.pop())
        while not(self.ik_joints == []):
            pm.delete(self.ik_joints.pop())
        while not(self.fk_joints == []):
            pm.delete(self.fk_joints.pop())
        while not(self.att == None):
            pm.delete(self.att)
          
    def createController(self):
        new_controller = pm.PyNode(cmds.spaceLocator(n=(self.prefix()+self.con_ext))[0])
        quickMoveTo(self.base_joints[2], new_controller)
        self.setController(new_controller)
        
    def destroyController(self):
        try:
            pm.delete(self.controller)
        except:
            print 'Could not destroy controller.\n'
          
    def getController(self):
        return self.controller
    
    def setController(self, new_controller):
        self.removeBindings()
        try:
            pm.delete(self.controller_reverse)
        except:
            pass
        self.controller = new_controller
        self.controller.addAttr(self.controller_attr_name, at='float', max=1, min=0, k=1, h=0)
        self.controller_attr = self.controller.attr(self.controller_attr_name)
        self.controller_att = createAtt(self.controller)
        self.controller_reverse = pm.nodetypes.Reverse(name=(self.prefix()+self.rv_ext))
        self.controller_attr.connect(self.controller_reverse.inputX)
        self.createBindings()
        
    def appendControllerSpaces(self, *args):
        self.removeBindings()
        for arg in args:           
            if isinstance(arg, Iterable):
                self.appendControllerSpaces(*arg)
            else:
                try:
                    self.controller_spaces.append(pm.PyNode(arg))
                except:
                    print 'The item {0} could not be added to the spaces list.\n'.format(repr(arg))
        self.controller_spaces = list(set(self.controller_spaces))
        self.createBindings()
        return self.controller_spaces
    
    def setControllerSpaces(self, *args):
        self.removeBindings()
        self.controller_spaces = []
        self.appendControllerSpaces(*args)
        self.createBindings()
        return self.controller_spaces
    
    def getControllerSpaces(self):
        return self.controller_spaces
    
    def createControllerSpaceAttachments(self):
        self.destroyControllerSpaceAttachments()
        for this_space in self.controller_spaces:
            #create att clone
            this_name = this_space.name()+self.controller_spaces_att_ext
            this_space_att = pm.duplicate(self.controller_att, po=1, name=this_name)
            #unparent clone in place
            try:
                pm.parent(this_space_att, w=1)
            except:
                #already a parent of world
                pass
            #parent clone in place to space node
            pm.parent(this_space_att, this_space)
            #append the bind node to the list of bind nodes
            self.controller_spaces_att.append(this_space_att)
        return self.controller_spaces_att
    
    def destroyControllerSpaceAttachments(self):
        while self.controller_spaces_att:
            pm.delete(self.controller_spaces_att.pop())
        
    def bindJoints(self):
        #setup simple blends on ik & fk to the base arm
        self.base_joints_blends = []
        for i, this_joint in enumerate(self.base_joints):
            #print 'i: {0}, this_joint: {1}\n'.format(repr(i), repr(this_joint))
            #print 'SimpleBlend({0},{1},{2})\n'.format(repr(self.ik_joints[i]), repr(self.ik_joints[i]), repr(this_joint))
            this_simple_blend = SimpleBlend(self.ik_joints[i], self.fk_joints[i], this_joint, p=0)
            self.base_joints_blends.append(this_simple_blend)
            self.bindings.append(this_simple_blend)
            
    def connectBoundJointsToController(self):
        # mutli/divide node
        for this_blend in self.base_joints_blends:
            this_blend_attr = this_blend.controller_attr.children()
            self.controller_attr.connect(this_blend_attr[0])
            self.controller_reverse.outputX.connect(this_blend_attr[1])
            
    def bindControllerToSpaces(self):
        this_simple_blend = SimpleBlend(self.controller_spaces_att, self.controller)
        self.bindings.append(this_simple_blend)
    
    def bindIKHandleToControllerPos(self):
        this_pc = pm.pointConstraint(self.controller, self.ikhd, name=(self.prefix()+'_ctrl_pc'))
        print repr(this_pc) 
        self.bindings.append(this_pc)
    
    def bindBaseEndtoControllerRot(self):
        #fk_oc = pm.orientConstraint(self.controller, self.fk_joints[2], name=(self.prefix()+'_fkctrl_oc'))
        ik_oc = pm.orientConstraint(self.controller, self.ik_joints[2], name=(self.prefix()+'_ikctrl_oc'))
        #self.bindings.append(fk_oc)
        self.bindings.append(ik_oc)
    

    def createBindings(self):
        print 'createBindings\n'
        try:
            joints_are_ready = (self.base_joints != []) and (self.ik_joints != []) and (self.fk_joints != [])
        except:
            joints_are_ready = False
        print 'joints_are_ready: {0}'.format(joints_are_ready)
        if joints_are_ready:
            self.bindJoints()
        
        try:
            controller_is_ready = (self.controller != None)
        except:
            controller_is_ready = False
        print 'controller_is_ready: {0}'.format(controller_is_ready)
        if controller_is_ready and joints_are_ready:
            self.connectBoundJointsToController()
            self.bindIKHandleToControllerPos()
            self.bindBaseEndtoControllerRot()
        
        try:
            spaces_exist = (self.controller_spaces != [])
        except:
            spaces_exist = False
        print 'spaces_exist: {0}'.format(spaces_exist)
        if spaces_exist:
            self.createControllerSpaceAttachments()
            self.bindControllerToSpaces()
            
        print 'createBindings return'
    
    def removeBindings(self):
        print 'removeBindings\n'
        print 'bindings: {0}\n'.format(repr(self.bindings))
        while self.bindings:
            this_bind = self.bindings.pop()
            print 'this_bind: {0}\n'.format(repr(this_bind))
            print 'this_bind.bindings: {0}\n'.format(repr(this_bind.bindings))
            try:
                this_bind.removeBindings()
            except:
                pass
            try:
                pm.delete(this_bind)
            except:
                pass
        print 'removeBindings return\n'

class PickleJar:
    pickles = []
    def __init__(self, name='pickleJar'):
        self.jar = pm.sys.scriptNode(n=name)
    def __del__(self):
        pass
    def addPickle(self, obj):
        pass
    def takePickle(self, pickle):
        pass
    def emptyIt(self):
        for pickle in self.pickles:
            self.takePickle(pickle)
    def dumpIt(self):
        pickles = []
        pass