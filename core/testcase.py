#!/usr/bin/env python

import unittest
import core

class OSHITestCase():
    def __init__(self):
        pass

    def __getattr__(self, attr):
        return getattr(core.OSHIConf['mainConn'], attr)
