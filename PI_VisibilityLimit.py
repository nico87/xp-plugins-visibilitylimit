# -*- coding: utf-8 -*-
"""
Visibility Limit Plugin v1.0.1

This plugin limits the current visibility basing on Wind speed and the difference between the temperature and the dew point.
"""

from XPLMDefs import *
from XPLMDisplay import *
from XPLMGraphics import *
from XPLMProcessing import *
from XPLMDataAccess import *
from XPLMUtilities import *
from SandyBarbourUtilities import *

HIGH_MAX_VIS = 50000.0		    # meters at high altitude (float)
NORMAL_MAX_VIS = 30000.0		# meters in normal conditions (float)
LOW_DPRATIO_VIS = 18000.0       # meters when difference between temp and dp is less than 5
TRANSITION = 8000               # transition altitude between HIGH and LOW levels (feet)


class PythonInterface:
    """
    XPluginStart

    Our start routine registers our window and does any other initialization we
    must do.
    """
    def XPluginStart(self):
        """
        First we must fill in the passed in buffers to describe our
        plugin to the plugin-system."""
        self.Name = "VisibilityLimitPlugin"
        self.Sig = "aimappy.xplane.PythonVisibilityLimit"
        self.Desc = "A plugin that limits the current visibility basing on Wind speed and the difference between the temperature and the dew point."
        self.RealWeatherDataRef = XPLMFindDataRef("sim/weather/use_real_weather_bool")
        self.VisibilityDataRef = XPLMFindDataRef("sim/weather/visibility_reported_m")
        self.TemperatureSL = XPLMFindDataRef("sim/weather/temperature_sealevel_c")
        self.DewPointSL = XPLMFindDataRef("sim/weather/dewpoi_sealevel_c")
        self.ElevatioDataRef = XPLMFindDataRef("sim/flightmodel/position/elevation")
        self.LastVisibility = -1
        self.SetWeather = 0
        self.AutoWeather = 0

        self.FlightLoopCB = self.FlightLoopCallback
        XPLMRegisterFlightLoopCallback(self, self.FlightLoopCB, 1.0, 0)

        return self.Name, self.Sig, self.Desc

    """
    XPluginStop

    Our cleanup routine deallocates our window.
    """
    def XPluginStop(self):
        # Unregister the callback
        XPLMUnregisterFlightLoopCallback(self, self.FlightLoopCB, 0)
        pass

    """
    XPluginEnable.

    We don't do any enable-specific initialization, but we must return 1 to indicate
    that we may be enabled at this time.
    """
    def XPluginEnable(self):
        return 1

    """
    XPluginDisable

    We do not need to do anything when we are disabled, but we must provide the handler.
    """
    def XPluginDisable(self):
        pass

    """
    XPluginReceiveMessage

    We don't have to do anything in our receive message handler, but we must provide one.
    """
    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass

    def calculateVisibility(self, minVisibility, maxVisibility, temp, dp):
        return minVisibility + (1 - max(0, dp) / temp) * (maxVisibility - minVisibility)

    def FlightLoopCallback(self, elapsedMe, elapsedSim, counter, refcon):
        visibility = XPLMGetDataf(self.VisibilityDataRef)
        # Apply a change only if the METAR visibility is higher than 10Km
        if (visibility < 10000):
            return 1.0
        temp = XPLMGetDataf(self.TemperatureSL)
        dp = XPLMGetDataf(self.DewPointSL)
        elev = XPLMGetDataf(self.ElevatioDataRef) / 0.3
        if (elev < TRANSITION):
            maxVis = self.calculateVisibility(LOW_DPRATIO_VIS, NORMAL_MAX_VIS, temp, dp)
        else:
            maxVis = self.calculateVisibility(NORMAL_MAX_VIS, HIGH_MAX_VIS, temp, dp)
        # Apply this change only if the visibility is changed for more than 500m
        if (visibility > maxVis and abs(self.LastVisibility - maxVis) > 500):
            # Keep track of the auto weather setting
            self.AutoWeather = XPLMGetDatai(self.RealWeatherDataRef)
            SandyBarbourPrint(self.Name + ": Vis. was " + str(visibility) + "m -> set it to " + str(maxVis) + "m")
            XPLMSetDataf(self.VisibilityDataRef, maxVis)
            self.LastVisibility = maxVis
            self.SetWeather = 1
            # Setting the visibility disables the auto weather.
            # We can't set the auto weather to on here. We must wait the next loop.
            # Return 1.0 to indicate that we want to be called again in 1 second.
            return 1.0
        if (self.SetWeather == 1 and self.AutoWeather == 1):
            SandyBarbourPrint(self.Name + ": autoweather re-enabled")
            # Reset the auto weather setting
            XPLMSetDatai(self.RealWeatherDataRef, 1)
            self.SetWeather = 0
        # Return 1.0 to indicate that we want to be called again in 1 second.
        return 1.0
