import replication_pb2_grpc
import replication_pb2
import grpc
import time
import os

LIDER_ENDERECO = 'localhost:50050'

def conectar_lider():
    channel = grpc.insecure_channel(LIDER_ENDERECO)
    stub = replication_pb2_grpc.LiderServicoStub(channel)
    return stub

def enviar_dados(stub):
    chave = input("Digite a chave: ").strip()
    valor = input("Digite o valor: ").strip()
    requisicao = replication_pb2.AppendRequest(chave=chave, valor=valor)
    try:
        resposta = stub.AppendData(requisicao)
        if resposta.sucesso:
            print("Dados gravados com sucesso.")
        else:
            print(f"Falha ao gravar: {resposta.mensagem}")
    except grpc.RpcError as e:
        print(f"Erro ao contatar o líder: {e}")

def retornar_dados(stub):
    chave = input("Digite a chave para consulta: ").strip()
    requisicao = replication_pb2.QueryRequest(chave=chave)
    try:
        resposta = stub.QueryData(requisicao)
        if resposta.committed:
            print(f"Valor encontrado: {resposta.valor}\n")
        else:
            print("Chave não encontrada ou não committed.")
    except grpc.RpcError as e:
        print(f"Erro ao consultar o líder: {e}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    stub = conectar_lider()
    while True:
        print("--------------------")
        print("       CLIENTE      ")
        print("--------------------\n")
        print("1. Enviar chave/valor")
        print("2. Consultar chave")
        print("3. Sair")
        escolha = input("Escolha: ").strip()

        if escolha == "1":
            enviar_dados(stub)
        elif escolha == "2":
            retornar_dados(stub)
        elif escolha == "3":
            print("Saindo...")
            time.sleep(3)
            break
        else:
            print("Opção inválida.")
            time.sleep(3)
            os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == '__main__':
    main()
