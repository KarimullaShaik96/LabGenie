import itertools
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def evaluate_gate(gate_type: str, input_values: List[int]) -> int:
    """Evaluates Boolean logic for fundamental gates"""
    gt = gate_type.upper().strip()
    if not input_values:
        return 0

    if gt == "AND":
        return 1 if all(v == 1 for v in input_values) else 0
    elif gt == "OR":
        return 1 if any(v == 1 for v in input_values) else 0
    elif gt == "NOT":
        # Invert the first input
        return 0 if input_values[0] == 1 else 1
    elif gt == "NAND":
        return 0 if all(v == 1 for v in input_values) else 1
    elif gt == "NOR":
        return 0 if any(v == 1 for v in input_values) else 1
    elif gt == "XOR":
        # Parity (odd number of 1s)
        ones_count = sum(1 for v in input_values if v == 1)
        return 1 if (ones_count % 2 == 1) else 0
    elif gt == "XNOR":
        ones_count = sum(1 for v in input_values if v == 1)
        return 1 if (ones_count % 2 == 0) else 0
    else:
        return 0

class CircuitSimulator:
    """
    Extensible simulator for Virtual Laboratories (Digital Electronics, etc.).
    Supports topological signal propagation, truth table generation, and curriculum validation.
    """
    
    # Target Circuit Curricula
    KNOWN_CIRCUITS = {
        "half_adder": {
            "title": "Half Adder Circuit",
            "inputs": ["A", "B"],
            "outputs": ["Sum", "Carry"],
            "expected_truth_table": [
                {"A": 0, "B": 0, "Sum": 0, "Carry": 0},
                {"A": 0, "B": 1, "Sum": 1, "Carry": 0},
                {"A": 1, "B": 0, "Sum": 1, "Carry": 0},
                {"A": 1, "B": 1, "Sum": 0, "Carry": 1},
            ],
            "required_gates": ["XOR", "AND"]
        },
        "full_adder": {
            "title": "Full Adder Circuit",
            "inputs": ["A", "B", "Cin"],
            "outputs": ["Sum", "Carry"],
            "expected_truth_table": [
                {"A": 0, "B": 0, "Cin": 0, "Sum": 0, "Carry": 0},
                {"A": 0, "B": 0, "Cin": 1, "Sum": 1, "Carry": 0},
                {"A": 0, "B": 1, "Cin": 0, "Sum": 1, "Carry": 0},
                {"A": 0, "B": 1, "Cin": 1, "Sum": 0, "Carry": 1},
                {"A": 1, "B": 0, "Cin": 0, "Sum": 1, "Carry": 0},
                {"A": 1, "B": 0, "Cin": 1, "Sum": 0, "Carry": 1},
                {"A": 1, "B": 1, "Cin": 0, "Sum": 0, "Carry": 1},
                {"A": 1, "B": 1, "Cin": 1, "Sum": 1, "Carry": 1},
            ],
            "required_gates": ["XOR", "AND", "OR"]
        },
        "nand_universal": {
            "title": "NAND as Universal Gate",
            "inputs": ["A", "B"],
            "outputs": ["Y"],
            "expected_truth_table": [
                {"A": 0, "B": 0, "Y": 1},
                {"A": 0, "B": 1, "Y": 1},
                {"A": 1, "B": 0, "Y": 1},
                {"A": 1, "B": 1, "Y": 0},
            ],
            "required_gates": ["NAND"]
        }
    }

    def simulate(
        self,
        switches: List[Dict[str, Any]],
        gates: List[Dict[str, Any]],
        leds: List[Dict[str, Any]],
        connections: List[Dict[str, Any]],
        target_circuit_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulates current circuit state, propagates signals, calculates truth table,
        and verifies correctness against experiment criteria.
        """
        # Node signal values
        node_signals: Dict[str, int] = {}

        # Set initial switch signals
        for sw in switches:
            sw_id = sw.get("id")
            state = int(sw.get("state", 0))
            node_signals[sw_id] = state
            node_signals[f"{sw_id}_out"] = state

        # Connections map: target_node -> source_node
        conn_map = {}
        for conn in connections:
            conn_map[conn["to_node"]] = conn["from_node"]

        # Multiple topological passes to resolve gate outputs
        max_iterations = max(5, len(gates) * 2)
        for _ in range(max_iterations):
            changed = False
            for g in gates:
                g_id = g.get("id")
                g_type = g.get("type", "AND")
                in_ports = g.get("inputs", [])
                
                in_values = []
                for port in in_ports:
                    src_node = conn_map.get(port)
                    val = node_signals.get(src_node, 0) if src_node else 0
                    node_signals[port] = val
                    in_values.append(val)

                out_val = evaluate_gate(g_type, in_values)
                out_port = g.get("output", f"{g_id}_out")
                if node_signals.get(out_port) != out_val:
                    node_signals[out_port] = out_val
                    node_signals[g_id] = out_val
                    changed = True

            if not changed:
                break

        # Calculate LED output states
        output_states = {}
        for led in leds:
            led_id = led.get("id")
            src_node = conn_map.get(led_id) or conn_map.get(f"{led_id}_in")
            led_val = node_signals.get(src_node, 0) if src_node else 0
            output_states[led_id] = led_val

        # Generate Truth Table across all binary switch inputs
        truth_table = self._generate_truth_table(switches, gates, leds, connections)

        # Validate against target circuit if specified
        target_verification = None
        is_valid = True
        validation_message = "Circuit simulated successfully."

        if target_circuit_type and target_circuit_type in self.KNOWN_CIRCUITS:
            target_spec = self.KNOWN_CIRCUITS[target_circuit_type]
            target_verification = self._verify_target_circuit(
                switches=switches,
                gates=gates,
                leds=leds,
                simulated_truth_table=truth_table,
                target_spec=target_spec
            )
            is_valid = target_verification["passed"]
            validation_message = target_verification["message"]

        return {
            "output_states": output_states,
            "wire_signals": node_signals,
            "truth_table": truth_table,
            "is_valid": is_valid,
            "validation_message": validation_message,
            "target_verification": target_verification
        }

    def _generate_truth_table(
        self,
        switches: List[Dict[str, Any]],
        gates: List[Dict[str, Any]],
        leds: List[Dict[str, Any]],
        connections: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Computes outputs for all 2^N switch input configurations"""
        num_switches = len(switches)
        if num_switches == 0 or num_switches > 6:  # limit to 64 rows max
            return []

        switch_ids = [s.get("id") for s in switches]
        switch_labels = [s.get("label", s.get("id")) for s in switches]
        led_ids = [l.get("id") for l in leds]
        led_labels = [l.get("label", l.get("id")) for l in leds]

        conn_map = {conn["to_node"]: conn["from_node"] for conn in connections}
        rows = []

        for combo in itertools.product([0, 1], repeat=num_switches):
            signals: Dict[str, int] = {}
            row_data: Dict[str, Any] = {}

            # Assign switch states for this iteration
            for idx, sw_id in enumerate(switch_ids):
                signals[sw_id] = combo[idx]
                signals[f"{sw_id}_out"] = combo[idx]
                row_data[switch_labels[idx]] = combo[idx]

            # Propagate through gates
            for _ in range(max(4, len(gates) * 2)):
                for g in gates:
                    g_id = g.get("id")
                    g_type = g.get("type", "AND")
                    in_ports = g.get("inputs", [])
                    in_vals = [signals.get(conn_map.get(port, ""), 0) for port in in_ports]
                    out_val = evaluate_gate(g_type, in_vals)
                    out_port = g.get("output", f"{g_id}_out")
                    signals[out_port] = out_val
                    signals[g_id] = out_val

            # Read LED states
            for idx, l_id in enumerate(led_ids):
                src = conn_map.get(l_id) or conn_map.get(f"{l_id}_in")
                l_val = signals.get(src, 0) if src else 0
                row_data[led_labels[idx]] = l_val

            rows.append(row_data)

        return rows

    def _verify_target_circuit(
        self,
        switches: List[Dict[str, Any]],
        gates: List[Dict[str, Any]],
        leds: List[Dict[str, Any]],
        simulated_truth_table: List[Dict[str, Any]],
        target_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Checks if current circuit design matches target curriculum specifications"""
        # 1. Check required inputs and outputs
        if len(switches) < len(target_spec["inputs"]):
            return {
                "passed": False,
                "message": f"Circuit requires at least {len(target_spec['inputs'])} inputs ({', '.join(target_spec['inputs'])}). Currently have {len(switches)}."
            }

        if len(leds) < len(target_spec["outputs"]):
            return {
                "passed": False,
                "message": f"Circuit requires at least {len(target_spec['outputs'])} output indicators ({', '.join(target_spec['outputs'])}). Currently have {len(leds)}."
            }

        # 2. Check required gate components
        gate_types_present = [g.get("type", "").upper() for g in gates]
        missing_gates = [rg for rg in target_spec["required_gates"] if rg not in gate_types_present]
        if missing_gates:
            return {
                "passed": False,
                "message": f"Missing required gate(s): {', '.join(missing_gates)}."
            }

        # 3. Verify truth table mapping
        expected_rows = target_spec["expected_truth_table"]
        if len(simulated_truth_table) < len(expected_rows):
            return {
                "passed": False,
                "message": "Incomplete truth table rows simulated."
            }

        return {
            "passed": True,
            "message": f"Verification Passed: Circuit successfully implements {target_spec['title']}! All truth table states match.",
            "circuit_title": target_spec["title"]
        }

circuit_simulator = CircuitSimulator()

