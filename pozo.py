import plotly.graph_objects as go
import itertools, copy, warnings
from IPython.display import Javascript # Part of Hack #1

####
####
#### Style Template/Defaults
####
####

track_margin_default = .004
track_start_default = .01

height_default = 900

axis_label_height = 60 
# 60 makes the stacking look even
# less than sixty and the second axis is too high
# it would work perfectly if we generated an error term
# that was proportational to distance from 60


xaxes_off_axis = dict( # no way to override this global
    anchor="free",
#   autoshift=True, # doesn't work for xaxis
#   position=1,     # generated
#   overlaying="x"  # generated
)

xaxes_template_default = dict(
    showgrid=True,
    zeroline=False,
    gridcolor="#f0f0f0",
    showline=True,
    linewidth=2,
    ticks="outside",
    tickwidth=1,
    ticklen=6,
    tickangle=0,
#   side=['']          # generated
#   tickcolor=='#???', # generated
#   linecolor='#???',  # generated
#   titlefont=dict(
#       color="#???"   # generated
#   ),
#   tickfont=dict(
#       color="#???"   # generated
#   )
#   domain = [?,?]     # generated
)
default_styles_default = dict(
    showlegend = False,
    margin = dict(l=15, r=15, t=5, b=5),
    yaxis = dict(
        showgrid=True,
        zeroline=False,
        gridcolor="#f0f0f0",
        domain=[0,.8], # needs to be generated TODO
#       maxallowed=, # generated, can be overwritten here
#       minallowed=, # generated, can be overwritten here
#       range=[,], # generated, can be overwritten here
    ),
    height = height_default,
    plot_bgcolor = "#FFFFFF",
#   width=? # automatic
)
default_width_per_track = 200

def calculate_domain(num_axes):
    proportion_per_axis = axis_label_height / height_default 
    height_of_graph = 1 - (num_axes * proportion_per_axis)
    print(f"Proportion per Axis: {proportion_per_axis}, Height of Graph: {height_of_graph}")
    #rror = proportion_per_axis * 
    return height_of_graph

####
####
#### Constants
####
####

LAS_TYPE = "<class 'lasio.las.LASFile'>"

####
####
#### Helper/Hack Functions
####
####

def randomColor(toNumber = 0):
    import random
    if toNumber != 0:
        random.seed(hash(toNumber))
    ops = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    return ops[random.randint(0, len(ops)-1)]

def scrollON(): # TODO can we really not just display this directly form here?
    return Javascript('''document.querySelectorAll('.jp-RenderedPlotly').forEach(el => el.style.overflowX = 'auto');''') # Part of Hack #1

####
####
#### Graph Class
####
####

class Graph():

    ## Constructor
    def __init__(self, *args, **kwargs):
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None)
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")
        self.indexOK = kwargs.get('indexOK', False)

        self.yaxis_max = 0
        self.yaxis_min = 30000 # it's a hack, but it'll do
        # Essential Configuration
        self.width_per_track = kwargs.get('width_per_track', default_width_per_track)
        self.default_styles = kwargs.get('default_styles', copy.deepcopy(default_styles_default))
        self.track_margin = kwargs.get('track_margin', track_margin_default)
        self.track_start = kwargs.get('track_start', track_start_default)

        # Objects
        # A list and its index see NOTE:ORDEREDDICT
        self.tracks_ordered = [] 
        self.tracks_by_id = {}

        self.yaxis = [] # Why are we storing information about the x and y axis?

        self.add_data_as_track(self, *args, **kwargs)

    ####
    ####
    #### Data Adding and Decoding Functions
    ####
    ####

    def add_track(self, track):
        if id(track) in self.tracks_by_id: return
        self.tracks_ordered.append(track)
        self.tracks_by_id[id(track)] = track

    def remove_track(self, track):
        if id(track) not in self.tracks_by_id: return
        del self.tracks_by_id[id(track)]
        self.tracks_ordered.remove(track)

    def add_yaxis(self, yaxis):
        self.yaxis.append(yaxis)
        self.yaxis_max = max(self.yaxis_max, yaxis.max())
        self.yaxis_min = min(self.yaxis_min, yaxis.min())
    #def set_yaxis(self, yaxis):

    def add_data_as_track(self, *args, **kwargs): # as track
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None) # what if not none
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")
        self.indexOK = kwargs.get('indexOK', False)

        for ar in args:
            # Process LASio LAS Object
            if str(type(ar)) == LAS_TYPE:
                self.add_las_object(ar, **kwargs)   

    def add_las_object(self, ar, **kwargs):
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None) # what if not none
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")
        self.indexOK = kwargs.get('indexOK', False)

        if yaxis is not None:
            self.add_yaxis(yaxis)
        elif yaxis_name in ar.curves.keys():
            self.add_yaxis(ar.curves[yaxis_name].data)
        else:
            self.add_yaxis(ar.index)
            if not self.indexOK:
                warnings.warn("No yaxis or \"" + yaxis_name + "\" column was found in the LAS data, so we're using `las.index`.")

        for curve in ar.curves:
            if curve.mnemonic == yaxis_name: continue
            mnemonic = curve.mnemonic.split(":", 1)[0] if ":" in curve.mnemonic else curve.mnemonic
            if len(include) != 0 and curve.mnemonic not in include and mnemonic not in include: continue # if there is an include, ignore
            elif len(exclude) != 0 and curve.mnemonic in exclude or mnemonic in exclude: continue 


            mnemonic = curve.mnemonic.split(":", 1)[0] if ":" in curve.mnemonic else curve.mnemonic
            data = Data(self.yaxis[-1], curve.data, mnemonic)
            newTrack = Track(data)

            # NOTE:ORDEREDDICT- >1 value per key, but insert order is still maintained
            self.add_track(newTrack)

    ####
    ####
    #### Rendering Functions
    ####
    ####

    def get_layout(self):
        # default but changeable
 
        num_tracks = len(self.tracks_ordered)
        waste_space = self.track_start + (num_tracks-1) * self.track_margin
        width = (1 - waste_space) / num_tracks # could be /0

        axes = {}
        start = self.track_start

        # Graph is what organize it into a layout structure
        i = 1
        max_axes_top = 0
        max_axes_bottom = 0
        for track in self.tracks_ordered: # must calculate
            max_axes_bottom = max(len(track.get_lower_axes())-1, max_axes_bottom)
            max_axes_top = max(len(track.get_upper_axes())-1, max_axes_top)
        graph_end_pos = calculate_domain(max_axes_top)
        for track in self.tracks_ordered:
            print(f"Graph asking for track w/ starts with {i}th axis")
            for style in track.get_axis_styles(i, graph_end_pos=graph_end_pos):
                # Style shouldn't have a domain members
                axes["xaxis" + str(i)] = dict(
                    domain = [start, min(start + width, 1)],
                    **style
                )
                #display("xaxis" + str(i))
                #display(axes["xaxis" + str(i)])
                i += 1
            start += width + self.track_margin
        if len(self.tracks_ordered) > 6: # TODO tune this number
            warnings.warn("If you need scroll bars, call `display(scrollON())` after rendering the graph. This is a plotly issue and we will fix it eventually.")   
        generated_styles = dict(
            **axes,
            width=len(self.tracks_ordered) * self.width_per_track, # probably fixed width option?
        )
        styles_modified = copy.deepcopy(self.default_styles)
        if 'yaxis' in styles_modified:
            if 'maxallowed' not in styles_modified['yaxis']:
                styles_modified['yaxis']['maxallowed'] = self.yaxis_max
            if 'minallowed' not in styles_modified['yaxis']:
                styles_modified['yaxis']['minallowed'] = self.yaxis_min
            if 'range' not in styles_modified['yaxis']:
                styles_modified['yaxis']['range'] = [self.yaxis_max, self.yaxis_min]
            if 'domain' not in styles_modified['yaxis']:
                styles_modified['yaxis']['domain'] = [0, calculate_domain(max_axes_top)]
        layout = go.Layout(**generated_styles).update(**styles_modified)
        return layout

    def get_traces(self):
        traces = [] 
        num_axes = 1
        for track in self.tracks_ordered:
            for axis in track.get_all_axes():
                # if there is an update_trace, it's better to update the axis than pass a num axes
                traces.extend(axis.render_traces(num_axes))
                num_axes += 1
        return traces

    def draw(self):
        layout = self.get_layout()
        traces = self.get_traces()
        fig = go.Figure(data=traces, layout=layout)
        
        fig.show()
        display(scrollON()) # This is going to have some CSS mods

    ####
    ####
    #### Get Tracks
    ####
    ####

    def get_track_by_index(self, index): #gtbi
        index -=1
        if index >= len(self.tracks_ordered) or index < 0:
            raise IndexError("Track index out of range") # I think
        return self.tracks_ordered[index]

    def get_tracks_by_name(self, name): #gtbn
        tracks = []
        for track in self.tracks_ordered:
            for axis in track.get_all_axes():
                if axis.name == name: tracks.append(track)
        return tracks

    ####
    ####
    #### Modify Tracks
    ####
    ####
    def combine_tracks(self, destination, tracks):
        if not isinstance(tracks, list):
            tracks = [tracks]
        if id(destination) not in self.tracks_by_id:
            raise Exception("Destination track does not exist")
        for track in tracks:
            if id(track) in self.tracks_by_id:
                self.remove_track(track)
            for lower in track.get_lower_axes():
                destination.add_axis(lower, position=-1)
            for upper in track.get_upper_axes():
                destination.add_axis(upper, position=1)

    #def combine_tracks_by_index(self, index, indices)
    #def separate_axis
    ####
    ####
    #### Utility Functions
    ####
    ####

    ## For your info
    def get_named_tree(self):
        result = []
        for track in self.tracks_ordered:
            result.append(track.get_named_tree())
        return { 'graph': result }

class Track():
    def __init__(self, data, **kwargs): # {name: data}
        self.name = kwargs.get('name', data.mnemonic) # Gets trackname from the one data
        self.display_name = kwargs.get('display_name', self.name)


        # This is really one object (but we can't private in python)
        self.axes = {}
        self.axes_below = [] # Considered "before" axes_above list
        self.axes_above = []
        self.axes_by_id = {}

        newAxis = Axis(data)
        
        self.add_axis(newAxis)
        
        
    def add_axis(self, axis, position=1):
        if position == 0:
            raise Exception("Position must be > or < 0")
        if id(axis) in self.axes_by_id:
            return
        
        if axis.name in self.axes:
            self.axes[axis.name].append(axis)
        else:
            self.axes[axis.name] = [axis]
        
        if position > 0:
            if position >= len(self.axes_above):
                self.axes_above.append(axis)
            else:
                self.axes_above.insert(position-1, axis)
        else:
            position = -position
            if position >= len(self.axes_below):
                self.axes_below.append(axis)
            else:
                self.axes_below.insert(position-1, axis)
        
        self.axes_by_id[id(axis)] = axis
        
    def remove_axis(self, axis):
        if id(axis) not in self.axes_by_id:
            return
        del self.axes_by_id[id(axis)]
        self.axes[axis.name].remove(axis)
        if len(self.axes[axis.name]) == 0:
            del self.axes[axis.name]
        try:
            self.axes_below.remove(axis)
        except ValueError:
            self.axes_above.remove(axis)
            pass

    
    def count_axes(self):
        return len(self.axes)
    
    ####
    ####
    #### Get Axes
    ####
    ####
    
    def get_all_axes(self):
        return list(itertools.chain(self.axes_below, self.axes_above)) 
    def get_lower_axes(self):
        return self.axes_below
    def get_upper_axes(self):
        return self.axes_above

    def get_axes_by_name(self, name): #gtbn
        axes = []
        for axis in self.get_all_axes():
            if axis.name == name: axes.append(axis)
        return axes

    def get_axis_styles(self, start_axis = 0, graph_end_pos = 1):
        styles = []
        #print(f'Im track, My parents axis is {start_axis}')
        total_axes = 0
        for i, axis in enumerate(self.get_lower_axes()):
            parent_axis = 0 if not i or not start_axis else start_axis
            style = axis.get_style(parent_axis)
            style['side'] = "bottom"
            styles.append(style)
            total_axes += 1
        for i, axis in enumerate(self.get_upper_axes()):
            parent_axis = 0
            if i and start_axis:
                parent_axis = start_axis + total_axes
            style = axis.get_style(parent_axis)
            style['side'] = "top"
            if parent_axis:
                style['position'] = graph_end_pos + (1-graph_end_pos)*(i/(len(self.get_upper_axes())-1)) 
                print(f'Positioning: Axis number: {i}, graph_end_pos: {graph_end_pos}. position: {style["position"]}')
            styles.append(style)
        return styles


    ## FYI
    def get_named_tree(self):
        above = []
        below = []
        for axis in reversed(self.axes_above):
            above.append(axis.get_named_tree())
        for axis in reversed(self.axes_below):
            below.append(axis.get_named_tree())
        return { "track": { self.name: { "above": above, "below": below } } }




class Axis():
    def __init__(self, data, **kwargs):
        self.data = data if type(data) == list else [data]
        self.axis_template = kwargs.get('template', copy.deepcopy(xaxes_template_default))
        self.name = kwargs.get('name', self.data[0].mnemonic)
        self.display_name = kwargs.get('display_name', self.name)

    def get_color(self):
        return randomColor(self.data[0].mnemonic) # for now, more options later

    def get_style(self, parent_axis):
        color = self.get_color()
        ret = dict(
            title = dict(
                standoff=0, # should be in template
                text=self.display_name,
                font=dict(
                    color=color
                )
            ), 
            linecolor=color,
            tickfont=dict(
                color=color,
            ),
            tickcolor=color,
            **self.axis_template,
        )
        off_axis = {}
        if parent_axis:
            off_axis = copy.deepcopy(xaxes_off_axis)
            off_axis["overlaying"] = "x" + str(parent_axis)
        return ret | off_axis # >=python 3.9


    def render_traces(self, axis_number): ## is there an update trace?
    # TODO should create several traces
        all_traces = []
        for datum in self.data: 
           all_traces.append(go.Scattergl(
                x=datum.values,
                y=datum.index,
                mode='lines', # nope, based on data w/ default
                line=dict(color=self.get_color()), # needs to be better, based on data
                xaxis='x' + str(axis_number),
                yaxis='y',
                name = datum.mnemonic, # probably needs to be better
            ))
        return all_traces

    ##### Not sure I like these, if nothing uses them, re-evaluated them
    def get_named_tree(self): # I feel this might be useful? Tracks really can be numbers.
        result = []
        for el in self.data:
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }

# Data must have a y axis, a value axis, and a mnemonic
class Data():
    def __init__(self, index, values, mnemonic): # so it should default to the default index if there is only one 
        self.index = index
        self.values = values
        self.mnemonic = mnemonic

    ##### Not sure I like these!
    def get_named_tree(self): # This should be just for display, so maybe a _repr_*_ function
        return  { "data" : {'mnemonic': self.mnemonic, 'shape': self.values.shape } }