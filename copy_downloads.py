"""Copies download data to downloads directory 
"""
import shutil, glob, os

files = glob.glob('dist/*.*')
PATH = os.path.join('doc','build','html','_downloads')
try:
    os.mkdir(PATH)
except:
    pass
def copy(fname):
    out = os.path.join(PATH,os.path.basename(fname))
    print 'Copying %s to %s' % (fname, out)
    shutil.copy(fname, out)    

for fname in files:
    copy(fname)

pdf = os.path.join('doc','build','latex', 'Labtools.pdf')

try:
    copy(pdf)
except IOError:
    print 'Labtools.pdf does not exist!'
    raise
