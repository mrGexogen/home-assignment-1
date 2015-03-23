import unittest

import mock
from tarantool import DatabaseError

from source.lib.worker import get_redirect_history_from_task, worker


__author__ = 'gexogen'


class WorkerTestCase(unittest.TestCase):
    def test_redirect(self):
        m_data = {'url': 'ya1.ru', 'id': 1, 'url_id': 1}

        class task:
            data = m_data
            task_id = 1

        with mock.patch('source.lib.get_redirect_history', return_value=([], ['ya1.ru'], [])):
            self.assertFalse(get_redirect_history_from_task(task(), 1)[0])

    def test_redirect_suspicious(self):
        m_data = {'url': 'ya1.ru', 'id': 1, 'url_id': 1, 'suspicious': True}

        class task:
            data = m_data
            task_id = 1

        with mock.patch('source.lib.get_redirect_history', return_value=([], ['ya1.ru'], [])):
            self.assertIn('suspicious', get_redirect_history_from_task(task(), 1)[1])

    def test_redirect_error(self):
        m_data = {'url': 'ya1.ru', 'id': 1, 'url_id': 1, 'suspicious': True}

        class task:
            data = m_data
            task_id = 1

        with mock.patch('source.lib.get_redirect_history', return_value=(['ERROR'], ['ya1.ru'], [])):
            self.assertTrue(get_redirect_history_from_task(task(), 1)[0])

    def test_worker(self):
        class task:
            task_id = 1
            ack = mock.Mock()
            meta = mock.Mock(return_value={'pri': 1})

        class tube:
            opt = {'tube': 1}
            queue = mock.Mock()
            take = mock.Mock(side_effect=[task(), None])
            put = mock.Mock()

        ex = mock.Mock(side_effect=[1, 1, 0])
        with mock.patch('source.lib.utils.get_tube', return_value=tube()):
            with mock.patch('source.lib.worker.get_redirect_history_from_task', side_effect=[(True, (1, 2))]):
                with mock.patch('os.path.exists', ex):
                    worker(mock.Mock(), 1)
        self.assertEqual(ex.call_count, 3)

    def test_worker_except(self):
        class task:
            task_id = 1
            ack = mock.Mock(side_effect=DatabaseError())
            meta = mock.Mock(return_value={'pri': 1})

        class tube:
            opt = {'tube': 1}
            queue = mock.Mock()
            take = mock.Mock(side_effect=[task(), None])
            put = mock.Mock()

        ex = mock.Mock(side_effect=[1, 1, 0])
        with mock.patch('source.lib.utils.get_tube', return_value=tube()):
            with mock.patch('source.lib.worker.get_redirect_history_from_task', side_effect=[(True, (1, 2))]):
                with mock.patch('os.path.exists', ex):
                    worker(mock.Mock(), 1)
        self.assertEqual(ex.call_count, 3)

    def test_worker_noinput(self):
        class task:
            task_id = 1
            ack = mock.Mock()
            meta = mock.Mock(return_value={'pri': 1})

        class tube:
            opt = {'tube': 1}
            queue = mock.Mock()
            take = mock.Mock(side_effect=[task(), None])
            put = mock.Mock()

        ex = mock.Mock(side_effect=[1, 1, 0])
        with mock.patch('source.lib.utils.get_tube', return_value=tube()):
            with mock.patch('source.lib.worker.get_redirect_history_from_task', side_effect=[(False, (1, 2))]):
                with mock.patch('os.path.exists', ex):
                    worker(mock.Mock(), 1)
        self.assertEqual(ex.call_count, 3)

    def test_worker_result(self):
        class task:
            task_id = 1
            ack = mock.Mock()
            meta = mock.Mock(return_value={'pri': 1})

        class tube:
            opt = {'tube': 1}
            queue = mock.Mock()
            take = mock.Mock(side_effect=[task(), None])
            put = mock.Mock()

        ex = mock.Mock(side_effect=[1, 1, 0])
        with mock.patch('source.lib.utils.get_tube', return_value=tube()):
            with mock.patch('source.lib.worker.get_redirect_history_from_task', side_effect=[None]):
                with mock.patch('os.path.exists', ex):
                    worker(mock.Mock(), 1)
        self.assertEqual(ex.call_count, 3)
