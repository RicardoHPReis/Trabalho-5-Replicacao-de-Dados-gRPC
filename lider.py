from concurrent import futures
import threading as th
import argparse as arg
import grpc
import time
import json
import os

import replication_pb2
import replication_pb2_grpc

PORTA = 50050
ARQUIVO_LOG = 'lider/lider_log.json'
ARQUIVO_COMMIT = 'lider/lider_committed.json'

class Lider(replication_pb2_grpc.LiderServicoServicer):
    def __init__(self, num_replicas):
        self.log = []
        self.epoca = 1
        self.offset = 0
        self.num_replicas = num_replicas
        self.committed_offsets = set()
        self.lock = th.Lock()
        
        self.replicas = [f'localhost:5005{i}' for i in range(1, num_replicas + 1)]

        self.carregar_arquivos()
        self.replica_stubs = self.conectar_replicas()

    def carregar_arquivos(self):
        if os.path.exists(ARQUIVO_LOG):
            with open(ARQUIVO_LOG, 'r') as f:
                self.log = json.load(f)
            if self.log:
                self.offset = self.log[-1]['offset'] + 1

        if os.path.exists(ARQUIVO_COMMIT):
            with open(ARQUIVO_COMMIT, 'r') as f:
                self.committed = json.load(f)
        else:
            self.committed = {}

    def conectar_replicas(self):
        stubs = []
        for addr in self.replicas:
            channel = grpc.insecure_channel(addr)
            stub = replication_pb2_grpc.ReplicaServicoStub(channel)
            stubs.append(stub)
        return stubs
    
    def salvar_log(self):
        with open(ARQUIVO_LOG, 'w') as f:
            json.dump(self.log, f)
            
    def apagar_log(self, offset):
        self.log = [item for item in self.log if item.get('offset') < offset]
        self.salvar_log()

    def salvar_commit(self):
        with open(ARQUIVO_COMMIT, 'w') as f:
            json.dump(self.committed, f)

    def sync_replica(self, stub, offset, offset_novo):
        print(f"[Lider] Reenviando entradas para réplica a partir do offset {offset+1} até {offset_novo-1}")
        for entrada in self.log:
            if entrada['offset'] > offset and entrada['offset'] < offset_novo:
                try:
                    stub.PushEntry(replication_pb2.LogEntry(**entrada))
                except grpc.RpcError:
                    print(f"[Lider] Falha ao reenviar entrada {entrada['offset']}")
    
    def AppendData(self, requisicao, contexto):
        with self.lock:
            entrada = {
                'epoca': self.epoca,
                'offset': self.offset,
                'chave': requisicao.chave,
                'valor': requisicao.valor
            }
            print(f"[Lider] Recebido do cliente: {entrada}")

            self.log.append(entrada)
            self.salvar_log()
            log_entrada = replication_pb2.LogEntry(**entrada)
            ack_cont = 0
            for i, stub in enumerate(self.replica_stubs):
                try:
                    resposta = stub.PushEntry(log_entrada)
                    if resposta.sucesso:
                        ack_cont += 1
                    else:
                        print(f"[Lider] Réplica {i+1} retornou falha: {resposta.mensagem}")
                        ultimo_offset = int(resposta.mensagem.split(':')[-1])
                        self.sync_replica(stub, ultimo_offset, self.offset)
                        ajuste = stub.PushEntry(log_entrada)
                        if ajuste.sucesso:
                            for j in range(ultimo_offset + 1, self.offset):
                                commit_ajuste = replication_pb2.CommitRequest(epoca=self.epoca, offset=j)
                                stub.CommitEntry(commit_ajuste)
                            ack_cont += 1
                        else:
                            print(f"[Lider] Ajuste falhou para réplica {i+1}.")
                except grpc.RpcError as e:
                    print(f"[Lider] Falha ao contatar réplica {i+1}.")

            if ack_cont > self.num_replicas / 2:
                print(f"[Lider] Quórum alcançado: Recebido {ack_cont} confirmações de {self.num_replicas} réplicas.")
                commit_req = replication_pb2.CommitRequest(epoca=self.epoca, offset=self.offset)
                for stub in self.replica_stubs:
                    try:
                        stub.CommitEntry(commit_req)
                    except grpc.RpcError:
                        pass

                self.committed[requisicao.chave] = requisicao.valor
                self.salvar_commit()
                self.committed_offsets.add(self.offset)

                print(f"[Lider] Committed offset {self.offset} com quórum.")
                self.offset += 1
                return replication_pb2.AppendResponse(sucesso=True, mensagem="Dados gravados com sucesso.")
            else:
                self.apagar_log(self.offset)
                print("[Lider] Falha ao obter quórum.")
                return replication_pb2.AppendResponse(sucesso=False, mensagem="Falha ao gravar: sem quórum.")

    def QueryData(self, requisicao, contexto):
        chave = requisicao.chave
        valor = self.committed.get(chave, "")
        return replication_pb2.QueryResponse(valor=valor, committed=chave in self.committed)


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    parser = arg.ArgumentParser()
    parser.add_argument("--replicas", type=int, required=True)
    args = parser.parse_args()
    
    lider = Lider(args.replicas)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replication_pb2_grpc.add_LiderServicoServicer_to_server(lider, server)
    server.add_insecure_port(f'[::]:{PORTA}')
    print("--------------------")
    print("        LIDER       ")
    print("--------------------\n")
    print(f"[Lider] Servidor iniciado na porta {PORTA}")
    server.start()
    server.wait_for_termination()