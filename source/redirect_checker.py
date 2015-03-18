#!/usr/bin/env python2.7
# coding: utf-8
import logging
from logging.config import dictConfig
import multiprocessing
import os
import sys
import time

from lib.utils import (daemonize)
from lib.worker import worker
import source


logger = logging.getLogger('redirect_checker')


def main_loop(config):
    logger.info(
        u'Run main loop. Worker pool size={}. Sleep time is {}.'.format(
            config.WORKER_POOL_SIZE, config.SLEEP
        ))
    parent_pid = os.getpid()
    while True:
        if source.lib.utils.check_network_status(config.CHECK_URL, config.HTTP_TIMEOUT):
            required_workers_count = config.WORKER_POOL_SIZE - len(
                multiprocessing.active_children())
            if required_workers_count > 0:
                logger.info(
                    'Spawning {} workers'.format(required_workers_count))
                source.lib.utils.spawn_workers(
                    num=required_workers_count,
                    target=worker,
                    args=(config,),
                    parent_pid=parent_pid
                )
        else:
            logger.critical('Network is down. stopping workers')
            for c in multiprocessing.active_children():
                c.terminate()

        time.sleep(config.SLEEP)


def main(argv):
    args = source.lib.utils.parse_cmd_args(argv[1:])

    if args.daemon:
        daemonize()

    if args.pidfile:
        source.lib.utils.create_pidfile(args.pidfile)

    config = source.lib.utils.load_config_from_pyfile(
        os.path.realpath(os.path.expanduser(args.config))
    )
    logging.config.dictConfig(config.LOGGING)
    main_loop(config)

    return config.EXIT_CODE


if __name__ == '__main__':
    sys.exit(main(sys.argv))
