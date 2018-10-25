.. _Calibration:

==================
DSCUSB Calibration
==================

DSCUSB has been calibrated to measure force in mN when sample is attached at the marked
position. The cantilever has a strain gauge attached that measures the bending
strain, and it has a dummy strain gauge for temperature compensation.
Because the active strain gauge resistance was different than the 
resistance of the non-active (dummy) strain gauge some extra resistors
were attached to the Wheatston bridge. A 48kOhm (I think, it could be also 56k)
is attached in parallel with the dummy resistor and some extra around 10 Ohm
resistor is added for compensation. This was needed to reduce the temperature 
effects. Apparently what happens is that resistance of both (active and dummy) 
resistors increase with temperature. However, because initial resistance
of the active is lower, the apparent increase of the resistance of the active
resistor is a bit lower than the change of the resistance of the dummy one. It appears as if
the active resistance is (when no stress is applied):

.. math::

    R_1 = k * (R_0 + \delta(T))

and the dummy goes as

.. math::

    R_2 = R_0 + \delta(T). 

wher :math:`R_0=368` Ohm at room temperature. 
The k factor comes from the fact that the active resistor was mounted on a
slightly bent surface, which acts as a residual strain, reducing the resistance.
To reduce temperature effects, the extra resistors were added
to the bridge to compensate these effects. The idea is to reduce temperature
effect of the resistor :math:`R_2` by attaching another dummy resistor in parallel.
The one that is attached worked OK. Temperature effect were much lower this
way. Without the resistor, the sginal had approx 300 mN of apparent 
strain at temperature change of 50 degrees C. With resistors
this effect was reduced by a factor of around 10.

Temperature calibration is performed as follows. A script 
:download:`calibration.py <calibration/calibration.py>` was written:

.. literalinclude:: calibration/calibration.py
   :linenos:

This script moves the arm of the translator between two positions.
Some known weight (mass = 5.95 g) was attached to the cantilever in 
a way that the translator was able to lift and lower the weight at the two 
positions defined. Temperature was slowly dropped from around 100 degrees
to 20 degrees C. Measurements were obtained at no weight and 
with weight attached at multiple temperatures (times). 

.. note::

   The temperature as measured by the DSC is lower than the actual
   temperature of the heat cell.

The difference between the weight-on and weight-off signal was plotted and is shown below

  .. plot:: calibration/plot_calibration.py
     :include-source:

Linear fits to the data gives you the temperature dependent gain coefficient.
Since the response is linear, two values of the gain coefficients were used
to set the temperature compensation table of DSC. Check the `Cell TAB`
by clicking the settings button in `pydsc`! 

.. note::

   DSC allows for temperature dependent offset calibration. The offset calibration
   was not performed, so you should set offset each time when changing
   temperatures! do not rely on the offset not changing with temperature.
   In principle it should be possible to calibrate offset as well, but 
   I have found that difficult to do because of signal drift. 
   Still working on that ... The version 2.0 of the stretcher should
   work better



   

   


