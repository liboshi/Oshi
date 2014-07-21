#!/usr/bin
# Import built-in modules
import logging
# Import monkeyrunner related modules
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
# Import framework modules
from scripting import Select, Touch, Sleep, DialNumber, PressKey
from view import DeviceViewInterface, DeviceView, ViewInterfaceFactory
from utils.monkey import MonkeyBasic

class Phone():
    def __init__(self, deviceId):
        self._deviceId = deviceId
        self._device = None
        self._logger = logging.getLogger('')
        self.viewClient = None
        self.select = Select(self)
        self.touch = Touch(self)
        self.sleep = Sleep(self)
        self.dialNumber = DialNumber(self)
        self.pressKey = PressKey(self)
        self.monkeyBasic = MonkeyBasic(self)

    def createConnection(self, connTime, timeOut):
        try:
            for i in range(connTime):
                self._device = MonkeyRunner.waitForConnection(timeOut, self._deviceId)
                if self._device is not None:
                    self.initViewClient('standard')
                    return self._device
        except Exception, e:
            print 'Connection error: %s' % e

    def adb(self, adbCommand):
        self._device.shell(adbCommand)

    def initViewClient(self, viewDumpMode):
        self.viewClient = ViewInterfaceFactory.factory(viewDumpMode, self._device, self._deviceId)
     
