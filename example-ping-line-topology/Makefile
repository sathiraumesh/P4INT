P4C = p4c
P4CFLAGS = --target bmv2 --arch v1model
P4SRC = ping.p4
P4OUT = build
P4INFO = $(P4OUT)/ping.p4info.txtpb 
P4JSON = $(P4OUT)

PYTHON = python3
TOPO_SCRIPT = topology.py

.PHONY: all run clean

all: clean build run

build: $(P4INFO) $(P4JSON)

$(P4INFO) $(P4JSON): $(P4SRC)
	@echo "🔧 Building P4 program..."
	@mkdir -p $(P4OUT)
	$(P4C) $(P4CFLAGS) --p4runtime-files $(P4INFO) -o $(P4JSON) $(P4SRC)

run:
	@echo "🚀 Running Mininet topology..."
	export PYTHONPATH=$(shell dirname $(PWD)) && $(PYTHON) $(TOPO_SCRIPT)

clean:
	@echo "🧹 Cleaning up..."
	rm -rf $(P4OUT)
	sudo mn -c
