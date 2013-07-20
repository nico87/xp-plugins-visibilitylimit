# -*- coding: utf-8 -*-
"""
Visibility Limit Plugin

This plugin limits the current visibility basing on Wind speed and the difference between the temperature and the dew point.

This file is released under the GNU GPL v2 licence.

Author: Claudio Nicolotti - https://github.com/nico87/

If you want to update this plugin or create your own fork please visit https://github.com/nico87/xp-plugins-windpressure
"""

from XPLMDefs import *
from XPLMDisplay import *
from XPLMGraphics import *
from XPLMProcessing import *
from XPLMDataAccess import *
from XPLMUtilities import *

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
        self.Name = "WindPressure"
        self.Sig = "aimappy.xplane.PythonVisibilityLimit"
        self.Desc = "A plugin that limits the current visibility basing on Wind speed and the difference between the temperature and the dew point."
        self.VisibilityDataRef = XPLMFindDataRef("sim/weather/visibility_reported_m")
        self.WindDirDataRef = XPLMFindDataRef("sim/weather/wind_direction_degt")
        self.WindSpeedDataRef = XPLMFindDataRef("sim/weather/wind_speed_kt")
        self.TemperatureSL = XPLMFindDataRef("sim/weather/temperature_sealevel_c")
        self.DewPointSL = XPLMFindDataRef("sim/weather/dewpoi_sealevel_c")
        self.elevation = XPLMFindDataRef("sim/flightmodel/position/elevation")

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
        maxVis = HIGH_MAX_VIS
        diff = XPLMGetDatai(self.TemperatureSL) - XPLMGetDatai(self.DewPointSL)
        elev = XPLMGetDatad(self.elevation) / 0.3
        if (elev < 8000):
            if (diff < 5):
                maxVis = LOW_DPRATIO_VIS
            elif (diff < 10):
                maxVis = MEDIUM_DPRATIO_VIS
        if (visibility > maxVis):
            XPLMSetDataf(self.VisibilityDataRef, maxVis)
        # Return 1.0 to indicate that we want to be called again in 1 second.
        return 1.0
