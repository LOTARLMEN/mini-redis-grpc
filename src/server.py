from concurrent import futures

import grpc

from src.generated.kvstore_pb2_grpc import add_KeyValueStoreServicer_to_server
from src.services.service import MiniRedisService


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    add_KeyValueStoreServicer_to_server(MiniRedisService(), server)

    listen_addr = "0.0.0.0:50051"
    server.add_insecure_port(listen_addr)

    server.start()

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
