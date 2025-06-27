from protos import replication_pb2, replication_pb2_grpc
from concurrent import futures
import argparse as arg
import pickle
import grpc
import os

class Replica(replication_pb2_grpc.ReplicationServiceServicer):
    def __init__(self):
        self.epoch = 1
        self.intermediario = []  # log intermediário: ainda não commitado
        self.final = []  # banco final
        self.load()

    def load(self):
        if os.path.exists("replica_data.pkl"):
            with open("replica_data.pkl", "rb") as f:
                self.epoch, self.intermediario, self.final = pickle.load(f)

    def save(self):
        with open("replica_data.pkl", "wb") as f:
            pickle.dump((self.epoch, self.intermediario, self.final), f)

    def PushLog(self, request, context):
        print(f"Recebido log: (epoch={request.epoch}, offset={request.offset}, data='{request.data}')")

        # Verificação de consistência com o último offset
        if len(self.intermediario) > 0:
            ultimo = self.intermediario[-1]
            esperado_offset = ultimo.offset + 1
        else:
            esperado_offset = 0

        if request.offset == esperado_offset and request.epoch == self.epoch:
            # Consistente, adicionar ao log intermediário
            self.intermediario.append(request)
            self.save()
            return replication_pb2.Ack(success=True, message="OK")
        else:
            # Inconsistência: truncar a partir do offset recebido
            print("Inconsistência detectada. Truncando log local...")
            self.intermediario = [e for e in self.intermediario if e.offset < request.offset]
            self.save()
            return replication_pb2.Ack(success=False, message="Inconsistente, truncado")

    def Commit(self, request, context):
        print(f"Commit recebido: (epoch={request.epoch}, offset={request.offset})")

        # Encontrar entrada correspondente no log intermediário
        for entry in self.intermediario:
            if entry.offset == request.offset and entry.epoch == request.epoch:
                self.final.append(entry)
                self.save()
                print(f"-> Aplicado no banco final: {entry.data}")
                return replication_pb2.Ack(success=True, message="Commit aplicado")

        print("-> Commit ignorado: entrada não encontrada.")
        return replication_pb2.Ack(success=False, message="Entrada não encontrada")

    def SyncLog(self, request, context):
        # Fornece o log intermediário atual
        return replication_pb2.SyncResponse(entries=self.intermediario)


if __name__ == '__main__':
    parser = arg.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    
    replica = Replica()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replication_pb2_grpc.add_ReplicationServiceServicer_to_server(replica, server)
    
    server.add_insecure_port(f'[::]:{args.port}')
    print(f"Réplica rodando na porta {args.port}")
    server.start()
    server.wait_for_termination()