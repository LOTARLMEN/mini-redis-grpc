import time
from collections import OrderedDict

import grpc

import src.generated.kvstore_pb2 as kpb2
from src.generated.kvstore_pb2_grpc import KeyValueStoreServicer


class MiniRedisService(KeyValueStoreServicer):
    MAX_SIZE = 10
    memory = OrderedDict()

    def Put(self, request, context):
        if request.ttl_seconds > 0:
            deadline = time.monotonic() + request.ttl_seconds
        else:
            deadline = None

        self.memory[request.key] = (request.value, deadline)
        self.memory.move_to_end(request.key)

        if len(self.memory) > self.MAX_SIZE:
            self.memory.popitem(last=False)

        return kpb2.PutResponse()

    def Get(
        self,
        request,
        context,
    ):
        if request.key not in self.memory:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return kpb2.GetResponse()

        value, deadline = self.memory[request.key]
        if deadline is not None and deadline < time.monotonic():
            self.memory.pop(request.key, None)

            context.set_code(grpc.StatusCode.NOT_FOUND)
            return kpb2.GetResponse()
        self.memory.move_to_end(request.key)
        return kpb2.GetResponse(value=value)

    def Delete(
        self,
        request,
        context,
    ):
        self.memory.pop(request.key, None)
        return kpb2.DeleteResponse()

    def List(self, request, context):
        response = kpb2.ListResponse()
        expired_keys = []
        current_time = time.monotonic()

        for key, (val, deadline) in self.memory.items():
            if key.startswith(request.prefix):
                if deadline is not None and deadline < current_time:
                    expired_keys.append(key)
                else:
                    response.items.append(kpb2.KeyValue(key=key, value=val))

        for key in expired_keys:
            self.memory.pop(key, None)

        return response
