import grpc
import bank_pb2
import bank_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
      stub = bank_pb2_grpc.GreeterStub(channel)
      response = stub.SayHello(bank_pb2.HelloRequest(name='Hanan'))
      print("Greeter client received following from server: " + response.message)   
run()


