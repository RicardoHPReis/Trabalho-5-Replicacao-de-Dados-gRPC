import replication_pb2_grpc
import replication_pb2
import grpc

LIDER_ENDERECO = 'localhost:50050'

def escrever_dado(stub):
    dado = input("Digite o dado a ser enviado: ")
    requisicao = replication_pb2.WriteRequest(data=dado)
    resposta = stub.Write(requisicao)
    print(f"[Resposta] Sucesso: {resposta.sucesso}, Mensagem: {resposta.mensagem}")

def consultar_dados(stub):
    requisicao = replication_pb2.QueryRequest()
    resposta = stub.Query(requisicao)
    print("\n[DADOS COMMITADOS NO LÍDER]")
    for entry in resposta.entries:
        print(f"- Época: {entry.epoca}, Offset: {entry.offset}, Data: '{entry.data}'")

def menu():
    with grpc.insecure_channel(LIDER_ENDERECO) as channel:
        stub = replication_pb2_grpc.ReplicationServiceStub(channel)
        while True:
            print("\n--- Cliente ---")
            print("1. Enviar dado")
            print("2. Consultar dados")
            print("3. Sair")
            opcao = input("Escolha: ")

            if opcao == '1':
                escrever_dado(stub)
            elif opcao == '2':
                consultar_dados(stub)
            elif opcao == '3':
                break
            else:
                print("Opção inválida.")

if __name__ == '__main__':
    menu()
