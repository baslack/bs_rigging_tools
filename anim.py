from func import * #@UnusedWildImport

def ripple(f):
    char_sel = cmds.selectionConnection('highlightList', q=1, obj=1)
    if not(char_sel):
        cmds.keyframe(sel(), r=1, tc=f, time=(cmds.currentTime(q=1),cmds.playbackOptions(q=1, aet=1)))
    else:
        chan = []
        for this_char in char_sel:
            chan = chan + cmds.character(this_char, q=1)
            #print repr(chan)
        chan = chan + sel()
        #print repr(chan)
        cmds.keyframe(chan, r=1, tc=f, time=(cmds.currentTime(q=1),cmds.playbackOptions(q=1, aet=1)))
      
def rippleAll(f):
    cmds.keyframe(cmds.ls(typ='animCurve'), r=1, tc=f, time=(cmds.currentTime(q=1),cmds.playbackOptions(q=1, aet=1)))

class Breakdown():
    def __init__(self):
        self.listBeforeValues = {}
        self.listAfterValues = {}
        self.channels = []
        #enable debug
        connectToEclipse()
        
        #only call once, else runtime error
        cmds.draggerContext('bdCtx', pc=self.press, dc=self.drag, rc=self.release, cursor='hand', i1='bs_breakdown.png')
        
    def deltaX(self):
        shift_scale = 1000
        norm_scale = 250
        ctrl_scale = 125
        start_pos = cmds.draggerContext('bdCtx', q=1, ap=1)
        mod = cmds.draggerContext('bdCtx', q=1, mo=1)
        current_pos = cmds.draggerContext('bdCtx', q=1, dp=1)
        if mod == 'ctrl':
            dX = smootherstep(start_pos[0]-ctrl_scale, start_pos[0]+ctrl_scale, current_pos[0])
        elif mod == 'shift':
            dX = smootherstep(start_pos[0]-shift_scale, start_pos[0]+shift_scale, current_pos[0])
        else:
            dX = smootherstep(start_pos[0]-norm_scale, start_pos[0]+norm_scale, current_pos[0])
        #print repr(dX)+'\n'
        return dX
      
    def press(self):
        self.channels = []
        self.listAfterValues = {}
        self.listBeforeValues = {}
        #selected objs
        for this_obj in sel():
            self.channels = self.channels + cmds.keyframe(this_obj, q=1, n=1)
        #highlighted char sets
        char_sel = cmds.selectionConnection('highlightList', q=1, obj=1)
        if char_sel:
            for this_char in char_sel:
                self.channels = self.channels + cmds.character(this_char, q=1)
        #clean out duplicate channel entries
        self.channels = list(set(self.channels))
        #store the pre and post keyframes
        for this_chan in self.channels:
            self.listBeforeValues[this_chan] = cmds.keyframe(this_chan, q=1, ev=1, t=(cmds.findKeyframe(this_chan, ts=1, w='previous'),))[0]
            self.listAfterValues[this_chan] = cmds.keyframe(this_chan, q=1, ev=1, t=(cmds.findKeyframe(this_chan, ts=1, w='next'),))[0]
    
    def drag(self):
        #using deltaX, blend between the first and the last keyframe for each channel
        blend_value = 0.0
        for this_chan in self.channels:
            blend_value = self.listBeforeValues[this_chan]*(1-self.deltaX()) + self.listAfterValues[this_chan]*(self.deltaX())
            cmds.setAttr(getAttrFromChannel(this_chan), blend_value)
            #cmds.setKeyframe(this_chan, v=blend_value)
        cmds.refresh()

    
    def release(self):
        pass
        #for this_chan in self.channels:
            #cmds.setKeyframe(this_chan)
                
    def start(self):
        cmds.setToolTo('bdCtx')