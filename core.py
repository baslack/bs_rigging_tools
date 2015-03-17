import re as re
from func import * #@UnusedWildImport
#from func import prepInput

def createAtt(*args, **flags):
    if args == None:
        selected = cmds.ls(sl=1)
    else:
        selected = args
    for this_node in selected:
        if not cmds.ls('att_{0!s}'.format(this_node)):
            att_node = cmds.createNode('transform', n='att_'+this_node, p=this_node)
            cmds.parent(att_node, w=1)
            cmds.parent(this_node, att_node)
        else:
            att_node = cmds.ls('att_{0!s}'.format(this_node))[0]
    return att_node
#alias createAtt
cAtt = createAtt

def rename(replacement_string, *target_nodes, **flags):

    connectToEclipse()
    if len(target_nodes) == 0:
        target_nodes = cmds.ls(sl=1)
    
    count = 0
    
    for this_node in target_nodes:
        if flagTest('p',flags):
            cmds.rename(this_node, replacement_string+'_'+this_node)
        if flagTest('s',flags):
            cmds.rename(this_node, this_node+'_'+replacement_string)
        if flagTest('r',flags):
            print this_node+'\n'
            this_node_renamed = unicode(re.sub(flags['r'], replacement_string, this_node))
            test = this_node == this_node_renamed
            if not(test):
                try:
                    cmds.rename(this_node, this_node_renamed)
                except:
                    pass
        if not(flagTest('p',flags) or flagTest('s',flags) or flagTest('r',flags)):
            if (count==0):
                multi_suffix = ''
            else:
                multi_suffix = '_'+str(count)
            cmds.rename(this_node, replacement_string+multi_suffix)
            count += 1         
#alias rename
rn = rename

def alignTo(align_node, *target_nodes, **flags):
    if len(target_nodes) == 0:
        target_nodes = cmds.ls(sl=1)
    
    #save selection
    selected = cmds.ls(sl=1)
    cmds.select(cl=1)
    
    for this_node in target_nodes:
        c_node = cmds.orientConstraint(align_node, this_node)
        cmds.delete(c_node)
        
    #restore selection
    cmds.select(*selected)
#alias quickAlign#
aT = alignTo

def moveTo(moveto_node, *target_nodes, **flags):
    if len(target_nodes) == 0:
        target_nodes = cmds.ls(sl=1)
    
    selected = cmds.ls(sl=1)
    cmds.select(cl=1)
    
    for this_node in target_nodes:
        c_node = cmds.pointConstraint(moveto_node, this_node)
        cmds.delete(c_node)
    
    cmds.select(*selected)
#alias
mT = moveTo

def lookAt(lookat_node, *target_nodes, **flags):
    
    if len(target_nodes) == 0:
        target_nodes = cmds.ls(sl=1)
    
    selected = cmds.ls(sl=1)
    cmds.select(cl=1)

    if not('aim' in flags):
        flags['aim'] = [1,0,0]
    
    if not('u' in flags):
        flags['u'] = [0,1,0]
    
    if not('wut' in flags):
        flags['wut'] = 'scene'
        
    if not('wuo' in flags):
        flags['wuo'] = None
    
    if not('wu' in flags):
        flags['wu'] = [0,1,0]
        
    for this_node in target_nodes:
        if (flags['wut'] == 'object') or (flags['wut'] == 'objectrotation'):
            c_node = cmds.aimConstraint(lookat_node, this_node, aim=flags['aim'],
            u=flags['u'], wu=flags['wu'], wut=flags['wut'], wuo=flags['wuo'] )
        else:
            c_node = cmds.aimConstraint(lookat_node, this_node, aim=flags['aim'],
            u=flags['u'], wu=flags['wu'], wut=flags['wut'])
        cmds.delete(c_node)

    cmds.select(*selected)
#alias
lA = lookAt

def attachHandle(handle_node, *target_nodes, **flags):
    if len(target_nodes) == 0:
        target_nodes = cmds.ls(sl=1)
    
    selected = cmds.ls(sl=1)
    cmds.select(cl=1)
    
    for this_node in target_nodes:
        this_handle = cmds.duplicate(handle_node)
        this_handle_shapes = cmds.listRelatives(this_handle, s=1)
        for this_shape in this_handle_shapes:
            new_shape_name = cmds.rename(this_shape, this_node+'Shape')
            cmds.parent(new_shape_name, this_node, r=1, s=1)
        cmds.delete(this_handle)
    
    if not("k" in flags):
        cmds.delete(handle_node)
    elif not(flags['k']):
        cmds.delete(handle_node)
    
    cmds.select(selected)        #alias
aH = attachHandle

def setupEnumSwitch(switch_node, enum_names, controlled_attrs, **flags):
    '''
    setupEnumSwitch(switch_node, enum_names, controlled_attrs, **flags)
    
    description:
    Setups up a basic enumerated switch attribute. Uses set driven key
    to drive the various controlled attributes. 
    
    flags accepted:
    switch_name: string, default: 'myEnum', the name of the attribute
    to be added to the switch_node.
    
    enum_values: dict or list,  overrides the default values of the enumerated 
    type with the values supplied. Must match the length of enum_names.
    
    states: dict of dict or dict of lists, format states[controlled_attribute]
    [enum_name]= value (float). Alternate format, states[controlled_attribute]
    <list of values>. By default, it will setup through the attributes and
    switch states, using a modulo to populate the states of the switches
    if they match. Setting this flag requires the user to specify the
    values for each attribute at each setting of the switch.
    
    '''
      
    #enable for debug
    connectToEclipse()
    
    #set defaults
    defaults = {
                'switch_name':'myEnum'
                }
    
    #setup for flag on states
    error_state = False
    try:
        #user supplied states
        states = flags['states']
        #check for dict
        if type(states) != type(dict()):
            error_state = True
            raise Warning('setupEnumSwitch: {0!r} passed via flag \'states\', expected dict.\n'.format(states))
        else:
            for this_attr in controlled_attrs:
                if type(states[this_attr]) == type(dict()):
                    for this_enum in enum_names:
                        if this_enum not in states[this_attr]:
                            error_state = True
                            raise Warning('setupEnumSwitch: enum_name, {0!s}, is not represented in flag \'states\', {1!s}.\n'.format(this_enum, this_attr))
                elif type(states[this_attr]) == type(list()):
                    if len(states[this_attr]) != len(enum_names):
                        error_state = True
                        raise Warning('setupEnumSwitch: {0!r} passed to flags \'states\' doesn\'t match length of {1!r}.\n'.format(states[this_attr], enum_names))
                    #convert the list to a dict so that the later code will only have one scenario to deal with
                    temp_dict = {}
                    for i, this_enum in enumerate(enum_names):
                        temp_dict[this_enum] = states[this_attr][i]
                    states[this_attr] = temp_dict
                else:
                    error_state = True
                    raise Warning('setupEnumSwitch: {0!r} passed via flag \'states\', expected dict or list.\n'.format(states[this_attr]))
    except:
        if error_state:
            return
        #default modulo setup for states
        states = {}
        for i, this_attr in enumerate(controlled_attrs):
            states[this_attr] = {}
            for j, this_enum in enumerate(enum_names):
                if i % len(enum_names) == j % len(controlled_attrs):
                    states[this_attr][this_enum] = 1.0
                else:
                    states[this_attr][this_enum] = 0.0
    
    #check for flag on switch name, overwrite default if it exists
    try:
        if flags['switch_name']:
            defaults['switch_name'] = flags['switch_name']
    except:
        pass
    
    #assemble string for enum names parameter, append values if they are supplied
    error_state = False
    try:
        #bombs if the flag isn't passed goes to the default case
        enum_values = flags['enum_values']
        #if it's a dict, make sure all the names are represented
        if type(enum_values) == type(dict()):
            for this_enum in enum_names:
                if this_enum not in enum_values:
                    error_state = True
                    raise Warning('setupEnumSwitch: enum_name, {0!s}, not represented in enum_values, {1!r}.\n'.format(this_enum, enum_values))
        #if it's a list, make sure there's enough values for the names
        elif type(enum_values) == type(list()):
            temp_dict = {}
            if len(enum_names) != len(enum_values):
                error_state = True
                raise Warning('setupEnumSwitch: length of enum_names, {0!r}, not equal to enum_values, {1!r}.\n'.format(enum_names, enum_values))
            else:
                for i, this_enum in enumerate(enum_names):
                    temp_dict[this_enum] = enum_values[i]
                enum_values = temp_dict
        #else, bomb out
        else:
            error_state = True
            raise Warning('setupEnumSwitch: {0!r} passed to enum_values, expected dict or list.\n'.format(enum_values))
        #compile the string for the enum, combing the names and values
        combo_list = []
        for this_enum in enum_names:
            combo_list.append(this_enum+'='+str(enum_values[this_enum]))
        enum_str = ':'.join(combo_list)
    except:
        if error_state:
            return
        enum_str = ':'.join(enum_names)
    
    #add enum to the switch node
    cmds.addAttr(switch_node, sn=defaults['switch_name'], at='enum', en=enum_str, k=1, h=0)
    
    #compile switch attr for linking
    switch_attr = '{0!s}.{1!s}'.format(switch_node, defaults['switch_name'])
    
    #for each controlled attr
        #create an animCurveUL node to drive that attr
        #set keyframes on the curve to the switch values
        #connect the switch to the input of the curve
        #connect the controlled attr to the output of the curve
      
    drivers = []    
    for i, this_attr in enumerate(controlled_attrs):
        this_driver = cmds.createNode('animCurveUL', n=this_attr.replace('.','_'))
        drivers.append(this_driver)
        for j, this_enum in enumerate(enum_names):
            cmds.setKeyframe(this_driver, f=enum_values[this_enum], v=states[this_attr][this_enum])
        cmds.connectAttr(switch_attr, '{0!s}.input'.format(this_driver))
        cmds.connectAttr('{0!s}.output'.format(this_driver), this_attr, f=1)
    
    cmds.select(switch_node)
    return switch_attr
                 
def setupAttrDouble(controller_node, driven_attrs, **flags):
    pass

class Apprentice():
    '''
    Just had an idea for this class. Apprentice would acts as a 
    interpretive macro. It would take simple input like.
    Apprentice.hookup('this_node', 'that_node'). It would then
    parse the attribute names of the two nodes and connect them
    based on some criteria. If it got two matches, it would ask
    for user input on what to do.
    '''
    pass

class Linker():
    '''
    Tool for creating meta links between nodes. Meta-link allows
    the user to see relationships between nodes, that are not
    strictly functional based on the DAG graph. They use message
    attributes as method of implementation.
    '''
    def __init__(self, name='bs_links'):
        self.attr_name = name
        self.attr_count = self.attr_name+'_cnt'
        connectToEclipse()
    def add(self, node, link):
        '''
        Adds a link to a node.
        '''
        # if node is a list of nodes, map add to each
        if type(node) == type(list()):
            seq_link = []
            for this_node in node:
                seq_link.append(link)
            map(self.add, node, seq_link)
        #if link is a list of links, map add to each
        elif type(link) == type(list()):
            seq_node = []
            for this_link in link:
                seq_node.append(node)
            map(self.add, seq_node, link)
        #base case, one node, one link
        else:
            #if the link doesn't exist already
            if not(self.check(node, link)):
                #create the link
                #link container doesn't exist, create it
                if not(cmds.attributeQuery(self.attr_name, n=node, ex=1)):
                    cmds.addAttr(node, sn=self.attr_name, m=1, at='message')
                    cmds.addAttr(node, sn=self.attr_count, at='byte', h=1, k=0, dv=0)
                    cmds.aliasAttr(link, '{0!s}.{1!s}[{2!s}]'.format(node,self.attr_name,0))
                    self.inc(node)
                else:
                    cmds.aliasAttr(link, '{0!s}.{1!s}[{2!s}]'.format(node,self.attr_name,self.count(node)))
                    self.inc(node)
                    
    def check(self, node, link):
        '''
        Checks to see if a link exists on a node.
        '''
        links = self.get(node)
        if link in links:
            return True
        else:
            return False
    
    def delete(self, node, link):
        '''
        Deletes a link from a node.
        '''
        if type(node) == type(list()):
            seq_link = []
            for this_node in node:
                seq_link.append(link)
            map(self.delete, node, seq_link)
        else:
            #get links
            links = self.get(node)
            #store connections
            connections = {}
            for this_link in links:
                connections[this_link] = {}
                connections[this_link]['in'] = [cmds.connectionInfo('{0!s}.{1!s}'.format(node, this_link), sfd=1)]
                connections[this_link]['out'] = cmds.connectionInfo('{0!s}.{1!s}'.format(node, this_link), dfs=1)
            #destroy links on the node
            self.destroy(node)
            #drop unneeded links
            if type(link) == type(list()):
                try:
                    map(links.remove, link)
                except:
                    pass
            else:
                links.remove(link)
            #recreate links
            self.add(node, links)
            #restore connections
            for this_link in links:
                in_attr = ['{0!s}.{1!s}'.format(node, this_link) for x in range(len(connections[this_link]['in']))]
                out_attr = ['{0!s}.{1!s}'.format(node, this_link) for x in range(len(connections[this_link]['out']))]
                if connections[this_link]['in'] != [unicode('')]:
                    map(cmds.connectAttr, connections[this_link]['in'], in_attr)
                if connections[this_link]['out'] != []:
                    map(cmds.connectAttr, out_attr, connections[this_link]['out'])
                
    def destroy(self, node):
        '''
        Delete's all links from a node, removes
        all supporting attributes.
        '''
        if type(node) == type(list):
            map(self.destroy, node)
        else:
            links = self.get(node)
            #break connections
            connections = {}
            for this_link in links:
                connections[this_link] = {}
                connections[this_link]['in'] = [cmds.connectionInfo('{0!s}.{1!s}'.format(node, this_link), sfd=1)]
                connections[this_link]['out'] = cmds.connectionInfo('{0!s}.{1!s}'.format(node, this_link), dfs=1)
                in_attr = ['{0!s}.{1!s}'.format(node, this_link) for x in range(len(connections[this_link]['in']))]
                out_attr = ['{0!s}.{1!s}'.format(node, this_link) for x in range(len(connections[this_link]['out']))]
                if connections[this_link]['in'] != [unicode('')]:
                    map(cmds.disconnectAttr, connections[this_link]['in'], in_attr)
                if connections[this_link]['out'] != []:
                    map(cmds.disconnectAttr, out_attr, connections[this_link]['out'])            
            #strip the aliases
            for this_link in links:
                cmds.aliasAttr('{0!s}.{1!s}'.format(node, this_link), rm=1)
            cmds.deleteAttr('{0!s}.{1!s}'.format(node, self.attr_name))
            cmds.deleteAttr('{0!s}.{1!s}'.format(node, self.attr_count))
        
    def count(self, node):
        '''
        Returns number of links on a node.
        '''
        if type(node) == type(list):
            return map(self.count, node)
        else:
            return cmds.getAttr('{0!s}.{1!s}'.format(node, self.attr_count))
        
    def inc(self, node):
        '''
        Increments the count of links on a node.
        '''
        if type(node) == type(list):
            return map(self.inc, node)
        else:
            cmds.setAttr('{0!s}.{1!s}'.format(node, self.attr_count), self.count(node)+1)
            return self.count(node)
        
    def dec(self, node):
        '''
        Decrements the count of links on a node.
        '''
        if type(node) == type(list):
            return map(self.dec, node)
        else:
            if self.count(node) >= 1:
                cmds.setAttr('{0!s}.{1!s}'.format(node, self.attr_count), self.count(node)-1)
            else:
                cmds.setAttr('{0!s}.{1!s}'.format(node, self.attr_count), 0)
            return self.count(node)

    def get(self, node):
        '''
        Returns all inks on a node as a list.
        '''
        try:
            links = []
            for i in range(self.count(node)):
                links.append(cmds.aliasAttr('{0!s}.{1!s}[{2!s}]'.format(node, self.attr_name, i), q=1))
            return links
        except:
            return []
                
    def connect(self, from_plug, to_plug):
        '''
        Connects one link to another.
        '''
        pass

class Tagger():
    '''
    Tool for adding meta data tags to nodes. Extremely simple,
    expects a "node" as its first argument and a "tag" as it's
    second. Both arguments should be strings (or unicode).
    '''
    def __init__(self, name='bs_tags'):
        '''
        Instantiates the tool, sets the master tag name. Default
        is 'bs_tags'.
        '''
        self.tag_attr_name = name
        connectToEclipse()
    def add(self, node, tag):
        '''
        To a give "node" add a specific "tag".
        '''
        if cmds.attributeQuery(self.tag_attr_name, n=node, ex=1):
            this_count = self.count(node)
            this_count = this_count + 1
            cmds.setAttr('{0!s}.{1!s}[{2!s}]'.format(node, self.tag_attr_name, this_count), tag, typ='string')
            cmds.setAttr('{0!s}.{1!s}[0]'.format(node, self.tag_attr_name), this_count, typ='string')
        else:
            cmds.addAttr(node, sn=self.tag_attr_name, m=1, dt='string')
            cmds.setAttr('{0!s}.{1!s}[0]'.format(node, self.tag_attr_name), '1', typ='string')
            cmds.aliasAttr('count', '{0!s}.{1!s}[0]'.format(node, self.tag_attr_name))
            cmds.setAttr('{0!s}.{1!s}[1]'.format(node, self.tag_attr_name), tag, typ='string') 
    def check(self, node, tag):
        '''
        On a given "node" if a specific "tag" exists, return True. 
        Else, return false.
        '''
        if not(cmds.attributeQuery(self.tag_attr_name, n=node, ex=1)):
            return False
        
        tags = self.get(node)
        if tag in tags:
            return True
        else:
            return False
    def delete(self, node, tag):
        '''
        On a given "node" remove a specific "tag".
        '''
        if self.check(node, tag):
            tags = self.get(node)
            tags.remove(tag)
            self.destroy(node)
            for this_tag in tags:
                self.add(node, this_tag)
            return 0
        else:
            return -1
    def destroy(self, node):
        '''
        Remove all tags from a given "node".
        '''
        cmds.aliasAttr('{0!s}.count'.format(node), rm=1)
        cmds.deleteAttr('{0!s}.{1!s}'.format(node, self.tag_attr_name))
    def copy(self, source_node, destination_node):
        '''
        Copy the tags from a given "source_node" to a
        given "destination_node." 
        '''
        if cmds.attributeQuery(self.tag_attr_name, n=source_node, ex=1):
            tags = self.get(source_node)
        else:
            return -1
        if cmds.attributeQuery(self.tag_attr_name, n=destination_node, ex=1):
            self.destroy(destination_node)
        else:
            for this_tag in tags:
                self.add(destination_node, this_tag)
            return 0
    def get(self, node):
        '''
        For a given "node" return all "tags" on that node as a list.
        '''
        tags = []
        for i in [x+1 for x in range(self.count(node))]:
            tags.append(cmds.getAttr('{0!s}.{1!s}[{2!s}]'.format(node, self.tag_attr_name, i)))
        return tags   
    def count(self, node):
        '''
        For a given "node" return the number of tags on that node.
        '''
        count = int(cmds.getAttr('{0!s}.{1!s}[0]'.format(node, self.tag_attr_name)))
        return count
    
    def clean(self, nodes, tag, option=True):
        scratch = []
        while nodes:
            this_node = nodes.pop()
            if self.check(this_node, tag) == option:
                scratch.append(this_node)
        scratch.reverse()
        return scratch
                 

class SimpleBlend():
    '''
    Simple Blend Tool
    ---
    This class collects several tools for working with blended nodes.
    Blended nodes use position and orientation constraints to blend
    the transform of the blend node between the transforms of various
    target nodes.
    
    Methods of this class work on selected nodes, with the assumption
    that the last node selected is the blend node and other 
    selected nodes are the target objects. These assumptions can be
    overridden with the following flags:
    
    blend(b), ex. b=[b1,...,bN], expects node list, overrides blend nodes
    target(t), ex. t=[t1,...,tN], expects node list, overrides target nodes
    '''
    def __init__(self):
        self.b_tag = 'sb_blendObj'
        self.c_tag = 'sb_constraint'

        #init internal tagger
        self.t = Tagger()
        
        # enable to debug
        #connectToEclipse()
                
    def create(self, **flags):
        '''
        Creates new blends. Skips existing blend nodes by default. 
        
        Accepts additional flag:
        force(f), ex. f=True, expects bool, forces new blend creation.
        '''
        #common input prep
        sb_input = prepInput('b', 't',**flags)
        blendObjs = sb_input[0]
        targetObjs = sb_input[1]
        
        if flagTest('f', flags):
            for obj in blendObjs:
                self.destroy(obj)
               
        #confirm that we have something to do
        if not((len(blendObjs) >= 1) and (len(targetObjs) >= 1)):
            raise Warning('SimpleBlend.create: Requires at least two transform nodes.')
            return
        
        #create the blends
        for obj in blendObjs:
            #create the constraints
            this_pc = cmds.pointConstraint(*(targetObjs+[obj]), n=obj+'_pc', mo=0)
            this_oc = cmds.orientConstraint(*(targetObjs+[obj]), n=obj+'_oc', mo=0)

            #add tracking attributes
            self.t.add(obj, self.b_tag)
            cmds.addAttr(obj, sn='sB_oC', at='message', ct='simpleBlend')
            cmds.addAttr(obj, sn='sB_pC', at='message', ct='simpleBlend')

            self.t.add(this_oc[0], self.c_tag)
            cmds.addAttr(this_oc, sn='sB_blendObj', at='message', ct='simpleBlend')
            
            self.t.add(this_pc[0], self.c_tag)
            cmds.addAttr(this_pc, sn='sB_blendObj', at='message', ct='simpleBlend')
            
            cmds.connectAttr(obj+'.sB_oC', this_oc[0]+'.sB_blendObj')
            cmds.connectAttr(obj+'.sB_pC', this_pc[0]+'.sB_blendObj')
            cmds.connectAttr(this_oc[0]+'.sB_blendObj', obj+'.sB_oC')
            cmds.connectAttr(this_pc[0]+'.sB_blendObj', obj+'.sB_pC')
            
            #add weighting attributes
            weights = cmds.pointConstraint(this_pc, q=1, wal=1)
            cmds.addAttr(obj, sn='sBw', m=1, at='double', dv=1.0, r=1, w=1, h=0, k=1, ct='simpleBlend')
            for i, this_weight in enumerate(weights):
                cmds.setAttr('{0!s}.sBw[{1!s}]'.format(obj, i), 1.0)
                cmds.aliasAttr('{0!s}'.format(this_weight), '{0!s}.sBw[{1!s}]'.format(obj, i))
                cmds.connectAttr('{0!s}.{1!s}'.format(obj, this_weight), this_oc[0]+'.'+this_weight)
                cmds.connectAttr('{0!s}.{1!s}'.format(obj, this_weight), this_pc[0]+'.'+this_weight)
            #endfor
        #endfor
            
    def add(self, **flags):
        '''
        Adds additional targets to an existing blend.
        '''
        #common input prep
        sb_input = prepInput('b','t',**flags)
        blendObjs = sb_input[0]
        targetObjs = sb_input[1]
        
        #make sure specified blends are blendsObjs, remove them if they're not    
       
        blendObjs = self.t.clean(blendObjs, self.b_tag)
        
        #check to see if we have anything to do
        if not((len(blendObjs) > 0) and (len(targetObjs)>0)):
            raise Warning('SimpleBlend.addTargets: Requires at least one blendObj and one targetObj.')
            return
        
        #add the targets
        for obj in blendObjs:
            #get the constraints
            this_pc = cmds.connectionInfo(obj+'.sB_pC', dfs=1)[0].split('.')[0]
            this_oc = cmds.connectionInfo(obj+'.sB_oC', dfs=1)[0].split('.')[0]
            
            #store existing target list and connections of blend object
            count = len(cmds.getAttr(obj+'.sBw')[0])
            existing_weights = []
            for i in range(count):
                this_weight = cmds.aliasAttr(obj+'.sBw[{0!s}]'.format(i), q=1)
                existing_weights.append(this_weight)
            
            #collect connections
            connections = {}
            for weight in existing_weights:              
                wt = obj+'.'+weight
                incoming = cmds.connectionInfo(wt, sfd=1)
                outgoing = cmds.connectionInfo(wt, dfs=1)
                if type(incoming) != type(list()):
                    incoming = [incoming]
                if type(outgoing) != type(list()):
                    outgoing = [outgoing]
                connections[weight] = {'in':incoming, 'out':outgoing}
            
            #drop sb_weights
            for this_alias in existing_weights:
                cmds.aliasAttr(obj+'.{0!s}'.format(this_alias), rm=1)
            cmds.deleteAttr(obj+'.sBw')
            
            #add new targets
            for this_target in targetObjs:
                if this_target not in cmds.pointConstraint(this_pc, q=1, tl=1):
                    cmds.pointConstraint(this_target, obj, n=this_pc)
                if this_target not in cmds.orientConstraint(this_oc, q=1, tl=1):
                    cmds.orientConstraint(this_target, obj, n=this_oc)
            
            #re-add sb_weights, establishg new connections
            new_weights = cmds.pointConstraint(this_pc, q=1, wal=1)
            cmds.addAttr(obj, sn='sBw', m=1, at='double', dv=1.0, r=1, w=1, h=0, k=1, ct='simpleBlend')
            for i, this_weight in enumerate(new_weights):
                cmds.setAttr('{0!s}.sBw[{1!s}]'.format(obj, i), 1.0)
                cmds.aliasAttr('{0!s}'.format(this_weight), '{0!s}.sBw[{1!s}]'.format(obj, i))
                cmds.connectAttr('{0!s}.{1!s}'.format(obj, this_weight), '{0!s}.{1!s}'.format(this_oc,this_weight))
                cmds.connectAttr('{0!s}.{1!s}'.format(obj, this_weight), '{0!s}.{1!s}'.format(this_pc,this_weight))
                           
            #restore old connections
            for weight, weight_connections in connections.iteritems():
                for direction, these_connections in weight_connections.iteritems():
                    for this_connection in these_connections:
                        if direction == 'in':
                            try:
                                cmds.connectAttr(this_connection, obj+'.'+weight)
                            except:
                                pass
                        elif direction == 'out':
                            try:
                                cmds.connectAttr(obj+'.'+weight, this_connection)
                            except:
                                pass
        #endfor

    def remove(self, **flags):
        '''
        Removes selected targets from existing blend.
        '''
        sb_input = prepInput('b','t',**flags)
        blendObjs = sb_input[0]
        targetObjs = sb_input[1]
        
        #make sure specified blends are blendsObjs, remove them if they're not    
        blendObjs = self.t.clean(blendObjs, self.b_tag)
        
        #throw an error if we have no blendObjs
        if not(len(blendObjs) > 0):
            raise Warning('SimpleBlend.removeTargets: Requires at least one blendObj.')
            return        

        for obj in blendObjs:
            this_pc = cmds.connectionInfo(obj+'.sB_pC', dfs=1)[0].split('.')[0]
            this_oc = cmds.connectionInfo(obj+'.sB_oC', dfs=1)[0].split('.')[0]
            
            #pull targets from one of the constraints
            this_target_list = cmds.pointConstraint(this_pc, q=1, tl=1)
            if type(this_target_list) != type(list()):
                this_target_list = [this_target_list]
            
            #intersect that list with the targetObjs list
            target_intersection = list(set(targetObjs) & set(this_target_list))
            
            #check length of intersection and skip to next blendObj if length < 1, targetObjs aren't in blend for that blendObj
            if len(target_intersection)<1:
                print 'blendObj: {0!r} does not target: {1!r}\n'.format(obj, targetObjs)
                continue
            
            #assuming an intersection exist (because you got this far)
            
            #backup exist weights and connections
            
            #get existing weights
            count = len(cmds.getAttr(obj+'.sBw')[0])
            existing_weights = []
            for i in range(count):
                this_weight = cmds.aliasAttr(obj+'.sBw[{0!s}]'.format(i), q=1)
                existing_weights.append(this_weight)     
            
            #collect connections
            connections = {}
            for weight in existing_weights:              
                wt = obj+'.'+weight
                incoming = cmds.connectionInfo(wt, sfd=1)
                outgoing = cmds.connectionInfo(wt, dfs=1)
                if type(incoming) != type(list()):
                    incoming = [incoming]
                if type(outgoing) != type(list()):
                    outgoing = [outgoing]
                connections[weight] = {'in':incoming, 'out':outgoing}
            
            #drop existing sb_weights
            for this_alias in existing_weights:
                cmds.aliasAttr(obj+'.{0!s}'.format(this_alias), rm=1)
            cmds.deleteAttr(obj+'.sBw')
            
            #remove intersection from constraints target lists
            cmds.pointConstraint(target_intersection, obj, e=1, rm=1)
            cmds.orientConstraint(target_intersection,obj, e=1, rm=1)
            
            #check to see if we still have blend
            if not cmds.pointConstraint(obj, q=1, n=1):
                #cleanup simpleblend
                #remove sB attrs from blendObj
                self.destroy(obj)
            else:
                #sB still exists
                #restore remaining connections
                
                #re-add sb_weights, establishing new connections
                new_weights = cmds.pointConstraint(this_pc, q=1, wal=1)
                cmds.addAttr(obj, sn='sBw', m=1, at='double', dv=1.0, r=1, w=1, h=0, k=1, ct='simpleBlend')
                for i, this_weight in enumerate(new_weights):
                    cmds.setAttr('{0!s}.sBw[{1!s}]'.format(obj, i), 1.0)
                    cmds.aliasAttr('{0!s}'.format(this_weight), '{0!s}.sBw[{1!s}]'.format(obj, i))
                    cmds.connectAttr('{0!s}.{1!s}'.format(obj, this_weight), '{0!s}.{1!s}'.format(this_oc,this_weight))
                    cmds.connectAttr('{0!s}.{1!s}'.format(obj, this_weight), '{0!s}.{1!s}'.format(this_pc,this_weight))
                               
                #restore old connections
                for weight, weight_connections in connections.iteritems():
                    for direction, these_connections in weight_connections.iteritems():
                        for this_connection in these_connections:
                            if direction == 'in':
                                try:
                                    cmds.connectAttr(this_connection, obj+'.'+weight)
                                except:
                                    pass
                            elif direction == 'out':
                                try:
                                    cmds.connectAttr(obj+'.'+weight, this_connection)
                                except:
                                    pass

    def copy(self, **flags):
        '''
        Adds existing blend's targets to new object. Ignores existing
        blend objects for target object. Assumes last selected is source
        and additonal are destination objects. Ignores existing blends objects
        after the first.
        
        Accepts additional flag:
        force(f), ex. f=True, expects bool, forces new blend creation on all targets
        '''
        
        #common input prep
        sb_input = prepInput('b','t',**flags)
        blendObjs = sb_input[0]
        targetObjs = sb_input[1]
        
        #check for more than one blend object source, boot if applicable
        if len(blendObjs) > 1:
            raise Warning('SimpleBlend.copyBlend: single source node required.\n')
        
        #check that blendObjs is indeed a blend obj
        if not(self.t.check(blendObjs[0], self.b_tag)):
                raise Warning('SimpleBlend.copyBlend: source node not a SimpleBlend.\n')
        
        # check for force flag, if enabled, destroy existing blends on targets
        if flagTest('f', flags):
            self.destroy(*targetObjs)
        
        # check for existing blends and discard them
        targetObjs = self.t.clean(targetObjs, self.b_tag, option=False)

        #for each target remaining, create a blend using that list
        target_list = cmds.pointConstraint(blendObjs[0], q=1, tl=1)
        
        for this_target in targetObjs:
            self.create(b=this_target, t=target_list)
                

    def destroy(self,*nodes, **flags):
        '''
        Removes all Simple Blend attributes from selected nodes. Breaks all
        connections. Deletes blending constraints.
        '''
        #if no nodes passed, get selected nodes
        if not(nodes):
            nodes = cmds.ls(sl=1)
        
        #discard untagged, non-blend obj nodes
        compiled_nodes = []+nodes      
        for this_node in nodes:
            if not(self.t.check(this_node, self.b_tag)):
                compiled_nodes.remove(this_node)
        nodes = compiled_nodes
        
        #for each remaining node, clear the constraints & drop the SB attrs
        for this_node in nodes:
            target_list = cmds.pointConstraint(this_node, q=1, tl=1)
            cmds.pointConstraint(target_list, this_node, e=1, rm=1)
            cmds.orientConstraint(target_list, this_node, e=1, rm=1)
            #rework for multi
            count = len(cmds.getAttr(this_node+'.sBw')[0])
            existing_weights = []
            for i in range(count):
                this_weight = cmds.aliasAttr(this_node+'.sBw[{0!s}]'.format(i), q=1)
                existing_weights.append(this_weight)   
            for this_alias in existing_weights:
                cmds.aliasAttr(this_node+'.{0!s}'.format(this_alias), rm=1)
            drop_attrs = cmds.listAttr(this_node, st='sB*')
            for this_attr in drop_attrs:
                cmds.deleteAttr(this_node+'.'+this_attr)
            if self.t.check(this_node, self.b_tag):
                self.t.delete(this_node, self.b_tag)
    
    def check(self, node):
        if type(node) == type(list()):
            return map(self.check, node)
        else:
            if self.t.check(node, self.b_tag) or self.t.check(node, self.c_tag):
                return True
            else:
                return False
   
    def getBlendObj(self, *constraints, **flags):
        '''
        Returns the names of constraints' blend objects, if they exist, as dictionary
        indexed by node name.
        '''
        results = dict()
        
        if not(constraints):
            constraints = cmds.ls(sl=1)
        
        while constraints:
            this_con = constraints.pop()
            if self.t.check(this_con, self.c_tag):
                results[this_con] = cmds.connectionInfo(this_con+'.sB_blendObj', dfs=1)[0].split('.')[0]
        
        return results
                
    def getConstraints(self, *blend_objects, **flags):
        '''
        Returns the names of blend objects' constraints, if they exist, as dictionary
        indexed by node name. 
        '''
        results = dict()
        
        if not(blend_objects):
            blend_objects = cmds.ls(sl=1)
        
        while blend_objects:
            this_blend = blend_objects.pop()
            if self.t.check(this_blend, self.b_tag):
                results[this_blend] = [cmds.connectionInfo(this_blend+'.sB_pC', dfs=1)[0].split('.')[0], cmds.connectionInfo(this_blend+'.sB_oC', dfs=1)[0].split('.')[0]]
        
        return results

class ControlSpaces():
    '''
    Tool to create control spaces for anim controllers. It accepts
    the following flags:
    
    'f' force, (bool), causes the tool to destroy existing spaces
      on the controller specified and replace them with the new.
      Default behavior is to ignore controllers that already have
      spaces specified.
      
    'o' objects, (str or list), specify objects to be bound to
        the control spaces. Default is to last item selected.
      
    's' spaces, (str or list), specify objects to be control spaces.
      Default is for all items but last selected.
      
    'e' enum, sets up an enum based control, using space names as values.
      Default is a series of float/double values.
    '''
    def __init__(self):
        self.obj_tag = 'cS_obj'
        self.spc_tag = 'cS_spc'
        self.t = Tagger()
        self.sb = SimpleBlend()
        #enable to debug
        connectToEclipse()
        
    def create(self, *args, **flags):
        '''
        Setup control spaces on specified anim nodes.
        '''
        cs_input = prepInput('o', 's', **flags)
        Objs = cs_input[0]
        Spaces = cs_input[1]
        
        #if force flag, wipe the control spaces on existing
        if flagTest('f', flags):
            self.destroy(Objs)
        
        #tag is found, boot the control for the list       
        Objs = self.t.clean(Objs, self.obj_tag, option=False)
        Objs = self.t.clean(Objs, self.spc_tag, option=False)

        
        #if no controller, dump
        if not(Objs):
            raise Warning('ControlSpaces.create: Requires at least one anim object.\n')
        
        #avoid complications of controllers that are themselves spaces
        Spaces = self.t.clean(Spaces, self.spc_tag, option=False)
        
        #if no spaces, dump
        if not(Spaces):
            raise Warning('ControlSpaces.create: Requires at least one control space object.\n')
        
        #with all the check out of the way, create the attachments
               
        #to hold the target nodes for the blends
        targets = dict()
        
        #for each object
        for this_obj in Objs:
            
            #create/get an att node
            this_att = cAtt(this_obj)
            
            #initalize empty list of targets for controller
            targets[this_obj] = list()
            
            #create a multi to keep messages from the space nodes
            cmds.addAttr(this_att, sn='cS_SpacesIn', at='message', m=1)
            
            #for each space...
            for this_space in Spaces:
            
                #create a control space node to reference the controller's transform
                this_target = cmds.createNode('transform', n=this_space+'_'+this_obj+'_cs')
                
                #add it to the target list
                targets[this_obj].append(this_target)
                
                #parent it relative, so it moves to the position of the controller
                cmds.parent(this_target, this_obj, r=1)
                
                #unparent it to world to get the ws transform
                cmds.parent(this_target, w=1)
                
                #parent it back to the control space, to put it in correct context
                cmds.parent(this_target, this_space)
                
                #create a message attr on the space node
                cmds.addAttr(this_space, sn='cS_SpacesOut', at='message', m=1)
                
                #attach it to a message attr on the att node
                cmds.connectAttr(this_space+'.cS_SpacesOut', this_att+'.cS_SpacesIn')
                
            #blend the att of the controller to the targets of the controller
            self.sb.create(b=this_att, t=targets[this_obj])

            #setup controls on the obj to drive the blend
            these_attrs = ['{0!s}.{1!s}'.format(this_att, this_attr) for this_attr in cmds.listAttr(this_att, st='sBw_*')]
            setupEnumSwitch(this_obj, targets[this_obj], these_attrs, switch_name = 'cS_switch')
                
                            
    def add(self, *args, **flags):
        '''
        Add an additional control space to anim nodes.
        '''
        #parse input
        cs_input = prepInput('o', 's', **flags)
        Objs = cs_input[0]
        Spaces = cs_input[1]
        
        #input error checks to be implemented
        #check that each object has control spaces applied
        for this_obj in Objs:
            try:
                if not (cmds.getAttr('{0!s}.tag'.format(this_obj)) == self.obj_tag):
                    #remove
                    Objs.remove(this_obj)
            except:
                pass
            
        #check that each space isn't already a control space of the obj
        space_dict = {}
        for this_obj in Objs:
            space_dict[this_obj] = []+Spaces
            for this_space in space_dict[this_obj]:
                #get source nodes from the cS plugs
                spaces_in = [this_connection.split('.')[0] for this_connection in cmds.connectionInfo('{0!s}.cS_SpacesIn'.format(this_obj), sfd=1)]
                if this_space in spaces_in:
                    space_dict[this_obj].remove(this_space)
        
        
        #for each obj
        targets = {}
        for this_obj in Objs:
            this_att = cAtt(this_obj)
            
            #for each new space supplied
            targets[this_obj] = []
            for this_space in space_dict[this_obj]:    
            
                #create an in place target
                new_target = cmds.createNode('transform', '{0!s}_{1!s}_cs'.format(this_space, this_obj))
                targets[this_obj].append(new_target)
                cmds.parent(new_target, this_obj, r=1)
                cmds.parent(new_target, w=1)
                cmds.parent(new_target, this_space)
                
                #create the linkages for cS tracking
                cmds.addAttr(this_space, sn='cS_SpacesOut', at='message', m=1)
                cmds.connectAttr(this_space+'.cS_SpacesOut', this_att+'.cS_SpacesIn')
            
            #append the new targets to the blend
            self.sb.add(b=this_att, t=targets[this_obj])
            
            #need to trace the switch for the attributes it drives and the curve nodes
            for this_connection in cmds.listConnections('{0!s}.cS_switch'.format(this_obj), d=1, t='animCurveUL'):
                cmds.delete(this_connection)
            cmds.deleteAttr('{0!s}.cS_switch'.format(this_obj))
            
            #now recreate the switch with the new weights added in
            these_attrs = ['{0!s}.{1!s}'.format(this_att, this_attr) for this_attr in cmds.listAttr(this_att, st='sBw_*')]
            setupEnumSwitch(this_obj, targets[this_obj], these_attrs, switch_name = 'cS_switch')
            
    def remove(self, *args, **flags):
        '''
        Remove a control space from anim nodes.
        '''
        pass
    def destroy(self, *args, **flags):
        '''
        Remove all control spaces from anim node and
        remove all Control Space parameters from node.
        '''
        pass
    def check(self, *args, **flags):
        '''
        Return a (bool) for whether anim node has control
        spaces.
        '''
        pass
    def getSpaces(self, *args, **flags):
        '''
        Return list of control spaces of anim node.
        '''
        pass
    def getAnim(self, *args, **flags):
        '''
        Return list of anim nodes using control space.
        '''
        pass
    
    def snapTo(self, node, current_space, target_space):
        '''
        Will create a one frame blend between two control
        spaces, keeping the world transform constant.
        '''
    
class Pivot():
    '''
    This is a python port of Jason Schleifer's Movable Pivot Techniques
    Website:    http://jasonschleifer.com
      
    This tool can be used to create and use movable pivots on any 
    transform node. It has the following functions:
    
    <toolname>.create() - This method creates and links the pivot
    objects to each item selected. It has no parameters.
    
    <toolname>.createMov() - Running this method will select the movable
    pivot. Relocate it and then use <toolname>.snap() to move change your
    transforms local space.
    
    <toolname>.snap() - This method will relocate your transform's pivot
    to the location of the movable pivot. It will set keyframes one frame
    before and on the current frame to ensure that your transform appears
    stationary. Should be used in concert with <toolname>.createMov()
    
    <toolname>.toggle(onOff) and <toolname>.mov_toggle(onOff) control
    visibility of the pivot objects. onOff can be one of three states:
    0 - off, 1 - on, or -1 for toggle.
    
    Note: in addition to creation of pivot objects, this tool creates
    several connections between nodes that it depends on to function.
    Users will find these connections in the extra attributes section.
    No not remove them unless you intend to remove the movable pivot
    functionality.
    
    Thanks to Jason Schleifer for his training materials which enabled
    me to make this port.
    
    -Benjamin Slack, 04142013, Kalamazoo, MI iam@nimajneb.com
        
    '''
    def __init__(self):
        '''
        Initializes and instance of the pivot tool.         
        '''
        self.objs = list()
        self.pivotObjects = list()
        self.pivotCount = 0
        #enable to debug
        #connectToEclipse()
    
    def create(self):
        '''
        Creates a moveable Pivot for all selected objects, no parameters.
        '''
        self.objs = cmds.ls(sl=1)
        
        for this_obj in self.objs:
            this_pivotObj = self.get(this_obj, 'pivotObj')
            if this_pivotObj == '':
                #create new pivot
                this_loc = cmds.spaceLocator()
                this_loc[0] = cmds.rename(this_loc[0], this_obj+'_pivot_anim')
                
                #get the position of the obj
                this_pos = cmds.xform(this_obj, q=1, ws=1, rp=1)
                
                #set position of the locator
                cmds.move(this_pos[0], this_pos[1], this_pos[2], this_loc[0], a=1, ws=1)
                
                #parent the locator under the object
                cmds.parent(this_loc[0], this_obj)
                
                #set the locators rotation to 0
                cmds.setAttr(this_loc[0]+'.r', *[0,0,0])
                
                #create a new loc for second pvt
                this_dup = cmds.duplicate(this_loc[0])
                this_duploc = cmds.rename (this_dup[0], this_obj+'_pivot_mov')
                
                #scale the duplicate
                cmds.scale(.8,.8,.8, this_duploc)
                
                #connect the loc's trans to the obj's rot pvt
                cmds.connectAttr(this_loc[0]+'.t', this_obj+'.rotatePivot', f=1)
                
                #set the locators' scale and rotate attr to locked and unkeyable
                these_attrs = ['rx', 'ry', 'rz', 'sx', 'sy', 'sz']
                for this_attr in these_attrs:
                    cmds.setAttr(this_loc[0]+'.'+this_attr, l=1, k=0)
                    cmds.setAttr(this_duploc+'.'+this_attr, l=1, k=0)
                    
                #set vis to unkey but unlocked
                cmds.setAttr (this_loc[0]+'.v', k=0)
                cmds.setAttr (this_duploc+'.v', k=0)
                
                cmds.hide(this_duploc)
                
                #add an attr called pivot
                cmds.addAttr(this_loc[0], sn='pivot', at='message')
                cmds.addAttr(this_duploc, sn='pivotMov', at='message')
                
                cmds.addAttr(this_obj, sn='pivotObj', at='message')
                cmds.addAttr(this_obj, sn='pivotMovObj', at='message')
                
                cmds.connectAttr(this_loc[0]+'.pivot', this_obj+'.pivotObj')
                cmds.connectAttr(this_duploc+'.pivotMov', this_obj+'.pivotMovObj')
                
                self.pivotObjects.append(this_loc[0])
                self.pivotObjects.append(this_duploc)
                
        return self.pivotObjects
    
    def createMov(self):
        '''
        Selects the movable pivot so that you can place it.
        Used in conjunction with <toolname>.snap()
        '''
        selected = list()
        count = 0
        for this_obj in self.objs:
            this_pivot = self.get(this_obj, 'pivotMovObj')
            if (this_pivot != ''):
                #make sure visibility isn't locked
                cmds.setAttr (this_pivot+'.v', l=0)
                cmds.showHidden(this_pivot)
                #get the position of the original object
                this_truePiv = self.get(this_obj, 'pivotObj')
                t = cmds.getAttr(this_truePiv+'.t')
                cmds.setAttr(this_pivot+'.t', *t[0])
                count += 1
                selected.append(this_pivot)
            #endif
        #endfor
        
        cmds.select(selected)
    
    def getObj(self, sel):
        '''
        Used internally by the other methods to extract the node
        being modified. Users should not require access to it.
        '''
        return_me = ''
        
        if (cmds.attributeQuery('pivotObj', n=sel, ex=1)):
            return_me = sel
        else:
            pivot_case = cmds.attributeQuery('pivot', n=sel, ex=1)
            pivotMov_case = cmds.attributeQuery('pivotMov', n=sel, ex=1)
            if pivot_case:
                message = '.pivot'
            if pivotMov_case:
                message = '.pivotMov'
            if pivot_case or pivotMov_case:    
                tmp = cmds.listConnections(sel+message, p=1, d=1)
                item = ''
                for item in tmp:
                    #check connections for pivotObj
                    if (re.search('pivot', item)):
                        #this is a pivot
                        return_me = ''
                        this_break = item.split('.')
                        return_me = this_break[0]
                    #endif
                #endfor
            #endif
        #endelse
        
        return return_me                    
    
    def snap(self):
        '''
        This method moves your transform from it's current pivot location
        to the location specified by your movable pivot location. It
        creates keyframes between the two positions so that your object
        remains stationary. Should be used in concert with <toolname>.createMov
        '''
        self.objs = cmds.ls(sl=1)
        for this_obj in self.objs:
            obj = self.getObj(this_obj)
            pivot = self.get(this_obj, 'pivotObj')
            pivotMov = self.get(this_obj, 'pivotMovObj')
            if (obj=='') or (pivot=='') or (pivotMov==''):
                raise Warning(this_obj+'was not setup to handle pivot modifications.\n')
            
            #save a keyframe at the previous frame for the object and the pivot
            frame = cmds.currentTime(q=1)
            print 'Pivot: Saving a for '+obj+' and '+pivot+' at frame '+str((frame-1))+'\n'
            cmds.setKeyframe(pivot, t=(frame-1), itt='linear', ott='linear')
            cmds.setKeyframe(obj, t=(frame-1))
            
            #ket loca trans of pivotMov
            trans = cmds.getAttr(pivotMov+'.t') #returns list single item tuple
            
            #get world pos
            world = cmds.xform(pivotMov, q=1, ws=1, rp=1) #returns list
            
            #set position of old pivot to be the same as the new
            cmds.setAttr(pivot+'.t', *trans[0])
            
            #move the object
            cmds.move(world[0], world[1], world[2], obj, rpr=1)
            
            #save a keyframe
            cmds.setKeyframe(pivot, t=frame, itt='linear', ott='linear')
            cmds.setKeyframe(obj, t=frame)
            cmds.select(obj)
        #endfor
    
    def toggle(self, onOff):
        '''
        Can be used to toggle the visibility of the regular pivot. Has one
        parameter, onOff, which accepts -1, 0, and 1 as inputs. 0 = off, 
        1 = on, and -1 = toggle vis.
        '''
        #this will toggle the pivot on or off
        self.objs = cmds.ls(sl=1)
        for this_obj in self.objs:
            pivot = self.get(this_obj, 'pivotObj')
            if (onOff == -1):
                onOff = not(cmds.getAttr(pivot+'.v'))
            cmds.setAttr(pivot+'.v', onOff)
        #endfor
    
    def mov_toggle(self, onOff):
        '''
        As <toolname>.toggle, but for the movable pivot.
        '''
        #this will toggle the pivot on or off
        self.objs = cmds.ls(sl=1)
        for this_obj in self.objs:
            pivot = self.get(this_obj, 'pivotMovObj')
            if (onOff == -1):
                onOff = not(cmds.getAttr(pivot+'.v'))
            cmds.setAttr(pivot+'.v', onOff)
        #endfor
    
    def get(self, obj, typ):
        '''
        An internal method used by the Pivot Tool. Users
        should not require it.
        '''
        return_me = ''
        tmp = ['']
        obj = self.getObj(obj)
        
        if obj != '':
            if cmds.attributeQuery(typ, n=obj, ex=1):
                #has pivot
                tmp = cmds.listConnections(obj+'.'+typ, t='transform')
                return_me = tmp[0]
            #endif
        #endif
        
        return return_me
#end Pivot 
    