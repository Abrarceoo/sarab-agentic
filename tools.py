SARAB_TOOLS = [
    {
        "name": "check_room_status",
        "description": "Check current room occupancy, AC level, lights, and energy waste status",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string"}
            },
            "required": ["room_id"]
        }
    },
    {
        "name": "control_hvac",
        "description": "Control the HVAC system - reduce, increase or turn off AC",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string"},
                "new_level": {"type": "integer", "minimum": 0, "maximum": 100},
                "reason": {"type": "string"}
            },
            "required": ["room_id", "new_level", "reason"]
        }
    },
    {
        "name": "control_lighting",
        "description": "Control room lighting - turn off, dim or maintain",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string"},
                "action": {"type": "string", "enum": ["off", "dim", "on"]},
                "reason": {"type": "string"}
            },
            "required": ["room_id", "action", "reason"]
        }
    },
    {
        "name": "calculate_savings",
        "description": "Calculate energy and cost savings from the proposed actions",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string"},
                "hvac_reduction_percent": {"type": "integer"},
                "lights_off": {"type": "boolean"},
                "duration_minutes": {"type": "integer"}
            },
            "required": ["room_id", "hvac_reduction_percent", "lights_off", "duration_minutes"]
        }
    },
    {
        "name": "store_to_memory",
        "description": "Store decision and pattern to long-term memory for future learning",
        "input_schema": {
            "type": "object",
            "properties": {
                "room_id": {"type": "string"},
                "decision": {"type": "string"},
                "savings_sar": {"type": "number"},
                "pattern_learned": {"type": "string"}
            },
            "required": ["room_id", "decision", "savings_sar"]
        }
    },
    {
        "name": "evaluate_decision",
        "description": "Evaluate if the decision was correct. Return true if correct, false if needs adjustment",
        "input_schema": {
            "type": "object",
            "properties": {
                "decision_summary": {"type": "string"},
                "is_correct": {"type": "boolean"},
                "reason": {"type": "string"},
                "adjustment_needed": {"type": "string"}
            },
            "required": ["decision_summary", "is_correct", "reason"]
        }
    }
]