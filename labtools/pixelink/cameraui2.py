#!/usr/bin/env python
"""
.. module:: pixelink.cameraui
   :synopsis: Pixelink camera controller GUI

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>


This is a GUI for the Camera object
"""


import enthought.traits.api as traits
import enthought.traits.ui.api as ui

import enthought.pyface.api as pyface

from labtools.pixelink.camera import Camera, get_number_cameras

import matplotlib.pyplot as plt
from scipy.misc.pilutil import toimage
import numpy, os

from labtools.utils.instrui import BaseDeviceUI, device_group, device_search_group, status_group

from .PxLAPI import *
from .PxLTypes import *
from .PxLCodes import *


_NO_CAMERAS = 'No cameras found!'

_FORMAT_KEYS = (PIXEL_FORMAT_MONO8, 
                PIXEL_FORMAT_MONO16,
                PIXEL_FORMAT_YUV422,
                PIXEL_FORMAT_BAYER8 ,
                PIXEL_FORMAT_BAYER16 ,
                PIXEL_FORMAT_RGB24,
                PIXEL_FORMAT_RGB48 )

_FORMAT_VALUES = ('MONO8',
                'MONO16',
                'YUV422',
                'BAYER8',
                'BAYER16',
                'RGB24',
                'RGB48')

_FORMAT = dict(list(zip(_FORMAT_KEYS,_FORMAT_VALUES)))


_SINGLE_VALUED_FEATURES = {'gain' : FEATURE_GAIN,
                  'shutter' : FEATURE_SHUTTER,
                  'format' : FEATURE_PIXEL_FORMAT}
                  
_COLORS = {
        PIXEL_FORMAT_MONO8 : 1,
        PIXEL_FORMAT_MONO16 : 1,
        PIXEL_FORMAT_BAYER8 : 1,
        PIXEL_FORMAT_BAYER16 : 1,
        PIXEL_FORMAT_RGB24 : 3,
        PIXEL_FORMAT_RGB48 : 3,
        }
            
_DTYPE = {
        PIXEL_FORMAT_MONO8 : 'uint8',
        PIXEL_FORMAT_MONO16 : 'uint16',
        PIXEL_FORMAT_BAYER8 : 'uint8',
        PIXEL_FORMAT_BAYER16 : 'uint16',
        PIXEL_FORMAT_RGB24 : 'uint8',
        PIXEL_FORMAT_RGB48 : 'uint16',
        }
                  
class RangeFeature(traits.HasTraits):
    """
    Defines a feature that is settable by slider
    """
    value = traits.Range('low','high','value_')
    value_ = traits.CFloat(0.)
    low = traits.CFloat(-10000.)
    high = traits.CFloat(10000.)
    is_settable = traits.Bool(False)
    id = traits.Property(depends_on = 'name')
    #index for multivalued features can be > 0
    index = traits.Int(0)
    name = 'gain'
    view = ui.View(ui.Item('value', show_label = False))
    
    def _get_id(self):
        return _SINGLE_VALUED_FEATURES.get(self.name)

class IntRangeFeature(traits.HasTraits):
    """
    Defines a feature that is settable by slider
    """
    value = traits.Range('low','high','value_')
    value_ = traits.CInt(0.)
    low = traits.CInt(-10000.)
    high = traits.CInt(10000.)
    is_settable = traits.Bool(False)
    id = traits.Property(depends_on = 'name')
    index = traits.Int(0)
    name = 'gain'
    view = ui.View(ui.Item('value', show_label = False, style = 'custom'))

    
    def _get_id(self):
        return _SINGLE_VALUED_FEATURES.get(self.name)

class MappedFeature(RangeFeature):
    """
    Defines a feature that is selectable
    """
    value = traits.CInt(0, editor = ui.EnumEditor(name = 'values'))
    low = traits.CInt(0)
    high = traits.CInt(1)
    map = traits.Dict({0:'feature0', 1: 'feature'})
    values = traits.Property(traits.Dict, depends_on = 'low,high,map')
        
    def _get_values(self):
        d = {}
        for i in range(self.low,self.high + 1):
            d[i] = self.map[i]
        return d


def create_range_feature(name, **kw):
    return traits.Instance(RangeFeature(name = name),(), **kw)
    
def create_int_range_feature(name, **kw):
    return traits.Instance(IntRangeFeature(name = name),(), **kw)    

def create_int_multirange_feature(name, index, **kw):
    return traits.Instance(IntRangeFeature(name = name, index = index),(), **kw) 

def create_mapped_feature(name, map, **kw):
    return traits.Instance(MappedFeature(name = name, map = map),(), **kw) 


class ROI(traits.HasTraits):
    top = create_int_multirange_feature('top',0)
    left = create_int_multirange_feature('left',1)
    width = create_int_multirange_feature('width',2)
    height = create_int_multirange_feature('height',3)
    
    values = traits.Property(traits.Int, depends_on = 'top.value,left.value,width.value,height.value')
    
    def _get_values(self):
        return self.top.value, self.left.value, self.width.value, self.height.value
    
    
    view = ui.View(
                ui.Item('top', style = 'custom'),
                ui.Item('left', style = 'custom'),
                ui.Item('width', style = 'custom'),
                ui.Item('height', style = 'custom'),
    )



class CameraUI(Camera,  BaseDeviceUI):
    """Camera settings defines basic camera settings
    """
 
    cameras = traits.List([_NO_CAMERAS],transient = True)
    camera = traits.Any(value = _NO_CAMERAS, desc = 'camera serial number', editor = ui.EnumEditor(name = 'cameras'))
    
    search = traits.Button(desc = 'camera search action')

    _initialized= traits.Bool(False, transient = True)
    
    play = traits.Button(desc = 'display preview action')
    stop = traits.Button(desc = 'close preview action')
    on_off = traits.Button('On/Off', desc = 'initiate/Uninitiate camera action')

    gain = create_range_feature('gain',desc = 'camera gain',transient = True)
    shutter = create_range_feature('shutter', desc = 'camera exposure time',transient = True)
    format = create_mapped_feature('format',_FORMAT, desc = 'image format',transient = True)
    roi = traits.Instance(ROI,transient = True)
    
    im_shape = traits.Property(depends_on = 'format.value,roi.values')
    im_dtype = traits.Property(depends_on = 'format.value')
    
    capture = traits.Button()
    save_button = traits.Button('Save as...')
    
    message = traits.Str(transient = True)
    
    view = ui.View(device_group, ui.Group(ui.HGroup(ui.Item('camera', springy = True),
                           ui.Item('search', show_label = False, springy = True),
                           ui.Item('on_off', show_label = False, springy = True),
                           ui.Item('play', show_label = False, enabled_when = 'is_initialized', springy = True),
                           ui.Item('stop', show_label = False, enabled_when = 'is_initialized', springy = True),
                           ),
                    ui.Group(
                        ui.Item('gain', style = 'custom'),
                        ui.Item('shutter', style = 'custom'),
                        ui.Item('format', style = 'custom'),
                        ui.Item('roi', style = 'custom'),
                        ui.HGroup(ui.Item('capture',show_label = False),
                        ui.Item('save_button',show_label = False)),
                        enabled_when = 'is_initialized',
                        ),
                        ),
                resizable = True,
                statusbar = [ ui.StatusItem( name = 'message')],
                buttons = ['OK'])
    
    #default initialization    
    def __init__(self, **kw):
        super(CameraUI, self).__init__(**kw)
        self.search_cameras()

    def _camera_control_default(self):
        return Camera()

    def _roi_default(self):
        return ROI()
        
    #@display_cls_error 
    def _get_im_shape(self):
        top, left, width, height = self.roi.values
        shape = (height, width)
        try:
            colors = _COLORS[self.format.value] 
            if colors > 1:
                shape += (colors,)
        except KeyError:
            raise NotImplementedError('Unsupported format')  
        return shape
    
    #@display_cls_error    
    def _get_im_dtype(self):
        try:        
            return _DTYPE[self.format.value]
        except KeyError:
            raise NotImplementedError('Unsupported format')        
        
   
    def _search_fired(self):
        self.search_cameras()
        
    #@display_cls_error
    def search_cameras(self):
        """
        Finds cameras if any and selects first from list
        """
        try:
            cameras = get_number_cameras()
        except Exception as e:
            cameras = []
            raise e
        finally:
            if len(cameras) == 0:
                cameras = [_NO_CAMERAS]
            self.devices = cameras
            self.device = cameras[0]

    #@display_cls_error
    def _camera_changed(self):
        if self._initialized:
            self._initialized= False
            self.close()
            self.message = 'Camera uninitialized'
    
    #@display_cls_error
    def init_camera(self):
        self._initialized= False
        if self.device != _NO_CAMERAS:
            self.init(self.device)
            self.init_features()
            self._initialized= True
            self.message = 'Camera initialized'
            
    #@display_cls_error
    def _on_off_fired(self):
        if self._initialized:
            self._initialized= False
            self.close()
            self.message = 'Camera uninitialized'
        else:
            self.init_camera()
            
    #@display_cls_error
    def init_features(self):
        """
        Initializes all features to values given by the camera
        """
        features = self.get_camera_features()
        self._init_single_valued_features(features)
        self._init_roi(features)
    
    #@display_cls_error
    def _init_single_valued_features(self, features):
        """
        Initializes all single valued features to camera values
        """
        for name, id in list(_SINGLE_VALUED_FEATURES.items()):
            feature = getattr(self, name)
            feature.low, feature.high = features[id]['params'][0]
            feature.value = self.get_feature(id)[0]
            
    #@display_cls_error
    def _init_roi(self, features):
        for i,name in enumerate(('top','left','width','height')):
            feature = getattr(self.roi, name)
            low, high = features[FEATURE_ROI]['params'][i]
            value = self.get_feature(FEATURE_ROI)[i]
            try:
                feature.value = value
            finally:
                feature.low, feature.high = low, high
                       
    @traits.on_trait_change('format.value')
    def _on_format_change(self, object, name, value):
        if self._initialized:
            self.set_preview_state(STOP_PREVIEW)
            self.set_stream_state(STOP_STREAM)
            self.set_feature(FEATURE_PIXEL_FORMAT, [value])
            
    @traits.on_trait_change('gain.value,shutter.value')
    def _single_valued_feature_changed(self, object, name, value):
        if self._initialized:
            self.set_feature(object.id, [value])

    #@display_cls_error
    def set_feature(self, id, values, flags = 2):
        self.set_feature(id, values, flags = flags)
            
    @traits.on_trait_change('roi.values')
    def a_roi_feature_changed(self, object, name, value):
        if self._initialized:
            self.set_feature(FEATURE_ROI, value)
            try:
                self._initialized= False
                self.init_features()
            finally:
                self._initialized= True
        
    #@display_cls_error                    
    def _play_fired(self):
        self.set_preview_state(STOP_PREVIEW)
        self.set_stream_state(STOP_STREAM)
        self.set_stream_state(START_STREAM)
        self.set_preview_state(START_PREVIEW)
        
    #@display_cls_error
    def _stop_fired(self): 
        self.set_preview_state(STOP_PREVIEW)
        self.set_stream_state(STOP_STREAM)
        self.error = ''
 
    #@display_cls_error
    def _format_changed(self, value):
        self.set_preview_state(STOP_PREVIEW)
        self.set_stream_state(STOP_STREAM)
        self.set_feature(FEATURE_PIXEL_FORMAT, [value],2)
    
    #@display_cls_error
    def _capture_fired(self):
        self.set_stream_state(STOP_STREAM)
        self.set_stream_state(START_STREAM)
        im = self.capture_image()
        plt.imshow(im)
        plt.show()

    def capture_image(self):
        im = numpy.empty(shape = self.im_shape, dtype = self.im_dtype)
        self.get_next_frame(im)
        return im.newbyteorder('>')
        
    def save_image(self, fname):
        """Captures image and saves to format guessed from filename extension"""
        im = self.capture_image()
        base, ext = os.path.splitext(fname)
        if ext == '.npy':
            numpy.save(fname, im)
        else:
            im = toimage(im)
            im.save(fname)

    def _save_button_fired(self):
        f = pyface.FileDialog(action = 'save as') 
                       #wildcard = self.filter)
        if f.open() == pyface.OK: 
            self.save_image(f.path)                 

    def capture_HDR(self):
        pass
                
    def __del__(self):
        try:
            self.set_preview_state(STOP_PREVIEW)
            self.set_stream_state(STOP_STREAM)
        except:
            pass
    
def main():
    settings = CameraUI()
    settings.configure_traits()
    
if __name__ == '__main__':
    main()
