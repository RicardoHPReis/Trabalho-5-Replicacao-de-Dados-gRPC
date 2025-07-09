import subprocess as sub
import time as t
import os

num_replicas = 3

pasta_sistema = os.path.dirname(os.path.abspath(__file__))

if not (os.path.exists("replication_pb2.py") and os.path.exists("replication_pb2_grpc.py")):
    sub.run(['python', '-m', 'grpc_tools.protoc', '-I=protos', '--python_out=.', '--grpc_python_out=.', 'protos/replication.proto'])

t.sleep(3)

sub.Popen(f'start cmd /k python "{os.path.join(pasta_sistema, "lider.py")}" --replicas {num_replicas}', shell=True)
t.sleep(1)
for i in range(1, num_replicas + 1):
    sub.Popen(f'start cmd /k python "{os.path.join(pasta_sistema, "replica.py")}" --id {i}', shell=True)
    t.sleep(0.5)
    
sub.Popen(f'start cmd /k python "{os.path.join(pasta_sistema, "cliente.py")}"', shell=True)
#start cmd /k python replica.py --id 1
#start cmd /k python replica.py --id 2