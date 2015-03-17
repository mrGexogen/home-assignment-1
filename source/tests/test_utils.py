__author__ = 'serg'

import unittest
import mock
from ..lib.utils import daemonize

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


if __name__ == '__main__':
    unittest.main()
