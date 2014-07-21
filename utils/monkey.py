#!/usr/bin/env python

# Import built-in modules
import os
import sys
import re
import logging
import logging.handlers
import time
import random
import optparse
import subprocess
import json

# Import monkey modules
import monkey_config
from log_analyzer import LogAnalyzer
from dev_event_sender import DeviceEvtSender

# Global settings

# Execution time limitation
EXECUTION_DURATION = 120 * 60
COUNT = str(int((EXECUTION_DURATION * 1000 / 300) + 0.5) + 1000)
APP_BLACK_LIST = 'app_black_list.json'
APP_WHITE_LIST = 'app_white_list.json'
APP_BALANCE_LIST = 'app_balance_list.json'
TIME_LABEL = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
LOG_FOLDER = './log_' + TIME_LABEL
RESULT_FILE = './result_' + TIME_LABEL + '.log'

supported_proto_list = ['N1', 'Athena']
init_optparse = optparse.OptionParser(usage = 'monkeyrunner monkey.py [options]')

# DUT
group = init_optparse.add_option_group('Device options')
group.add_option('-d', '--device-id',
        default = None,
        dest = 'deviceId', help = 'DUT connection id <$adb devices>')
group.add_option('--proto-type',
        default = None,
        dest = '--proto-type', help = 'Specified proto type when running package level monkey test')
group.add_option('--count',
        dest = 'COUNT', help = 'Total number of events')

# General
group = init_optparse.add_option_group('General options')
group.add_option('-v',
        dest = 'verbosity', help = 'Verbosity level')

# Evnets
group = init_optparse.add_option_group('Events options')
group.add_option('-s',
        dest = '-s', help = '<seed> Seed value for pseudo-random number generator')
group.add_option('--throttle',
        default = 300,
        dest = '--throttle', help = '<milliseconds> Inserts a fixed delay between events')
group.add_option('--pct-touch',
        dest = '--pct-touch', help = '<percent> Adjust percentage of touch events')
group.add_option('--pct-motion',
        dest = '--pct-motion', help = '<percent> Adjust percentage of motion events')
group.add_option('--pct-trackball',
        dest = '--pct-trackball', help = '<percent> Adjust percentage of trackball event')
group.add_option('--pct-nav',
        dest = '--pct-nav', help = '<percent> Adjust percentage of "basic" navigation events')
group.add_option('--pct-majornav',
        dest = '--pct-majornav', help = '<percent> Adjust percentage of "major" navigation event')
group.add_option('--pct-syskeys',
        dest = '--pct-syskeys', help = '<percent> Adjust percentage of "system" key events')
group.add_option('--pct-appswitch',
        dest = '--pct-appswitch', help = '<percent> Adjust percentage of activity launches')
group.add_option('--pct-anyevent',
        dest = '--pct-anyevent', help = '<percent> Adjust percentage of other types of events')

# Constraints
group = init_optparse.add_option_group('Constraints options')
group.add_option('--packages',
        default = None,
        dest = 'packages', help = '<allowed-package-name> Specify one packages')
group.add_option('-c',
        dest = '-c', help = 'main-category Specify one or more categories')
group.add_option('--system',
        default = False,
        action = 'store_true',
        dest = 'system', help = 'Execute system level monkey test')

# Debugging
debugging_desc = 'More details, please refer to: http://developer.android.com/tools/help/monkey.html'
group = init_optparse.add_option_group('Debugging options')
group.add_option('--dbg-no-events',
        dest = '--dbg-no-events', help = debugging_desc)
group.add_option('--hprof',
        dest = '--hprof', help = debugging_desc)
group.add_option('--ignore-crashes',
        dest = '--ignore-crashes', help = debugging_desc)
group.add_option('--ignore-timeouts',
        dest = '--ignore-timeouts', help = debugging_desc)
group.add_option('--ignore-security-exceptions',
        dest = '--ignore-security-exceptions', help = debugging_desc)
group.add_option('--kill-process-after-error',
        dest = '--kill-process-after-error', help = debugging_desc)

# Logging
def log_config(log_file):
    if not os.path.exists(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)
    log_filename = os.path.join(LOG_FOLDER, log_file + '.log')
    logger = logging.getLogger('Android-Monkey-Logger')
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes = 1024 * 1024 * 10, backupCount = 7)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return (logger, handler)

# Analysis log file
def analysis_log(package):
    log_analyzer = LogAnalyzer(package, RESULT_FILE)
    log_file_list = os.listdir(LOG_FOLDER)
    for log_file in log_file_list:
        if log_file.startswith(package):
            print '======= Analysis Monkey test log: (%s)...' % log_file
            log_analyzer.analyzer(os.path.join(LOG_FOLDER, log_file))
    log_analyzer.write_result()

# Get black_list
def get_app_black_list():
    with open(APP_BLACK_LIST, 'r') as fp:
        jp = json.load(fp)
        return jp['black_list']

# Get white_list
def get_app_white_list():
    with open(APP_WHITE_LIST, 'r') as fp:
        jp = json.load(fp)
        return jp['white_list']

# Get balance_list
def get_app_balance_list():
    if not os.path.exists(APP_BALANCE_LIST):
        with open(APP_BALANCE_LIST, 'w') as fp:
            fp.writelines('{"balance_list": []}')
            fp.close()
    with open(APP_BALANCE_LIST, 'r') as fp:
        jp = json.load(fp)
        return jp['balance_list']

# Set balance_list
def set_app_balance_list(package):
    app_balance_list = []
    if not os.path.exists(APP_BALANCE_LIST):
        with open(APP_BALANCE_LIST, 'w') as fp:
            fp.writelines('{"balance_list": []}')
            fp.close()
    with open(APP_BALANCE_LIST, 'r') as fp:
        jp = json.load(fp)
        app_balance_list = jp['balance_list']
        app_balance_list.append(package)
    with open(APP_BALANCE_LIST, 'w') as fp:
        json.dump({'balance_list': app_balance_list}, fp)

# Get files from dropbox
def get_files_from_dropbox(deviceId, package):
    print '======= Get log files from dropbox...'
    if not os.path.exists(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)
    folder = LOG_FOLDER + r'/' + package
    if not os.path.exists(folder):
        os.mkdir(folder)
    ret = os.system('adb -s %s pull /data/system/dropbox %s' % (deviceId, folder))
    ret = os.system('adb -s %s pull /data/tombstones %s' % (deviceId, folder))
    ret = os.system('adb -s %s pull /storage/sdcard1/logs %s' % (deviceId, folder))
    return ret

# Delete all files in dropbox
def delete_all_files_in_dropbox(deviceId):
    print '======= Delete all files in dropbox...'
    ret = os.system('adb -s %s shell rm -r /data/system/dropbox/' % deviceId)
    ret = os.system('adb -s %s shell rm -r /data/tombstones/' % deviceId)
    ret = os.system('adb -s %s shell rm -r /storage/sdcard1/logs/' % deviceId)
    return ret

class MonkeyBasic():
    def __init__(self, device_id, package, count, logger):
        print '======= Execution start ======='
        self.exec_count = 0
        self.start_time = time.time()
        self.deviceId = device_id
        self.package = package
        self.count = count
        self.logger = logger
        self.extra_args = None
        self.packages = None
        self.parseCommandLine()

    def parseCommandLine(self):
        options, args = init_optparse.parse_args()
        self.extra_args = vars(options)
        self.extra_args.pop('deviceId')
        self.extra_args.pop('COUNT')
        self.extra_args.pop('system')
        self.extra_args.pop('--proto-type')
        self.packages = self.extra_args.pop('packages')

    def command(self):
        adb_cmd = ['adb', '-s', str(self.deviceId), 'shell', 'monkey']
        args_lst = []
        [args_lst.extend([str(k), str(v)]) for k, v in self.extra_args.items() if v]
        if self.package:
            args_lst.extend(['-p', self.package])
        if self.packages:
            args_lst.extend(['-p ' + item.strip() for item in self.packages.split(', ')])
        args_lst.append('-v -v')
        args_lst.append(self.count)
        args_lst.append('--bugreport')
        adb_cmd.extend(args_lst)
        return adb_cmd

    def execute(self):
        self.exec_count += 1
        ver_str = None
        adb_cmd = self.command()
        try:
            proc = subprocess.Popen(adb_cmd, stdout = subprocess.PIPE)
        except ValueError, err:
            print 'Error: %s' % err
        while proc.poll() == None:
            ver_str = proc.stdout.readline().strip()
            # Console output
            # print ver_str
            self.logger.info(ver_str)
            current_time = time.time()
            if (current_time - self.start_time > EXECUTION_DURATION) or \
                    (self.exec_count > 500):
                self.terminate(proc)
                time.sleep(3)
                self.stop()
                return 1
        else:
            current_time = time.time()
            if (current_time - self.start_time) < 60:
                print 'This package maybe not be launched...'
                if self.package:
                    self.update_app_black_list(self.package)
                return 2
            else:
                print '======= Resume'
                self.logger.info(ver_str)
                return 0
    
    def update_app_black_list(self, package):
        app_black_list = []
        with open(APP_BLACK_LIST, 'r') as fp:
            jp = json.load(fp)
            app_black_list = jp['black_list']
            app_black_list.append(package)
        with open(APP_BLACK_LIST, 'w') as fp:
            json.dump({'black_list': app_black_list}, fp)

    def stop(self):
        print '======= Stop current monkey testing...'
        cmd = '''
            adb -s %s shell ps | awk '/com\.android\.commands\.monkey/ { system ("adb -s %s shell kill " $2) }'
        ''' % (self.deviceId, self.deviceId)
        ret = os.system(cmd)
        return ret

    def force_stop_app(self):
        print '======= Force stop running package: (%s)...' % self.package
        ret = os.system('adb -s %s shell am force-stop %s'
                        % (self.deviceId, self.package))
        return ret

    def terminate(self, proc):
        print '======= Terminate the subprocess...'
        try:
            if proc:
                proc.terminate()
        except OSError, err:
            pass

    def resume(self, package):
        self.execute(package)

    def reboot(self):
        print '======= Reboot the device: (%s)...' % self.deviceId
        ret = os.system('adb -s %s reboot' % self.deviceId)
        return ret

    def wait_for_device(self):
        print '======= Wait for the device: (%s)...' % self.deviceId
        ret = os.system('adb -s %s wait-for-device' % self.deviceId)
        print '======= The device: (%s) is online...' % self.deviceId
        return ret

    def check_device_is_ready(self):
        print '======= Check Device (%s) is ready...' % self.deviceId
        result = 0
        proc = None
        temp_list = None
        adb_cmd = ['adb', '-s', self.deviceId, 'shell', 'getprop']
        pattern = '\[sys\.boot_completed\]:\s\[1\]'
        while True:
            try:
                proc = subprocess.Popen(adb_cmd, stdout = subprocess.PIPE)
                temp_list = proc.stdout.read().strip()
                for item in temp_list.split('\r\n'):
                    if re.match(pattern, item):
                        result = 1
                        break
            except Exception, err:
                print 'Error: %s' % err
                break

            if result == 1:
                print '======= Device (%s) is ready...' % self.deviceId
                break
            else:
                time.sleep(5)
        del temp_list

    def logcat_trigger(self):
        print '======= Start Logcat...'
        cmd = 'adb -s %s logcat -v time' % self.deviceId
        ret = os.system(cmd)
        return ret

    def logcat_cleaner(self):
        print '======= Clean the logcat output...'
        cmd = 'adb -s %s logcat -c' % self.deviceId
        ret = os.system(cmd)
        return ret

class CheckBugreport():
    def __init__(self):
        pass

    def pull_bugreport_to_local(self, local_file):
        pass

    def export_html_bugreport(self):
        pass

    def export_overall_report(self):
        pass

def main():
    options, args = init_optparse.parse_args()
    extra_args = vars(options)
    device = extra_args.pop('deviceId')
    is_sys_test = extra_args.pop('system')
    proto_type = extra_args.pop('--proto-type')
    if device == None:
        print '======= PLEASE SPECIFIED DEVICE ID ======='
        sys.exit()
    exec_done = 0
    if is_sys_test:
        delete_all_files_in_dropbox(device)
        print '======= System level Monkey test on Device %s...' % device
        exec_done = 0
        (logger, handler) = log_config('com.android.systemtest')
        mb = MonkeyBasic(device, None, COUNT, logger)
        while True:
            if exec_done == 0:
                exec_done = mb.execute()
            else:
                break
            time.sleep(3)
        print '======= System level Monkey test Done...'
        logger.removeHandler(handler)
        analysis_log('com.android.systemtest')
        get_files_from_dropbox(device, 'com.android.systemtest')
        delete_all_files_in_dropbox(device)
    else:
        if proto_type not in supported_proto_list:
            print '======= UNSUPPORTED PROTP TYPE ======='
            sys.exit()
        delete_all_files_in_dropbox(device)
        app_list = monkey_config.extract_app_list(device_id = device)
        app_white_list = get_app_white_list()
        devEvtSender = DeviceEvtSender(device)
        for package in app_list:
            if package in app_white_list:
                balance_list = get_app_balance_list()
                if package in balance_list:
                    print '======= This package has run in other device...'
                else:
                    set_app_balance_list(package)
                    print '======= Package Monkey test: (%s)...' % package
                    exec_done = 0
                    (logger, handler) = log_config(package)
                    mb = MonkeyBasic(device, package, COUNT, logger)
                    while True:
                        if exec_done == 0:
                            exec_done = mb.execute()
                        else:
                            break
                        time.sleep(3)
                    print '======= Package (%s) Monkey test Done...' % package
                    logger.removeHandler(handler)
                    analysis_log(package)
                    get_files_from_dropbox(device, package)
                    delete_all_files_in_dropbox(device)
                    time.sleep(2)
                    mb.reboot()
                    mb.wait_for_device()
                    mb.check_device_is_ready()
                    time.sleep(10)
                    if proto_type == 'N1':
                        devEvtSender.sendSwipeEvent(450, 400, 150, 400)
                    elif proto_type == 'Athena':
                        devEvtSender.sendSwipeEvent(200, 700, 200, 100)
                        time.sleep(2)
                        devEvtSender.sendInputTextEvent("201449")
                    time.sleep(5)

if __name__ == '__main__':
    main()
    '''
    # Test reboot
    device = "ff09ed"
    devEvtSender = DeviceEvtSender(device)
    mb = MonkeyBasic(device, None, COUNT, None)
    mb.reboot()
    mb.wait_for_device()
    mb.check_device_is_ready()
    time.sleep(10)
    devEvtSender.sendSwipeEvent(200, 700, 200, 100)
    time.sleep(2)
    devEvtSender.sendInputTextEvent("201449")
    '''


