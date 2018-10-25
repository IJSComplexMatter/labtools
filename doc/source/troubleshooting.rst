.. _Troubleshooting:

===============
Troubleshooting
===============

Standa
------

**Drivers not installed correctly**
   On some  machines I have found out that installation of 
   the driver is not performed automatically. After installing the driver,
   the driver and programs are put in the MicroSMC folder inside the Program 
   Files, but the driver is not assigned to the device.
   When the USB is plugged in, the device is found in the device list, but no 
   driver assigned. You need to use the `Windows device manager`
   and set up the driver manually, by assigning the driver which is in the 
   MicroSMC folder.

**Translator overshoots when performing move**
    When calling :meth:`StandaTranslator.move` the translator moves and overshoots
    the target position and then returns to the target with a different speed. 
    When you move back to initial position the translator does not reach target
    completely, but then increases (or decreases) speed and finally reaches target.
    This means that the `backlash compensation` is turned on. You should turn it 
    off LoftEn option in the Settings. With LoftEn turned off, do some movement
    and then click on save button to store last sent parameters to flash.
    This should set this parameter permanently.
    

Mantracourt
-----------

**Spikes in the signal when calling `DSCUSB.get` with a slow rate**
    When testing DSCUS I have found out that a continuous call to get('SYS') method
    with a slow rate does not work well. In the output signal, spikes can be seen.
    Even if hardware denoising is turned on, it works even worse. The signal 
    from time to time jumps high above the average and above the typical noise of the 
    signal. When readout rate is increased, this spikes disappear. The solution to
    the problem is to measure multiple times and then average. This is why the 
    :meth:`DSCUSB.get_force` function was made to work with multiple readouts
    and then calculating an average. The averaging is performed in a way that 
    these spikes (which still appear, but only at the first measurement of 
    the obtained multiple measurement readout) are removed. The median function
    that is used to filter the results might not be the best, but it works OK.


    .. note::
        
        The `median` function is used intentionally. It works better than `mean`
        because it removes spikes from the signal. See :meth:`~labtools.mantracourt.dscusb.get_force`
        for implementation details.
