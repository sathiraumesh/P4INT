#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8>  PROTOCOL_ICMP = 1;
const bit<8> ICMP_TYPE_ECHO_REQUEST = 8;
const bit<8> ICMP_TYPE_ECHO_REPLY = 0;
const bit<32> MIRROR_SESSION_ID = 99;

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header icmp_t {
    bit<8>  type;
    bit<8>  code;
    bit<16> checksum;
    bit<16> identifier;
    bit<16> sequence;
}

struct digest_t {
   bit<48> ingress_ts;
   bit<32> packet_hash;
}

struct metadata {
    bit<32> hash_key;
    bit<1> is_request;
}

header icmp_timestamp_t {
    bit<48> ingress_ts;
}

struct headers {
    ethernet_t ethernet;
    ipv4_t     ipv4;
    icmp_t     icmp;
}

// Register to store timestamps
register<bit<48>>(1024) rtt_times;
register<bit<48>>(1024) rtt_result;

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {
    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            PROTOCOL_ICMP: parse_icmp;
            default: accept;
        }
    }

    state parse_icmp{
      packet.extract(hdr.icmp);  
      transition accept;
    } 

}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    action compute_hash(bit<16> id, bit<16> seq) {
        hash(meta.hash_key, HashAlgorithm.crc32, 32w0, { id, seq }, 16w1024);
    }

    action clone_to_cpu() {
      clone(CloneType.I2E, MIRROR_SESSION_ID);
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
        if (hdr.ipv4.isValid()) {
          if (hdr.icmp.isValid()){
               compute_hash(hdr.icmp.identifier, hdr.icmp.sequence);
            if (hdr.icmp.type == ICMP_TYPE_ECHO_REQUEST) {
                // rtt_times.write(meta.hash_key, standard_metadata.ingress_global_timestamp);
                digest<digest_t>(0, {standard_metadata.ingress_global_timestamp,  meta.hash_key});
            } else if (hdr.icmp.type == ICMP_TYPE_ECHO_REPLY) {
                // bit<48> ts = hdr.icmp_ts.ingress_ts;

                digest<digest_t>(0, {standard_metadata.ingress_global_timestamp, meta.hash_key});
                clone(CloneType.I2E, 99);
                // // rtt_times.read(ts, meta.hash_key);
                // bit<48> rtt = standard_metadata.ingress_global_timestamp - ts;
                // rtt_result.write(1, ts);
                // rtt_result.write(2, rtt);
            }
          }
          clone_to_cpu();
          ipv4_lpm.apply();
        }
    }
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.icmp);
        
    }
}

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
