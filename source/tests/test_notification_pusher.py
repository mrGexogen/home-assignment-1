import unittest

import mock
from gevent.queue import Queue

from source.notification_pusher import *


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
        # self.assertRaises(gevent_queue.Empty)