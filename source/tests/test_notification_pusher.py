import unittest
from requests import Response, RequestException

import mock
from gevent.queue import Queue

from source.notification_pusher import *
from ..notification_pusher import notification_worker


class NotificationPusherTestCase(unittest.TestCase):
    def testDone(self):
        queue = Queue()
        task = mock.Mock()
        queue.put((task, 'ack'))
        done_with_processed_tasks(queue)
        self.assertEqual(queue.qsize(), 0)

    def testDoneEmpty(self):
        queue = Queue()
        queue.qsize = mock.Mock(side_effect=[1, 0])
        done_with_processed_tasks(queue)
        self.assertRaises(gevent_queue.Empty)

    def test_notification_worker(self):
        url = 'foo.ru'
        m_data = {'callback_url': url, 'id': 1}
        m_data_2 = {'id': 1}

        class task:
            data = m_data
            task_id = 1

        resp = Response()
        resp.status_code = 200
        m_request = mock.Mock(return_value=resp)
        m_task_queue = mock.Mock()
        with mock.patch("requests.post", m_request):
            notification_worker(task, m_task_queue)
        m_task_queue.put.assert_called_once_with((task, 'ack'))
        m_request.assert_called_once_with(url, data=json.dumps(m_data_2))

    def test_notification_worker_except(self):
        url = 'foo.ru'
        m_data = {'callback_url': url, 'id': 1}
        m_data_2 = {'id': 1}

        class task:
            data = m_data
            task_id = 1

        resp = Response()
        resp.status_code = 200
        m_request = mock.Mock(side_effect=RequestException)
        m_task_queue = mock.Mock()
        with mock.patch("requests.post", m_request):
            notification_worker(task, m_task_queue)
        m_task_queue.put.assert_called_once_with((task, 'bury'))
