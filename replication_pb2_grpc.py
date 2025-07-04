# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import replication_pb2 as replication__pb2

GRPC_GENERATED_VERSION = '1.73.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in replication_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class LiderServicoStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.AppendData = channel.unary_unary(
                '/replication.LiderServico/AppendData',
                request_serializer=replication__pb2.AppendRequest.SerializeToString,
                response_deserializer=replication__pb2.AppendResponse.FromString,
                _registered_method=True)
        self.QueryData = channel.unary_unary(
                '/replication.LiderServico/QueryData',
                request_serializer=replication__pb2.QueryRequest.SerializeToString,
                response_deserializer=replication__pb2.QueryResponse.FromString,
                _registered_method=True)


class LiderServicoServicer(object):
    """Missing associated documentation comment in .proto file."""

    def AppendData(self, request, context):
        """Cliente → Líder: Solicita gravação de um par chave-valor
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def QueryData(self, request, context):
        """Cliente → Líder: Consulta dados por chave
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LiderServicoServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'AppendData': grpc.unary_unary_rpc_method_handler(
                    servicer.AppendData,
                    request_deserializer=replication__pb2.AppendRequest.FromString,
                    response_serializer=replication__pb2.AppendResponse.SerializeToString,
            ),
            'QueryData': grpc.unary_unary_rpc_method_handler(
                    servicer.QueryData,
                    request_deserializer=replication__pb2.QueryRequest.FromString,
                    response_serializer=replication__pb2.QueryResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'replication.LiderServico', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('replication.LiderServico', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class LiderServico(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def AppendData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/replication.LiderServico/AppendData',
            replication__pb2.AppendRequest.SerializeToString,
            replication__pb2.AppendResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def QueryData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/replication.LiderServico/QueryData',
            replication__pb2.QueryRequest.SerializeToString,
            replication__pb2.QueryResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)


class ReplicaServicoStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.PushEntry = channel.unary_unary(
                '/replication.ReplicaServico/PushEntry',
                request_serializer=replication__pb2.LogEntry.SerializeToString,
                response_deserializer=replication__pb2.AckResponse.FromString,
                _registered_method=True)
        self.CommitEntry = channel.unary_unary(
                '/replication.ReplicaServico/CommitEntry',
                request_serializer=replication__pb2.CommitRequest.SerializeToString,
                response_deserializer=replication__pb2.AckResponse.FromString,
                _registered_method=True)


class ReplicaServicoServicer(object):
    """Missing associated documentation comment in .proto file."""

    def PushEntry(self, request, context):
        """Líder → Réplica: Envia nova entrada de log
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CommitEntry(self, request, context):
        """Líder → Réplica: Confirma que a entrada deve ser aplicada (commit)
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReplicaServicoServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'PushEntry': grpc.unary_unary_rpc_method_handler(
                    servicer.PushEntry,
                    request_deserializer=replication__pb2.LogEntry.FromString,
                    response_serializer=replication__pb2.AckResponse.SerializeToString,
            ),
            'CommitEntry': grpc.unary_unary_rpc_method_handler(
                    servicer.CommitEntry,
                    request_deserializer=replication__pb2.CommitRequest.FromString,
                    response_serializer=replication__pb2.AckResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'replication.ReplicaServico', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('replication.ReplicaServico', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class ReplicaServico(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def PushEntry(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/replication.ReplicaServico/PushEntry',
            replication__pb2.LogEntry.SerializeToString,
            replication__pb2.AckResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def CommitEntry(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/replication.ReplicaServico/CommitEntry',
            replication__pb2.CommitRequest.SerializeToString,
            replication__pb2.AckResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
