from concurrent import futures
import argparse
import grpc
import json
import os

import replication_pb2
import replication_pb2_grpc

class Replica (replication_pb2_grpc.ReplicaServicoServicer):
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.ARQUIVO_UNCOMMITED = f"replica/replica_{replica_id}_uncommitted.json"
        self.ARQUIVO_COMMITED = f"replica/replica_{replica_id}_committed.json"
        self.epoca = 1
        
        self.uncommitted_log = []
        self.committed = {}
        self.carregar_arquivos()

    def carregar_arquivos(self):
        if os.path.exists(self.ARQUIVO_UNCOMMITED):
            with open(self.ARQUIVO_UNCOMMITED, 'r') as f:
                self.uncommitted_log = json.load(f)
        if os.path.exists(self.ARQUIVO_COMMITED):
            with open(self.ARQUIVO_COMMITED, 'r') as f:
                self.committed = json.load(f)

    def salvar_log(self):
        with open(self.ARQUIVO_UNCOMMITED, 'w') as f:
            json.dump(self.uncommitted_log, f)

    def salvar_commit(self):
        with open(self.ARQUIVO_COMMITED, 'w') as f:
            json.dump(self.committed, f)


    def PushEntry(self, requisicao, contexto):
        entry = {
            'epoca': requisicao.epoca,
            'offset': requisicao.offset,
            'chave': requisicao.chave,
            'valor': requisicao.valor
        }

        # Validar consistência do log
        expected_offset = self.uncommitted_log[-1]['offset'] + 1 if self.uncommitted_log else 0
        if requisicao.offset != expected_offset:
            print(f"[Replica {self.replica_id}] Inconsistência detectada. Esperado offset {expected_offset}, recebido {requisicao.offset}")
            self.uncommitted_log = [
                e for e in self.uncommitted_log if e['offset'] < requisicao.offset
            ]
            self.salvar_log()
            return replication_pb2.AckResponse(
                sucesso=False,
                mensagem="Offset inconsistente. Log truncado."
            )

        print(f"[Replica {self.replica_id}] Recebido log válido: {entry}")
        self.uncommitted_log.append(entry)
        self.salvar_log()
        return replication_pb2.AckResponse(sucesso=True, mensagem="Log recebido com sucesso.")


    def CommitEntry(self, requisicao, contexto):
        print(f"[Replica {self.replica_id}] Commit recebido para offset {requisicao.offset}")
        entry = next((e for e in self.uncommitted_log if e['offset'] == requisicao.offset and e['epoca'] == requisicao.epoca), None)

        if entry:
            self.committed[entry['chave']] = entry['valor']
            self.salvar_commit()
            print(f"[Replica {self.replica_id}] Commit aplicado: {entry}")
        else:
            print(f"[Replica {self.replica_id}] Entrada para commit não encontrada: epoca={requisicao.epoca}, offset={requisicao.offset}")

        return replication_pb2.AckResponse(sucesso=True, mensagem="Commit aplicado.")


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    parser = argparse.ArgumentParser()
    parser.add_argument('--porta', type=int, required=True)
    args = parser.parse_args()
    port = args.porta
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replica = Replica(args.porta)
    replication_pb2_grpc.add_ReplicaServicoServicer_to_server(replica, server)
    server.add_insecure_port(f'[::]:{port}')
    print("--------------------")
    print(f"   REPLICA {args.porta}")
    print("--------------------\n")
    print(f"[Replica {args.porta}] Servidor iniciado na porta {port}")
    server.start()
    server.wait_for_termination()