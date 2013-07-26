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
MEDIUM_DPRATIO_VIS = 21000.0    # meters when difference between temp and dp is less than 10
LOW_DPRATIO_VIS = 18000.0       # meters when difference between temp and dp is less than 5


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

    def FlightLoopCallback(self, elapsedMe, elapsedSim, counter, refcon):
        visibility = XPLMGetDataf(self.VisibilityDataRef)
        diff = XPLMGetDataf(self.TemperatureSL) - XPLMGetDataf(self.DewPointSL)
        elev = XPLMGetDataf(self.ElevatioDataRef) / 0.3
        if (elev < 8000):
            if (diff < 5):
                maxVis = LOW_DPRATIO_VIS
            elif (diff < 10):
                maxVis = MEDIUM_DPRATIO_VIS
            else:
                maxVis = NORMAL_MAX_VIS
        else:
            if (diff < 5):
                maxVis = NORMAL_DPRATIO_VIS
            else:
                maxVis = HIGH_MAX_VIS
        if (visibility > maxVis):
            # Keep track of the auto weather setting
            self.AutoWeather = XPLMGetDatai(self.RealWeatherDataRef)
            SandyBarbourPrint(self.Name + ": Vis. was " + str(visibility) + "m -> set it to " + str(maxVis) + "m (diff was " + str(diff) + "°C and elev was " + str(elev) + "feet)")
            XPLMSetDataf(self.VisibilityDataRef, maxVis)
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
