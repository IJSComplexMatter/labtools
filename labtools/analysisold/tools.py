"""
Here is a collection of tools for data analysis.

* :class:`Filenames` which is a glob interface, and filenames list holder
  for easy filenames list retrieval, with sorting possibilities. Use :meth:`filenames_from_list` 
  and :meth:`filenames_from_directory` functions for Filenames generation
* :class:`BaseFileAnalyzer` which is a base classs for creating gui interface for: 
  "for fname in files: do_something(fname)" stuff. This is done through
  :meth:`BaseFileAnalyzer.process_selected` method.
  
example of :class:`Filenames` usage:

>>> files = filenames_from_list(['bla.txt', 'bla.txt']) #specify filenames list
>>> files = filenames_from_directory('testdata', pattern = '*.txt') #or read from directory

Actual files are sorted and storred in a list:
    
>>> actual_filenames = files.filenames 

You can do:
    
>>> for fname in files: pass #iteration is possible

but this increases :attr:`Filenames.index` each time and sets selected filename to 
:attr:`Filenames.selected`. 
So if you want to do iteration again, you have to reset it

>>> files.index = 0 
>>> fname = files[0] #indexisng also works

example of :class:`BaseFileAnalyzer` usage:
    
>>> class FileAnalyzer(BaseFileAnalyzer):
...     def init(self):
...         self.index = 0
...         self.results = []
...         return True    
...     def process_selected(self):
...         result = self.selected.split('.')[1]
...         self.results.append(result)
...     def finish(self):
...         return self.results
...
>>> a = FileAnalyzer(filenames = files)
>>> a.process_all() == ['txt','txt','txt']
True
>>> for result in a: pass #this calls proces_file method, without init, process_result and finish

again, you have to reset index if you want to do processing again

>>> a.index = 0
"""

from enthought.traits.api import HasTraits, DelegatesTo, \
     Property,Str, List,  Instance,  Bool, \
     Button, on_trait_change, Directory,  Int, Event, File
     
from enthought.traits.ui.api import View, Item, \
     Group,  ListStrEditor, ListEditor, FileEditor

from labtools.utils.processing import ProcessingQueue

import os
import glob
import re

from labtools.log import create_logger
log = create_logger(__name__)

def _error_to_str(e):
    """Converts error to a nice string
    """
    #return str(sys.exc_info()[1])
    return e.__class__.__name__ + ' ' + str(e)
    #return e.__class__.__name__ + ' ' + ','.join(map(str,e.args))

def _my_comp (x,y):
    """
    Za sortiranje po cifrah v datoteki
    """
    import scipy
    def getNum(str):
        try:
            return float(re.findall(r'\d+',str)[-1])
        except:
            return 1.
            
    return cmp(getNum(x),getNum(y)) 
     
filenames_view = View(
                    Group(
                        
                        #Item('directory', style = 'simple'),
                        #Item('pattern', style = 'simple'),
                        Item('filenames',style = 'custom',
                             editor = ListStrEditor(selected = 'selected',
                                                    operations = ['insert','edit','move','delete','append'],
                                                    auto_add = True,
                                                    drag_move = True),
                             height = -100,
                             width = -300),
                       
                        Item('is_reversed', style = 'simple'), ),
Item('from_directory_bttn', show_label = False),
#                    statusbar = [ StatusItem( name = 'error')],
                    resizable = True,
                    )        

def filenames_from_list(filenames):
    """A helper function. Returns a :class:`Filenames` object from a given filenames list
    
    :param list filenames:
        List of filenames
    :returns:
        :class:`Filenames`
    """
    f = Filenames()
    f.from_list(filenames)
    return f

def filenames_from_directory(directory = os.path.abspath(os.path.curdir), pattern = '*.*'):
    """A helper function. Returns a :class:`Filenames` object from a given directory and pattern
    
    :param str directory:
        Directory where files are searched, default is os.path.curdir
    :param str pattern:
        A search pattern "*.*" by default
    :returns:
        :class:`Filenames`
    """
    f = Filenames()
    f.from_directory(directory, pattern)
    return f

class SearchPattern(HasTraits):
    """Search pattern collector.. For use with :class:`Filenames`
    """
    #: directory that is used to search
    directory = Directory(os.path.abspath(os.path.curdir),
                          desc = 'directory of files to be processed',)
                        #auto_set = False, enter_set = True)
    #: a search pattern str  
    pattern = Str('*.*',
                  desc = 'pattern of files, for instance "*.bin"',)
                  #auto_set = False, enter_set = True)    

class Filenames(HasTraits):
    """
    Glob interface with nice GUI view. When using GUI, the selected file is storred
    in :attr:`selected` and the actual filenames list is storred in
    :attr:`filenames`, but yu can get :attr:`basenames` instead    
    
    >>> files = Filenames() 
    >>> files.from_directory('testdata', pattern = '*.txt') 
    >>> files.is_reversed = True
    >>> files.basenames == ['text10.txt','text2.txt','text1.txt']
    True
    
    You can then use it like an iterator. At each step :attr:`selected` is updated:
        
    >>> for i, f in enumerate(files): 
    ...     f == files.selected and i == files.index
    True
    True
    True
    
    You can also index it. Here also :attr:`selected` is updated:
        
    >>> os.path.basename(files[1]) == 'text2.txt'
    True
    >>> files[1] == files.selected
    True
    """
    #: index of selected filename
    index = Property(Int, depends_on = 'selected')
    
    #: selected filename str
    selected = Str()
    
    #: search pattern instance of :class:`SearchPattern`
    search_pattern = Instance(SearchPattern,())
                  
    #: bool whether list is reversed or not              
    is_reversed = Bool(False)
    
    #: actual filenmaes list
    filenames = List(File)
    
    #: basenames list
    basenames = Property(depends_on = 'filenames')
    
    #: this event is called when filenames are updated
    updated = Event
    
    from_directory_bttn = Button('Search in directory')
    
    view = filenames_view
    
    def _from_directory_bttn_fired(self):
        if self.search_pattern.edit_traits(kind = 'modal').result:
            self.from_directory(self.search_pattern.directory, self.search_pattern.pattern)
    
    def from_directory(self, directory = os.path.abspath(os.path.curdir), pattern = '*.*'):
        """Fills list of files from a given directory and a pattern string
        """
        self.search_pattern.directory = directory
        self.search_pattern.pattern = pattern
        filenames = glob.glob(os.path.join(directory, pattern))
        self._set_filenames_(filenames)
        
    def from_file(self,fname, directory = '.'):
        """Reads a file and files filenames from 
        """
        pass
    
    def from_list(self, filenames, sort = False):
        """Sets filenames from a given list  and sorts them if specified
        """
        self._set_filenames_(filenames, sort = sort)

    def _set_filenames_(self, filenames, sort = True):
        if sort == True:
            filenames = sorted(filenames)
            filenames.sort(_my_comp)       
        if self.is_reversed:
            filenames.reverse()
        self.filenames = filenames           
        
        
    def _is_reversed_changed(self):
        self.filenames.reverse()
        
    @on_trait_change('filenames,filenames[]')
    def _filenames_chang(self, value):
        try:
            self.selected = value[0]
            self.updated = True
        except IndexError:
            pass

    def _filenames_default(self):
        return ['']
       
    def _get_index(self):
        return self.filenames.index(self.selected)   
        
    def _set_index(self, value):
        self.selected = self.filenames[value]
        
    def _get_basenames(self):
        return list(map(os.path.basename, self.filenames))
      
    def __getitem__(self, item):
        self.index = item
        return self.selected
        
    def __len__(self):
        return len(self.filenames)
        
    def __iter__(self):
        self._index = self.index
        return self
        
    def __next__(self):
        try:
            self.index = self._index
            return self.selected
        except:
            raise StopIteration
        finally:
            self._index += 1
            
file_analyzer_group = Group(
                Item('filenames',show_label = False, style = 'custom'),
                '_',
                Item('process_selected_btn',show_label = False),
                Item('process_all_btn',show_label = False),
                )

class BaseFileAnalyzer(HasTraits):
    """A file analyzer. It defines a process method which cals 
    process_file method, that should be defined in a subclass
    """
    #: Filenames instance
    filenames = Instance(Filenames,())
    #: selected filename
    selected = DelegatesTo('filenames')
    #: index of selected filename
    index = DelegatesTo('filenames')
    queue = Instance(ProcessingQueue)

    process_all_btn = Button('Process all')
    process_selected_btn = Button('Process selected')
    
    view = View(file_analyzer_group, resizable = True)
    
    def _queue_default(self):
        return ProcessingQueue(continuous_run = False)
        
    def init(self):
        """Initialization is called first when process_all is called
        Must return True if OK to process. See: :meth:`process` source
        """
        return True
    
    @on_trait_change('process_all_btn')      
    def process_all(self):
        """Process all files listed in :attr:`filenames`
        """
        if self.init():
            log.info('processing:\n '+ str(self.filenames.filenames))
            for result in self:
                pass
            return self.finish()    

    def _process_selected_btn_fired(self):
        self.process_selected()
        
    def process_selected(self):
        """Process selected file
        """
        return 1
        
    def finish(self):
        """Called when processing is finished. See: :meth:`process` source
        """
        return True
      
    def __getitem__(self, item):
        self.filenames.index = item
        return self.process_selected()
        
    def __len__(self):
        return len(self.filenames)    
        
    def __iter__(self):
        self._index = self.index
        return self
        
    def __next__(self):
        try:
            self.index = self._index
            return self.process_selected()
        except:
            raise StopIteration
        finally:
            self._index += 1

            

#images_view = View(
#                Group(
#                    Group(Item('files', style = 'custom', show_label = False),
#                        label = 'Files', show_border = True),
#                    Group('_',
#                        Group(
#                            Item('format', show_label = False, 
#                                 style = 'custom', 
#                                 height = 200), 
#                            show_border = True, 
#                            label = 'Image format'
#                            ),
#                        Item('reload', show_label = False),
#                        Item('save', show_label = False),
#                        statistics_group,
#                        )
#                    ),
#                statusbar = [ StatusItem( name = 'error')],
#                resizable = True,
##                title = 'Image collection'
#                )

#class Images(Image):
#    """
#    Image collection, defines next method which opens and returns next image in filenames list
#    """
#    files = Instance(Filenames,())
#    
#    filenames = DelegatesTo('files')
#    filename = DelegatesTo('files')
#    directory = DelegatesTo('files')
#    
#    view = images_view 
#                
#                
#    def next(self):
#        try:
#            self.filename = self.filenames[self.next_index]
#            self.next_index += 1
#        except IndexError:
#            self.next_index = 0
#            raise StopIteration
#            
#        return self.array
#        
#    def __len__(self):
#        return len(self.filenames)
#        
#    def __iter__(self):
#        self.next_index = 0
#        return self
        
#processor_view = View(
#                    Group(
#                        Group(
#                            Item('files', 
#                                 style = 'custom', 
#                                 show_label = False),
#                            label = 'Files', 
#                            show_border = True
#                            ),
#                        Group(
#                            '_',
#                            Group(
#                                Item('format', show_label = False, 
#                                     style = 'custom', 
#                                     height = 200), 
#                                show_border = True, 
#                                label = 'Image format'
#                                ),
#                            Item('reload', show_label = False),
##                            Item('save', show_label = False),
#                            statistics_group,
#                            ),
#                        'do_process',
#                        enabled_when = 'is_processing == False',
#                        ),
#                    statusbar = [ StatusItem( name = 'error')],
#                    resizable = True,
##                    title = 'Image processor'
#                    ) 

#class BaseProcessor(Filenames):
#    """
#    Subclass this, you must define process function, see Converter
#    """
#    do_process = Button()
#    is_processing = Bool(False,transient = True)
#    
#    view = processor_view    
#                
#    def _do_process_fired(self):
#        def stop_process():
#            progress.update(max_t)
#            self.is_processing = False
#            progress.close()  
#
#        self.is_processing = True
#        self.init()
#        max_t = len(self.filenames)
#        progress = ProgressDialog(title="progress", message="Processing... ", max=max_t, show_time=True, can_cancel=True)
#        progress.open()
#        try:
#            for i ,image in enumerate(self):
#                (cont, skip) = progress.update(i)
#                self.process(image, i)
#                if not cont or skip:
#                    break                      
#        except Exception as e:
#            self.error = error_to_str(e)
#            raise e
#        finally:
#            stop_process() 
#
#        self.post_process()    
#        
#    def process_all(self):
#        self.is_processing = True
#        try:
#            self.init()
#            for i, image in enumerate(self):
#                self.process(image, i)
#            self.post_process() 
#        finally:
#            self.is_processing = False
#                
#    def process(self, image, index):
#        pass
#    
#    def init(self):
#        pass
#        
#    def post_process(self):
#        pass
#
#converter_view = View(
#                    Group(
#                        Group(
#                            Group(
#                                Item('files', 
#                                     style = 'custom', 
#                                     show_label = False),
#                                label = 'Files', 
#                                show_border = True
#                                ),
#                            Group(
#                                '_',
#                                Group(
#                                    Item('format', show_label = False, 
#                                         style = 'custom', 
#                                         height = 200), 
#                                    show_border = True, 
#                                    label = 'Image format'
#                                    ),
#                                Item('reload', show_label = False),
##                                Item('save', show_label = False),
#                                statistics_group,
#                                ),
#                            show_border = True, 
#                            label = 'Input'                            
#                            ),
#                        Group(
#                            'directory',
#                            'extension',
#                            'overwrite',
#                            show_border = True, 
#                            label = 'Output'
#                            ),
#                        'do_process',
#                        enabled_when = 'is_processing == False',
#                        ),
#                    statusbar = [ StatusItem( name = 'error')],
#                    resizable = True,
##                    title = 'Image converter'
#                    ) 

#class Converter(BaseProcessor):
#    """
#    """
#    do_process = Button('convert')
#    
#    #output extension
#    extension = Enum('.tiff',('.jpg','.tiff','.png','.bmp'), desc = 'output  format type', label = 'format')
#    
#    #output directory
#    directory = Directory(os.path.abspath(os.path.curdir), desc = 'output folder name')
#
#    overwrite = Bool(False)
#    view = converter_view    
#                
#    def process(self, image, index):
#        name = os.path.basename(self.filename)
#        name, ext = os.path.splitext(name)
#        path = os.path.join(self.directory, name + self.extension)
#        if not os.path.exists(path) or self.overwrite:
#            ExtFormat.save(path, image)
#        else:
#            raise IOError, 'File exists'         
    

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    f = Filenames()
    f.configure_traits()
    f = BaseFileAnalyzer()
    f.configure_traits()
#    im = Image()
#    im.configure_traits()
#    im = Images()
#    im.configure_traits()  
#    im = BaseProcessor()
#    im.configure_traits()    
#    im = Converter()
#    im.configure_traits('conv')
