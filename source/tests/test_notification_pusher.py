import json
import unittest
import mock
from requests import Response, RequestException

from ..notification_pusher import notification_worker

class NotificationPusherTestCase(unittest.TestCase):
    def test_notification_worker(self):
        url='foo.ru'
        m_data={'callback_url': url, 'id': 1}
        m_data_2={'id': 1}
        class task:
            data = m_data
            task_id = 1
        resp = Response()
        resp.status_code=200
        m_request = mock.Mock(return_value=resp)
        m_task_queue = mock.Mock()
        with mock.patch("requests.post", m_request):
            notification_worker(task, m_task_queue)
        m_task_queue.put.assert_called_once_with((task, 'ack'))
        m_request.assert_called_once_with(url, data=json.dumps(m_data_2))

    def test_notification_worker_except(self):
        url='foo.ru'
        m_data={'callback_url': url, 'id': 1}
        m_data_2={'id': 1}
        class task:
            data = m_data
            task_id = 1
        resp = Response()
        resp.status_code=200
        m_request = mock.Mock(side_effect=RequestException)
        m_task_queue = mock.Mock()
        with mock.patch("requests.post", m_request):
            notification_worker(task, m_task_queue)
        m_task_queue.put.assert_called_once_with((task, 'bury'))
