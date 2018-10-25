"""
.. module:: mercury
   :synopsis: PI mercury controller

.. moduleauthor:: Andrej Petelin <andrej.petelin@gmail.com>

This is a program for PI motion controller manipulation. It also defines a command line 
interface

.. seealso::
    
    Module :mod:`.translator` is a more user-friendly PI translator controller
    
"""

import time
from serial import Serial

class PIError(Exception):
    """
    Exception raised by Controller
    """
    pass

def set_value(f):
    """For TMCM310Axis.. value check
    """
    def _set_value(self, value, *args,**kw):
        if self.is_reversed:
            value = -value
        else:
            value = value
        return f(self, value, *args,**kw)
    return _set_value
    
def get_value(f):
    """For TMCM310Axis.. value check
    """
    def _get_value(self, *args, **kw):
        value = f(self, *args, **kw)
        if self.is_reversed:
            try:
                value = -value
            except:
                pass    
        return value
    return _get_value     


class PIController(object):
    """All PI controllers should be a subclass of this... for type checking.
    Currently only :class:`Controller862` is defined
    """
    pass

class Controller862(PIController):
    """
    Controller for various type of PI translators, mikes, rotators.
    
    Examples
    --------

    >>> s = Serial(port = 0)
    >>> c = Controller862(s, ID = 0) 
    >>> c.write('MR1000') #move relative 1000 
    >>> c.ask('TP') #tell position 
    'P:+0000001000' 
    >>> c.tell_position(as_string = True) #tell position 
    'P:+0000001000' 
    >>> c.tell_position() #tell position 
    1000
    >>> s.close()
    """
    
    def __init__(self, serial, ID = None, is_reversed = False,):
        if ID not in [None] + range(16):
            raise PIError, 'Invalid controller ID'
        self.serial = serial
        self.ID = ID
        self.is_reversed = is_reversed

    @staticmethod        
    def scan_axes(serial):
        """
        Searches for all controllers connected to serial, returns a list if IDs
        """
        controllers = range(16)
        out = []
        serial.flushInput()
        for controller in controllers:
            command = Controller862._set_command('TB', controller)
            line = serial.ask(command)
            if line:
                out.append(controller)
        return out       

    def select_axis(self, ID):
        """
        Selects controller raises PIError if not available
        """
        self.ID = ID
        line = self.ask('TP')
        if not line:
            self.ID = None
            raise PIError, "Controller '%s' not found" % str(ID)


    def _set_command(self,command, ID):
        """
        Internal, returns command if a valid controller, else PIError
        If len(command) != 1 then adds \r at the end, signle char commands do not have \r, according to the manual 
        """
        def appendCR(command):
            if len(command) != 1:
                command += '\r'
            return command
        command = appendCR(command)
        try:
            return '\x01' + hex(ID)[-1] + command
        except TypeError:
            return command
 

    def wait(self, display = None):
        """
        Waits until motor is moving if display is given, it should be a function that displays the result
        """
        pos1 = self.tell_position()
        while True:
            if display is not None:
                display(pos1)
            else:
                print pos1            
            time.sleep(0.1)
            pos2 = self.tell_position()
            if pos2 == pos1:
                break
            else:
                pos1 = pos2
        self.abort()
            
    def ask(self,command, ID = None):
        """
        Writes commands to PI controller, returns answer or '' if no answer        
        If len(command) == 1, assume single letter comand, else append '\r'
        """
        self.write(command, ID)
        c = None
        s = ''
        while c not in ('\x03' , ''):
            c = self.serial.read()
            s+= c
        return s.strip('\r\n\x03')


    def write(self,command, ID = None):
        """
        Writes commands to PI controller, no return
        If len(command) == 1, assume single letter comand, else append '\r'
        """
        if not ID:
            ID = self.ID
        command = self._set_command(command, ID) 
        self.serial.write(command)

    
    @get_value
    def tell_position(self , ID = None, as_string = False):
        """
        Return current PI position, if as_string == True, return as string
        """
        pos = self.ask("'", ID).strip().split()[-1].strip() #make sure to take last line
        try:
            if as_string:
                return pos
            else:
                return int(pos[2:])
        except:
            raise
            return None

    def tell_status(self, ID = None):
        """
        Return current PI position
        """      
        status = self.ask("%", ID).strip().split()[-1].strip()
        try:
            return status[2:]
        except:
            return None   
    
    def define_home(self, ID = None):
        """
        Writes current position as home position
        """
        self.write('!,DH,MF', ID)

    def go_home(self, ID = None):
        """
        Moves to home position
        """
        self.write('!,GH,WS0,MF', ID)
        
    @set_value
    def move_relative(self,steps, ID = None):
        """
        Move relative from current position
        """
        self.write('!,MR%i,WS0,MF' % steps, ID)
        
    @set_value
    def move_absolute(self,position, ID = None):
        """
        Move absolute from home position
        """     
        self.write('!,MA%i,WS0,MF' % position, ID)
        
    def set_acceleration(self, value, ID = None):
        """Sets acceleration
        """
        self.write('SA%i' % value, ID)
    
    def set_velocity(self, value, ID = None):
        """Sets velocity
        """
        self.write('SV%i' % value, ID)
        
    def tell_acceleration(self, ID = None, as_string = False):
        """
        Return current PI position
        """      
        acceleration = self.ask("TL", ID).strip().split()[-1].strip() #make sure to take last line
        try:
            if as_string:
                return acceleration
            else:
                return int(acceleration[2:])
        except:
            return None     
            
    def tell_velocity(self, ID = None, as_string = False):
        """
        Return current PI position
        """      
        velocity = self.ask("TY", ID).strip().split()[-1].strip() #make sure to take last line
        try:
            if as_string:
                return velocity
            else:
                return int(velocity[2:])
        except:
            return None     
            
    def abort(self, ID = None):
        """
        abort move
        """
        self.write('!,MF', ID)
        
    def __del__(self):
        try:
            self.abort()
        except:
            pass

def main():
    """Command line program
    """
    from argparse import ArgumentParser
    import sys
    parser = ArgumentParser()
    
    parser.add_argument("-p", "--port", help="Serial port number, default 0", default = 0, type = int)
    parser.add_argument("-c", "--controller", help="Controller ID, default 0", dest = 'ID', default = 0, type = int)

    parser.add_argument("-a", "--absolute_move" , help="Move to absolute coordinate", dest = 'position', type = int, default = None)   
    parser.add_argument("-r", "--relative_move" , help="Relative move by a given number of steps", dest = 'move', type = int, default = None)
    parser.add_argument("-t", "--tell" , help="Reads current position", dest = 'tell',  action = 'store_true', default = False)
    parser.add_argument("-g", "--go_home" , help="Move to home position", dest = 'home',  action = 'store_true', default = False)
    parser.add_argument("-d", "--define_home" , help="Defines current position as home position", dest = 'define',  action = 'store_true', default = False)
    parser.add_argument("-w", "--write" , help="Write raw string to controller, see PI manual for possible commands", dest = 'write', default = '', type = str)
    
    options = parser.parse_args()
   
    try:
        s = Serial(port = options.port)
        c = Controller862(s, ID = options.ID)
        c.select_axis(options.ID)
    except:
        s.close()
        raise
        
    try:
        if options.tell:
            print c.tell_position(as_string = True)
        elif options.home:
            print 'Moving to home position'
            c.go_home()
            c.wait()
        elif options.define:
            print 'Defining home position'
            c.define_home()
        elif options.move is not None:
            print 'Moving by %i steps' % options.move
            c.move_relative(options.move)  
            c.wait()
        elif options.position is not None:
            print 'Moving to absolute position %i' % options.position 
            c.move_absolute(options.position)
            c.wait()
        elif options.write:
            print 'Executing raw string'
            out = c.ask(options.write)
            if out:
                print out.strip()
            c.wait()
        else:
            parser.error("No commands given!")
    except:
        print 'aborting'
        c.abort()
    finally:
        s.close()
        
if __name__=='__main__':
    main()
    



   

        

