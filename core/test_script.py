#!/usr/bin/env python

import unittest
from testcase import OSHITestCase

class TestClass(OSHITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def main(self):
        self.monkeyBasic.execute()

