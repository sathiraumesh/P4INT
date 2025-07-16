# 🛰️ Simple P4 Ping Topology

This project sets up a simple Mininet topology with two hosts connected through a P4-enabled BMv2 switch. It demonstrates basic IPv4 forwarding and manual ARP/static rule configuration.

---

## 🧱 Topology

h1 --- s1 --- h2


- `h1` IP: `10.0.0.1`, MAC: `00:00:00:00:00:01`
- `h2` IP: `10.0.0.2`, MAC: `00:00:00:00:00:02`
- `s1`: Single P4 software switch (BMv2)

## 📦 Contents

| File            | Description                                    |
|-----------------|----------------------------------------------- |
| `ping.p4`       | P4 program implementing basic IPv4 forwarding. |
| `topology.py`   | Python script to define Mininet topology.      |
| `Makefile`      | Build and run commands.                        |
| `switch_s1.log` | Logs of the BMV2 switch.                       |

---

## 🚀 Run Instructions

### 1. Compile and Launch the Topology

Run the following command to:
- Compile the P4 program
- Set up the switch
- Create and launch the Mininet topology

```bash
# compile and run the program
make

# connect to the emulated running BMV2 switch
sudo simple_switch_CLI --thrift-port 9090

# add table rules for forwarding
table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.0.1/32 => 00:00:00:00:00:01 1
table_add MyIngress.ipv4_lpm MyIngress.ipv4_forward 10.0.0.2/32 => 00:00:00:00:00:02 2
```

## Test 
Once inside the mininet cli run the command
```bash
h1 ping h2
```
