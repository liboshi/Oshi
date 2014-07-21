'''
************************************Description******************************************

Test case description. 

*****************************************************************************************
'''
import os
import sys

try:
    OSHI_HOME = os.environ['OSHI_HOME']
except KeyError:
    print >>sys.stderr, "%s: ERROR: OSHI_HOME not set in environment" % __file__
    sys.exit(1)

sys.path.append(OSHI_HOME + '/OSHIRunner/src')
sys.path.append(OSHI_HOME + '/OSHIRunner/cases')
sys.path.append(OSHI_HOME + '/OSHIRunner/cases/util')

from core.phone import Phone
from core.phone import ValueNotFoundException
from core.nstCaseBase import OSHICaseBase
from core.nstCaseBase import OSHICaseResult
from misc import UnlockNDevice
import Helpers

from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice


class ClassName(OSHICaseBase):
    def __init__(self):
        self._grouNO = '0000'
        self._caseNO = '000'
        super(ClassName, self).__init__(self._grouNO, self._caseNO)

    def setUp(self):
        super(ClassName, self).setUp()

        '''
        Unlock the device
        '''
        if(self.phone.getConfigItem('needunlock')=='1'):
            unlocker = UnlockNDevice(self.phone._device)
            unlocker.unlock()

        """ Insert brief description of the setup logic"""
        # Insert code to perform pre-condition steps

        self.phone.backToStartWindow()

    def tearDown(self):
        """ Insert brief description of the teardown logic"""
        # Insert code to perform clean up operations

        self.phone.pureBack(self)
        if not Helpers.forceStopAppWithPackageName(self, InsertPackageName):
            self._logger.warning("%s: tearDown: Cannot go back to application menu." % (self._grouNO + self._caseNO))

        super(ClassName, self).tearDown()

    def runTest(self):
        self._logger.info("1. Test step description ...")
        '''
        Test step1
        '''

        self._logger.info("2. Test step description ...")
        '''
        Test step2
        '''

    def main(self):
        '''
            setUp
        '''
        try:
            self.setUp()
        except RuntimeError, rte:
            self._logger.warning("RuntimeError occurs in setUp, Details: %s ." % (str(rte)))
        except Exception, err:
            self._logger.warning("Exception occurs in setUp, Details: %s ." % (str(err)))

        '''
            test Function
        '''
        try:
            self.runTest()
        except RuntimeError, rte:
            self._logger.error("RuntimeError occurs in runTest, Details: %s ." % (str(rte)))
            result = OSHICaseResult(msg = 'Failed!', isSuc = False)
            self.saveResult(result)
        except Exception, err:
            self._logger.error("Exception occurs in runTest, Details: %s ." % (str(err)))
            result = OSHICaseResult(msg = 'Failed!', isSuc = False)
            self.saveResult(result)
        else:
            result = OSHICaseResult(msg = 'Successful!', isSuc = True)
            self.saveResult(result)

        '''
            tearDown
        '''
        try:
            self.tearDown()
        except RuntimeError, rte:
            self._logger.warning("RuntimeError occurs in tearDown, Details: %s ." % (str(rte)))
        except Exception, err:
            self._logger.warning("Exception occurs in tearDown, Details: %s ." % (str(err)))


if __name__ == '__main__':
    testCase = ClassName()
    testCase.main()
