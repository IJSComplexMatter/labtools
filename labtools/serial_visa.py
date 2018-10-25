from serial import Serial
from serial.tools.list_ports import comports

import warnings, time, struct, re

def get_instruments_list(use_aliases=True):
    """Get a list of all connected devices. Returns 
    a list of strings with the names of all connected devices, ready for being
    used to open each of them.

    """
    return [port[0] for port in comports()]

    
def instrument(resource_name, **keyw):
    """Factory function for instrument instances.

    Parameters
    ----------
    resource_name : str
        the VISA resource name of the device.  It may be an
        alias.
    keyw : optional
        keyword argument for the class constructor of the device instance
        to be generated.  See the class Instrument for further information.

    Returns
    -------
    The generated instrument instance.

    """
    return SerialInstrument(resource_name, **keyw)
    
def _warn_for_invalid_keyword_arguments(keyw, allowed_keys):
    for key in keyw.iterkeys():
        if key not in allowed_keys:
            warnings.warn("Keyword argument \"%s\" unknown" % key,
                          stacklevel = 3)

no_parity = 0

ascii      = 0
single     = 1
double     = 3
big_endian = 4

   
CR = b'\r'
LF = b'\n'

class InvalidBinaryFormat(Exception):
    pass
     
class SerialInstrument(object):
    chunk_size = 20*1024
    """How many bytes are read per low-level call"""
    term_chars = None
    """Termination character sequence.  See below."""
    delay = 0.0
    """Seconds to wait after each high-level write"""
    values_format = ascii
    """floating point data value format"""
    def __init__(self, resource_name, **keyw):
        """Constructor method.

        Parameters
        ----------
        resource_name : str
            the instrument's resource name or an alias, may be
            taken from the list from get_instruments_list().

        timeout : flost
            the VISA timeout for each low-level operation in
            milliseconds.
        term_chars : str
            the termination characters for this device, see
            description of class property "term_chars".
        chunk_size : int 
            size of data packets in bytes that are read from the
            device.
        lock -- whether you want to have exclusive access to the device.
            Default: VI_NO_LOCK
        delay : float
            waiting time in seconds after each write command. Default: 0
        send_end : bool 
            whether to assert end line after each write command.
            Default: True
        values_format : int 
            floating point data value format.  Default: ascii (0)

        """
        _warn_for_invalid_keyword_arguments(keyw,
           ("timeout", "term_chars", "chunk_size", "lock",
            "delay", "send_end", "values_format",
            "baud_rate", "data_bits", "end_input", "parity", "stop_bits"))
        
        self._resource_name = resource_name
        timeout = keyw.get("timeout",5.)

        self.term_chars    = keyw.get("term_chars",CR)
        self.chunk_size    = keyw.get("chunk_size", self.chunk_size)
        self.delay         = keyw.get("delay", 0.0)
        self.send_end      = keyw.get("send_end", True)
        self.values_format = keyw.get("values_format", self.values_format)

        baud_rate = keyw.get("baud_rate", 9600)
        self.data_bits = keyw.get("data_bits", 8)
        self.stop_bits = keyw.get("stop_bits", 1)
        self.parity    = keyw.get("parity", no_parity)
        #self.end_input = keyw.get("end_input", term_chars_end_input)
        
        self.serial = Serial(port = self._resource_name, baudrate = baud_rate, timeout = timeout)
    
    @property
    def resource_name(self):
        return self._resource_name
    
    @property
    def timeout(self):
        return self.serial.timeout
        
    @timeout.setter    
    def timeout(self, value):
        self.serial.timeout = value
        
    @property
    def baud_rate(self):
        return self.serial.baudrate
        
    @baud_rate.setter    
    def baud_rate(self, value):
        self.serial.baudrate = value     
        
    def __repr__(self):
        return "Instrument(\"%s\")" % self.resource_name

    def write(self, message):
        """Write a string message to the device.

        Parameters
        ----------
        message : str
            the string message to be sent.  The term_chars are appended
            to it, unless they are already.

        """
        if self.term_chars and not message.endswith(self.term_chars):
            message += self.term_chars
        elif self.term_chars is None and not message.endswith(CR+LF):
            message += CR+LF
        self.serial.write(message)
        if self.delay > 0.0:
            time.sleep(self.delay)
            
    def _strip_term_chars(self, buffer):
        if self.term_chars:
            if buffer.endswith(self.term_chars):
                buffer = buffer[:-len(self.term_chars)]
            else:
                warnings.warn("read string doesn't end with "
                              "termination characters", stacklevel=2)
        return buffer.rstrip(CR+LF)
        
    def read_raw(self):
        """Read the unmodified string sent from the instrument to the computer.

        In contrast to read(), no termination characters are checked or
        stripped.  You get the pristine message.
        """
        out = self.serial.read()
        while not out.endswith(self.term_chars):
            n = self.serial.inWaiting()
            nr = max(1,min(n, self.chunk_size))
            c = self.serial.read(nr)
            if c == '':
                break
            else:
                out += c
        return out            
    
    def read(self):
        """Read a string from the device.

        Reading stops when the device stops sending (e.g. by setting
        appropriate bus lines), or the termination characters sequence was
        detected.  Attention: Only the last character of the termination
        characters is really used to stop reading, however, the whole sequence
        is compared to the ending of the read string message.  If they don't
        match, a warning is issued.

        All line-ending characters are stripped from the end of the string.


        Returns
        -------
        The string read from the device.

        """
        return self._strip_term_chars(self.read_raw())
        
    def read_values(self, format=None):
        """Read a list of floating point values from the device.

        Parameters
        ----------
        format : int (optional) 
            the format of the values.  If given, it overrides
            the class attribute "values_format".  Possible values are bitwise
            disjunctions of the above constants ascii, single, double, and
            big_endian.  Default is ascii.

        Returns
        -------
        The list with the read values.

        """
        if not format:
            format = self.values_format
        if format & 0x01 == ascii:
            float_regex = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\d*\.\d+)"
                                     "(?:[eE][-+]?\d+)?")
            return [float(raw_value) for raw_value in
                    float_regex.findall(self.read())]
        # Okay, we need to read binary data
        original_term_chars = self.term_chars
        self.term_chars = b""
        try:
            data = self.read_raw()
        finally:
            self.term_chars = original_term_chars
        hash_sign_position = data.find("#")
        if hash_sign_position == -1 or len(data) - hash_sign_position < 2:
            raise InvalidBinaryFormat
        if hash_sign_position > 0:
            data = data[hash_sign_position:]
        if data[1].isdigit() and int(data[1]) > 0:
            number_of_digits = int(data[1])
            # I store data and data_length in two separate variables in case
            # that data is too short.  FixMe: Maybe I should raise an error if
            # it's too long and the trailing part is not just CR/LF.
            data_length = int(data[2:2+number_of_digits])
            data = data[2+number_of_digits:2+number_of_digits + data_length]
        elif data[1] == "0" and data[-1] == "\n":
            data = data[2:-1]
            data_length = len(data)
        else:
            raise InvalidBinaryFormat
        if format & 0x04 == big_endian:
            endianess = ">"
        else:
            endianess = "<"
        try:
            if format & 0x03 == single:
                result = list(struct.unpack(endianess +
                                            str(data_length/4) + "f", data))
            elif format & 0x03 == double:
                result = list(struct.unpack(endianess +
                                            str(data_length/8) + "d", data))
            else:
                raise ValueError, "unknown data values format requested"
        except struct.error:
            raise InvalidBinaryFormat, "binary data itself was malformed"
        return result

    def ask(self, message):
        """A combination of write(message) and read()"""
        self.write(message)
        return self.read()
        
    def ask_for_values(self, message, format=None):
        """A combination of write(message) and read_values()"""
        self.write(message)
        return self.read_values(format)
        
    def clear(self):
        """Resets the device.  This operation is highly bus-dependent."""
        pass
        
    def trigger(self):
        """Sends a software trigger to the device."""
        pass
    
    def close(self):
        """Closes serial port"""
        self.serial.close()
    

