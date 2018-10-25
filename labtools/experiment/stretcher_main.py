"""
.. module:: stretcher_main
   :synopsis: Main command line program for stress-strain measurements

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This  module defines a main function, which can be used a a stand-alone 
command line progrqm to obtain stree-strain data.
"""

DESCRIPTION = \
"""
This program measures stress-strain data based on the stretching parameters.
The translator is moved in steps, and after each step force is measured.
At the end, translator is moved to the starting position. Results are 
displayed and saved to text file.
"""

import argparse

parser = argparse.ArgumentParser(description = DESCRIPTION)

parser.add_argument('steps', help = 'how many steps to make', 
                    type = int)
parser.add_argument('delta', help = 'translator step size in mm', 
                    type = float)
parser.add_argument('-x',  help = 'translator start position in mm (default = 0.0)' , 
                    type = float, default = 0.)
parser.add_argument('-p', help = 'sleep time in seconds after each move (default = 1.0)', 
                    type = float, default = 1., dest = 'pause')
parser.add_argument('-n',  help = 'number of force measurements to perform (default = 1)' , 
                    type = int, default = 1)
parser.add_argument('-i', help = 'interval (in seconds) at which measurements are performed if n > 1 (default = 1.0)', 
                    type = float, default = 1.)  
parser.add_argument('--ion',help = 'display results continuously', 
                    action = 'store_true')                    
parser.add_argument('--noshow', help = 'do not show results when finished', 
                    action = 'store_true' )  
parser.add_argument('--abs', help = 'defines absolute movements (relative by default)', 
                    action = 'store_true' )  
parser.add_argument('-o', help = 'measured data output filename (default = results.dat)', 
                    type = str, default = 'results.dat', dest = 'output')  
parser.add_argument('-f', '--force', help = 'force overwriting data', 
                    action = 'store_true')   
              
def main():
    """Main program. It parses arguments, runs measurements and saves
    and displays results
    """
    args = parser.parse_args()
    positions = [args.x + i*args.delta for i in range(args.steps)] 
    ion = not args.noshow and args.ion
    
    import os,sys
    if os.path.exists(args.output) and not args.force:
        parser.error('File "%s" exists! Use "-f" option to overwrite.' % args.output)
    if args.abs:
        print 'Translator will move from %f to %f in %i steps (absolute)' % (positions[0], positions[-1], args.steps)
    else:
        print 'Translator will move from %f to %f in %i steps (relative)' % (positions[0], positions[-1], args.steps)
    if raw_input('OK? (default: yes) ').lower() not in ('yes','y','ok',''):
        sys.exit(2)
    from stress_strain import measure, display, save

    data = measure(positions = positions, sleep = args.pause,  n = args.n, interval = args.i, ion = ion, relative = not args.abs)
   
    save(args.output, data) #save results       
    if args.noshow == False:
        display(data)



if __name__ == '__main__':
    main()
