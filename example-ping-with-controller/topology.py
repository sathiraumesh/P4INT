from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.p4 import P4Switch
from utils.p4 import P4Controller

HOST_DETAILS = [
    {"name": "h1", "ip": "10.0.0.1", "mac": "00:00:00:00:00:01", "port": 1},
    {"name": "h2", "ip": "10.0.0.2", "mac": "00:00:00:00:00:02", "port": 2},
]

SWITCH = {"name": "s1", "address": "127.0.0.1:50051", "device_id": 0}


class PingTopo(Topo):
    """Ping topology single switch two hosts"""

    def build(self):
        s1 = self.addSwitch(
            "s1", cls=P4Switch, grpc_port=50051, json_path="./build/ping.json"
        )

        for host in HOST_DETAILS:
            h = self.addHost(host["name"], ip=f'{host["ip"]}/24', mac=host["mac"])
            self.addLink(h, s1)


def main():
    """Main"""
    setLogLevel("info")

    topo = PingTopo()
    net = Mininet(topo=topo, controller=None, link=TCLink, autoSetMacs=True)
    net.start()
    info("*** Network started\n")

    controller = P4Controller(
        switch_map={"s1": SWITCH},
        p4info_path="./build/ping.p4info.txtpb",
        json_path="./build/ping.json",
    )

    controller.connect("s1")

    for host in HOST_DETAILS:
        controller.install_ipv4_forwarding_rule(
            switch_name="s1", ip=host["ip"], mac=host["mac"], port=host["port"]
        )
    print("*** Forwarding rules installed successfully!")

    net.staticArp()
    CLI(net)
    net.stop()
    info("*** Network stopped\n")


if __name__ == "__main__":
    main()
