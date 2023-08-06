import logging
import signal
import threading
from concurrent import futures

import grpc
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from sentry_sdk import init as sentry_init

from protos.python.wallet_pb2_grpc import add_WalletServiceServicer_to_server
from src.anilius.core.settings import settings
from src.anilius.core.singleton import Singleton
from src.service import Servicer

NUM_SECS_TO_WAIT = 10

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class App(metaclass=Singleton):
    def __init__(self):
        self.event_shutting_down = threading.Event()
        self.server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            interceptors=(PromServerInterceptor(),),
        )
        start_http_server(8081)
        self.set_signals()
        sentry_init(debug=settings["DEBUG"], dsn=settings["SENTRY_DSN"])

    def set_signals(self):
        signal.signal(signal.SIGTERM, self.on_done)

    def on_done(self, signum, frame):
        self.logger.info("Got signal {}, {}".format(signum, frame))
        self.event_shutting_down.set()

    @property
    def logger(self):
        return logger

    def graceful_stop(self):
        self.logger.info("Stopped RPC server, Waiting for RPCs to complete...")
        self.server.stop(NUM_SECS_TO_WAIT).wait()
        self.logger.info("Done stopping server")
        self.server.wait_for_termination()

    def run(self):
        try:
            add_WalletServiceServicer_to_server(Servicer(), self.server)
            self.server.add_insecure_port("[::]:8080")
            self.server.start()
            self.logger.info("Started server at " + "8080")
            self.event_shutting_down.wait()
            self.graceful_stop()
        except KeyboardInterrupt:
            self.graceful_stop()
