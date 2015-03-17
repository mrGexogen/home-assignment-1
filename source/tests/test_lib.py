import unittest

from ..lib import to_unicode, to_str, get_counters, COUNTER_TYPES


class LibTestCase(unittest.TestCase):
    def testUnicode(self):
        msg = u"Hello world"
        self.assertTrue(isinstance(to_unicode(msg), unicode))

    def testNoneUnicode(self):
        msg = "42 "
        msg.encode('utf-16')
        self.assertFalse(isinstance(msg, unicode))
        self.assertTrue(isinstance(to_unicode(msg), unicode))

    def testToStrUnicode(self):
        msg = u"Hello world"
        self.assertFalse(isinstance(to_str(msg), unicode))

    def testToStrNoneUnicode(self):
        msg = "Hello world"
        self.assertFalse(isinstance(to_str(msg), unicode))

    def testCounters(self):
        content = "src='www.google-analytics.com/ga.js.min'"
        self.assertIn(get_counters(content).pop(), [i[0] for i in COUNTER_TYPES])

    def testCountersAbsent(self):
        content = "src='www.google-analytics.com/ga.js.min'"
        self.assertIn(get_counters(content).pop(), [i[0] for i in COUNTER_TYPES])