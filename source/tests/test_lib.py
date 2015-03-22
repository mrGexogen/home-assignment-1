import unittest

import mock

import source.lib


class LibTestCase(unittest.TestCase):
    def testUnicode(self):
        msg = u"Hello world"
        self.assertIsInstance(source.lib.to_unicode(msg), unicode)
        self.assertEqual(source.lib.to_unicode(msg), u"Hello world")

    def testNotUnicode(self):
        msg = "42 "
        msg.encode('utf-16')
        self.assertIsInstance(source.lib.to_unicode(msg), unicode)
        self.assertEqual(source.lib.to_unicode(msg), u"42 ")

    def testNoneUnicode(self):
        self.assertIsNone(source.lib.to_unicode(None))

    def testToStrUnicode(self):
        msg = u"Hello world"
        self.assertIsInstance(source.lib.to_str(msg), str)
        self.assertEqual(source.lib.to_str(msg), "Hello world")

    def testToStrNotUnicode(self):
        msg = "Hello world"
        self.assertFalse(isinstance(source.lib.to_str(msg), unicode))
        self.assertEqual(source.lib.to_str(msg), "Hello world")

    def testToStrNone(self):
        self.assertIsNone(source.lib.to_str(None))

    def testCounters(self):
        content = "src='www.google-analytics.com/ga.js.min'"
        self.assertEqual(len(source.lib.get_counters(content)), 1)
        self.assertIn(source.lib.get_counters(content)[0], [i[0] for i in source.lib.COUNTER_TYPES])

    def testCountersAbsent(self):
        content = "src='www.wrath.com/ga.js.min'"
        self.assertEqual(len(source.lib.get_counters(content)), 0)

    def testCountersNone(self):
        content = None
        self.assertEqual(len(source.lib.get_counters(content)), 0)

    def testMetaNone(self):
        self.assertIsNone(source.lib.check_for_meta(None, None))

    def testMeta(self):
        content = '<meta http-equiv="refresh" content="5;url=https://merchant.webmoney.ru/"><head>'
        self.assertEqual(source.lib.check_for_meta(content, ''), 'https://merchant.webmoney.ru/')

    def testMetaIncorrectRedirect(self):
        content = '<meta http-equiv="refresh"><head>'
        self.assertIsNone(source.lib.check_for_meta(content, ''))

    def testMetaIncorrectContent(self):
        content = '<meta http-equiv="refresh" content="url=https://merchant.webmoney.ru/"><head>'
        self.assertIsNone(source.lib.check_for_meta(content, ''))

    def testMetaIncorrectUrl(self):
        content = '<meta http-equiv="refresh" content="2;https://merchant.webmoney.ru/"><head>'
        self.assertIsNone(source.lib.check_for_meta(content, ''))

    def testMarketNone(self):
        self.assertIsNone(source.lib.fix_market_url(42))

    def testMarket(self):
        url = 'market://search?q=pname:net.mandaria.tippytipper'
        self.assertEqual(source.lib.fix_market_url(url),
                         'http://play.google.com/store/apps/search?q=pname:net.mandaria.tippytipper')

    def testPrepareUrlNone(self):
        self.assertIsNone(source.lib.prepare_url(None))

    def testPrepareUrl(self):
        url = 'https://tech-mail.ru/#comment_id_17828'
        self.assertEqual('https://tech-mail.ru/%23comment_id_17828', source.lib.prepare_url(url))

    def testPycurl(self):
        content = "Hi 42"
        redirectUrl = "ya.ru"

        mockCurl = mock.Mock()
        mockCurl.getinfo.return_value = redirectUrl

        mockIO = mock.Mock()
        mockIO.getvalue.return_value = content

        with mock.patch("pycurl.Curl", mock.Mock(return_value=mockCurl)):
            with mock.patch("StringIO.StringIO", mock.Mock(return_value=mockIO)):
                self.assertEqual(source.lib.make_pycurl_request('ya.ru', 1)[1], redirectUrl)

    def testPycurlUseragent(self):
        userAgent = "Mozila"

        mockCurl = mock.Mock()
        mockSetopt = mock.Mock()
        mockCurl.setopt = mockSetopt

        with mock.patch("pycurl.Curl", mock.Mock(return_value=mockCurl)):
            source.lib.make_pycurl_request('ya.ru', 1, userAgent)
            mockSetopt.assert_any_call(source.lib.pycurl.USERAGENT, userAgent)

    def testPycurlNoRedirect(self):
        mockCurl = mock.Mock()
        mockCurl.getinfo.return_value = None

        with mock.patch("pycurl.Curl", mock.Mock(return_value=mockCurl)):
            self.assertEqual(source.lib.make_pycurl_request('ya.ru', 1)[1], None)

    def testGetUrl(self):
        content = "Hi 42"
        url = "market://ya.ru"
        with mock.patch("source.lib.make_pycurl_request", mock.Mock(return_value=(content, url))):
            self.assertTupleEqual((u'http://play.google.com/store/apps/ya.ru', 'http_status', 'Hi 42'),
                                  source.lib.get_url('', 1))

    def testGetUrlMatch(self):
        content = "Hi 42"
        url = "http://odnoklassniki.ru/st.redirect"
        with mock.patch("source.lib.make_pycurl_request", mock.Mock(return_value=(content, url))):
            self.assertTupleEqual((None, None, 'Hi 42'), source.lib.get_url('', 1))

    def testGetUrlNone(self):
        content = "Hi 42"
        url = None
        with mock.patch("source.lib.make_pycurl_request", mock.Mock(return_value=(content, url))):
            self.assertTupleEqual((None, None, 'Hi 42'), source.lib.get_url('', 1))

    def testGetUrlMeta(self):
        content = "Hi 42"
        url = None
        with mock.patch("source.lib.make_pycurl_request", mock.Mock(return_value=(content, url))):
            with mock.patch("source.lib.check_for_meta", mock.Mock(return_value="q.com")):
                self.assertTupleEqual(('q.com', 'meta_tag', 'Hi 42'), source.lib.get_url('', 1))

    def testGetUrlEx(self):
        with mock.patch("source.lib.make_pycurl_request", mock.Mock(side_effect=ValueError())):
            self.assertTupleEqual(('', 'ERROR', None), source.lib.get_url('', 1))

    def testRedHist(self):
        with mock.patch("source.lib.get_url", mock.Mock(side_effect=[('q.com', '', ''), (None, '', '')])):
            self.assertTupleEqual(([''], ['ya.ru', 'q.com'], []), source.lib.get_redirect_history('ya.ru', 1, 2))

    def testRedHistError(self):
        with mock.patch("source.lib.get_url", mock.Mock(side_effect=[('q.com', '', ''), ('Non', 'ERROR', '')])):
            self.assertTupleEqual((['', 'ERROR'], ['ya.ru', 'q.com', 'Non'], []),
                                  source.lib.get_redirect_history('ya.ru', 1, 2))

    def testRedHistLen(self):
        with mock.patch("source.lib.get_url", mock.Mock(side_effect=[('q.com', '', ''), ('Non', 'ERROR', '')])):
            self.assertTupleEqual(([], ['ya.ru'], []), source.lib.get_redirect_history('ya.ru', 1, 0))

    def testRedHistRE(self):
        self.assertTupleEqual(([], [u'http://odnoklassniki.ru/'], []),
            source.lib.get_redirect_history('http://odnoklassniki.ru/', 1, 0))
