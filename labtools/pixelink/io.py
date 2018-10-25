"""
.. module:: pixelink.io
   :synopsis: Pixelink camera IO

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>


This module defines some functions for pixelink data IO

* :func:`open_bw` Use this to open pixelink raw data
* :func:`open_pds` Use this to read pixelink data stream (video)
* :func:`pds_to_avi` Use this to convert pds video to AVI.

"""
import struct
from numpy import memmap, dtype, fromfile
import numpy as np
import os

from labtools.log import create_logger
from labtools.pixelink.conf import  LOGLEVEL

logger = create_logger(__name__, LOGLEVEL)

from PxLTypes import PXL_MAX_STROBES,PXL_MAX_KNEE_POINTS,\
    PIXEL_FORMAT_MONO8,PIXEL_FORMAT_MONO16,\
    PIXEL_FORMAT_RGB24,PIXEL_FORMAT_RGB48,\
    PIXEL_FORMAT_BAYER8,PIXEL_FORMAT_BAYER16, CLIP_FORMAT_AVI
    
PIXEL_FORMAT = {PIXEL_FORMAT_MONO8 : ('gray', dtype('uint8')),
                PIXEL_FORMAT_MONO16: ('gray', dtype('uint16')),
                PIXEL_FORMAT_BAYER8 : ('gray', dtype('uint8')),
                PIXEL_FORMAT_BAYER16 : ('gray', dtype('uint16')),
                PIXEL_FORMAT_RGB24: ('rgb', dtype('uint8')),
                PIXEL_FORMAT_RGB48: ('rgb', dtype('uint16'))}

#: pixelink endian type for data stream
ENDIAN = '<'

#: frame descriptor number of items
FRAME_DESC_SIZE = (37 + PXL_MAX_KNEE_POINTS + 5 * PXL_MAX_STROBES)
#: header type for stream data
HEADER = '%sII' % ENDIAN
#: frame desc type for stream data
FRAME_DESC = ('%sIfI' + ((FRAME_DESC_SIZE-3) * 'f')) % ENDIAN 

#: numpy frame descriptor dtype
FRAME_DESC_DTYPE = dtype([\
        ('Size', 'uint32'),
        ('FrameTime', 'float32'),
        ('FrameNumber', 'uint32'),
        ('Brightness', 'float32'),
        ('AutoExposure', 'float32'),
        ('Sharpness', 'float32'),
        ('whiteBalance', 'float32'),
        ('Hue', 'float32'),
        ('Saturation', 'float32'),
        ('Gamma', 'float32'),
        ('Shutter', 'float32'),
        ('Gain', 'float32'),
        ('Iris', 'float32'),
        ('Focus', 'float32'),
        ('Temperature', 'float32'),
        ('Trigger', 'float32',(5,)),
        ('Zoom', 'float32'),
        ('Pan', 'float32'),
        ('Tilt', 'float32'),
        ('OpticalFilter', 'float32'),
        ('GPIO', 'float32', (5,PXL_MAX_STROBES)),
        ('FrameRate', 'float32'),
        ('ROI', 'float32', (4,)),
        ('Flip', 'float32', (2,)),
        ('Decimation', 'float32'),
        ('PixelFormat', 'float32'),
        ('ExtendedShutter', 'float32', (PXL_MAX_KNEE_POINTS,)),
        ('AutoROI','float32', (4,))])

def open_bw(filename, size=(1024,1280), bits = 10,  data_offset = 0, as_float = False, order = ENDIAN):
    """
    Opens pixelink raw file. 
    
    :param str filename:
        filename string
    :param tuple size:
        size of an image 
    :param int bits:
        determines how many bits are actually used (camera bits)
    :param int data_offset:
        determines offset to the data
    :param bool as_float:
        if set to True (False by default) data is rescaled so that max is 1.
    :param order:
        must be either '>' or '<', determines order in which files are stored
        '<' is a default pixelink order.
    """
    DTYPE = {8 : 'uint8', 16 : 'uint16'}
    if bits > 0 and bits <= 8:
        dtype = 8
    elif bits <= 16:
        dtype = 16
    else:
        raise ValueError, 'bits must be between 1 and 16 '
    
    a = memmap(filename, dtype = DTYPE[dtype], mode = 'c', shape = size, offset = data_offset)
    a = a.newbyteorder(order)
    if as_float == True:
        a = a / (2** bits - 1.)
    return a

def pds_to_avi(pdsname, aviname = None):
    """Converts pixelink data stream file to avi file.
    if aviname is not specified it is determined from input filename
    """
    from PxLAPI import PxLFormatClip #import it here to report warnings here if SDK not installed
    from PxLCodes import ERRORS
    
    if aviname is None:
        aviname, ext = os.path.splitext(pdsname) 
        aviname = os.path.abspath(aviname + '.avi')
    pdsname = os.path.abspath(pdsname)
        
    logger.info('Converting %s to %s.' % (pdsname, aviname))
    ret = PxLFormatClip(pdsname,aviname, CLIP_FORMAT_AVI)

    if ret != 0:
        msg = 'Error converting %s to %s.' % (pdsname, aviname)
        logger.error(msg)
        raise ERRORS.get(ret)(msg)
    
                                                                                                    
def open_pds(fname):
   """Returns an :class:`PixelinkDataStream` object that can then be used as an iterator
   or a frame by frame data getter.
   
   :param str fname:
       filename string
   
   >>> from labtools.pixelink.camera import Camera
   >>> c = Camera()
   >>> c.init()
   >>> c.save_clip('test.pds',1)# single frame clip
   >>> c.wait() #wait for video to be written
   >>> c.close()
   
   Now you can read data with
   
   >>> stream = open_pds('test.pds')
   >>> for frame in stream: pass #you can itterate over frames
   
   Each frame consists of a descriptor and image data. You can get frames also
   by calling:
       
   >>> desc, im = stream.get_frame(0) #get first frame descriptor and image array
   >>> desc, im = stream.get_frame(-1) #get last frame
   
   """ 
   stream = PixelinkDataStream()
   stream.open(fname)
   return stream


class PixelinkDataStream(object):
    """This object can be used to get frames frame-by-frame from a 
    pixelink data stream file

    >>> stream = PixelinkDataStream()
    >>> stream.open('test.pds')
    >>> desc, im = stream.get_frame(0) #get first frame descriptor and image array
    >>> desc, im = stream.get_frame(-1) #get last frame
    
    """
    
    def open(self, filename):
        """Opens filename for reading. This function reads frame dexcriptions
        of all frames and fills frame_desc attributes
        
        :param str filename:
            filename string
        :raises:
            IOError fi it is not a valid pds file
        """
        logger.info('Opening pixelink data stream file %s' % filename)
        with open(filename,'r') as f:
            magic, n = struct.unpack(HEADER, f.read(8))
            if magic != 0x04040404:
                raise IOError('Not a valid psd file')
            self._filename = filename
            self._n = n # number of frames
            self._offsets = {0 : f.tell()} #storres offset info of each frame
            self._index = 0 # current running index (for get_frame, next methods)
            
    def get_frame(self, index = None):
        """Returns a frame. If no argument is scpecified it will return next frame.
        
        Parameters
        ----------
        index : int
            frame number (can be negative (-1) for last frame)
            
        Returns
        -------
        A tuple of descriptor, frame np.arrays.

        Raises
        ------
        IndexError if frame does not exist
            
        """
        if index == None:
            index = self._index #just use current frame
        if index < 0:
            index = self._n +index # recalculate for negative lookback.
        logger.info('Reading frame %d' % index)
        #check if frame exists or not
        if index >= self._n or index < 0:
            raise IndexError('Frame %i does not exist' % index)
        #if it exists then try to get info from the storred offsets,
        try:
            self._index, offset = index, self._offsets[index]
            return self._get_frame(offset)
        #otherwise iterate over frames to get the desired frame
        except KeyError:
            while index >= self._index:
                offset = self._offsets[self._index]
                desc, im = self._get_frame(offset)
            return desc, im 
        
    def _get_frame(self, offset):
        """Reads description info and frame at a given offset
        """
        with open(self._filename) as f:
            logger.debug('Opening image descriptior at %i' % offset)
            f.seek(offset)
            desc = fromfile(f, dtype = FRAME_DESC_DTYPE, count = 1).newbyteorder(ENDIAN).reshape(()) # change byteorder and make it 0 dimensional
            im_shape = int(desc['ROI'][3]/desc['Decimation']), int(desc['ROI'][2]/desc['Decimation']) #height, width
            try:
                color, dt = PIXEL_FORMAT[int(desc['PixelFormat'])]
                if color == 'rgb':
                    im_shape = im_shape + (3,)
            except KeyError:
                raise ValueError('Unknown pixlenik format "%i", only RGB and Mono supported' % int(desc['PixelFormat']))    
        offset += desc['Size']
        logger.debug('Opening image data at %i' % offset)
        #first change byte order to pixelink byteorder, then swap (because strem is in swapped order!)
        im = np.memmap(self._filename, dtype = dt, mode = 'c', shape = im_shape, offset = offset ).newbyteorder(ENDIAN).byteswap()
        self._index += 1
        self._offsets[self._index] = offset + im.size * im.dtype.itemsize 
        return desc, im
        
    def next(self):
        if self._index  == self._n:  
            raise StopIteration
        logger.info('Reading frame %d' % self._index)
        offset = self._offsets[self._index]
        return self._get_frame(offset)
        
    def __iter__(self):
        self._index = 0
        return self