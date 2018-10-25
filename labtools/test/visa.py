from numpy.random import rand

def get_instruments_list():
    return ['GPIB0::12']
    
def instrument(s,timeout = 1):
    return Instrument()
   
    
class VisaIOError(Exception):
    pass 

class Instrument():
    nplc = 1
    
    def write(self, command):
        if command.startswith("SENSe:VOLT:NPLCycles"):
            print(command)
            self.nplc = 1#int(command.strip("SENSe:VOLT:NPLCycles").strip())
    
    def ask(self,command):
        if command == 'READ?':
            out = []
            for i in range(self.nplc):
                out += ['%.5fVCD' % rand() ,'','','']
            return ','.join(out)
            
    def close(self):
        pass