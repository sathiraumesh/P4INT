import asyncio
from collections import defaultdict, deque
import logging
import re
from pathlib import Path

import finsy as fy
from finsy.switch import ApiVersion
from prometheus_client import start_http_server, Gauge

digest_store = defaultdict(list)
rtt_map = {}
rtt_map = {}
recent_rtts = deque(maxlen=10) 

start_http_server(8090)

avg_rtt_gauge = Gauge("packet_avg_rtt_ms", "Average RTT in milliseconds")
min_rtt_gauge = Gauge("packet_min_rtt_ms", "Minimum RTT in milliseconds")
max_rtt_gauge = Gauge("packet_max_rtt_ms", "Maximum RTT in milliseconds")

async def _handle_digests(switch: fy.Switch):
    async for digest in switch.read_digests("digest_t"):
        print(f"Received digest: {digest}")

        for entry in digest.data:
            packet_hash = entry["packet_hash"]
            ingress_ts = entry["ingress_ts"]

            digest_store[packet_hash].append(ingress_ts)

            if len(digest_store[packet_hash]) == 2:
                t1, t2 = sorted(digest_store[packet_hash])
                rtt = abs(t2 - t1)
                rtt_map[packet_hash] = rtt
                recent_rtts.append(rtt)

                # Print RTT details
                print(f"RTT for packet_hash={packet_hash}: {rtt} ms")

                if len(recent_rtts) >= 1:
                    avg_rtt = sum(recent_rtts) / len(recent_rtts)
                    max_rtt = max(recent_rtts)
                    min_rtt = min(recent_rtts)

                    avg_rtt_gauge.set(avg_rtt)
                    min_rtt_gauge.set(min_rtt)
                    max_rtt_gauge.set(max_rtt)

                    print(
                        f"Last {len(recent_rtts)} RTTs - Avg: {avg_rtt/1000:.2f} ms, Max: {max_rtt/1000} ms, Min: {min_rtt/1000} ms"
                    )

          
        await switch.write([digest.ack()])

# Digest listener
async def ready_handler(sw: fy.Switch):

    await sw.write(
        [
            +fy.P4DigestEntry("digest_t", max_list_size=1, ack_timeout_ns=int(1e9)),
            +fy.P4TableEntry(
                "MyIngress.ipv4_lpm",
                match=fy.P4TableMatch({"hdr.ipv4.dstAddr": ("10.0.0.1", 32)}),
                action=fy.P4TableAction(
                    "MyIngress.ipv4_forward", dstAddr="00:00:00:00:01:01", port=1
                ),
            ),
            +fy.P4TableEntry(
                "MyIngress.ipv4_lpm",
                match=fy.P4TableMatch({"hdr.ipv4.dstAddr": ("10.0.0.2", 32)}),
                action=fy.P4TableAction(
                    "MyIngress.ipv4_forward", dstAddr="00:00:00:00:01:02", port=2
                ),
            ),
            +fy.P4TableEntry(
                "MyIngress.ipv4_lpm",
                match=fy.P4TableMatch({"hdr.ipv4.dstAddr": ("10.0.1.0", 24)}),
                action=fy.P4TableAction(
                    "MyIngress.ipv4_forward", dstAddr="00:aa:bb:cc:01:ff", port=3
                ),
            ),
            +fy.P4TableEntry(
                "MyIngress.ipv4_lpm",
                match=fy.P4TableMatch({"hdr.ipv4.dstAddr": ("10.0.2.0", 24)}),
                action=fy.P4TableAction(
                    "MyIngress.ipv4_forward", dstAddr="00:aa:bb:cc:01:ff", port=3
                ),
            ),
            +fy.P4TableEntry(
                "MyIngress.ipv4_lpm",
                match=fy.P4TableMatch({"hdr.ipv4.dstAddr": ("10.0.3.0", 24)}),
                action=fy.P4TableAction(
                    "MyIngress.ipv4_forward", dstAddr="00:aa:bb:cc:01:ff", port=3
                ),
            ),
    
        ]
    )
    print("✅ Forwarding rules installed")

    sw.create_task(_handle_digests(sw))
    async for packet in sw.read_packets():
        print("📥 Clone packet received:")
        print(f"  Payload: {packet.payload.hex()}")
        print(f"  Metadata: {[ (md.name, md.value) for md in packet.metadata ]}")


# Finsy contoller
async def main():
    options = fy.SwitchOptions(
        p4info=Path(
            "build/ping.p4info.txtpb"
        ),
        p4blob=Path("build/ping.json"),
        device_id=0,
        ready_handler=ready_handler,
    )

    async with fy.Switch(
        "sw1",
        "127.0.0.1:50051",
        options,
    ) as sw1:
        print("Switch connected and pipeline installed.")
        await asyncio.Event().wait()

fy.run(main())
