"""
.. module:: main
   :synopsis: Labtools command line programs

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This module defines functions for command line programs
"""


def pi_main():
    """PI command line program
    """
    from argparse import ArgumentParser
    parser = ArgumentParser()
    
    parser.add_argument("-p", "--port", help="Serial port (COM1, ...)", default = None, type = str)
    parser.add_argument('-s', '--step',  help="Motor step size", default = None, type = float)
    parser.add_argument("-c", "--controller", help="Controller ID", dest = 'device', default = 0, type = int)
    parser.add_argument("-m", "--move" , help="Move to coordinate", type = float, default = None)   
    parser.add_argument("-r", "--relative" , help="Relative move by a given number of steps", action = 'store_true', default = False)
    parser.add_argument("-t", "--tell" , help="Reads current position", dest = 'tell',  action = 'store_true', default = False)
    parser.add_argument("-g", "--go_home" , help="Move to home position", dest = 'home',  action = 'store_true', default = False)
    parser.add_argument("-d", "--define_home" , help="Defines current position as home position", dest = 'define',  action = 'store_true', default = False)
    parser.add_argument("-w", "--write" , help="Write raw string to controller, see PI manual for possible commands", dest = 'write', default = '', type = str)
    parser.add_argument( "--reversed" , help="Reversed motor rotation", dest = 'reversed', action = 'store_true', default = False)
        
    options = parser.parse_args()

    from labtools.pi.mercury import main
    status = main(options)
    if status == 2:
        parser.error("No commands given!")
    elif status == -1:    
        parser.exit(status, 'Unknown error!')
    else:
        parser.exit(status)
        
