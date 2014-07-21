#!/usr/bin/

# Import built-in modules
import os
import sys
import re
import time
# Import OSHI Framework modules
from core.testcase_exceptions import TestException
# Import monkeyrunner related modules
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice
from com.nokia.nst.viewMgnt import View, ViewParser
# Import OSHI framework modules
from view import DeviceViewInterface, DeviceView, ViewInterfaceFactory

class UIState():
    def __init__(self, phone):
        self.phone = phone
        self.currentState = None

    def getCurrentState(self):
        if self.currentState == None:
            self.currentState = self.phone.adb('uiautomator dump /dev/tty > /dev/null')
        return self.currentState

    def getScreenWidth(self):
        pass

    def getScreenHeight(self):
        pass


class Sleep():
    def __init__(self, phone):
        self.phone = phone

    def __call__(self, seconds):
        print '========== Sleep (%s) seconds ==========' % seconds
        MonkeyRunner.sleep(seconds)


class Select():
    def __init__(self, phone):
        self.phone = phone

    def text(self, text, isNeedDump = False, wait = 2):
        print '========== Select text: (%s) ==========' % text
        if isNeedDump:
            self.phone.viewClient.dump()

        textView = self.phone.viewClient.findViewWithText(text)
        if textView.isExist():
            textView.touch(timeout = wait)
        else:
            raise TestException()

    def view(self, attrMaps, isNeedDump = False, wait = 2):
        print '========== Select view object =========='
        if isNeedDump:
            self.phone.viewClient.dump()

        viewObj = self.phone.viewClient.findViewWithAttributes(attrMaps)
        if viewObj.isExist():
            viewObj.touch(timeout = wait)
        else:
            raise TestException()


class Touch():
    def __init__(self, phone):
        self.phone = phone

    def __call__(self, x, y, type = MonkeyDevice.DOWN_AND_UP,\
            length = 0.05, wait = 2):
        print '========== Touch coordinate: (%d, %d) ==========' % (x, y)
        if type == MonkeyDevice.DOWN_AND_UP:
            self.phone._device.touch(x, y, MonkeyDevice.DOWN)
            MonkeyRunner.sleep(length)
            self.phone._device.touch(x+10, y+10, MonkeyDevice.UP)
        else:
            self.phone._device.touch(x, y, type)
        time.sleep(wait)


class DialNumber():
    keyNumPadDict = None

    def __init__(self, phone):
        self.phone = phone

    @staticmethod
    def initKeyNumPadDict():
        DialNumber.keyNumPadDict = {
                        '0': 'KEYCODE_NUMPAD_0', 
                        '1': 'KEYCODE_NUMPAD_1',
                        '2': 'KEYCODE_NUMPAD_2',
                        '3': 'KEYCODE_NUMPAD_3',
                        '4': 'KEYCODE_NUMPAD_4',
                        '5': 'KEYCODE_NUMPAD_5',
                        '6': 'KEYCODE_NUMPAD_6',
                        '7': 'KEYCODE_NUMPAD_7',
                        '8': 'KEYCODE_NUMPAD_8',
                        '9': 'KEYCODE_NUMPAD_9',
                        'ENTER':'KEYCODE_NUMPAD_ENTER'
                        }                    

    def __call__(self, number = '10086', sleepSec = 0.01):
        print '========== Dial number: (%s) ==========' % number
        if DialNumber.keyNumPadDict is None:
            DialNumber.initKeyNumPadDict()
        for c in number:
            self.phone._device.press(DialNumber.keyNumPadDict[c], MonkeyDevice.DOWN_AND_UP)
            MonkeyRunner.sleep(sleepSec)


class PressKey():
    def __init__(self, phone):
        self.phone = phone

    def press(self, keyCode, pressType = MonkeyDevice.DOWN_AND_UP, length = 1, count = 1):
        print '========== Press key: (%s) %s times ==========' % (keyCode, str(count))
        for i in range(count):
            self.phone._device.press(keyCode, pressType)
            MonkeyRunner.sleep(length)

    def longPress(self, keyCode, length = 2, count = 1):
        print '========== Long press key: (%s) %s times ==========' % (keyCode, str(count))
        for i in range(count):
            self.phone._device.press(keyCode, MonkeyDevice.DOWN)
            MonkeyRunner.sleep(length)
            self.phone._device.press(keyCode, MonkeyDevice.UP)


