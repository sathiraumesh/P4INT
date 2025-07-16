import os
import sys
import time
from mininet.util import quietRun
from mininet.node import Switch
from p4runtime_lib.switch import SwitchConnection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import p4runtime_lib.helper

from mininet.node import Switch
from mininet.util import quietRun
import time


class P4Switch(Switch):
    """Custom P4 BMv2 switch for Mininet"""

    def __init__(
        self,
        name,
        json_path="build/bmv2.json",
        grpc_port=50051,
        thrift_port=9090,
        cpu_port=255,
        device_id=0,
        **kwargs,
    ):
        Switch.__init__(self, name, **kwargs)
        self.json_path = json_path
        self.grpc_port = grpc_port
        self.thrift_port = thrift_port
        self.device_id = device_id
        self.cpu_port = cpu_port
        self.cmd_log = f"./switch_{self.name}.log"

    def start(self, controllers):
        """Start switch"""
        intfs = sorted(self.intfList(), key=lambda intf: intf.name)
        iface_args = ""
        port_num = 1
        for intf in intfs:
            if not intf.name.startswith("lo"):
                iface_args += f"-i {port_num}@{intf.name} "
                port_num += 1
        print(iface_args)

        cmd = "simple_switch_grpc "
        cmd += f"--device-id {self.device_id} "
        cmd += f"--thrift-port {self.thrift_port} "
        cmd += "--log-console "
        cmd += iface_args
        cmd += f"{self.json_path} -- --grpc-server-addr 0.0.0.0:{self.grpc_port} > {self.cmd_log} 2>&1 &"

        print(cmd)
        print(f"*** Starting P4 switch {self.name} on gRPC port {self.grpc_port}")
        self.cmd(cmd)

        time.sleep(0.5)
        if not self._check_running():
            raise Exception(
                f"ERROR: simple_switch_grpc for switch {self.name} failed to start!"
            )

    def _check_running(self):
        """Check if simple_switch_grpc is running for this switch."""
        output = quietRun("pgrep -f simple_switch_grpc")
        return bool(output.strip())

    def stop(self):
        """Stops switch"""
        self.cmd("kill %simple_switch_grpc")


class P4Controller:
    """Custom P4 Controller"""
    def __init__(self, switch_map, p4info_path, json_path):
        self.p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_path)
        self.json_path = json_path
        self.switches = {}

        for name, cfg in switch_map.items():
            self.switches[name] = SwitchConnection(
                name=cfg["name"],
                address=cfg["address"],
                device_id=cfg["device_id"],
                proto_dump_file=f'./{cfg["name"]}_grpc.txt',
            )

    def connect(self, switch_name):
        """connects the switch"""
        if switch_name not in self.switches:
            print(f"Switch '{switch_name}' not found in controller.")
            return

        conn = self.switches[switch_name]
        try:
            conn.MasterArbitrationUpdate()
            conn.SetForwardingPipelineConfig(
                p4info=self.p4info_helper.p4info, bmv2_json_file_path=self.json_path
            )
            print(f"[{switch_name}] Connected and pipeline set.")
        except Exception as e:
            print(f" [{switch_name}] Connection or pipeline error: {e}")

    def install_ipv4_forwarding_rule(self, switch_name, ip, mac, port):
        """Install forwading rules"""
        entry = self.p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={"hdr.ipv4.dstAddr": (ip, 32)},
            action_name="MyIngress.ipv4_forward",
            action_params={"dstAddr": mac, "port": port},
        )
        self.switches[switch_name].WriteTableEntry(entry)
        print(f" [{switch_name}] Installed rule for {ip} -> {mac} via port {port}")

    def read_table_rules(self, switch_name):
        """Read table rules"""
        conn = self.switches[switch_name]
        print(f"\n----- Reading table rules for {switch_name} -----")
        for response in conn.ReadTableEntries():
            for entity in response.entities:
                entry = entity.table_entry
                table_name = self.p4info_helper.get_tables_name(entry.table_id)
                print(f"{table_name}: ", end="")
                for m in entry.match:
                    print(
                        f"{self.p4info_helper.get_match_field_name(table_name, m.field_id)} {self.p4info_helper.get_match_field_value(m)}",
                        end=" ",
                    )
                action = entry.action.action
                action_name = self.p4info_helper.get_actions_name(action.action_id)
                print(f"-> {action_name}(", end="")
                for p in action.params:
                    param_name = self.p4info_helper.get_action_param_name(
                        action_name, p.param_id
                    )
                    print(f"{param_name}={p.value}", end=", ")
                print(")")
