from concurrent import futures
import replication_pb2_grpc
import replication_pb2
import argparse as arg
import pickle
import grpc
import os

class Replica(replication_pb2_grpc.ReplicationServiceServicer):
    def __init__(self):
        self.epoca = 1
        self.intermediario = []  # log intermediário: ainda não commitado
        self.final = []  # banco final
        self.load()

    def load(self):
        if os.path.exists("replica_data.pkl"):
            with open("replica_data.pkl", "rb") as f:
                self.epoca, self.intermediario, self.final = pickle.load(f)

    def save(self):
        with open("replica_data.pkl", "wb") as f:
            pickle.dump((self.epoca, self.intermediario, self.final), f)

    def PushLog(self, requisicao, contexto):
        print(f"Recebido log: (epoca={requisicao.epoca}, offset={requisicao.offset}, data='{requisicao.data}')")

        # Verificação de consistência com o último offset
        if len(self.intermediario) > 0:
            ultimo = self.intermediario[-1]
            esperado_offset = ultimo.offset + 1
        else:
            esperado_offset = 0

        if requisicao.offset == esperado_offset and requisicao.epoca == self.epoca:
            # Consistente, adicionar ao log intermediário
            self.intermediario.append(requisicao)
            self.save()
            return replication_pb2.Ack(sucesso=True, mensagem="OK")
        else:
            # Inconsistência: truncar a partir do offset recebido
            print("Inconsistência detectada. Truncando log local...")
            self.intermediario = [e for e in self.intermediario if e.offset < requisicao.offset]
            self.save()
            return replication_pb2.Ack(sucesso=False, mensagem="Inconsistente, truncado")

    def Commit(self, requisicao, contexto):
        print(f"Commit recebido: (epoca={requisicao.epoca}, offset={requisicao.offset})")

        # Encontrar entrada correspondente no log intermediário
        for entry in self.intermediario:
            if entry.offset == requisicao.offset and entry.epoca == requisicao.epoca:
                self.final.append(entry)
                self.save()
                print(f"-> Aplicado no banco final: {entry.data}")
                return replication_pb2.Ack(sucesso=True, mensagem="Commit aplicado")

        print("-> Commit ignorado: entrada não encontrada.")
        return replication_pb2.Ack(sucesso=False, mensagem="Entrada não encontrada")

    def SyncLog(self, requisicao, contexto):
        # Fornece o log intermediário atual
        return replication_pb2.SyncResponse(entries=self.intermediario)


if __name__ == '__main__':
    parser = arg.ArgumentParser()
    parser.add_argument("--porta", type=int, required=True)
    args = parser.parse_args()
    
    replica = Replica()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replication_pb2_grpc.add_ReplicationServiceServicer_to_server(replica, server)
    
    server.add_insecure_port(f'[::]:{args.porta}')
    print(f"Réplica rodando na porta {args.porta}")
    server.start()
    server.wait_for_termination()