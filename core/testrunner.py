#!/usr/bin/env python

import os
import sys
import re
import time
import xml.dom.minidom

from testcase_exceptions import TestException

class OSHITestRunner():
    def __init__(self):
        self.__testData = None
        self.__currentCaseNo = None
        self.__currentGrouNo = None
        self.__testFiles = []
        self.__currentTestCase = []

    def run(self, testData):
        '''
            Run test case(s) according to given test data.
            Parameters:
                testData - test plan xml or
                           test case info [Directory of test script]
        '''
        self.__configureAndRun(testData)

    def __configureAndRun(self, testData):
        if os.path.exists(testData):
            if os.path.splitext(testData)[1] == '.xml':
                self.__runTestplan(testData)

    def __parseXml(self, xmlFile):
        domTree = xml.dom.minidom.parse(xmlFile)
        root = domTree.documentElement
        testCases = root.getElementsByTagName('testcase')
        return testCases

    def __runTestplan(self, testPlanFilePath):
        importedModule = None
        classToBeExecuted = None
        testCases = self.__parseXml(testPlanFilePath)
        for testCase in testCases:
            tcFilePath = testCase.getAttribute('location')
            tcClass = testCase.getAttribute('class')
            tcLoop = testCase.getAttribute('loop')
            if not tcLoop:
                tcLoop = 1
            tcLoop = int(tcLoop)
            if tcFilePath:
                if os.path.exists(tcFilePath):
                    tcDir = os.path.dirname(tcFilePath)
                    tcModule = os.path.splitext(os.path.basename(tcFilePath))[0]
                    importedModule = self.__importModule(tcDir, tcModule)
            classToBeExecuted = getattr(importedModule, tcClass)
            for i in range(tcLoop):
                print '############### Begin to run test case: (%s), Loop: (%s) ##########'\
                        % (tcClass, (i + 1))
                classToBeExecuted().main()
                print '############### Ending test case: (%s), Loop: (%s) ###############'\
                        % (tcClass, (i + 1))
                time.sleep(5)

    def __importModule(self, tcDir, tcModule):
        importedModule = None
        try:
            if not tcDir in sys.path:
                sys.path.append(tcDir)
            # Import the module
            importedModule = __import__(tcModule, globals(), locals())
        except Exception, importError:
            raise TestException('Unable to import module %s from %s' % \
                    tcModule, tcDir)
        else:
            return importedModule
        finally:
            if importedModule:
                del importedModule
            #if tcDir in sys.path:
            #    sys.path.remove(tcDir)
