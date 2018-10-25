#!/usr/bin/env python

"""
Image manipulation classes....
"""

from enthought.traits.api import *
from enthought.traits.ui.api import *
from enthought.pyface.api import FileDialog, OK, ProgressDialog


from format import AnyFormat, ExtFormat, BaseFormat
import os
import glob
import re
import sys


#class StoppableThread (threading.Thread):
#    """Thread class with a stop() method. 
#    target must be a function that returns a target function which checks for stop argument
#    
#    >>> def f(stop):
#    ...     def _f():
#    ...         for i in range(10):
#    ...             if stop == True:
#    ...                 break
#    ...             else:
#    ...                 do_something_slow()
#    ...     return _f
#    ...
#    >>> t = StoppableThread(f)
#    >>> t.start()
#    >>> t.stop()
#    """
#
#    def __init__(self, target, **kwds):
#        self._stop = threading.Event()
#        target = target(self.stopped)
#        super(StoppableThread, self).__init__(target = target, **kwds)
#        
#    def stop(self):
#        self._stop.set()
#    
#    @property
#    def stopped(self):
#        return self._stop.isSet()
    

def error_to_str(e):
    """Converts error to a nice string
    """
    #return str(sys.exc_info()[1])
    return e.__class__.__name__ + ' ' + str(e)
    #return e.__class__.__name__ + ' ' + ','.join(map(str,e.args))

def my_comp (x,y):
    """
    Za sortiranje po cifrah v datoteki
    """
    def get_num(path):
        str = os.path.splitext(path)[0]
        try:
            r = map(float,re.findall(r'[\d]*[.]{0,1}[\d]+',str))
            print r
            return r
        except:
            return path
    comparison = cmp(get_num(x),get_num(y)) 
    if comparison == 0:
        return cmp(x,y)
    else:
        return comparison

def my_comp (x,y):
    """
    Za sortiranje po cifrah v datoteki
    """
    import re,scipy
    def getNum(str):
        try:
            tmp=float(re.findall(r'\d+',str)[-1])
        except:
            tmp=float(scipy.rand(1))
        return tmp
            
    return cmp(getNum(x),getNum(y)) 

statistics_group = Group('name','shape','colors','dtype', 
                         style = 'readonly', 
                         enabled_when = 'image', 
                         springy = True,
                         show_border = True,
                         label = 'Image info')

image_view = View(
                Item(
                    'filename', 
                    show_label = False),
                '_',
                Group(
                    Item(
                        'format', 
                        show_label = False, 
                        style = 'custom',
                        height = 200), 
                    show_border = True, 
                    label = 'Image format'),
                Item('reload', show_label = False),
                Item('open', show_label = False),
                Item('save', show_label = False),
                statistics_group,
                statusbar = [ StatusItem( name = 'error')],
                resizable = True ,
#                title = 'Image'
                )


class Image(HasTraits):
    """ 
    >>> im = Image(format = ExtFormat(), filename = 'test.jpg') #default format is AnyFormat
    >>> im.open_image()
    >>> im.array.dtype == 'uint8'
    True
    """
    
    #image input format settings
    format = Instance(BaseFormat)
    
    #image filename
    filename = File(desc = 'image filename', label = 'Image')

    #image array
    array = Array(transient = True)
    
    reload = Button()
    
    open = Button()
    save = Button()
    
    #------read only data
    name = Property(Str, depends_on = '_name')  
    shape = Property(Tuple, depends_on = 'array')
    dtype = Property(Str, depends_on = 'array')
    colors = Property(Str, depends_on = 'array')
    
    #------private data
    _name = Str(transient = True) 
    is_open = Property(Bool, depends_on = 'array')
    opened = Event()
    
    #errors are written here
    error = Str('', transient = True)
    
    view = image_view
    
    def _filename_changed(self,new):
        self._reload_fired()


    def _format_default(self):
        return AnyFormat()
    
    @cached_property
    def _get_is_open(self):
        if len(self.array.shape) >= 2:
            return True
        else:
            return False
            
    def _get_name(self):
        return self._name
  
    def _get_shape(self):
        return tuple(self.array.shape[0:2])
    
    def _get_dtype(self):
        return self.array.dtype
        
    def _get_colors(self):
        shape = self.array.shape
        if len(shape) == 2:
            return 'Gray'
        elif len(shape) > 2:
            if shape[2] == 3 : return 'RGB'
            if shape[2] == 4 : return 'RGBA'
    
    def _save_fired(self):
        f = FileDialog(action = 'save as', 
                       default_path = self.filename, 
                       wildcard = '*.jpg;*.tiff;*.bmp;*.png')
        if f.open() == OK:
            try:
                self.save_image(f.path)
                self.error = ''
            except Exception as e:
                self.error = error_to_str(e)
            
            
    def _open_fired(self):
        f = FileDialog(action = 'open', 
                       default_path = self.filename)
        if f.open() == OK:
            self.filename = f.path
            
    def _reload_fired(self):
        try:
            self.open_image()
            self._name = os.path.split(self.filename)[-1]
            self.opened = True
            self.error = ''
        except Exception as e:
            self.error = error_to_str(e)
                
    def open_image(self):
        self.array = self.format.open(self.filename)
            
    def save_image(self, filename):
        ExtFormat.save(filename, self.array)
        
filenames_view = View(
                    Group(
                        Item('directory', style = 'simple'),
                        Item('pattern', style = 'simple'),
                        Item('reverse', style = 'simple'),
                        Item('populate', style = 'simple', show_label = False),
                        Item('filenames', show_label = False,
                             editor = ListStrEditor(selected = 'filename'),
                             height = -150,
                             width = -300),
                        ),
                    statusbar = [ StatusItem( name = 'error')],
                    resizable = True,
#                    title = 'Filenames'
                    )        


class Filenames(HasTraits):
    """
    >>> files = Filenames(pattern = '*.jpg') #glob in current directory
    >>> files = Filenames(directory = 'test', pattern = '*.jpg') 
    #get files:
    >>> for f in files: print f
    #indexing works
    >>> files[0]
    """
    #selected filename
    filename = Str()
    
    directory = Directory(os.path.abspath(os.path.curdir),
                          desc = 'directory of files to be processed',
                          auto_set = False, enter_set = True)
    pattern = Str('',
                  desc = 'pattern of files, for instance "*.bin"',
                  auto_set = False, enter_set = True)
                  
    reverse = Bool(False)
    
    populate = Button()   
    
    filenames = List(Str)
    
    view = filenames_view
                
    def __init__(self, **kwds):
        kwds.setdefault('pattern', '*.*')
        super(Filenames, self).__init__(**kwds)

    @on_trait_change('populate,pattern,directory,reverse')
    def set_files(self):
        filenames = glob.glob(os.path.join(self.directory, self.pattern) )
        filenames.sort(my_comp, reverse = self.reverse)
        self.filenames = filenames

    def _filenames_default(self):
        return ['']
    
    def __iter__(self):
        return iter(self.filenames)  
      
    def __getitem__(self, item):
        return self.filenames[item]
        
    def __len__(self):
        return len(self.filenames)

images_view = View(
                Group(
                    Group(Item('files', style = 'custom', show_label = False),
                        label = 'Files', show_border = True),
                    Group('_',
                        Group(
                            Item('format', show_label = False, 
                                 style = 'custom', 
                                 height = 200), 
                            show_border = True, 
                            label = 'Image format'
                            ),
                        Item('reload', show_label = False),
                        Item('save', show_label = False),
                        statistics_group,
                        )
                    ),
                statusbar = [ StatusItem( name = 'error')],
                resizable = True,
#                title = 'Image collection'
                )

class Images(Image):
    """
    Image collection, defines next method which opens and returns next image in filenames list
    """
    files = Instance(Filenames,())
    
    filenames = DelegatesTo('files')
    filename = DelegatesTo('files')
    directory = DelegatesTo('files')
    
    view = images_view 
                
                
    def next(self):
        try:
            self.filename = self.filenames[self.next_index]
            self.next_index += 1
        except IndexError:
            self.next_index = 0
            raise StopIteration
            
        return self.array
        
    def __len__(self):
        return len(self.filenames)
        
    def __iter__(self):
        self.next_index = 0
        return self
        
processor_view = View(
                    Group(
                        Group(
                            Item('files', 
                                 style = 'custom', 
                                 show_label = False),
                            label = 'Files', 
                            show_border = True
                            ),
                        Group(
                            '_',
                            Group(
                                Item('format', show_label = False, 
                                     style = 'custom', 
                                     height = 200), 
                                show_border = True, 
                                label = 'Image format'
                                ),
                            Item('reload', show_label = False),
#                            Item('save', show_label = False),
                            statistics_group,
                            ),
                        'do_process',
                        enabled_when = 'is_processing == False',
                        ),
                    statusbar = [ StatusItem( name = 'error')],
                    resizable = True,
#                    title = 'Image processor'
                    ) 

class BaseProcessor(Images):
    """
    Subclass this, you must define process function, see Converter
    """
    do_process = Button()
    is_processing = Bool(False,transient = True)
    
    view = processor_view    
                
    def _do_process_fired(self):
        def stop_process():
            progress.update(max_t)
            self.is_processing = False
            progress.close()  

        self.is_processing = True
        self.init()
        max_t = len(self.filenames)
        progress = ProgressDialog(title="progress", message="Processing... ", max=max_t, show_time=True, can_cancel=True)
        progress.open()
        try:
            for i ,image in enumerate(self):
                (cont, skip) = progress.update(i)
                self.process(image, i)
                if not cont or skip:
                    break                      
        except Exception as e:
            self.error = error_to_str(e)
            raise e
        finally:
            stop_process() 

        self.post_process()    
        
    def process_all(self):
        self.is_processing = True
        try:
            self.init()
            for i, image in enumerate(self):
                self.process(image, i)
            self.post_process() 
        finally:
            self.is_processing = False
                
    def process(self, image, index):
        pass
    
    def init(self):
        pass
        
    def post_process(self):
        pass

converter_view = View(
                    Group(
                        Group(
                            Group(
                                Item('files', 
                                     style = 'custom', 
                                     show_label = False),
                                label = 'Files', 
                                show_border = True
                                ),
                            Group(
                                '_',
                                Group(
                                    Item('format', show_label = False, 
                                         style = 'custom', 
                                         height = 200), 
                                    show_border = True, 
                                    label = 'Image format'
                                    ),
                                Item('reload', show_label = False),
#                                Item('save', show_label = False),
                                statistics_group,
                                ),
                            show_border = True, 
                            label = 'Input'                            
                            ),
                        Group(
                            'directory',
                            'extension',
                            'overwrite',
                            show_border = True, 
                            label = 'Output'
                            ),
                        'do_process',
                        enabled_when = 'is_processing == False',
                        ),
                    statusbar = [ StatusItem( name = 'error')],
                    resizable = True,
#                    title = 'Image converter'
                    ) 

class Converter(BaseProcessor):
    """
    """
    do_process = Button('convert')
    
    #output extension
    extension = Enum('.tiff',('.jpg','.tiff','.png','.bmp'), desc = 'output  format type', label = 'format')
    
    #output directory
    directory = Directory(os.path.abspath(os.path.curdir), desc = 'output folder name')

    overwrite = Bool(False)
    view = converter_view    
                
    def process(self, image, index):
        name = os.path.basename(self.filename)
        name, ext = os.path.splitext(name)
        path = os.path.join(self.directory, name + self.extension)
        if not os.path.exists(path) or self.overwrite:
            ExtFormat.save(path, image)
        else:
            raise IOError, 'File exists'         
    

if __name__ == '__main__':
    im = Image()
    im.configure_traits()
    im = Images()
    im.configure_traits()  
    im = BaseProcessor()
    im.configure_traits()    
    im = Converter()
    im.configure_traits('conv')
