import ipaddress
import time
import random
from typing import Dict, Any, List

class NetworksService:
    """
    Virtual Laboratory Service for Computer Networks (Module 6).
    Provides IP Subnetting calculation, network routing simulation, and ICMP ping diagnostics.
    """

    def calculate_subnet(self, ip_str: str, prefix: int) -> Dict[str, Any]:
        """
        Calculates network addressing parameters given an IP address and CIDR prefix.
        """
        try:
            # Parse network with strict=False to allow host IP
            net = ipaddress.IPv4Network(f"{ip_str.strip()}/{prefix}", strict=False)
            total_hosts = net.num_addresses
            usable_hosts = max(0, total_hosts - 2) if prefix < 31 else total_hosts
            
            # Usable IP range
            first_host = str(net.network_address + 1) if prefix < 31 else str(net.network_address)
            last_host = str(net.broadcast_address - 1) if prefix < 31 else str(net.broadcast_address)
            usable_range = f"{first_host} - {last_host}" if usable_hosts > 0 else "N/A"

            # Determine IP Class
            first_octet = int(str(net.network_address).split('.')[0])
            if first_octet <= 127:
                ip_class = "Class A (Unicast)"
            elif first_octet <= 191:
                ip_class = "Class B (Unicast)"
            elif first_octet <= 223:
                ip_class = "Class C (Unicast)"
            elif first_octet <= 239:
                ip_class = "Class D (Multicast)"
            else:
                ip_class = "Class E (Experimental)"

            # Convert subnet mask to binary
            mask_octets = str(net.netmask).split('.')
            binary_mask = ".".join([f"{int(o):08b}" for o in mask_octets])

            return {
                "ip_address": ip_str,
                "cidr": prefix,
                "subnet_mask": str(net.netmask),
                "network_address": str(net.network_address),
                "broadcast_address": str(net.broadcast_address),
                "total_hosts": total_hosts,
                "usable_hosts": usable_hosts,
                "usable_range": usable_range,
                "binary_mask": binary_mask,
                "ip_class": ip_class
            }
        except Exception as e:
            raise ValueError(f"Invalid IP address or CIDR prefix: {e}")

    def simulate_packet_ping(
        self,
        source_node: str,
        target_node: str,
        topology_type: str = "routed_wan"
    ) -> Dict[str, Any]:
        """
        Simulates multi-hop packet routing and ICMP ping echo request/reply cycle.
        """
        hops = []
        if topology_type == "routed_wan":
            hops = [
                {"hop": 1, "device": "Host A (Workstation)", "ip": "192.168.1.10", "delay_ms": 0.2, "status": "Transmitted"},
                {"hop": 2, "device": "Switch SW-1 (Layer 2)", "ip": "192.168.1.2", "delay_ms": 0.8, "status": "Switched (VLAN 10)"},
                {"hop": 3, "device": "Router R1 (Gateway)", "ip": "192.168.1.1", "delay_ms": 1.4, "status": "Routed (OSPF Next-Hop)"},
                {"hop": 4, "device": "Router R2 (Remote GW)", "ip": "10.0.0.1", "delay_ms": 2.1, "status": "Routed (Direct Route)"},
                {"hop": 5, "device": "Host B (Target Server)", "ip": "10.0.0.5", "delay_ms": 3.8, "status": "Echo Reply Generated"}
            ]
        elif topology_type == "lan_switch":
            hops = [
                {"hop": 1, "device": "Host A", "ip": "192.168.1.10", "delay_ms": 0.1, "status": "Transmitted"},
                {"hop": 2, "device": "Core Switch SW-0", "ip": "192.168.1.254", "delay_ms": 0.5, "status": "MAC Forwarded"},
                {"hop": 3, "device": "Host B", "ip": "192.168.1.20", "delay_ms": 0.9, "status": "Echo Reply Generated"}
            ]
        else:
            hops = [
                {"hop": 1, "device": "Source Node", "ip": "172.16.0.5", "delay_ms": 0.3, "status": "Transmitted"},
                {"hop": 2, "device": "Access Point / Hub", "ip": "172.16.0.1", "delay_ms": 1.2, "status": "Broadcasted"},
                {"hop": 3, "device": "Destination Node", "ip": "172.16.0.15", "delay_ms": 1.8, "status": "Echo Reply Generated"}
            ]

        avg_rtt = round(sum(h["delay_ms"] for h in hops), 2)
        log_lines = [
            f"PING {target_node} from {source_node} (56 data bytes):",
            f"64 bytes from target: icmp_seq=1 ttl=62 time={avg_rtt} ms",
            f"64 bytes from target: icmp_seq=2 ttl=62 time={round(avg_rtt - 0.2, 2)} ms",
            f"64 bytes from target: icmp_seq=3 ttl=62 time={round(avg_rtt + 0.1, 2)} ms",
            f"64 bytes from target: icmp_seq=4 ttl=62 time={avg_rtt} ms",
            "",
            f"--- {target_node} ping statistics ---",
            "4 packets transmitted, 4 packets received, 0.0% packet loss",
            f"round-trip min/avg/max/stddev = {round(avg_rtt - 0.2, 2)}/{avg_rtt}/{round(avg_rtt + 0.1, 2)}/0.12 ms"
        ]

        return {
            "packets_sent": 4,
            "packets_received": 4,
            "packet_loss_percent": 0.0,
            "average_rtt_ms": avg_rtt,
            "hops": hops,
            "success": True,
            "log_output": "\n".join(log_lines)
        }

networks_service = NetworksService()

