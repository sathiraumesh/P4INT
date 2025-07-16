from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.p4 import P4Switch

HOST_DETAILS = [
    {"name": "h1", "ip": "10.0.0.1", "mac": "00:00:00:00:00:01"},
    {"name": "h2", "ip": "10.0.0.2", "mac": "00:00:00:00:00:02"},
]


class PingTopo(Topo):
    """Ping topology single switch two hosts"""

    def build(self):
        """Builds the topology"""
        s1 = self.addSwitch(
            "s1", cls=P4Switch, grpc_port=50051, json_path="./build/ping.json"
        )

        for host in HOST_DETAILS:
            h = self.addHost(host["name"], ip=f"{host['ip']}/24", mac=host["mac"])
            self.addLink(h, s1)


def main():
    """Main"""
    setLogLevel("info")

    topo = PingTopo()
    net = Mininet(topo=topo, controller=None, link=TCLink, autoSetMacs=True)

    net.start()
    info("*** Network started\n")

    # We add this because BMV2 doesn't support ARP flooding so we try to emulate it
    # only considering ipv4 to be handeled in the P4 progrms
    net.staticArp()

    CLI(net)

    net.stop()
    info("*** Network stopped\n")


if __name__ == "__main__":
    main()
