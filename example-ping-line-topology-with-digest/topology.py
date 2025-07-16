from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI

import sys
import os
from p4runtime_lib.switch import ShutdownAllSwitchConnections, SwitchConnection
import p4runtime_lib.helper

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.p4 import P4Switch


SWITCHES = [
    {
        "name": "s1",
        "address": "127.0.0.1:50051",
        "device_id": 0,
        "subnet": "10.0.0.0/24",
        "thrift_port": 9090
    },
    {
        "name": "s2",
        "address": "127.0.0.1:50052",
        "device_id": 1,
        "subnet": "10.0.1.0/24",
        "thrift_port": 9091
    },
    {
        "name": "s3",
        "address": "127.0.0.1:50053",
        "device_id": 2,
        "subnet": "10.0.2.0/24",
        "thrift_port": 9092
    },
    {
        "name": "s4",
        "address": "127.0.0.1:50054",
        "device_id": 3,
        "subnet": "10.0.3.0/24",
        "thrift_port": 9093
    }
]

HOST_DETAILS = [
    {
        'name': 'h1',
        'ip': '10.0.0.1',
        'mac': '00:00:00:00:01:01',
        'port': 1,
        'subnet': '10.0.0.0/24',
        'gateway': {
            'ip': '10.0.0.254',
            'mac': '00:aa:bb:cc:00:ff'
        }
    },
    {
        'name': 'h2',
        'ip': '10.0.0.2',
        'mac': '00:00:00:00:01:02',
        'port': 2,
        'subnet': '10.0.0.0/24',
        'gateway': {
            'ip': '10.0.0.254',
            'mac': '00:aa:bb:cc:00:ff'
        }
    },
    {
        'name': 'h3',
        'ip': '10.0.1.1',
        'mac': '00:00:00:00:02:01',
        'port': 1,
        'subnet': '10.0.1.0/24',
        'gateway': {
            'ip': '10.0.1.254',
            'mac': '00:aa:bb:cc:01:ff'
        }
    },
    {
        'name': 'h4',
        'ip': '10.0.1.2',
        'mac': '00:00:00:00:02:02',
        'port': 2,
        'subnet': '10.0.1.0/24',
        'gateway': {
            'ip': '10.0.1.254',
            'mac': '00:aa:bb:cc:01:ff'
        }
    },
    {
        'name': 'h5',
        'ip': '10.0.2.1',
        'mac': '00:00:00:00:03:01',
        'port': 1,
        'subnet': '10.0.2.0/24',
        'gateway': {
            'ip': '10.0.2.254',
            'mac': '00:aa:bb:cc:02:ff'
        }
    },
    {
        'name': 'h6',
        'ip': '10.0.2.2',
        'mac': '00:00:00:00:03:02',
        'port': 2,
        'subnet': '10.0.2.0/24',
        'gateway': {
            'ip': '10.0.2.254',
            'mac': '00:aa:bb:cc:02:ff'
        }
    },
    {
        'name': 'h7',
        'ip': '10.0.3.1',
        'mac': '00:00:00:00:04:01',
        'port': 1,
        'subnet': '10.0.3.0/24',
        'gateway': {
            'ip': '10.0.3.254',
            'mac': '00:aa:bb:cc:03:ff'
        }
    },
    {
        'name': 'h8',
        'ip': '10.0.3.2',
        'mac': '00:00:00:00:04:02',
        'port': 2,
        'subnet': '10.0.3.0/24',
        'gateway': {
            'ip': '10.0.3.254',
            'mac': '00:aa:bb:cc:03:ff'
        }
    }
]

SWITCH_LINKS_FORWARDING_RULES = [
    {'switch': 's1', 'name': 's1-s2', 'subnet': '10.0.1.0', 'port': 3, 'mac': '00:aa:bb:cc:01:ff'},
    {'switch': 's1', 'name': 's1-s3', 'subnet': '10.0.2.0', 'port': 3, 'mac': '00:aa:bb:cc:01:ff'},
    {'switch': 's1', 'name': 's1-s4', 'subnet': '10.0.3.0', 'port': 3, 'mac': '00:aa:bb:cc:01:ff'},
    {'switch': 's2', 'name': 's2-s1', 'subnet': '10.0.0.0', 'port': 3, 'mac': '00:aa:bb:cc:00:ff'},
    {'switch': 's2', 'name': 's2-s3', 'subnet': '10.0.2.0', 'port': 4, 'mac': '00:aa:bb:cc:02:ff'},
    {'switch': 's2', 'name': 's2-s4', 'subnet': '10.0.3.0', 'port': 4, 'mac': '00:aa:bb:cc:02:ff'},
    {'switch': 's3', 'name': 's3-s1', 'subnet': '10.0.0.0', 'port': 3, 'mac': '00:aa:bb:cc:01:ff'},
    {'switch': 's3', 'name': 's3-s2', 'subnet': '10.0.1.0', 'port': 3, 'mac': '00:aa:bb:cc:01:ff'},
    {'switch': 's3', 'name': 's3-s4', 'subnet': '10.0.3.0', 'port': 4, 'mac': '00:aa:bb:cc:03:ff'},
    {'switch': 's4', 'name': 's4-s1', 'subnet': '10.0.0.0', 'port': 3, 'mac': '00:aa:bb:cc:02:ff'},
    {'switch': 's4', 'name': 's4-s2', 'subnet': '10.0.1.0', 'port': 3, 'mac': '00:aa:bb:cc:02:ff'},
    {'switch': 's4', 'name': 's4-s3', 'subnet': '10.0.2.0', 'port': 3, 'mac': '00:aa:bb:cc:02:ff'},
]

class PingTopo(Topo):
    """Ping topology line topology"""

    def build(self):
        switches = {}
        hosts = {}
        
        for sw in SWITCHES:
          switches[sw["name"]] = self.addSwitch(
              sw["name"],
              cls=P4Switch,
              grpc_port=int(sw["address"].split(":")[1]),
              thrift_port=sw['thrift_port'],
              device_id=sw["device_id"],
              json_path="./build/ping.json"
          )

        for host in HOST_DETAILS:
          hosts[host["name"]] = self.addHost(
              host["name"],
              ip=f"{host['ip']}/24",
              mac=host["mac"]
          )
        
        self.addLink(hosts["h1"], switches["s1"])
        self.addLink(hosts["h2"], switches["s1"])

        self.addLink(hosts["h3"], switches["s2"])
        self.addLink(hosts["h4"], switches["s2"])

        self.addLink(hosts["h5"], switches["s3"])
        self.addLink(hosts["h6"], switches["s3"])

        self.addLink(hosts["h7"], switches["s4"])
        self.addLink(hosts["h8"], switches["s4"])

        self.addLink(switches["s1"], switches["s2"])
        self.addLink(switches["s2"], switches["s3"])
        self.addLink(switches["s3"], switches["s4"])

def main():
    setLogLevel("info")

    topo = PingTopo()
    net = Mininet(topo=topo, controller=None, link=TCLink, autoSetMacs=True)

    net.start()
    info("*** Network started\n")

    p4info_helper = p4runtime_lib.helper.P4InfoHelper("./build/ping.p4info.txtpb")

    
    for SWITCH in SWITCHES:
      sw = SwitchConnection(
          name=SWITCH["name"],
          address=SWITCH["address"],
          device_id=SWITCH["device_id"],
          proto_dump_file=f"./{SWITCH['name']}_grpc.txt",
      )

      sw.MasterArbitrationUpdate()
      sw.SetForwardingPipelineConfig(
          p4info=p4info_helper.p4info,
          bmv2_json_file_path="./build/ping.json"
      )


      for host in HOST_DETAILS:
          if host.get("subnet") == SWITCH.get("subnet"):
              table_entry = p4info_helper.buildTableEntry(
                  table_name="MyIngress.ipv4_lpm",
                  match_fields={"hdr.ipv4.dstAddr": (host["ip"], 32)},
                  action_name="MyIngress.ipv4_forward",
                  action_params={
                      "dstAddr": host["mac"],
                      "port": host["port"]
                  }
              )
              sw.WriteTableEntry(table_entry=table_entry)
              print(f"Installed rule for {host['ip']} on {SWITCH['name']}")
    
      for table_entry in SWITCH_LINKS_FORWARDING_RULES: 
        if SWITCH['name'] == table_entry['switch']:
            table_entry = p4info_helper.buildTableEntry(
                  table_name="MyIngress.ipv4_lpm",
                  match_fields={"hdr.ipv4.dstAddr": (table_entry["subnet"], 24)},
                  action_name="MyIngress.ipv4_forward",
                  action_params={
                      "dstAddr": table_entry["mac"],
                      "port":  table_entry["port"]
                  }
              )
            sw.WriteTableEntry(table_entry=table_entry)
      
    net.staticArp()
    # add default gate way 
    for host in HOST_DETAILS:
        h = net.get(host["name"])
        gateway_ip = host["gateway"]["ip"]
        gateway_mac = host["gateway"]["mac"]
        h.cmd(f"route add default gw {gateway_ip}")
        h.cmd(f"arp -s {gateway_ip} {gateway_mac}")
   
    CLI(net)

    net.stop()
    info("*** Network stopped\n")


if __name__ == "__main__":
    main()
