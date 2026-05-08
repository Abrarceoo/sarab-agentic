from datetime import datetime
from memory import SarabMemory

def execute_tool(tool_name: str, tool_input: dict, state: dict, memory: SarabMemory) -> dict:
    
    print(f"\n⚡ ACT — Tool: {tool_name}")
    print(f"   Input: {tool_input}")

    # ── check_room_status ──
    if tool_name == "check_room_status":
        memory.add_to_short_term("observe", f"Checked room {state['room_id']}")
        result = {
            "room_id": state["room_id"],
            "is_empty": state["is_empty"],
            "empty_duration_minutes": state["empty_duration"],
            "ac_level_percent": state["ac_level"],
            "lights_on": state["lights_on"],
            "next_booking_minutes": state["next_booking"],
            "temperature_celsius": state["temperature"],
            "waste_detected": state["is_empty"] and state["ac_level"] > 30,
            "memory_context": memory.retrieve_for_llm(f"room {state['room_id']}")
        }

    # ── control_hvac ──
    elif tool_name == "control_hvac":
        old_level = state["ac_level"]
        new_level = tool_input["new_level"]
        state["ac_level"] = new_level
        memory.add_to_short_term(
            "act", 
            f"HVAC changed from {old_level}% to {new_level}% — {tool_input.get('reason','')}"
        )
        memory.add_to_long_term(
            f"Room {state['room_id']}: HVAC reduced from {old_level}% to {new_level}%"
        )
        result = {
            "success": True,
            "previous_level": old_level,
            "new_level": new_level,
            "reduction_percent": old_level - new_level,
            "reason": tool_input.get("reason", "")
        }

    # ── control_lighting ──
    elif tool_name == "control_lighting":
        old_state = "on" if state["lights_on"] else "off"
        action = tool_input["action"]
        state["lights_on"] = action == "on"
        memory.add_to_short_term(
            "act",
            f"Lighting changed from {old_state} to {action} — {tool_input.get('reason','')}"
        )
        memory.add_to_long_term(
            f"Room {state['room_id']}: Lights turned {action}"
        )
        result = {
            "success": True,
            "previous_state": old_state,
            "new_state": action,
            "reason": tool_input.get("reason", "")
        }

    # ── calculate_savings ──
    elif tool_name == "calculate_savings":
        hvac_reduction = tool_input.get("hvac_reduction_percent", 0)
        lights_off = tool_input.get("lights_off", False)
        duration = tool_input.get("duration_minutes", 60)
        hvac_kwh = (hvac_reduction / 100) * 2.5 * (duration / 60)
        light_kwh = 0.036 * (duration / 60) if lights_off else 0
        total_kwh = hvac_kwh + light_kwh
        savings_sar = round(total_kwh * 0.18 * 20, 2)
        state["current_savings"] = savings_sar
        memory.add_to_short_term("observe", f"Calculated savings: {savings_sar} SAR")
        result = {
            "total_kwh_saved": round(total_kwh, 3),
            "savings_sar": savings_sar,
            "co2_reduced_kg": round(total_kwh * 0.5, 2)
        }

    # ── store_to_memory ──
    elif tool_name == "store_to_memory":
        memory.save_structured(
            room_id=tool_input["room_id"],
            decision=tool_input["decision"],
            savings=tool_input["savings_sar"]
        )
        memory.add_to_long_term(
            f"Decision for {tool_input['room_id']}: {tool_input['decision']} — "
            f"saved {tool_input['savings_sar']} SAR — "
            f"pattern: {tool_input.get('pattern_learned', '')}"
        )
        result = {
            "stored": True,
            "total_decisions": len(memory.structured["decisions"]),
            "total_saved": memory.structured["total_saved"]
        }

    # ── evaluate_decision ──
    elif tool_name == "evaluate_decision":
        is_correct = tool_input["is_correct"]
        state["is_correct"] = is_correct
        state["evaluation_result"] = tool_input["reason"]
        memory.add_to_short_term(
            "reflect",
            f"Evaluation: {'correct' if is_correct else 'incorrect'} — {tool_input['reason']}"
        )
        result = {
            "is_correct": is_correct,
            "reason": tool_input["reason"],
            "adjustment_needed": tool_input.get("adjustment_needed", "none"),
            "loop_again": not is_correct
        }

    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    print(f"   Result: {result}")
    return result