#!/usr/bin/env python

import sys
import re
import os
import subprocess

# How to extract application list from phone software.
# Resolved.

APP_EXCLUDE_LIST = [
            'com\.qualcomm.*',
        ]

def get_devices():
    _devcie_list = []
    proc = None
    adb_cmd = ['adb', 'devices']
    try:
        proc = subprocess.Popen(adb_cmd, stdout = subprocess.PIPE)
        _device_list = proc.stdout.read().strip()
    except Exception, err:
        print 'Error: %s' % err
    _device_list = _device_list.split('\n')
    del _device_list[0]
    _device_list = [item.split('\t')[0] for item in _device_list]
    return _device_list

def extract_app_list(device_id = None):
    if device_id == None:
        print 'Device id is None...'
        sys.exit()
    _app_list = []
    _app_list_tmp = None
    proc = None
    adb_cmd = ['adb', '-s', device_id, 'shell', 'pm', 'list', 'packages']
    try:
        proc = subprocess.Popen(adb_cmd, stdout = subprocess.PIPE)
        _app_list_tmp = proc.stdout.read().strip()
    except Exception, err:
        print 'Error: %s' % err
    if _app_list_tmp != '':
        _app_list_tmp = [item.split(':')[1] for item in _app_list_tmp.split('\r\n')]
        for pattern_app in APP_EXCLUDE_LIST:
            for app in _app_list_tmp:
                if not re.match(pattern_app, app):
                    _app_list.append(app)
    del _app_list_tmp
    return _app_list

# Test
if __name__ == '__main__':
    devices = get_devices()
    for device in devices:
        app_list = extract_app_list(device_id = device)
        print app_list
