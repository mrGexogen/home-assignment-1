import unittest

import mock

from source.redirect_checker import main, main_loop


class RedirectCheckerTestCase(unittest.TestCase):
    def testMain(self):
        class Args:
            daemon = True
            pidfile = 1
            config = ''

        with mock.patch('source.lib.utils.parse_cmd_args', return_value=Args()):
            with mock.patch('source.lib.utils.create_pidfile'):
                with mock.patch('source.lib.utils.load_config_from_pyfile'):
                    with mock.patch('logging.config.dictConfig'):
                        with mock.patch('source.redirect_checker.main_loop') as m:
                            main([1])
                            self.assertEqual(m.call_count, 1)

    def testMainNone(self):
        class Args:
            daemon = False
            pidfile = None
            config = ''

        with mock.patch('source.lib.utils.parse_cmd_args', return_value=Args()):
            with mock.patch('source.lib.utils.create_pidfile'):
                with mock.patch('source.lib.utils.load_config_from_pyfile'):
                    with mock.patch('logging.config.dictConfig'):
                        with mock.patch('source.redirect_checker.main_loop') as m:
                            main([1])
                            self.assertEqual(m.call_count, 1)

    def testLoop(self):
        c = mock.Mock()
        c.WORKER_POOL_SIZE = 1
        with mock.patch('source.lib.utils.check_network_status', side_effect=[True, True, False, Exception()]):
            with mock.patch('multiprocessing.active_children', side_effect=[[], [mock.Mock()], [mock.Mock()]]):
                with mock.patch('source.lib.utils.spawn_workers'):
                    with mock.patch('time.sleep') as m:
                        try:
                            main_loop(c)
                        except:
                            self.assertEqual(m.call_count, 3)