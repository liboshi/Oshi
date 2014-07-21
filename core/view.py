# This Python file uses the following encoding: utf-8
"""
NST internal
"""

import re
import sys
import subprocess
import os
import signal
import time
import datetime
import logging
import warnings
import org.python.modules.sre.PatternObject
import codecs
import java
import java.lang.Exception
from java.util import HashMap
from com.android.ddmlib import ShellCommandUnresponsiveException
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

from com.nokia.nst.viewMgnt import View, ViewParser

DEBUG = False
DEBUG_DEVICE = DEBUG and False
DEBUG_RECEIVED = DEBUG and False
DEBUG_TREE = DEBUG and False
DEBUG_GETATTR = DEBUG and False
DEBUG_CALL = DEBUG and False
DEBUG_COORDS = DEBUG and False  
DEBUG_TOUCH = DEBUG and False
DEBUG_STATUSBAR = DEBUG and False
DEBUG_WINDOWS = DEBUG and False
DEBUG_BOUNDS = DEBUG and False
DEBUG_DISTANCE = DEBUG and False

WARNINGS = False

class DeviceViewInterface():
    '''
    Based on UIAutomator, ADB channel, communicate with device side; 
    
    Main functionalities:
        (1)Dump the view xml file;
        (2)Parse and return the view information;
    
    '''
    
    def __init__(self, device, deviceStr, autodump=False, ignoreuiautomatorkilled=False):
        '''
        Constructor
        
        @type device: MonkeyDevice
        @param device: The device running the C{View server} to which this client will connect
        @type serialno: str
        @param serialno: the serial number of the device or emulator to connect to
        '''
        self._device = device
        self._deviceStr = deviceStr
        self._autodump = autodump
        self._viewParser = ViewParser(self._deviceStr)
        self._ignoreuiautomatorkilled = ignoreuiautomatorkilled
        
        self._logger = logging.getLogger('')
        
        try:
            codecs.lookup('cp65001')
        except:
            def cp65001(name):
                if name.lower() == 'cp65001':
                    return codecs.lookup('utf-8')
            codecs.register(cp65001)
    
    def host_exec(self, cmd):
      p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      out, msg= p.communicate()
      return out
    
    def dump(self, sleep=1):
        '''
        Dumps the window content and return the root of parsed view.
        
        Sleep is useful to wait some time before obtaining the new content when something in the
        window has changed.
        
        @type sleep: int
        @param sleep: sleep in seconds before proceeding to dump the content
        
        @return: return the root value of the 
        '''
        if(sleep > 0):
            MonkeyRunner.sleep(sleep)
        
        '''
        Using /dev/tty this works even on devices with no sdcard
        '''
        startTime = datetime.datetime.now()
        
        try:
            rawReceived = self.host_exec('adb -s %s shell uiautomator dump /dev/tty' % self._deviceStr)
                
            if rawReceived:
                received = rawReceived.replace('UI hierchary dumped to: /dev/tty', '')
            else:
                received = rawReceived
        except (ShellCommandUnresponsiveException):
            self._logger.warn("Empty UIAutomator dump was received, will dump again!--")
            rawReceived = self.host_exec('adb -s %s shell uiautomator dump /dev/tty' % self._deviceStr)
            
            received = rawReceived.replace('UI hierchary dumped to: /dev/tty\r\r\n', '')
        except Exception, value:
            errMsg = "ERROR: uiautomator dump /dev/tty >/dev/null error occurs, will dump again!"
            self._logger.error(errMsg)
            MonkeyRunner.sleep(3)
            received = self._device.shell('uiautomator dump /dev/tty >/dev/null')
        
        for i in range(1,3):
            '''
            Try another 2 times;
            '''
            if not received:      
                '''
                Retry the dump 
                '''
                MonkeyRunner.sleep(2)
                self._logger.warn("Empty UIAutomator dump was received, will dump again, dump counter:(%d)!" % (i+1))
                
                rawReceived = self.host_exec('adb -s %s shell uiautomator dump /dev/tty' % self._deviceStr)
                
                if rawReceived:
                    received = rawReceived.replace('UI hierchary dumped to: /dev/tty', '')
            
            else:
                break
        
        #print received
        finishTime = datetime.datetime.now()
        
        timeDelta = finishTime - startTime
        #self._logger.debug(received)
        #self._logger.debug(timeDelta)
        
        if not received:
                
                errMsg = 'ERROR: Empty UIAutomator dump was received after 3 dump action!'            
                self._logger.error(errMsg)
                raise RuntimeError(errMsg)
        

        '''received = received.encode('utf-8', 'ignore')'''
        self.received = received
        
        if DEBUG:
            self.received = received
            print >> sys.stdout, self.received
        if DEBUG_RECEIVED:
            print >> sys.stderr, "received %d chars" % len(received)
            print >> sys.stderr
            print >> sys.stderr, repr(received)
            print >> sys.stderr
        onlyKilledRE = re.compile('[\n\S]*Killed[\n\r\S]*', re.MULTILINE)
        if onlyKilledRE.search(received):
            raise RuntimeError('''ERROR: UiAutomator output contains no valid information. UiAutomator was killed, no reason given.''')
        '''
        In rare case, this maybe used;
        '''
        if self._ignoreuiautomatorkilled:
            if DEBUG_RECEIVED:
                print >> sys.stderr, "ignoring UiAutomator Killed"
            killedRE = re.compile('</hierarchy>[\n\S]*Killed', re.MULTILINE)
            if killedRE.search(received):
                received = re.sub(killedRE, '</hierarchy>', received)
            elif DEBUG_RECEIVED:
                print "UiAutomator Killed: NOT FOUND!"
            
            ''' 
            It seems that API18 uiautomator spits this message to stdout
            '''
            dumpedToDevTtyRE = re.compile('</hierarchy>[\n\S]*UI hierchary dumped to: /dev/tty.*', re.MULTILINE)
            if dumpedToDevTtyRE.search(received):
                received = re.sub(dumpedToDevTtyRE, '</hierarchy>', received)
            if DEBUG_RECEIVED:
                print >> sys.stderr, "received=", received
        
        if re.search('\[: not found', received):
            raise RuntimeError('''ERROR: Some emulator images (i.e. android 4.1.2 API 16 generic_x86) does not include the '[' command.
                                While UiAutomator back-end might be supported 'uiautomator' command fails.
                                You should force ViewServer back-end.''')

        
        self._rootViewNode = self._viewParser.ParseToViewByStr(received)
 
        return self._rootViewNode
    

    def setRootView(self, rootView):
        '''
        set the root view of the current parser
        '''
        self._rootViewNode = rootView._viewObject
    
    def findViewWithText(self, viewText):
        '''
        Find the view according to the view text;
        Return the DeviceView instance;
        '''
        viewByText = self._viewParser.FindViewByText(self._rootViewNode, viewText)
        return DeviceView(self._device, viewByText)
    
    def findViewWithTextContained(self, viewText):
        '''
        Find the view according to the view text, where contains the viewText;
        Return the DeviceView instance;
        '''
        viewByTextC = self._viewParser.FindViewByTextContained(self._rootViewNode, viewText)
        return DeviceView(self._device, viewByTextC)
    
    def findViewByClassAndIndex(self, vClassName, vIndex):
        '''
        Find the view according to the class and index;
        '''
        viewRet = self._viewParser.FindViewByClassAndIndex(self._rootViewNode, vClassName, vIndex)
        return DeviceView(self._device, viewRet)
    
    def findViewByClassAndText(self, vClassName, vText):
        '''
        Find the view according to the class and index;
        '''
        viewRet = self._viewParser.FindViewByClassAndText(self._rootViewNode, vClassName, vText)
        return DeviceView(self._device, viewRet)
    
    def findViewWithAttribute(self, attr='content-desc', value='OK'):
        '''
        Find the view according to the attribute and value;
        Return the DeviceView instance;
        ***To be noticed, other means not implemented yet;***
        '''
        if attr == 'content-desc':
            viewByCont = self._viewParser.FindViewByContDesc(self._rootViewNode, value)
            return DeviceView(self._device, viewByCont)
        else:
            attrsMap = {attr:value}
            viewOjbect = self.findViewWithAttributes(attrsMap)
            return viewOjbect
    
    def findViewWithAttributes(self, attrMap = {"content-desc":"OK"}):
        '''
        Find the view by attribute:value pair;
        '''
        attrHashMap = HashMap()
    
        for key in attrMap.keys():
            attrHashMap.put(key, attrMap[key])
    
        viewRet = self._viewParser.FindViewByAttibutes(self._rootViewNode, attrHashMap)
        return DeviceView(self._device, viewRet)
    
    def findViewsWithAttributes(self, attrMap = {"content-desc":"OK"}):
        '''
        Find all the views by attribute:value pair;
        Support the regex pattern for the text search;
        
        return the matched view list;
        
        '''
        attrHashMap = HashMap()
    
        for key in attrMap.keys():
            attrHashMap.put(key, attrMap[key])
    
        viewRets = self._viewParser.FindViewsByAttibutes(self._rootViewNode, attrHashMap)
    
        dViewRets = []
        
        for v in viewRets:
            dViewRets.append(DeviceView(self._device, v))
        
        return dViewRets
    
 
class NDeviceViewInterface(DeviceViewInterface):
    '''
    Tailored for NDevice View Dump
    '''
    def __init__(self, device, deviceStr, autodump=False, ignoreuiautomatorkilled=False):
        DeviceViewInterface.__init__(self, device, deviceStr,autodump, ignoreuiautomatorkilled)
    
    def dump(self, sleep=1):
        '''
        Dumps the window content.
        
        Sleep is useful to wait some time before obtaining the new content when something in the
        window has changed.
        
        @type sleep: int
        @param sleep: sleep in seconds before proceeding to dump the content
        
        @return: return the root value of the 
        '''
        if(sleep > 0):
            MonkeyRunner.sleep(sleep)
        
        '''
        Using /dev/tty this works even on devices with no sdcard
        '''
        startTime = datetime.datetime.now()
        
        try:
            received = self._device.shell('/system/bin/uiautomator client')
        except:
            raise RuntimeError("ERROR: /system/bin/uiautomator client error occurs!")

        finishTime = datetime.datetime.now()
        
        timeDelta = finishTime - startTime
        
        self._logger.debug(timeDelta)
        
        if not received:            
            errMsg = 'ERROR: Empty UIAutomator dump was received'            
            self._logger.error(errMsg)
            raise RuntimeError(errMsg)

        '''received = received.encode('utf-8', 'ignore')'''
        
        if DEBUG:
            self.received = received
            print >> sys.stdout, self.received
        if DEBUG_RECEIVED:
            print >> sys.stderr, "received %d chars" % len(received)
            print >> sys.stderr
            print >> sys.stderr, repr(received)
            print >> sys.stderr
        onlyKilledRE = re.compile('[\n\S]*Killed[\n\r\S]*', re.MULTILINE)
        if onlyKilledRE.search(received):
            raise RuntimeError('''ERROR: UiAutomator output contains no valid information. UiAutomator was killed, no reason given.''')
 
        self._rootViewNode = self._viewParser.ParseToViewByStr(received)
        
        self._logger.info(self._rootViewNode)
        
        return self._rootViewNode

class ViewInterfaceFactory:
    
    @staticmethod
    def factory(ViewDumpMode,device, deviceStr):
        if ViewDumpMode == 'NType':
            return NDeviceViewInterface(device, deviceStr)
        else:
            return DeviceViewInterface(device, deviceStr)

class DeviceView:
    '''
    Device view to be operated;
    '''
    def __init__(self, device,viewObject):
        self._device = device
        self._viewObject = viewObject
        
    
    def touch(self, type=MonkeyDevice.DOWN_AND_UP, timeout=2):
        '''
        Touches the center of this View
        '''
        (x, y) = self.getCenter()
        if type == MonkeyDevice.DOWN_AND_UP:
            self._device.touch(x, y, MonkeyDevice.DOWN)
            time.sleep(50/1000.0)
            self._device.touch(x+10, y+10, MonkeyDevice.UP)
        else:
            self._device.touch(x, y, type)
        time.sleep(timeout)

    def getCenter(self):
        '''
        Gets the center coords of the View
        '''
        x = self._viewObject.getStartX()
        y = self._viewObject.getStartY()
        width = self._viewObject.getWidth()
        height = self._viewObject.getHeight()
        
        centerX = x + width / 2
        centerY = y + height / 2
        return (centerX, centerY)
    
    def swipeToUpperBoundary(self):
        '''
        swipe from center to upper boundary
        '''
        (x, y) = self.getCenter()
        y2 = self._viewObject.getStartY()

        self._device.drag((x,y),(x, 0), 1,10)
        
    def swipeToDownBoundary(self):
        '''
        swipe from center to down boundary
        '''
        (x, y) = self.getCenter()
        
        deviceHeight = int(self._device.getProperty('display.height')) 

        self._device.drag((x,y),(x, deviceHeight), 1,10)

    def swipeToLeft(self):
        '''
        swipe from right to left within the boundary of this view
        '''
        (x, y) = self.getCenter()
        x2 = self._viewObject.getStartX()
        width = self._viewObject.getWidth()
                
        self._device.drag((x2+width-1,y),(x2+1, y), 1,10)

    
    def swipeToRight(self):
        '''
        swipe from left to right within the boundary of this view
        '''
        (x, y) = self.getCenter()
        x2 = self._viewObject.getStartX()
        width = self._viewObject.getWidth()
                
        self._device.drag((x2+1,y),(x2+width-1, y), 1,10)
    
    def getSubViews(self):
        '''
        return the subviews contained
        '''    
        subViews = []
        
        subViewOjbects = self._viewObject.getChildrenViews()
        
        
        for element in subViewOjbects:  
            viewEle = DeviceView(self._device, element)
            subViews.append(viewEle)
        
        return subViews
    
    def isExist(self):
        return self._viewObject is not None
        
        
'''
Execution Tips: 
monkeyrunner -plugin C:\nst\NSTViewMngt\build\lib\NSTViewMngt.jar C:\nst\NSTRunner\src\core\view.py
monkeyrunner C:\nst\NSTRunner\src\core\view.py
'''
if __name__ == '__main__':
    print 'running'
