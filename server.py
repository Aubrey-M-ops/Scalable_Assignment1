from concurrent import futures

#import greeting_pb2
#import greeting_pb2_grpc

import grpc
import bank_pb2
import bank_pb2_grpc

class Greeter(bank_pb2_grpc.GreeterServicer):
   def SayHello(self, request, context):
      print("Got request " + str(request))
      return bank_pb2.HelloReply(message='Hello, %s!' % request.name)
	  
def server():
   server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
   bank_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
   server.add_insecure_port('localhost:50051')
   print("gRPC starting")
   server.start()
   server.wait_for_termination()
   exit()

server()


