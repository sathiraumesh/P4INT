# 🛰️ P4-Based RTT Measurement in a Linear Topology

This project sets up a simple Mininet topology using P4 and BMv2 switches, designed to demonstrate basic in-band telemetry by measuring **round-trip time (RTT)** at the switch level.

---

## 📘 Project Overview

This project sets up a simple Mininet topology with **8 hosts and 4 P4-enabled switches** arranged in a **linear topology**, where each switch is connected to its immediate neighbors. Each switch is also connected to **two hosts**, and every switch-host group resides in a **distinct subnet**.

### 🎯 Goal: RTT Measurement

The primary goal of this project is to measure **round-trip time (RTT)** using a lightweight method:

- Each switch captures the **ingress timestamp** of ICMP or TCP request packets.
- It associates the timestamp with a **unique identifier** (such as an ICMP sequence number or TCP port).
- Upon receiving the corresponding reply packet, the switch or controller calculates the **RTT**.

> ⚠️ **Limitations**:
> - Limited scalability due to memory constraints on the switch.
> - Difficult to handle high-throughput or long-duration flows.


## 🧱 Topology
```bash
 h1         h3         h5         h7
  |          |          |          |
  s1────────s2─────────s3─────────s4
  |          |          |          |
 h2         h4         h6         h8
```

### 🖥️ Hosts

- `h1` IP: `10.0.0.1`, MAC: `00:00:00:00:01:01`
- `h2` IP: `10.0.0.2`, MAC: `00:00:00:00:01:02`
- `h3` IP: `10.0.1.1`, MAC: `00:00:00:00:02:01`
- `h4` IP: `10.0.1.2`, MAC: `00:00:00:00:02:02`
- `h5` IP: `10.0.2.1`, MAC: `00:00:00:00:03:01`
- `h6` IP: `10.0.2.2`, MAC: `00:00:00:00:03:02`
- `h7` IP: `10.0.3.1`, MAC: `00:00:00:00:04:01`
- `h8` IP: `10.0.3.2`, MAC: `00:00:00:00:04:02`

### 🔀 Switches

- `s1`: gRPC: `127.0.0.1:50051`, Thrift: `9090`, Subnet: `10.0.0.0/24`
- `s2`: gRPC: `127.0.0.1:50052`, Thrift: `9091`, Subnet: `10.0.1.0/24`
- `s3`: gRPC: `127.0.0.1:50053`, Thrift: `9092`, Subnet: `10.0.2.0/24`
- `s4`: gRPC: `127.0.0.1:50054`, Thrift: `9093`, Subnet: `10.0.3.0/24`


## 📦 Contents

| File            | Description                                    |
|-----------------|----------------------------------------------- |
| `ping.p4`       | P4 program implementing basic IPv4 forwarding. |
| `topology.py`   | Python script to define Mininet topology.      |
| `Makefile`      | Build and run commands.                        |
| `switch_*.log` | Logs of the BMV2 switch.                       |

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
```

## Test 
Once inside the mininet CLI run the command

```bash
h1 ping h2
```

In the appropriate switch log check for `rtt_result`. You should be able to see something like:

```
[17:25:38.443] [bmv2] [T] [thread 411825] [59.0] [cxt 0] Wrote register 'rtt_times' at index 385 with value 234
```

Where the time is in micoroseconds.

For example, add link delay of 5 seconds among `s1` and `s2` switches and see the increase in RTT is appropriate.

```bash
s1 tc qdisc add dev s1-eth3 root netem delay 5000ms
s2 tc qdisc add dev s2-eth3 root netem delay 5000ms
```

Then run the ping again:

```bash
h1 ping h2
```

Now you should see something like in the switch logs:

```
Wrote register 'rtt_result' at index 385 with value 10000000000
```

This shows the RTT has increased appropriately (e.g. 10 seconds).

To remove the artificial delay after testing, run:

```bash
s1 tc qdisc del dev s1-eth3 root
s2 tc qdisc del dev s2-eth3 root
```

