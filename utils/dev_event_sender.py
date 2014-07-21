#!/usr/bin/env python

# Import built-in modules
import os
import time

class DeviceEvtSender():
    def __init__(self, deviceId):
        self.deviceId = deviceId

    def commands(self, cmd):
        print '======= Execute Command: %s...' % cmd
        ret = os.system(cmd)
        return ret

    # Send event via input command
    def sendKeyEvent(self, key_code):
        cmd = 'adb -s %s shell input keyevent %d' % (self.deviceId, key_code)
        self.commands(cmd)

    def sendTapEvent(self, x, y):
        cmd = 'adb -s %s shell input tap %d %d' % (self.deviceId, x, y)
        self.commands(cmd)

    def sendSwipeEvent(self, x1, y1, x2, y2):
        cmd = 'adb -s %s shell input swipe %d %d %d %d'\
                % (self.deviceId, x1, y1, x2, y2)
        self.commands(cmd)

    def sendInputTextEvent(self, txt):
        cmd = "adb -s %s shell input text '%s'" % (self.deviceId, txt)
        self.commands(cmd)

    # Send event via sendevent command, don't recommanded
    def sendTouchEvent(self, p1, p2, p3):
        cmd = 'adb -s %s shell sendevent /dev/input/event0 %d %d %d'\
                % (self.deviceId, p1, p2, p3)
        self.commands(cmd)


# Test
if __name__ == '__main__':
    dev = DeviceEvtSender("c2a43b2")
    #dev.sendKeyEvent(26) # Powerkey
    #dev.sendTapEvent(100, 200)
    #dev.sendSwipeEvent(450, 400, 150, 400)
    #dev.sendInputTextEvent("Mytest")

