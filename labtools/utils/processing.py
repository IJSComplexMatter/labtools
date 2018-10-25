"""
Defines ProcessingQue class
There are two classes of interest here:
    
* :class:`.Progress` that can be used for progress tracking
* :class:`.ProcessingQue` that can be used for generating a queued processing program

"""
from traits.api import HasTraits, Int,\
        Button, Instance, Bool,Any, \
        Property, Range, on_trait_change, Str, DelegatesTo, Float, cached_property
from traitsui.api import View, Item
from pyface.timer.api import Timer

from threading import Thread
from Queue import Queue
import time, datetime

from labtools.log import create_logger
from display_message import display_message, error_message

log = create_logger(__name__)

def queued_function(f):
    """
    Decorator function. Puts a slow class function to que. Displays error if any
    """
    def _queued_function(self,*args,**kw):
        def _f():
            try:
                return f(self,*args,**kw)
            except:
                log.exception('Execution failed!', display = True)
        self.queue.put(_f)
    return _queued_function

def queued_stop_on_error(f):
    """
    Decorator function. Puts a slow class function to que. clears que on error
    """
    def _queued_function(self,*args,**kw):
        def _f():
            try:
                return f(self,*args,**kw)
            except:
                log.exception('Execution failed! Stopping!', display = True)
                try:
                    self.cancel()
                except:
                    log.exception('Stopping failed!', display = True)
        self.queue.put(_f)
    return _queued_function

class Progress(HasTraits):
    """Use this for progress tracking, estimating time to complete and to obtain
    progress messages.
    
    Examples
    --------

    >>> p = Progress()
    >>> p.start(9) #9 tasks to finish, timer is started
    >>> p.percentage
    0
    >>> p.task_add() # 10 tasks to finish
    >>> p.task_done() # 9 tasks to finish
    >>> p.tasks_all #10 tasks in total
    10
    >>> p.tasks_done #one completed
    1
    >>> p.percentage
    10
    >>> p.stop() #0 tasks to finish, timer is stopped
    >>> p.percentage
    100
    >>> p.task_add() # 1 task to finish, timer is started
    """
    #: integer describing how many tasks have completed in percentage
    percentage = Property(Int, depends_on = 'tasks_done,tasks_all')
    #: descirbes how many tasks have completed. This string is empty when all tasks done
    message = Property(Str, depends_on = 'percentage')
    #: specifies time when start is called
    start_time = Float()
    # specifies current time. This gets updated every second by the timer
    current_time = Float
    #: specifies total run time (a timedelta)
    run_time = Property(depends_on = 'current_time,start_time')
    #: specifies total run time (a timedelta)
    run_time_str = Property(depends_on = 'run_time')
    #: estimated time to complete (a timedelta)
    estimated_time = Property(depends_on = 'start_time,percentage,run_time') 
    #: estimated time string to complete
    estimated_time_str = Property(Str,depends_on = 'estimated_time')    
    #: number of all tasks to complete
    tasks_all = Range(low = 0, value = 0)
    #: number of completed tasks
    tasks_done = Range(low = 0, value = 0)
    #: calculated speed of task completion... needed for estimating time to complete
    speed = Property(depends_on='percentage')
    #: a timer that updates current time, should have a pyface Timer interface
    timer = Any
    def start(self, tasks):
        """This can be called to start timer and to define unfinished tasks
        """
        self.tasks_all = tasks
        self.start_time = time.time()
        try:
            self.timer.Start(1000)
        except AttributeError:
            self.timer = Timer(1000, self._timer_task)

    def task_done(self):
        """This must be called when task is finished
        """
        self.tasks_done += 1
        if self.percentage == 100:
            self.stop()

    def task_add(self):
        """This can be called either after start function to add a task
        It can be called without calling start first.
        """
        if self.tasks_all == 0:
            self.start(1)
        else:
            self.tasks_all += 1

    def stop(self):
        """This clears progress and puts everything to initial state
        """
        try:
            self.timer.Stop()
        except AttributeError:
            pass
        self.tasks_done = 0
        self.tasks_all = 0

    def _timer_task(self):
        self.current_time = time.time()
    
    @cached_property
    def _get_run_time(self):
        return datetime.timedelta(seconds = max(self.current_time - self.start_time,0))
        
    @cached_property
    def _get_percentage(self):
        try:
            return min(int((100. * self.tasks_done) / self.tasks_all),100)
        except ZeroDivisionError:
            return 100
            
    @cached_property        
    def _get_speed(self):
        try:
            return 1.0* self.percentage / (self.run_time.seconds)
        except ZeroDivisionError:
            return 0.
    
    @cached_property        
    def _get_message(self):
        if self.percentage == 100:
            return ''
        else:
            return 'In progress ... %d%% completed.' % self.percentage
            
    @cached_property
    def _get_estimated_time(self):
        if self.percentage == 100:
            return
        else:
            try:
                return datetime.timedelta(seconds = int(100./self.speed - self.run_time.seconds))
            except ZeroDivisionError:
                return
    @cached_property                     
    def _get_estimated_time_str(self):
        if self.estimated_time:
            return 'Estimated time: %s' % self.estimated_time
        else:
            return ''

    @cached_property                     
    def _get_run_time_str(self):
            return 'Total time: %s' % self.run_time
            
    def __del__(self):
        self.stop()

class ProcessingQueue(HasTraits):
    """ProcessingQueue is a class for putting slow functions that should be executed
    to que. This functions are then executed in a sepperate thread.
    
    Examples
    --------

    >>> p = ProcessingQueue()
    >>> p.put(time.sleep, (1,))
    >>> p.put(time.sleep, (1,))
    
#    >>> p.configure_traits()
#    True
    """

    queue = Instance(Queue,transient = True)
    progress = Instance(Progress, transient = True)
    thread = Instance(Thread, (),transient = True)
    message = DelegatesTo('progress')
    estimated_time_str = DelegatesTo('progress')

    #: Defines whether queue is processed continuously, or executed with run() function instead
    continuous_run = Bool(True, transient = True, desc = 'whether queue is processed continuously')

    #----- Settable attributes
    #: Defines tracback level for functions in que that fail
    traceback = Range(0,4,0, desc = 'traceback level. 0 for no traceback')
    #: Should the queue be cleared if error occurs
    clear_on_error = Bool(False, desc = 'whether to clear queue on error')
    #: How many tasks are yet unfinished
    unfinished_tasks = Property(Int, depends_on = '_unfinished_tasks')
    #: Is True if tasks are in progress
    is_processing = Property(Bool, depends_on = '_unfinished_tasks,_run_ok')

    #-----Private attributes
#    _stop = Bool(False, transient = True)
    _unfinished_tasks = Int(0, transient = True)
    _run_ok = Bool(False, transient = True)

    #----Buttons
    clear_button = Button()
    run_button = Button()

    view = View('continuous_run','clear_on_error',Item('is_processing', style = 'readonly'),
                Item('unfinished_tasks', style = 'readonly'),
                'clear_button','run_button',Item('object.progress.percentage', style = 'custom'))

    def __init__(self,*args, **kw):
        super(ProcessingQueue,self).__init__(*args,**kw)
        self.thread.start()

    def _thread_default(self):
        def worker():
            while True:
                while self.continuous_run == False or self.queue.empty() == True:
                    if self._run_ok == True:
                        break
                    time.sleep(1)
#                if self._stop == True:
#                    return
                if self.queue.empty():
                    self._run_ok = False
                else:
                    funct = self.queue.get()
                    funct()


        thread = Thread(target = worker)
        thread.daemon = True
        return thread
        
    def _progress_default(self):
        return Progress()

    def _queue_default(self):
        return Queue()

    def _get_unfinished_tasks(self):
        return self._unfinished_tasks

    def _get_is_processing(self):
        if self._run_ok == True:
            return True
        else:
            if self._unfinished_tasks != 0:
                return True
            else:
                return False

    def __unfinished_tasks_changed(self, old,new):
        if new == 0:
            # stop has to be forced in case of clear function call
            self.progress.stop()

    def put(self, f, args = ()):
        """
        Puts a function to processing queue, Optional args are arguments to the
        function
        """
        def _f():
            try:
                f(*args)
                self.queue.task_done()
            except Exception as e:
                message = 'Function "%s" raised an exception: %s' % (f.__name__, error_message(self.traceback))
                log.exception(message)
                display_message(message,'error')
                self.queue.task_done()
                if self.clear_on_error == True:
                    self.clear()
            finally:
                self.progress.task_done()
                self._unfinished_tasks = self.queue.unfinished_tasks

        if self.continuous_run == True:
            self.progress.task_add()
        self._unfinished_tasks = self.queue.unfinished_tasks +1
        self.queue.put(_f)


    @on_trait_change('clear_button')
    def clear(self):
        """
        Clears unfinished tasks of processing queue
        """
        while True:
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except:
                break
            finally:
                self._unfinished_tasks = self.queue.unfinished_tasks

    @on_trait_change('run_button')
    def run(self):
        """Starts executing processing queue if continuous_run = False
        """
        if self.continuous_run == False:
            self.progress.start(self.queue.unfinished_tasks)
            self._run_ok = True
            
    def join(self):
        self.queue.join()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    p = Progress()
    p.start(10) #10 tasks to finish, timer is started
    p.configure_traits()
    p.task_done()
    p.configure_traits()
    p.stop()
    p.configure_traits()
    