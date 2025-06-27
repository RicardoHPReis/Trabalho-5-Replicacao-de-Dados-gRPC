from protos import replication_pb2, replication_pb2_grpc
import grpc

LIDER_ADDRESS = 'localhost:50050'

def escrever_dado(stub):
    dado = input("Digite o dado a ser enviado: ")
    req = replication_pb2.WriteRequest(data=dado)
    res = stub.Write(req)
    print(f"[Resposta] Sucesso: {res.success}, Mensagem: {res.message}")

def consultar_dados(stub):
    req = replication_pb2.QueryRequest()
    res = stub.Query(req)
    print("\n[DADOS COMMITADOS NO LÍDER]")
    for entry in res.entries:
        print(f"- Epoch: {entry.epoch}, Offset: {entry.offset}, Data: '{entry.data}'")

def menu():
    with grpc.insecure_channel(LIDER_ADDRESS) as channel:
        stub = replication_pb2_grpc.ReplicationServiceStub(channel)
        while True:
            print("\n--- Cliente ---")
            print("1. Enviar dado")
            print("2. Consultar dados")
            print("0. Sair")
            opcao = input("Escolha: ")

            if opcao == '1':
                escrever_dado(stub)
            elif opcao == '2':
                consultar_dados(stub)
            elif opcao == '0':
                break
            else:
                print("Opção inválida.")

if __name__ == '__main__':
    menu()
