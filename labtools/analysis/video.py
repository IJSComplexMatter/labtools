"""Some tools for extracting and displaying video frame-by-frame 
"""
from enthought.traits.api import HasTraits, Instance,  File, Range, Array, \
        Property, Int, Float, Long, on_trait_change, Enum
from enthought.traits.ui.api import View, Item, RangeEditor


from scipy.misc.pilutil import fromimage

from labtools.analysis.figure import Figure
from labtools.instruments.pixelink.io import PixelinkDataStream

try:
    import pyffmpeg
    VIDEO_TYPES = ('ffmpeg','pixelink')
except ImportError:
    VIDEO_TYPES = ('pixelink',)
    import warnings
    warnings.warn('pyffmpeg not installed. Please install it if you want to import avi files')

class FrameInfo(HasTraits):
    """This holds information about each frame. This is to be used in :class:`Video`
    """
    #: frame index
    index = Range(low = '_low',high = '_high')
    #: frame time
    time = Property(depends_on = 'index,fps', editor = RangeEditor(is_float = True,low_name = 'object._low_', high_name = 'duration'))
    #: duration of the movie
    duration = Float(1.)
    #: frame rate
    fps = Float(1.)
    #: number of frames
    n_frames = Long(1)
    
    view = View('index','time')
    
    _low = Int(0)
    _high = Property(depends_on= 'n_frames')
    _low_ = Float(0)
    
    def _get_time(self):
        return self.index/self.fps
        
    def _set_time(self,value):
        value = int(round(self.fps*value + 0.5))
        if value > self.n_frames -1:
            value = self.n_frames -1
        self.index = value
        
    def _get__high(self):
        return self.n_frames -1
    
class Video(HasTraits):
    """this can be used for video frame-by-frame display and frame getter
    It uses ffmpeg stream, so movies that are supported by ffmpeg can be loaded.
    Also pixelink data streams can be loaded. can be used as an iterrator
    
    >>> v = Video(video_type = 'ffmpeg')
    >>> v.open_stream('/home/andrej/Desktop/Film10/10.avi')
    >>> im = v.get_frame(0)
    >>> for im in v: pass
    """
    #: specifies video filename
    filename = File
    #: specifies video type
    video_type = Enum(*VIDEO_TYPES)
    #: frame information is storred here
    frame_info = Instance(FrameInfo,())
    #: actual frame data as numpy array is storred here
    image = Array
    #: display figure
    figure = Instance(Figure,())
    view = View('filename','video_type',Item('figure',style = 'custom', show_label = False),
                Item('frame_info', label = 'Frame', style = 'custom'),resizable = True)
    
    def __init__(self, **kw):
        super(Video,self).__init__(**kw)
        if self.filename:
            self.open_stream(self.filename)

    
    @on_trait_change('frame_info.index')
    def get_frame(self, index):
        """Opens frame and returns image storred in numpy array
        
        :param index:
            specifies frame index
        :returns numpy.array of a given frame
            
        """
        if self.video_type == 'pixelink':
            self.image = self.stream.get_frame(index)
            self.figure.update_image(self.image)
        else:
            self.image = fromimage(self.stream.GetFrameNo(index))
            self.figure.update_image(self.image[:,:,0])
        return self.image
        
    def open_stream(self, filename):
        """Opens stream from filename
        
        :param str filename:
            must be a valid filename
        """
        if self.video_type == 'pixelink':
            self.stream = PixelinkDataStream()
            self.stream.open(filename)
            self.frame_info.index = 0
            self.get_frame(0)
            self.frame_info.n_frames = len(self.stream.frame_desc)
            self.frame_info.duration = self.stream.frame_desc[-1]['FrameTime'] - \
                                        self.stream.frame_desc[0]['FrameTime']
            self.frame_info.fps = self.stream.frame_desc[0]['FrameRate']
            
        else:
            self.stream = pyffmpeg.VideoStream()
            self.stream.open(filename)
            self.frame_info.index = 0
            self.get_frame(0)
            self.frame_info.n_frames = (self.stream.tv.duration() -1)
            self.frame_info.duration = self.stream.vr.duration_time()
            self.frame_info.fps = self.stream.tv.get_fps() 
        self.filename = filename
        
    def _filename_changed(self,name):
        self.open_stream(name)
        
    def _video_type_changed(self):
        if self.filename:
            self.open_stream(self.filename)
        
    def __iter__(self):
        self._iteration_start = True
        return self
    
    def __next__(self):
        try:
            if self._iteration_start:
                self._iteration_start = False
            else:
                self.frame_info.index +=1
            return self.image
        except:
            raise StopIteration

if __name__ == '__main__':   
    v = Video()
    v.configure_traits()
    
#    for frame in v:
#        print 'extracting frame %d' % v.frame_info.index
        
    
    
    
