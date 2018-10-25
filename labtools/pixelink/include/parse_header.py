import os, re

OUTPUT = os.path.join('_PixeLINKTypes.py')
OUTPUT = os.path.abspath(OUTPUT)

PATH = 'PixeLINKTypes.h'

TYPEDEF_STRUCT = '(typedef\s+?struct\s*?\w*?\s*)\{(.*?)\}([\s\w*]+?),?([\s\w*]*?);'
TYPES_RE = re.compile('%s' % (TYPEDEF_STRUCT,),re.DOTALL)

VECTYPE = '(\w+[\s*]*)\s*\[([0-9\s]*?)\]'                                       
VECTYPE_RE = re.compile(VECTYPE,re.DOTALL)

FUNCT = '(^DWORD\s+|^void\s+)(USMC_.+?)\((.*?)\)\s*;'
FUNCT_RE = re.compile(FUNCT,re.MULTILINE)
  
ITEMS = r'(\w+[ \t*]*)[ \t]*([\w,\[\] \t]*?);(.*)'                                            
ITEMS_RE = re.compile(ITEMS)

FUNCT_ITEM = r'(\s*\w+[ \t*]*)[ \t]*([\w\[\] \t]+)'   
FUNCT_ITEM_RE = re.compile(FUNCT_ITEM)

HEADER = """
\"\"\"This file was generated automatically from %s header file. Should not be changed manually...
It defines all structures needed, and sets arguments and return values of all functions, to prevent user errors
\"\"\"

from ctypes import *

#---------------------------------
#   ctypes declarations start here
#---------------------------------

"""

INNER = """
from ctypes.util import find_library
from .conf import USMCDLL, SIMULATE
import warnings

USMC_WARNING = ''
USMC_LOADED = True

if SIMULATE  == True:
    from ._test import usmcdll as lib
else:
    if USMCDLL == 'default':
        USMCDLL = find_library('USMCDLL')
    if USMCDLL is None:
        USMC_LOADED = False
        USMC_WARNING = "'USMCDLL.dll not found in your system. Please install the driver  or set the path in conf.py'"
        warnings.warn(USMC_WARNING)
        class lib: pass
    else:
        lib = cdll.LoadLibrary(USMCDLL)

try:
"""

INNER = ""

#ctypes types.. for automatic conversion of c to ctypes
CTYPES = {
'float' :'c_float',
'int' : 'c_int',
'char': 'c_char',
'BOOL' : 'c_int',
'BYTE' : 'c_ubyte',
'DWORD' : 'c_uint32',
'WORD' : 'c_uint16',
'char**' : 'POINTER(c_char_p)',
'void' : None,
'char*' : 'c_char_p',
'size_t': 'c_size_t',
'float*' : 'POINTER(c_float)',

'U32': 'c_uint32',
'U16' : 'c_uint16',
'U8' : 'c_uint8',

'S32' : 'c_int32', 
'S16' : 'c_int16',
'S8' : 'c_int8',

'F32' : 'c_float',

'PXL_RETURN_CODE' : 'c_int',
}

STRUCT = """
class %(structure)s(Structure):
    _fields_ = [%(fields)s]
"""

FUNCTION = """
    lib.%(name)s.restype = %(restype)s
    lib.%(name)s.argtypes = [%(argtype)s]
    %(name)s = lib.%(name)s
"""

FIELD = '(%s, %s)'  
              
def parse_items(string):
    r"""Takes a string and finds all c-declarations, returns a list of (type, name) pairs
   
    >>> parse_items(' int  var1 ;\t// comment\n\tint var2;')
    [('int', 'var1'), ('int', 'var2')]
    >>> parse_items(' float * var1 [34], var2[23] ;')
    [('float*', 'var1 [34]'), ('float*', 'var2[23]')]
    >>> parse_items(' float * var1 [34], var2[23] ; \\ asddsf \n \\ asdafd\n \\ asd - Step asdfas  \n int var;')
    [('float*', 'var1 [34]'), ('float*', 'var2[23]'), ('int', 'var')]
    
    """
    items = []
    ms = re.finditer(ITEMS_RE, string)
    for i,m in enumerate(ms):
        typ, item = m.group(1,2)
        #print i, m.group(1,2)
        for i in item.split(','):
            items.append((''.join(typ.split()), i.strip()))
    return items

def parse_funct_items(string):
    r"""Takes a string and finds all c-declarations, returns a list of (type, name) pairs
   
    >>> parse_funct_items(' int  var1 , int var2')
    [('int', 'var1'), ('int', 'var2')]
    """
    items = []
    for i,s in enumerate(string.split(',')):
        m = FUNCT_ITEM_RE.match(s)
        typ, item = m.group(1,2)
        items.append((''.join(typ.split()), item.strip()))
    return items
  
def process_item(item):
    """Takes an item from a list returned by parse_items and converts it to ctypes definition
    
    >>> process_item(('float', 'par1'))
    ("'par1'", 'c_float')
    >>> process_item(('char**', 'par2'))
    ("'par2'", 'POINTER(c_char_p)')
    >>> process_item(('float', 'par[2]'))
    ("'par'", 'c_float * 2')
    """
    typ, name = item
    m = re.match(VECTYPE_RE, name)
    try:
        if m is not None: 
            name, i = m.group(1,2)
            return "'%s'" % name, CTYPES[typ] + ' * %i' % int(i)
        else:
            return "'%s'" % name, CTYPES[typ]
    except KeyError:
        raise Exception('Unknown name: %s type: %s' % (name, typ))
  
  
def process_items(items, structname):
    fields = ''
    structname = structname.strip()
    for i, item in enumerate(items):
        if i>0:
            fields += ',\n' + ' '*16 #add new line before every new element
        nametyp = process_item(item)
        fields += FIELD % nametyp
    CTYPES[structname+'*'] = 'POINTER(%s)' % structname #add new struct typec to CTYPES definitions
    return STRUCT % {'structure' : structname, 
                    'fields' : fields}

def process_funct_items(name, restype,arguments):
    args = ''
    restype = restype.strip()
    for i, item in enumerate(arguments):
        if i>0:
            args += ','
        nametyp = process_item(item)[1]
        if nametyp == None:
            args = '' #if None it is void.. no arguments
        else:
            args += nametyp
    return FUNCTION % {'name' : name,
                      'argtype' : args, 
                      'restype' : CTYPES[restype]}
def create_definition(string):
    with open(OUTPUT,'w') as f:
        f.write(HEADER)
        structures = TYPES_RE.findall(string)
        print(structures)
        for structure in structures:
            structdef, definition, name, extra = structure
            items = parse_items(definition)
            struct=process_items(items, name)
            f.write(struct)
        f.write(INNER)

        m = FUNCT_RE.findall(string)  
        for fun in m:
            out, name, definition = fun
            items = parse_funct_items(definition)
            funct=process_funct_items(name, out, items)
            f.write(funct)
        f.write('\nexcept AttributeError:\n    pass')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    with open(PATH) as f:
        data = f.read()
        create_definition(data)
