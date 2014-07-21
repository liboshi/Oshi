#!/usr/bin/env python

'''
- OSHI Framework launcher
- Command Line parameters:
    --help       -- Print usage
    --testplan   -- Path to test plan xml file
                   Example: /home/<user name>/nst/testplan/testplan.xml
- For further questions, please contact nst tool team:
    --  xxx@nokia.com
    -- xxxx@nokia.com
'''

# Import built-in modules
import os
import sys
import re
import getopt

# Append needed paths to sys.path
paths = [\
        os.path.dirname(os.path.realpath(__file__))
        ]
paths.reverse()

for path in paths:
    if not path in sys.path:
        sys.path.insert(0, path)

# Import OSHI Framework modules
import core
from core.phone import Phone
from core.testcase_exceptions import TestException
from core import testrunner
# Import the monkeyrunner modules used by this program
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice

core.OSHIConf = {
        'testplan':        None,
        'mainPhoneId':     None,
        'refPhoneId':      None,
        'mainConn':        None,
        'refConn':         None,
        }

def usage():
    print __doc__

def parseCommandLine():
    try:
        optlst, args = getopt.getopt(sys.argv[1:], 'h', \
                ['help', 'testplan=', 'mainphone=', 'refphone'])
        if optlst == []:
            usage()
            sys.exit(2)

        for option, argument in optlst:
            if option in ['h', '--help']:
                usage()
                sys.exit()

            if option in ['--testplan']:
                assert os.path.isfile(argument), 'Invalid test plan file...'
                core.OSHIConf['testplan'] = argument

            if option in ['--mainphone']:
                assert argument, 'Please give the main phone ID...'
                core.OSHIConf['mainPhoneId'] = argument

            if option in ['--refphone']:
                assert argument, 'Please give the reference phone ID...'
                core.OSHIConf['refPhoneId'] = argument
    except getopt.GetoptError, err:
        print err
        usage()
        sys.exit(1)

if __name__ == '__main__':
    parseCommandLine()
    if core.OSHIConf['testplan']:
        pass

    if not core.OSHIConf['mainPhoneId']:
        raise TestException('Confuration Error: \
                Main phone ID is not given...')
    mainConn = Phone(core.OSHIConf['mainPhoneId'])
    if mainConn.createConnection(1, 60):
        core.OSHIConf['mainConn'] = mainConn
    # Initialize test runner
    testRunner = testrunner.OSHITestRunner()
    testRunner.run(core.OSHIConf['testplan'])
