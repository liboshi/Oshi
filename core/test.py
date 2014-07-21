#!/uer/bin/env python

class Test():
    @classmethod
    def say(cls, name):
        print 'Hello %s' % name

    def sayHello(self, name):
        print 'Hi %s' % name

if __name__ == '__main__':
    test = getattr(Test, 'say')
    test('LiBoshi')
    obj = Test()
    a = getattr(obj, 'sayHello')
    a('LiBoshi')
