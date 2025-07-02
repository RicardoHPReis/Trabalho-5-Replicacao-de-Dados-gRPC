from concurrent import futures
import replication_pb2_grpc
import replication_pb2
import argparse as arg
import threading
import asyncio
import grpc

PORTA = 50050
EPOCA = 1

class Lider(replication_pb2_grpc.ReplicationServiceServicer):
    def __init__(self, num_replicas):
        self.log = []  # lista de entradas: epoca, offset, data, committed
        self.num_replicas = num_replicas
        print(f"Inicializando líder com {num_replicas} réplicas...")
        self.replicas = [f'localhost:5005{i}' for i in range(1, num_replicas + 1)]
        self.offset = 0
        self.lock = threading.Lock()


    def _gravar_log_local(self, data):
        with self.lock:
            entry = {
                "data": data,
                "epoca": EPOCA,
                "offset": self.offset,
                "committed": False
            }
            self.log.append(entry)
            self.offset += 1
        return entry


    def _enviar_para_replicas(self, entry):
        async def send():
            acks = 0
            tarefas = []
            for replica in self.replicas:
                tarefas.append(self._push_para_replica(replica, entry))
            respostas = await asyncio.gather(*tarefas, return_exceptions=True)
            for resultado in respostas:
                if isinstance(resultado, bool) and resultado:
                    acks += 1
            return acks
        return asyncio.run(send())


    async def _push_para_replica(self, endereco, entry):
        async with grpc.aio.insecure_channel(endereco) as channel:
            stub = replication_pb2_grpc.ReplicationServiceStub(channel)
            log_entry = replication_pb2.LogEntry(
                data=entry["data"],
                epoca=entry["epoca"],
                offset=entry["offset"]
            )
            try:
                ack = await stub.PushLog(log_entry)
                return ack.sucesso
            except Exception as e:
                print(f"Erro ao enviar para {endereco}: {e}")
                return False


    def _commit_replicas(self, entry):
        async def send_commit():
            tasks = []
            for replica in self.replicas:
                async with grpc.aio.insecure_channel(replica) as channel:
                    stub = replication_pb2_grpc.ReplicationServiceStub(channel)
                    commit_msg = replication_pb2.CommitRequest(
                        epoca=entry["epoca"],
                        offset=entry["offset"]
                    )
                    try:
                        await stub.Commit(commit_msg)
                    except Exception as e:
                        print(f"Erro no commit para {replica}: {e}")         
        asyncio.run(send_commit())


    def Write(self, request, context):
        print(f"Recebido do cliente: {request.data}")
        entry = self._gravar_log_local(request.data)

        print("Enviando para réplicas...")
        ack_count = self._enviar_para_replicas(entry)

        if ack_count > self.num_replicas / 2:
            print("Maioria confirmou, enviando commit.")
            entry["committed"] = True
            self._commit_replicas(entry)
            return replication_pb2.WriteResponse(sucesso=True, mensagem="Gravação replicada e committed.")
        else:
            print("Falha ao atingir maioria.")
            return replication_pb2.WriteResponse(sucesso=False, mensagem="Falha na replicação.")


    def Query(self, request, context):
        committed_entries = [
            replication_pb2.LogEntry(data=e["data"], epoca=e["epoca"], offset=e["offset"])
            for e in self.log if e["committed"]
        ]
        return replication_pb2.QueryResponse(entries=committed_entries)


if __name__ == '__main__':
    parser = arg.ArgumentParser()
    parser.add_argument("--replicas", type=int, required=True)
    args = parser.parse_args()
    
    lider = Lider(args.replicas)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    replication_pb2_grpc.add_ReplicationServiceServicer_to_server(lider, server)
    server.add_insecure_port(f'[::]:{PORTA}')
    print(f"Líder rodando na porta {PORTA}...")
    server.start()
    server.wait_for_termination()