compile:
	python3.9 -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/helloworld.proto
