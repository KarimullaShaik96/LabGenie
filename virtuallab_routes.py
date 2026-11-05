from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from app.schemas import (
    CircuitSimulationRequest,
    CircuitSimulationResponse,
    NetworkSubnetRequest,
    NetworkSubnetResponse,
    NetworkPingRequest,
    NetworkPingResponse,
    SQLExecuteRequest,
    SQLExecuteResponse
)
from app.models import User
from app.auth import get_current_user
from app.services.circuit_service import circuit_simulator
from app.services.networks_service import networks_service
from app.services.dbms_service import dbms_service

router = APIRouter(prefix="/virtuallab", tags=["Virtual Laboratory"])

# ==================== Digital Electronics ====================
@router.post("/simulate", response_model=CircuitSimulationResponse)
def simulate_circuit(
    req: CircuitSimulationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Simulates digital logic circuit connections, propagates node signals,
    computes full truth table, and verifies correctness against target curriculum.
    """
    switches_data = [s.dict() for s in req.switches]
    gates_data = [g.dict() for g in req.gates]
    leds_data = [l.dict() for l in req.leds]
    connections_data = [c.dict() for c in req.connections]

    result = circuit_simulator.simulate(
        switches=switches_data,
        gates=gates_data,
        leds=leds_data,
        connections=connections_data,
        target_circuit_type=req.target_circuit_type
    )

    return result

@router.get("/presets")
def get_circuit_presets(current_user: User = Depends(get_current_user)):
    """Provides standard digital electronics experiment templates"""
    return [
        {
            "id": "half_adder",
            "title": "Half Adder Circuit",
            "description": "Construct Half Adder using XOR and AND gates: Sum = A ^ B, Carry = A & B.",
            "target_type": "half_adder",
            "default_switches": [
                {"id": "sw_a", "label": "Input A", "state": 1, "x": 60, "y": 80},
                {"id": "sw_b", "label": "Input B", "state": 0, "x": 60, "y": 200}
            ],
            "default_gates": [
                {"id": "g_xor", "type": "XOR", "x": 260, "y": 70, "inputs": ["g_xor_in1", "g_xor_in2"], "output": "g_xor_out"},
                {"id": "g_and", "type": "AND", "x": 260, "y": 190, "inputs": ["g_and_in1", "g_and_in2"], "output": "g_and_out"}
            ],
            "default_leds": [
                {"id": "led_sum", "label": "Sum (S)", "x": 480, "y": 75},
                {"id": "led_carry", "label": "Carry (C)", "x": 480, "y": 195}
            ],
            "default_connections": [
                {"from_node": "sw_a_out", "to_node": "g_xor_in1"},
                {"from_node": "sw_b_out", "to_node": "g_xor_in2"},
                {"from_node": "sw_a_out", "to_node": "g_and_in1"},
                {"from_node": "sw_b_out", "to_node": "g_and_in2"},
                {"from_node": "g_xor_out", "to_node": "led_sum_in"},
                {"from_node": "g_and_out", "to_node": "led_carry_in"}
            ]
        },
        {
            "id": "nand_universal",
            "title": "NAND Gate Verification",
            "description": "Verify the truth table of a 2-input NAND Gate: Y = NOT (A AND B).",
            "target_type": "nand_universal",
            "default_switches": [
                {"id": "sw_1", "label": "Input A", "state": 1, "x": 60, "y": 100},
                {"id": "sw_2", "label": "Input B", "state": 1, "x": 60, "y": 220}
            ],
            "default_gates": [
                {"id": "g_nand", "type": "NAND", "x": 280, "y": 140, "inputs": ["g_nand_in1", "g_nand_in2"], "output": "g_nand_out"}
            ],
            "default_leds": [
                {"id": "led_y", "label": "Output Y", "x": 480, "y": 145}
            ],
            "default_connections": [
                {"from_node": "sw_1_out", "to_node": "g_nand_in1"},
                {"from_node": "sw_2_out", "to_node": "g_nand_in2"},
                {"from_node": "g_nand_out", "to_node": "led_y_in"}
            ]
        }
    ]

# ==================== Computer Networks Virtual Lab (Module 6) ====================
@router.post("/networks/subnet", response_model=NetworkSubnetResponse)
def calculate_subnet(
    req: NetworkSubnetRequest,
    current_user: User = Depends(get_current_user)
):
    """Calculates IPv4 subnet parameters, mask, usable host range, and binary breakdown"""
    try:
        return networks_service.calculate_subnet(req.ip_address, req.cidr_prefix)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/networks/ping", response_model=NetworkPingResponse)
def simulate_ping(
    req: NetworkPingRequest,
    current_user: User = Depends(get_current_user)
):
    """Simulates multi-hop packet routing and ICMP ping echo sequence with telemetry"""
    return networks_service.simulate_packet_ping(
        source_node=req.source_node,
        target_node=req.target_node,
        topology_type=req.topology_type
    )

# ==================== DBMS Virtual Lab (Module 6) ====================
@router.post("/dbms/execute", response_model=SQLExecuteResponse)
def execute_dbms_query(
    req: SQLExecuteRequest,
    current_user: User = Depends(get_current_user)
):
    """Executes SQL statements in the isolated DBMS laboratory database"""
    return dbms_service.execute_sql_query(req.sql)

@router.get("/dbms/schema")
def get_dbms_schema(current_user: User = Depends(get_current_user)):
    """Returns sample database tables and columns for students"""
    return dbms_service.get_schema_summary()
