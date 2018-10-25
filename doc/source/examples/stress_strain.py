"""This is a script for obtaining elastomer stress-strain measurements.
It uses modules for instrument controle from the 'labtools' package and uses 
matplotlib/numpy for data plotting. 
It creates POSITIONS list for all positions of the translator at which
stress measurements are performed. Results obtained are written to file
and stress-strain curve is displayed."""


from labtools.standa.translator import StandaTranslator# instrument control
from labtools.mantracourt.dscusb import DSCUSB
import matplotlib.pyplot as plt # import plotting library into namespace `plt`
import numpy as  np # import numerical library into namespace `np`
import time, datetime

# parameters of the experiment:
START_POSITION = 0.    # position of the translator in mm for first measurement
STEP = 0.1             # step size in mm 
NSTEPS = 10            # how many steps to perform
SLEEP = 1.              # time to sleep in seconds after each step
NFORCE = 1             #how many force measurements to perform
INTERVAL = 1.#interval rate at which force measurements are performed
INTERACTIVE = True   #set to True if you wish to display the measured data on the fly...
OUTPUT = 'results.txt' #name of the file to save results to
RELATIVE = True       #should translator position be viewed relative to the initial position
# a list of positions calculated from the above parameters:
POSITIONS = [START_POSITION + i*STEP for i in range(NSTEPS)] 

def measure(positions = POSITIONS, sleep = SLEEP, n = NFORCE, interval = INTERVAL, 
            ion = INTERACTIVE, relative = RELATIVE):
    """This function sets up the experiment and performs force measurements, 
    at positions and based on the parameters specified. 
    
    Parameters
    ----------
    positions : list of floats
        determines at which positions (in mm) of the translator force is measured.
    sleep : float
        time to wait (in seconds ) after stretching is performed.
    n : int
        number of force measuremnets to perform at each step
    interval : float
        interval (seconds) at which force measurements are obtained (if n > 1)
    ion : bool 
        interactive on. Defines whether the obtained data is displayed while measuring.
    relative : bool
        defines if stretching is relative to current physical position of the motor.
        
    Returns
    -------
    data : array
        measured data (position: first column, force : second column)
    """
    # set up the modules:
    translator = StandaTranslator() #creates an instance of Standatranslator
    translator.init() #initiate (load drivers)    
    dsc = DSCUSB() # creates an instance of DSCUSB for force measurements
    dsc.init() #initialize: open port and set things up.
    homepos = translator.tell() / 1000. # tell() returns microns
    print('Motor home position is %f' % homepos)
    
    if relative == True:
        # if we use relative positions, calculate absolute values first
        abspositions = [p + homepos for p in positions]
    else:
        abspositions = positions 
    
    results = [] # measurement results will be storred here
    if ion == True:
        plt.ion() #interactive mode on 
        
    try:
        for i, position in enumerate(abspositions):
            print('\nPerforming measurement %i/%i' % (i + 1, len(positions)))
            print('Moving translator to %.3f' % position)
            translator.move(position * 1000.) # move takes position in microns
            translator.wait()
            print('Waiting for %.1f seconds' % sleep)
            time.sleep(sleep) # wait SLEEP seconds
            print('Measuring force %i times with interval %f seconds:' % (n, interval))
            force = dsc.get_force_list(n,interval)
            print([f[1] for f in force])
            results.append([position] + [item for sublist in force for item in sublist])

            if ion == True:
                data = np.array(results) # convert results to numerical data for plotting
                plot(data) 
                
    except (KeyboardInterrupt, SystemExit):
        print('Moving back to start position %f' % homepos)
        translator.move(homepos * 1000.)         #move to start position if program killed by user
        translator.wait()
        raise
        
    print('Moving back to start position %f' % homepos)
    translator.move(homepos * 1000.)
    translator.wait()
    data = np.array(results)
    print('Done!')
    return data

def plot(data):
    """Plots stress-strain data
    """
    plt.cla() #clear axes to plot new data
    plt.xlabel('Stretch [mm]')
    plt.ylabel('Force [mN]')
    plt.title('Stress-strain')
    x,y = data.shape
    for j in range((y-1)/2):
        plt.plot(data[:,0],data[:,j *2+ 2])
    plt.draw()    
  
def display(data):
    """Plots stress-strain data and shows it
    """
    plt.ioff()
    plot(data)
    plt.show()   
    
def save(fname, data):
    """Saves data to text file
    """
    print('Saving results to "%s"' % fname)
    runs, cols = data.shape
    with open(fname,'w') as f:
        f.write('#Date: %s\n' % datetime.datetime.today())
        f.write('#Columns: position' +', time, force' * ((cols - 1)//2))
        f.write('\n')
        np.savetxt(f, data) #save results        

def main():
    """Performs measurements, based on the default settings,
    displays the data and saves results to a text file
    """ 
    data = measure() #perform measurements
    save(data, OUTPUT)
    display(data)

# the following part gets executed when the module run from the shell
if __name__ == '__main__':
    main()