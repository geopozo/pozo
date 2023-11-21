import plotly.graph_objects as go
import itertools, copy, warnings

from IPython.display import Javascript # Part of Hack #1

# Actually, this doesn't matter. If the depths are the same, it's fine.
"""
class ConflictingDepths(Exception): # Not sure if subclassing Exception is the best answer here
    def __init__(self):
        self.message = "More than one data source has a \"DEPTH\" column- TrackExplorer doesn't know which to use as a Y Axis. You can use \"yaxiname=COLUMN_NAME\" or \"maindata=DATA_SOURCE\" to disambiguate."
    def __str__(self): return self.message
"""

# Get visuals better (legend on hover, labels, colors)

# Combine Tracks

# Flatten

# Save transformation on a LAS files

# go through to-do list
# doc strings w/ tags
# get rid of legend
# make sure to reverse (autorange=reversed)
# get names up on traces
# play around with axis positioning
# combining tracks. combing traces.
# initializizers
# what if you just want a bare track, a bare axis, a bare data, what does it create
# What if you want to access tracks? We can have two functions, one plural, one singular, like HTML.
# Helper Functions
# Plotly Functions
# Dealing with widget (pausing rendering)
LAS_TYPE = "<class 'lasio.las.LASFile'>"
def randomColor(toNumber = 0):
    import random
    if toNumber != 0:
        random.seed(hash(toNumber))
    ops = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    return ops[random.randint(0, len(ops)-1)]

def scrollON(): # TODO can we really not just display this directly form here?
    return Javascript('''document.querySelectorAll('.jp-RenderedPlotly').forEach(el => el.style.overflow = 'scroll');''') # Part of Hack #1

# Data must have a y axis, a value axis, and a mnemonic
class Data():
    def __init__(self, index, values, mnemonic): # so it should default to the default index if there is only one 
        self.index = index
        self.values = values
        self.mnemonic = mnemonic
    def info(self):
        return  { "data" : {'mnemonic': self.mnemonic, 'shape': self.values.shape } }

class Graph():
    axes_template_default = dict(showgrid=False, zeroline=False)
    default_styles_default = dict( # change this to default
        showlegend = False,
        margin = dict(l=5, r=5, t=5, b=5),
        yaxis = dict(
            autorange='reversed',
            showgrid=False,
            zeroline=False,
        ),
        height = 600,
        plot_bgcolor = "#FFFFFF",
    )



    def __init__(self, *args, **kwargs):
        # Essential Configuration
        self.yaxisname = kwargs.get('yaxisname',"DEPTH")
        self.width_per_track = kwargs.get('width_per_track', 200)
        self.axes_template = kwargs.get('axes_template', copy.deepcopy(self.axes_template_default))
        self.default_styles = kwargs.get('default_styles', copy.deepcopy(self.default_styles_default))
        # Random Configuration
        self.indexOK = kwargs.get('indexOK', False) # Supresses warning about using index, not column.
                                                    # Probably need a way to conform to index

        # Objects
        # A list and its index see NOTE:ORDEREDDICT
        self.tracks_ordered = [] 
        self.tracks = {}
        self.track_by_id = {}

        self.yaxis = [] # what if we have weird axes? axes that contain other axes?

        for ar in args:
            
            # Process LASio LAS Object
            if str(type(ar)) == LAS_TYPE:

                ## Create Y-Axis
                # Probably need this idea of flattening y axes
                if self.yaxisname in ar.curves.keys():
                    self.yaxis.append(ar.curves[self.yaxisname].data)
                else:
                    self.yaxis.append(ar.index)
                    if not indexOK:
                        warnings.warn("No " + self.yaxisname + " column was found in the LAS data, so we're using `las.index`. set ")

                ## Create Data and Tracks
                for curve in ar.curves:
                    if curve.mnemonic == self.yaxisname: continue

                    data = Data(self.yaxis[-1], curve.data, curve.mnemonic)
                    # TODO: need to check if mnemonic is modified, now!
                    newTrack = Track(data)

                    # NOTE:ORDEREDDICT- >1 value per key, but insert order is still maintained
                    self.tracks_ordered.append(newTrack)
                    if data.mnemonic in self.tracks:
                        self.tracks[data.mnemonic].append(newTrack)
                    else:
                        self.tracks[data.mnemonic] = [newTrack]
                    self.track_by_id[id(newTrack)] = newTrack
                    

    def get_named_tree(self):
        result = []
        for track in self.tracks_ordered:
            result.append(track.get_named_tree())
        return { 'graph': result }
    def get_unnamed_tree(self):
        result = []
        for track in self.tracks_ordered:
            result.append(track.get_unnamed_tree())
        return result

    # calculate number of ticks based on width TODO (4)
    # don't use tree like that
    # Rendering Functions
    def get_layout(self):
        # default but changeable
        margin = .002
        start = .01 
        num_tracks = len(self.tracks_ordered)
        waste_space = start + (num_tracks-1) * margin
        width = (1 - waste_space) / num_tracks

        axes = {}
        i = 0
        for track in self.tracks_ordered:
            for axis in track.get_all_axes():
                i+=1
                axes["xaxis"+str(i)] = dict(
                    domain = [start, start + width if start+width <= 1 else 1],
                    title = dict(
                        text=axis.display_name,
                        font=dict(
                            color=randomColor(axis.data[0].mnemonic) # TODO call a color behavior
                        )
                    ), 
                    **self.axes_template
                )
            start += width + margin
        if len(self.tracks_ordered) > 6: # TODO tune this number
            warnings.warn("If you need scroll bars, call `display(scrollON())` after rendering the graph. This is a plotly issue and we will fix it eventually.")   
        generated_styles = dict(
            **axes,
            width=len(self.tracks_ordered) * self.width_per_track,
        )
        layout = go.Layout(**generated_styles).update(**self.default_styles)
        return layout

    def get_traces(self):
        traces = []
        tree = self.get_unnamed_tree() # really don't know if this is the best way to iterate given we need styling information for trace (its not all in layout) and this object only contains the actual data. 
        num_axes = 1
        for track in tree:
            for axis in track[0]: # these are... below
                for data in axis:
                    suffix = str(num_axes)
                    traces.append(
                        go.Scattergl(
                            x=data.values,
                            y=data.index,
                            mode='lines',
                            line=dict(color=randomColor(data.mnemonic)),
                            xaxis='x' + suffix,
                            yaxis='y',
                            name = data.mnemonic,
                        
                    ))
                num_axes += 1
            for axis in track[1]: # these are above
                for data in axis:
                    suffix = str(num_axes)
                    traces.append(
                        go.Scattergl(
                            x=data.values,
                            y=data.index,
                            mode='lines',
                            line=dict(color=randomColor(data.mnemonic)),
                            xaxis='x' + suffix,
                            yaxis='y',
                            name = data.mnemonic,
                    ))
                num_axes += 1
        return traces
    def draw(self):
        layout = self.get_layout()
        traces = self.get_traces()
        return go.Figure(data=traces, layout=layout)

# TODO: how would we accept multiple data
# What do we do with multiple data?
# How do we organize the axis?
# If we want them on the same axis, they must pass an Axis structure
# If they pass a data, it will be wrapped in an axis
class Track():
    # TODO Track also as to take axes
    # TODO What do do with multiple data
    def __init__(self, data, **kwargs): # {name: data}
        self.name = kwargs.get('name', data.mnemonic) # Gets trackname from the one data
        self.display_name = kwargs.get('display_name', self.name)
        

        # This is really one object (but we can't private in python)
        self.axes = {}
        self.axes_above = []
        self.axes_below = [] # Probably return these as combined iterator
        self.axes_by_id = {}
        
        newAxis = Axis(data)

        if newAxis.name in self.axes:
            self.axes[newAxis.name].append(newAxis)
        else:
            self.axes[newAxis.name] = [newAxis]

        # There will have to be a switch for this TODO
        self.axes_below.append(newAxis)
        self.axes_by_id[id(newAxis)] = newAxis

    def count_axes(self):
        return len(self.axes)

    def get_named_tree(self):
        above = []
        below = []
        for axis in reversed(self.axes_above):
            above.append(axis.get_named_tree())
        for axis in reversed(self.axes_below):
            below.append(axis.get_named_tree())
        return { "track": { self.name: { "above": above, "below": below } } }
    def get_unnamed_tree(self):
        above = []
        below = []
        for axis in reversed(self.axes_above):
            above.append(axis.get_unnamed_tree())
        for axis in reversed(self.axes_below):
            below.append(axis.get_unnamed_tree())
        return [above, below]
    def get_all_axes(self):
       return list(itertools.chain(self.axes_below, self.axes_above)) 
        

# Axis can take multiple data
# It will place all the data on the same axis
# What happens if the axis has multiple y data?
# If it should be on a different y axis, that's the users problem
# We should accept data, data, data and [data, data], data
# Do we allow formatting in construction?
# Will it be able to create a "pause render" function?
class Axis():
    def __init__(self, data, **kwargs):
        if type(data) != list:
            self.data = [data]
        else:
            self.data = data
        self.name = kwargs.get('name', self.data[0].mnemonic)
        self.display_name = kwargs.get('display_name', self.name)
    def get_named_tree(self):
        result = []
        for el in self.data:
            result.append(el.info())
        return { "axis" : { self.name: result } }
    def get_unnamed_tree(self):
        result = []
        for el in self.data:
            result.append(el)
        return result



# Dropping in your  
# -lasio LAS file
# - panda dataframe
# - welly well
# - well project
# - curve
# - whatever

# Constructing custom tracks! (several axes on one track, several curves on one axes)
# Modifying tracks and axis (combining two tracks into one track w/ two axes)
# Changing (and specifying) color schemes, Graph Schemes
# Deviation
# Getting at plotly

# they all need destructors, to indicate if they don't exist anymore

# this tree thign is bad, should probably be like "get tracks" "get axis" etc