
lint:
	flake8

proto:
	rm -f ./leea_agent_sdk/protocol/*_pb2.py*
	protoc --proto_path=./protocol --pyi_out=./leea_agent_sdk/protocol --python_out=./leea_agent_sdk/protocol ./protocol/*.proto

test:
	python3 -m pytest
