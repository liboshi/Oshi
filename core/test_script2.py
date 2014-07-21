from testcase import OSHITestCase

class TestClass2(OSHITestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def main(self):
        self.pressKey.longPress('KEYCODE_VOLUME_UP')
        self.sleep(2)
        self.pressKey.longPress('KEYCODE_VOLUME_DOWN')

