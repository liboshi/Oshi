#!/usr/bin/env python

# Import built-in modules
import os
import sys
import re

class LogAnalyzer():
    _pattern_anr = '(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3}\s-\s)+ANR\s+in\s+com\.*'
    _pattern_sys_crash = '(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3}\s-\s)+\*\*\s+System\s+appears\s+to\s+have\s+crashed*'

    def __init__(self, package, result_file):
        self.package = package
        self.result_file = result_file
        self.app_name = None
        self.anr_counter = 0
        self.sys_crash_counter = 0
        self.app_crash_counter = 0
        self.anr = []
        self.sys_crash = []
        self.app_crash = []

    def to_string(byte_data):
        return str(byte_data, 'latin1')

    def analyzer(self, file_name):
        with open(file_name, 'rb') as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                try:
                    line = self.to_string(line)
                except TypeError, err:
                    pass
                m_anr = re.match(self._pattern_anr, line)
                m_sys_crash = re.match(self._pattern_sys_crash, line)
                if m_anr:
                    self.anr_counter += 1
                    #self.anr.append(m_anr.group())
                    self.anr.append(line)
                if m_sys_crash:
                    self.sys_crash_counter += 1
                    #self.sys_crash.append(m_sys_crash.group())
                    self.sys_crash.append(line)

    def write_result(self):
        with open(self.result_file, 'a+') as fp:
            fp.write('======= %s\n' % self.package)
            fp.write('Application Not Response (ANR) number: %d\n' % self.anr_counter)
            fp.write('Details:\n')
            for item in self.anr:
                fp.write(item)
            fp.write('\n')
            fp.write('System crash number: %d\n' % self.sys_crash_counter)
            fp.write('Details:\n')
            for item in self.sys_crash:
                fp.write(item)
            fp.write('\n')
            fp.write('\n')


# Test
if __name__ == '__main__':
    tester = LogAnalyzer('com.android.calculator2')
    tester.analyzer(r'/home/bouli/android-monkey/com.android.calculator2.log')
