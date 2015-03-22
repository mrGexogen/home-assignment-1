import unittest

import mock

from source.redirect_checker import main, main_loop


class RedirectCheckerTestCase(unittest.TestCase):
    def testMain(self):
        class Args:
            daemon = False
            pidfile = False
            config = ''

        with mock.patch('source.lib.utils.parse_cmd_args', return_value=Args()):
            with mock.patch('source.lib.utils.load_config_from_pyfile'):
                with mock.patch('logging.config.dictConfig'):
                    with mock.patch('source.redirect_checker.main_loop') as m:
                        main([1])
                        self.assertEqual(m.call_count, 1)

    def test_main_daemonize(self):
        class Args:
            daemon = True
            pidfile = False
            config = ''

        with mock.patch('source.lib.utils.parse_cmd_args', return_value=Args()):
            with mock.patch('source.lib.utils.daemonize') as m:
                with mock.patch('source.lib.utils.load_config_from_pyfile'):
                    with mock.patch('logging.config.dictConfig'):
                        with mock.patch('source.redirect_checker.main_loop'):
                            main([1])
                            self.assertEqual(m.call_count, 1)

    def test_main_pidfile(self):
        class Args:
            daemon = False
            pidfile = 1
            config = ''

        with mock.patch('source.lib.utils.parse_cmd_args', return_value=Args()):
            with mock.patch('source.lib.utils.create_pidfile') as m:
                with mock.patch('source.lib.utils.load_config_from_pyfile'):
                    with mock.patch('logging.config.dictConfig'):
                        with mock.patch('source.redirect_checker.main_loop'):
                            main([1])
                            self.assertEqual(m.call_count, 1)

    def test_loop_network_down(self):
        c = mock.Mock()
        c.WORKER_POOL_SIZE = 1
        process = mock.Mock()
        process.terminate = mock.Mock()
        with mock.patch('source.lib.utils.check_network_status', return_value=False):
            with mock.patch('multiprocessing.active_children', return_value=[process]):
                with mock.patch('source.lib.utils.spawn_workers'):
                    with mock.patch('time.sleep', side_effect=KeyboardInterrupt):
                        with self.assertRaises(KeyboardInterrupt):
                            main_loop(c)
        process.terminate.assert_called_once_with()

    def test_loop_network_ok_no_workers(self):
        c = mock.Mock()
        c.WORKER_POOL_SIZE = 1
        with mock.patch('source.lib.utils.check_network_status', return_value=True):
            with mock.patch('multiprocessing.active_children', return_value=[mock.Mock()]):
                with mock.patch('source.lib.utils.spawn_workers') as m:
                    with mock.patch('time.sleep', side_effect=KeyboardInterrupt):
                        with self.assertRaises(KeyboardInterrupt):
                            main_loop(c)
                            self.assertEqual(m.call_count, 0)

    def test_loop_network_ok_with_workers(self):
        c = mock.Mock()
        c.WORKER_POOL_SIZE = 2
        with mock.patch('source.lib.utils.check_network_status', return_value=True):
            with mock.patch('multiprocessing.active_children', return_value=[mock.Mock()]):
                with mock.patch('source.lib.utils.spawn_workers') as m:
                    with mock.patch('time.sleep', side_effect=KeyboardInterrupt):
                        with self.assertRaises(KeyboardInterrupt):
                            main_loop(c)
                            self.assertEqual(m.call_count, 1)