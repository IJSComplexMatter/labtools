#!/usr/bin/env python

"""
Image format classes for opening images to numpy arrays
Use AnyFormat or ExtFormat
"""

from enthought.traits.api import *
from enthought.traits.ui.api import *
from PIL import Image as PIL_Image
from scipy.misc.pilutil import fromimage, toimage

from numpy import save, load, memmap
import os

def open_bw(filename, size=(1024,1280), bits = 10, order = '>', shift_bits = True, data_offset = 0, as_float = False):
    """
    odpre raw file 'filename', velikost slike size = (st. vrstic,st. stolpcev) 
    format zapisa je lahko 8 ali 16 bitni unsigned int, medtem ko 
    - bits pove koliko bitov je dejansko uporabljenih
    - order je lahko '>', '<', (big oz. little endian)
    - shift_bits = True skalira sliko z 2 ** (format - bits), drugace ne skalira
    - data_offset koliko bytov preskoci
    - as_float skalira tako da max = 1.0
    """
    DTYPE = {8 : 'uint8', 16 : 'uint16'}
    if bits > 0 and bits <= 8:
        dtype = 8
    elif bits <= 16:
        dtype = 16
    else:
        raise ValueError('bits must be between 1 and 16 ')
    
    a = memmap(filename, dtype = DTYPE[dtype], mode = 'c', shape = size, offset = data_offset)
    a = a.newbyteorder(order)
    if as_float == True and shift_bits == True:
        a = 1.0 * a / (2** dtype - 2 ** (dtype - bits) )
    elif as_float == True:
        a = a / (2** dtype - 1.)
    elif shift_bits == True:
        a = a / (2 ** (dtype - bits))
    return a



class Pil(object):
    """
    Defines open and save functions to open/save image to/from numpy array
    """
    @classmethod
    def open(self, filename):
        return fromimage(PIL_Image.open(filename))  
    @classmethod    
    def save(self, filename, data):
        im = toimage(data)
        im.save(filename)
        
class Numpy(object):
    """
    Defines open and save functions to open/save image to/from numpy array
    """    
    @classmethod
    def open(self, filename):
        return load(filename)  
    @classmethod    
    def save(self, filename, data):
        save(filename, data) 
        
class Binary(HasTraits):
    """
    Defines open and save functions to open/save image to/from numpy array
    Info about the binary format and a open function that returns the array
    """   
    bits = Range(value = 10, low = 1,high = 16)
    order = Trait('bigendian', {'littleendian' : '<', 'bigendian' : '>'})
    shift_bits = Bool(True)
    width = Int(1024)
    height = Int(768)
    #size is (width, height)
    size = Property(Tuple(Int,Int))
    as_float = Bool(False)
        
    def _get_size(self):
        return (self.height, self.width)
    
    def _set_size(self, value):
        self.height, self.width = value
        
    view = View('size', 'bits', 'shift_bits','order', 'as_float',
                buttons = ['OK','Cancel']
                )

    def open(self, filename):
        return open_bw(filename, size = self.size, order = self.order, 
                         bits = self.bits, shift_bits = self.shift_bits, as_float = self.as_float)
                         
    def save(self, filename, data):
        raise NotImplementedError 
       
class BasePixelink(HasTraits):
    """
    Base Class, you must override _get_size 
    """
    bits = Trait('MONO16',{'MONO8' : 8, 'MONO16' : 10})
    shift_bits = Bool(True)
    size = Property(Tuple(Int,Int))
    as_float = Bool(False)
    
    view = View(Item('bits', label = 'Format'),
                'shift_bits',
                'as_float',
                Item('size', style = 'readonly'))
                
    def _get_size(self):
        return (0,0)
        
    def open(self, filename):
        return open_bw(filename, size = self.size, order = '>', 
                         bits = self.bits_, shift_bits = self.shift_bits, as_float = self.as_float)
                         
    def save(self, filename, data):
        raise NotImplementedError    
      
class PixelinkA862(BasePixelink):
    """
    Defines open and save functions to open/save image to/from numpy array
    """
    bits = Trait('MONO16',{'MONO8' : 8, 'MONO16' : 12})
    
    def _get_size(self):
        return (1040,1392)
        
def create_format_item(name):
    return Item(name, 
                show_label = False,
                style = 'custom',
                visible_when = 'format == ' + repr(name)),

class BaseFormat(HasTraits):
    pass

class AnyFormat(BaseFormat):
    """
    Defines open/save functions for any format. Format is selectable with name attribute
    >>> f = AnyFormat(format = 'PIL')
    >>> im = f.open('test.jpg')
    >>> f.format = 'numpy'
    >>> f.save('test.npy', im)
    """
    #image format name
    format = Enum('PIL','binary', 'pixelink_A862', 'numpy', desc = 'camera model')
    
    #extra image formats
    pixelink_A862 = Instance(PixelinkA862,())
    binary = Instance(Binary,())
    #base image formats
    PIL = Instance(Pil,(),transient = True)
    numpy = Instance(Numpy,())
    
    #actual image format
    _format = Property(depends_on = 'format')
    
    view = View(Item('format', show_label = False),
                Group(
                create_format_item('binary'),
                create_format_item('pixelink_A862')),
                height = 200,
                )
    
    @cached_property
    def _get__format(self):
        return getattr(self, self.format)
    
    def open(self, filename):
        return self._format.open(filename)
                         
    def save(self, filename, data):  
        self._format.save(filename, data)
        
class ExtFormat(BaseFormat):
    """
    Defines open/save functions. Image type is determined from extension of given filename
    """
    format = Str('Auto format')
    view = View(Item('format', style = 'readonly'))
    
    @classmethod 
    def open(self, filename):
        if os.path.splitext(filename)[1] in ('.npy',):
            return Numpy.open(filename)
        else:
            return Pil.open(filename)
    @classmethod         
    def save(self, filename, data):
        if os.path.splitext(filename)[1] in ('.npy',):
            Numpy.save(filename, data)
        else:
            Pil.save(filename, data)

        
if __name__ == '__main__':
    f = AnyFormat()
    print(f.configure_traits())
                      
