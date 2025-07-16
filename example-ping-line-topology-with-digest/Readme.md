# 🛰️ P4-Based RTT Measurement in a Linear Topology

This project sets up a simple Mininet topology using P4 and BMv2 switches, designed to demonstrate basic in-band telemetry by measuring **round-trip time (RTT)** at the controller level using digests.

---

## 📘 Project Overview

This project sets up a simple Mininet topology with **8 hosts and 4 P4-enabled switches** arranged in a **linear topology**, where each switch is connected to its immediate neighbors. Each switch is also connected to **two hosts**, and every switch-host group resides in a **distinct subnet**.

### 🎯 Goal: RTT Measurement

The primary goal of this project is to measure **round-trip time (RTT)** using digests:

- Each switch captures the **ingress timestamp** of ICMP or TCP request packets.
- It associates the timestamp with a **unique identifier** (such as an ICMP sequence number or TCP port).
- Upon receiving the corresponding reply packet, the switch sends digests info to the controller calculates the **RTT**.
- Here we have used [Finsy](https://pypi.org/project/finsy/0.10.0/) as a seperate contoller that will listn to digests from the connected switch


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

# load venv and run the following command to let finsy controller to connect to the switch here s1
# note that you might have to re reun the whole setps from above since the current forwarding rules are applied only if not present and will delete existing when finsy connects
`python3 controller.py`

```

## Test 
Once inside the mininet CLI run the command

```bash
h1 ping h2
```

In the contoller console you should see something like 
```
ata=[{'ingress_ts': 90062814, 'packet_hash': 510}])
Received digest: P4DigestList(digest_id='digest_t', list_id=146, timestamp=6741545785480103, data=[{'ingress_ts': 90060537, 'packet_hash': 510}])
RTT for packet_hash=510: 2277 ms
Last 10 RTTs - Avg: 2.55 ms, Max: 4.347 ms, Min: 2.183 ms
Received digest: P4DigestList(digest_id='digest_t', list_id=147, timestamp=6741545790125245, data=[{'ingress_ts': 91065259, 'packet_hash': 68}])
Received digest: P4DigestList(digest_id='digest_t', list_id=148, timestamp=6741546786650571, data=[{'ingress_ts': 91061581, 'packet_hash': 68}])
RTT for packet_hash=68: 3678 ms
Last 10 RTTs - Avg: 2.70 ms, Max: 4.347 ms, Min: 2.257 ms
Received digest: P4DigestList(digest_id='digest_t', list_id=149, timestamp=6741546790507196, data=[{'ingress_ts': 92065713, 'packet_hash': 210}])
Received digest: P4DigestList(digest_id='digest_t', list_id=150, timestamp=6741547787542434, data=[{'ingress_ts': 92062555, 'packet_hash': 210}])
RTT for packet_hash=210: 3158 ms
Last 10 RTTs - Avg: 2.78 ms, Max: 4.347 ms, Min: 2.257 ms
Received digest: P4Digest
```

For example, add link delay of 5 seconds among `s1` and `s2` switches and see the increase in RTT is appropriate.

```bash
s1 tc qdisc add dev s1-eth3 root netem delay 5000ms
s2 tc qdisc add dev s2-eth3 root netem delay 5000ms
```

Then run the ping again:

```bash
h1 ping h2
```

This shows the RTT has increased appropriately.
To remove the artificial delay after testing, run:

```bash
s1 tc qdisc del dev s1-eth3 root
s2 tc qdisc del dev s2-eth3 root
```

if you wnat to monitor the rtts in grafana you can use 

```bash
docker-compose up -d
# note that this part is temporly done
# use ssh tunnerling from vm to access the dashboard according to your configs
```
# P4INT<img width="2550" alt="Screenshot 2025-06-06 at 1 29 58 PM" src="https://github.com/user-attachments/assets/95fa5ed3-2a78-4b07-957a-c1e6b0c0a9be" />


