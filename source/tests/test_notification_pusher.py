import unittest
from requests import Response, RequestException

import mock
from gevent.queue import Queue

from source.notification_pusher import *
from ..notification_pusher import notification_worker, done_with_processed_tasks, stop_handler, parse_cmd_args, install_signal_handlers, main_loop, set_run_application


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
            with mock.patch("notification_pusher.logger.exception", mock.Mock()):
                notification_worker(task, m_task_queue)
        m_task_queue.put.assert_called_once_with((task, 'bury'))


    def test_done_with_processed_tasks_getattr_exception(self):
        queue = Queue()
        task = mock.Mock()
        task.ack = mock.Mock(side_effect=tarantool.DatabaseError)
        queue.put((task, 'ack'))
        with mock.patch("notification_pusher.logger.exception", mock.Mock()):
            done_with_processed_tasks(queue)
        self.assertRaises(tarantool.DatabaseError)

    def test_parse_cmd_args(self):
        conf = "conf.conf"
        path_to_pid = "path/to/pid"
        args = ["-c", conf, "-d", "-P", path_to_pid]
        parsed = parse_cmd_args(args)
        self.assertEqual(parsed.config, conf)
        self.assertEqual(parsed.pidfile, path_to_pid)
        self.assertTrue(parsed.daemon)

    def test_install_signal_handlers(self):
        m_gevent = mock.Mock()
        with mock.patch("gevent.signal", m_gevent):
            install_signal_handlers()
        m_gevent.assert_has_calls([mock.call(signal.SIGTERM, stop_handler, signal.SIGTERM),
                                   mock.call(signal.SIGINT, stop_handler, signal.SIGINT),
                                   mock.call(signal.SIGHUP, stop_handler, signal.SIGHUP),
                                   mock.call(signal.SIGQUIT, stop_handler, signal.SIGQUIT)])

    class Config:
        def __init__(self, _host, _port, _space, _tube, _queue_timeout, _worker_pool_size, _http_timeout):
            self.QUEUE_HOST = _host
            self.QUEUE_PORT = _port
            self.QUEUE_SPACE = _space
            self.QUEUE_TUBE = _tube
            self.QUEUE_TAKE_TIMEOUT = _queue_timeout
            self.WORKER_POOL_SIZE = _worker_pool_size
            self.SLEEP = 0
            self.HTTP_CONNECTION_TIMEOUT = _http_timeout
    class Tube:
        def __init__(self, _task):
            self.task = _task
        def take(self, timeout):
            stop_handler(signal.SIGTERM)
            return self.task
    class Task:
        def __init__(self, _id):
            self.task_id = _id
    def test_main_loop(self):
        config = self.Config("aaa", 8765, 0, "tube", 0, 1, 0)
        task_id = 1
        task = self.Task(task_id)
        tube = self.Tube(task)
        m_start = mock.Mock()
        with mock.patch("tarantool_queue.Queue.tube", mock.Mock(return_value=tube)):
            with mock.patch("gevent.Greenlet.start", m_start):
                main_loop(config)
        m_start.assert_called_once_with()

    def test_main_loop_stopped(self):
        config = self.Config("aaa", 8765, 0, "tube", 0, 1, 0)
        task_id = 1
        task = self.Task(task_id)
        tube = self.Tube(task)
        m_start = mock.Mock()
        stop_handler(signal.SIGTERM)
        with mock.patch("tarantool_queue.Queue.tube", mock.Mock(return_value=tube)):
            with mock.patch("gevent.Greenlet.start", m_start):
                main_loop(config)
        m_start.assert_has_calls([])

    def test_main_loop_no_task(self):
        config = self.Config("aaa", 8765, 0, "tube", 0, 1, 0)
        task_id = 1
        task = self.Task(task_id)
        tube = self.Tube(None)
        set_run_application(True)
        m_start = mock.Mock()
        with mock.patch("tarantool_queue.Queue.tube", mock.Mock(return_value=tube)):
            with mock.patch("gevent.Greenlet.start", m_start):
                main_loop(config)
        m_start.assert_has_calls([])
