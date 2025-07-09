from concurrent import futures
import argparse
import grpc
import json
import os

import replication_pb2
import replication_pb2_grpc

LIDER_ENDERECO = 'localhost:50050'
class Replica (replication_pb2_grpc.ReplicaServicoServicer):
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.ARQUIVO_INTERMEDIARIO = f"replica/intermediario/replica_{replica_id}_intermed.json"
        self.ARQUIVO_FINAL = f"replica/final/replica_{replica_id}_final.json"
        self.epoca = 1
        
        self.dados_intermediarios = []
        self.dados_finais = {}
        self.carregar_arquivos()

    def carregar_arquivos(self):
        if os.path.exists(self.ARQUIVO_INTERMEDIARIO):
            with open(self.ARQUIVO_INTERMEDIARIO, 'r') as f:
                self.dados_intermediarios = json.load(f)
        if os.path.exists(self.ARQUIVO_FINAL):
            with open(self.ARQUIVO_FINAL, 'r') as f:
                self.dados_finais = json.load(f)

    def salvar_log(self):
        with open(self.ARQUIVO_INTERMEDIARIO, 'w') as f:
            json.dump(self.dados_intermediarios, f)
            
    def apagar_log(self, offset):
        self.dados_intermediarios = [item for item in self.dados_intermediarios if item.get('offset') < offset]
        self.salvar_log()

    def salvar_commit(self):
        with open(self.ARQUIVO_FINAL, 'w') as f:
            json.dump(self.dados_finais, f)

    def PushEntry(self, requisicao, contexto):
        entrada = {
            'epoca': requisicao.epoca,
            'offset': requisicao.offset,
            'chave': requisicao.chave,
            'valor': requisicao.valor
        }

        offset_esperado = self.dados_intermediarios[-1]['offset'] + 1 if self.dados_intermediarios else 0
        if requisicao.offset != offset_esperado:
            print(f"[Replica {self.replica_id}] Inconsistência detectada. Esperado {offset_esperado}, recebido {requisicao.offset}")
            self.apagar_log(requisicao.offset)
            ultimo_offset = offset_esperado-1
            return replication_pb2.AckResponse(sucesso=False, mensagem=f"Offset inconsistente. Ultimo offset:{ultimo_offset}")

        print(f"[Replica {self.replica_id}] Recebido log válido: {entrada}")
        self.dados_intermediarios.append(entrada)
        self.salvar_log()
        return replication_pb2.AckResponse(sucesso=True, mensagem="Log recebido com sucesso.")


    def CommitEntry(self, requisicao, contexto):
        print(f"[Replica {self.replica_id}] Commit recebido para offset {requisicao.offset}")
        entrada = next((e for e in self.dados_intermediarios if e['offset'] == requisicao.offset and e['epoca'] == requisicao.epoca), None)

        if entrada:
            self.dados_finais[entrada['chave']] = entrada['valor']
            self.salvar_commit()
            print(f"[Replica {self.replica_id}] Commit aplicado: {entrada}")
        else:
            print(f"[Replica {self.replica_id}] Entrada para commit não encontrada: epoca={requisicao.epoca}, offset={requisicao.offset}")

        return replication_pb2.AckResponse(sucesso=True, mensagem="Commit aplicado.")


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', type=int, required=True)
    args = parser.parse_args()
    porta = args.id + 50050
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replica = Replica(args.id)
    replication_pb2_grpc.add_ReplicaServicoServicer_to_server(replica, server)
    server.add_insecure_port(f'[::]:{porta}')
    print("--------------------")
    print(f"   REPLICA {args.id}")
    print("--------------------\n")
    print(f"[Replica {args.id}] Servidor iniciado na porta {porta}")
    server.start()
    server.wait_for_termination()