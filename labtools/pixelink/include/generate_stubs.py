#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Generator script building the ctypes wrapper for the libraw.so.'''

import os
import re
import logging

import glob, time

#-------defines
HEADER_PATH = ''
from ctypes.util import find_library

LIBRARY= find_library('PxLAPI40')
print(LIBRARY)
from ctypeslib import h2xml, xml2py
time.sleep(2)
LIBRARY_PATH, LIBRARY_NAME = os.path.split(LIBRARY)
INCLUDE_PATH = '' #header filesfor parsing  are put here
HEADER = 'PixeLINKApi.h'
#HEADER_CONSTANTS = 'libraw_const.h'
SYMBOLS = ['PxL'] #katere simbole naj se dodatno vkljuci

#----end defines

#all paths must be absolute,so i force that here
INCLUDE_PATH = os.path.abspath(INCLUDE_PATH)

GENERATOR_PATCH = """
#---------------- patch start
# also replaced "%s" with "%s" where found

from _setup import *
import _setup

_libraries = {}
_libraries['%s'] = _setup._init()

STRING = c_char_p

#---------------- patch end
"""  % (LIBRARY,LIBRARY_NAME,LIBRARY_NAME)

#def clean_headers():
#    """Cleans header files of __cplusplus syntax so that h2xml.py works"""
#    try:
#        os.mkdir(INCLUDE_PATH)
#    except:
#        pass
#    headers = glob.glob(os.path.join(HEADER_PATH,'*.h'))
#    logging.info('Cleaning header %s' % headers)  
#    for header_name in headers:
#        cleaned_header_name = os.path.join(INCLUDE_PATH,os.path.split(header_name)[1])   
#
#        
#        with open(header_name) as fr:
#            
#            with open(cleaned_header_name,'w') as fw:
#                level = 0
#                cut_level = -1
#                write_line = True
#                for line in fr:
#                    splitted = line.split()
#                    try:
#                        if splitted[0].startswith('#if'):  
#                            level += 1
#                            if splitted[1] == '__cplusplus':
#                                cut_level = level-1
#                                if splitted[0]== '#ifndef':
#                                    write_line = True
#                                    line = '\n'
#                                else:
#                                    write_line = False
#                                    
#                        elif splitted[0].startswith('#else'):
#                            if level == (cut_level + 1) and write_line == True:
#                                write_line = False
#                            
#                        elif splitted[0].startswith('#endif'):
#                            level -= 1
#                    except IndexError:
#                        pass
#                    if level == cut_level:
#                        cut_level = -1
#                        line = '\n'
#                        write_line = True
#                    if write_line:
#                        fw.write(line)
#                    else:
#                        fw.write('\n')

def exported_constants():
    finder = re.compile(r'^enum ([a-zA-Z0-9_]+)')
    #header_path = os.path.join(INCLUDE_PATH, HEADER_CONSTANTS)
    header_path = os.path.join(INCLUDE_PATH, HEADER)
    fd = open(header_path)
    content = fd.readlines()
    fd.close()
    exported = [finder.search(x).group(1) for x in content if finder.search(x)]
    exported.sort(reverse = True) 
    logging.info('Found %d constants to export for wrapping.' % len(exported))
    return exported

def exported_functions():
    finder = re.compile(r'^DllDef\s+.*?\s+\*?([a-zA-Z0-9_]+)\(')
    header_path = os.path.join(INCLUDE_PATH, HEADER)
    fd = open(header_path)
    content = fd.readlines()
    fd.close()
    exported = [finder.search(x).group(1) for x in content if finder.search(x)]
    exported.sort(reverse = True) ## kljucnega pomena, drugace xml2py v dolocenih primerih spusti funkcije ki imajo isto zacetnico
    logging.info('Found %d functions to export for wrapping.' % len(exported))
        
    return exported
        

def patch_module():
    header_basename = os.path.splitext(HEADER)[0].split('-')[0]
    module_name = '_%s.py' % header_basename
    module_path = os.path.join('generated', module_name)
    logging.info('Patching module %s.' % module_path)
    fd = open(module_path)
    lines = fd.readlines()

    for i, line in enumerate(lines):
	lines[i] = line.replace(LIBRARY, LIBRARY_NAME)
    fd.close()
    fd = open(module_path, 'w')
    fd.write(lines[0])
    fd.write('#' + '#'.join(lines[1:6]))
    fd.write(GENERATOR_PATCH)
    fd.writelines(lines[6:])
    fd.close()
    

def parse_header():
    logging.info('Parsing HEADER file %s.' % HEADER)
    header_path = os.path.join(INCLUDE_PATH, HEADER)
    header_basename = os.path.splitext(HEADER)[0].split('-')[0]
    argv = ['h2xml.py',
            header_path, '-k','-c',
            '-o', '%s.xml' % header_basename]
    h2xml.main(argv)

    
def generate_code():
    header_basename = os.path.splitext(HEADER)[0].split('-')[0]
    symbols=[]
    symbols = exported_functions()
    symbols.extend(SYMBOLS)
    symbols.extend(exported_constants())
    symbols_expressions = '|'.join(symbols)
    module_name = '_%s.py' % header_basename
    module_path = os.path.join('generated', module_name)
    logging.info('Generating code for module %s.' % module_path)
    argv = ['xml2py.py','-v','-d',
            '-kdfste',
            '-l%s' % LIBRARY, 
            '-o', module_path,
            '-r%s' % symbols_expressions,
            '%s.xml' % header_basename]
    print('xml2py',argv,'\n\n')
    xml2py.main(argv)
    print('\ndone\n')

def main():
    #clean_headers()
    parse_header()
    #generate_code()
    #patch_module()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s\t%(message)s')
    main()
    logging.info('Code generation done.')
