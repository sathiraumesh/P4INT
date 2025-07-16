
# 🛰️ SDN INT (In-Band Network Telemetry)

This project demonstrates the use of P4 and BMv2 to implement In-Band Network Telemetry (INT), with support for RTT measurement, Mininet simulation, and optional integration with Finisy.

---

## ✅ Prerequisites

Before running the project, ensure the following are installed on your system:

- Python 3
- [Mininet](http://mininet.org/)
- [P4Runtime (P4Rc)](https://github.com/p4lang/p4runtime)
- [BMv2 (Behavioral Model v2)](https://github.com/p4lang/behavioral-model)
- [P4C (P4 Compiler)](https://github.com/p4lang/p4c)
- [Finsy](https://pypi.org/project/finsy/0.10.0/)

---

## 🐍 Python Virtual Environment (Only for Finisy)

If you intend to use **Finisy**, you'll need to set up a Python virtual environment and install its dependencies.

### Step 1: Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install required packages

```bash

pip install -r requirements.txt

# before running make sure that you copy paste alrady compiled p4 to venv env or compile the protobufs mannualy.
cp -r /usr/lib/python3/dist-packages/p4 /home/sathira/SDN-INT/venv/lib/python3.12/site-packages/p4
```


> 📝 This setup is **only required if you are running Finisy**. For core INT functionality with P4 and BMv2, this step is not needed.
> The example-ping-line-topology-with-digest requires this
---

## 🔧 Commands

### Log into a BMv2 switch:

```bash
sudo simple_switch_CLI --thrift-port 9090
```

Replace `9090` with the appropriate port number depending on your topology (e.g., 9091, 9092...).

Example commands inside the CLI:

```bash
show_tables
register_read rtt_result 0
```

## TODO
- Move contoller logic of all to finsy 
- Do Some refactoring and Re-organizing of files 

