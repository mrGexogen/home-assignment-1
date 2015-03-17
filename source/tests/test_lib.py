import unittest
from mock import Mock

from ..lib import to_unicode, to_str, get_counters, COUNTER_TYPES, check_for_meta, fix_market_url, prepare_url


class LibTestCase(unittest.TestCase):
    def testUnicode(self):
        msg = u"Hello world"
        self.assertTrue(isinstance(to_unicode(msg), unicode))

    def testNotUnicode(self):
        msg = "42 "
        msg.encode('utf-16')
        self.assertFalse(isinstance(msg, unicode))
        self.assertTrue(isinstance(to_unicode(msg), unicode))

    def testNoneUnicode(self):
        self.assertIsNone(to_unicode(None))

    def testToStrUnicode(self):
        msg = u"Hello world"
        self.assertFalse(isinstance(to_str(msg), unicode))

    def testToStrNotUnicode(self):
        msg = "Hello world"
        self.assertFalse(isinstance(to_str(msg), unicode))

    def testToStrNone(self):
        self.assertIsNone(to_str(None))

    def testCounters(self):
        content = "src='www.google-analytics.com/ga.js.min'"
        self.assertEqual(len(get_counters(content)), 1)
        self.assertIn(get_counters(content)[0], [i[0] for i in COUNTER_TYPES])

    def testCountersAbsent(self):
        content = "src='www.wrath.com/ga.js.min'"
        self.assertEqual(len(get_counters(content)), 0)

    def testCountersNone(self):
        content = None
        self.assertEqual(len(get_counters(content)), 0)

    def testMetaNone(self):
        self.assertIsNone(check_for_meta(None, None))

    def testMeta(self):
        content = '<meta http-equiv="refresh" content="5;url=https://merchant.webmoney.ru/"><head>'
        self.assertEqual(check_for_meta(content, ''), 'https://merchant.webmoney.ru/')

    def testMetaIncorrectRedirect(self):
        content = '<meta http-equiv="refresh"><head>'
        self.assertIsNone(check_for_meta(content, ''))

    def testMetaIncorrectContent(self):
        content = '<meta http-equiv="refresh" content="url=https://merchant.webmoney.ru/"><head>'
        self.assertIsNone(check_for_meta(content, ''))

    def testMetaIncorrectUrl(self):
        content = '<meta http-equiv="refresh" content="2;https://merchant.webmoney.ru/"><head>'
        self.assertIsNone(check_for_meta(content, ''))

    def testMarketNone(self):
        self.assertIsNone(fix_market_url(42))

    def testMarket(self):
        url = 'market://search?q=pname:net.mandaria.tippytipper'
        self.assertEqual(fix_market_url(url),
                         'http://play.google.com/store/apps/search?q=pname:net.mandaria.tippytipper')

    def testPrepareUrlNone(self):
        self.assertIsNone(prepare_url(None))

    def testPrepareUrl(self):
        url = 'https://tech-mail.ru/#comment_id_17828'
        self.assertEqual('https://tech-mail.ru/%23comment_id_17828', prepare_url(url))
