import subprocess as sub
import os

num_replicas = 3

pasta_sistema = os.path.dirname(os.path.abspath(__file__))
sub.Popen(f'start cmd /k python -m grpc_tools.protoc -I=protos --python_out=. --grpc_python_out=. replication.proto')
sub.Popen(f'start cmd /k python "{os.path.join(pasta_sistema, "cliente.py")}"', shell=True)
sub.Popen(f'start cmd /k python "{os.path.join(pasta_sistema, "lider.py")}" --replicas {num_replicas}', shell=True)
    
for i in range(1, num_replicas):
    sub.Popen(f'start cmd /k python "{os.path.join(pasta_sistema, "replica.py")}" --id {i} --porta {50000 + i}', shell=True)