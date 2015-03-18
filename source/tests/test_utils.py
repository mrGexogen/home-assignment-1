import urllib2

__author__ = 'serg'

import unittest

import mock

from ..lib.utils import daemonize, create_pidfile, load_config_from_pyfile, parse_cmd_args, get_tube, spawn_workers, \
    check_network_status


class UtilsTestCase(unittest.TestCase):
    def test_daemonize_not_0(self):
        pid = 22
        m_os_exit = mock.Mock()
        with mock.patch("os.fork", mock.Mock(return_value=pid)):
            with mock.patch("os._exit", m_os_exit):
                daemonize()
        m_os_exit.assert_called_once_with(0)

    def test_daemonize_0_above_0(self):
        pid_1 = 0
        pid_2 = 3
        m_os_exit = mock.Mock("os.exit")
        m_os_setsid = mock.Mock()
        with mock.patch("os.fork", mock.Mock(side_effect=[pid_1, pid_2])):
            with mock.patch("os._exit", m_os_exit):
                with mock.patch("os.setsid", m_os_setsid):
                    daemonize()
        m_os_exit.assert_called_once_with(0)
        m_os_setsid.assert_called_once_with()


    def test_daemonize_except_1(self):
        with mock.patch("os.fork", mock.Mock(side_effect=OSError)):
            try:
                daemonize()
            except Exception as ex:
                self.assertEqual(type(ex), TypeError)

    def test_daemonize_except_2(self):
        pid_1 = 0
        pid_2 = 3
        m_os_setsid = mock.Mock()
        with mock.patch("os.fork", mock.Mock(side_effect=[0, OSError])):
            with mock.patch("os.setsid", m_os_setsid):
                try:
                    daemonize()
                except Exception as ex:
                    self.assertEqual(type(ex), TypeError)


    def test_daemonize_0_below_0(self):
        pid_1 = 0
        pid_2 = -3
        m_os_exit = mock.Mock("os.exit")
        m_os_setsid = mock.Mock("os.setsid")
        with mock.patch("os.fork", mock.Mock(side_effect=[pid_1, pid_2])):
            with mock.patch("os._exit", m_os_exit):
                with mock.patch("os.setsid", m_os_setsid):
                    daemonize()
        m_os_exit.assert_has_calls([])
        m_os_setsid.assert_called_once_with()

    def test_create_pidfile(self):
        pid = 42
        m_open = mock.mock_open()
        with mock.patch("__builtin__.open", m_open, create=True):
            with mock.patch('os.getpid', mock.Mock(return_value=pid)):
                create_pidfile('/file/path')
        m_open.assert_called_once_with('/file/path', 'w')
        m_open().write.assert_called_once_with(str(pid))

    def test_load_config_from_pyfile(self):
        def side_effect(path, vars):
            vars.__setitem__("HELLO", "friend")
            vars.__setitem__("bye", "friend")

        m_exec = mock.Mock(side_effect=side_effect)
        with mock.patch("__builtin__.execfile", m_exec, create=True):
            cfg = load_config_from_pyfile("bla/bla")
        self.assertEqual(getattr(cfg, "HELLO"), "friend")
        self.assertFalse(hasattr(cfg, "bye"))

    def test_parse_cmd_args(self):
        args = ["-c", "path"]
        parsed = parse_cmd_args(args=args)
        self.assertEqual(parsed.config, "path")

    def test_get_tube(self):
        m_queue = mock.Mock(return_value=1)
        m_tarantul = mock.Mock(return_value=m_queue)
        host = "dfgsdfg"
        port = 1312
        space = 1234
        name = "ssdf"
        with mock.patch("lib.utils.tarantool_queue.Queue", m_tarantul):
            get_tube(host, port, space, name)
        m_tarantul.assert_called_once_with(host=host, port=port, space=space)
        m_queue.tube.assert_called_once_with(name)

    def testSpawn(self):
        p = mock.Mock()
        with mock.patch('multiprocessing.Process', p):
            spawn_workers(2, None, None, None)
        self.assertEqual(2, p.call_count)

    def testUrlCheck(self):
        with mock.patch('urllib2.urlopen'):
            self.assertTrue(check_network_status('ya.com', 1))

    def testUrlCheckExcept(self):
        with mock.patch('urllib2.urlopen', side_effect=urllib2.URLError('!')):
            self.assertFalse(check_network_status('ya.com', 1))


if __name__ == '__main__':
    unittest.main()
