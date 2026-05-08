from flask import Flask, jsonify, Response, stream_with_context, render_template
from flask_cors import CORS
from memory import SarabMemory
from executor import execute_tool
from tools import SARAB_TOOLS
import anthropic
import json

app = Flask(__name__, template_folder='templates')
CORS(app)
##set your API KEY HERE 
import os
client = Anthropic(api_key=os.getenv("API_KEY"))

SCENARIOS = {
    "room_4b": {
        "room_id": "Conference Room 4B",
        "scenario": "Obvious Waste",
        "is_empty": True,
        "empty_duration": 52,
        "ac_level": 80,
        "lights_on": True,
        "next_booking": 90,
        "temperature": 22.0
    },
    "room_4c": {
        "room_id": "Conference Room 4C",
        "scenario": "Critical Timing",
        "is_empty": True,
        "empty_duration": 30,
        "ac_level": 60,
        "lights_on": True,
        "next_booking": 20,
        "temperature": 23.0
    },
    "room_4a": {
        "room_id": "Conference Room 4A",
        "scenario": "Occupied Room",
        "is_empty": False,
        "empty_duration": 0,
        "ac_level": 70,
        "lights_on": True,
        "next_booking": 0,
        "temperature": 24.0
    }
}

memory = SarabMemory()

@app.route('/')
def home():
    return render_template('demo.html')

@app.route('/api/scenarios')
def get_scenarios():
    return jsonify(SCENARIOS)

@app.route('/api/run/<room_key>')
def run_agent(room_key):
    if room_key not in SCENARIOS:
        return jsonify({"error": "Room not found"}), 404

    room_data = SCENARIOS[room_key].copy()
    state = room_data.copy()
    state["is_correct"] = False
    state["current_savings"] = 0.0
    state["evaluation_result"] = None

    def generate():
        system_prompt = """You are SARAB, an autonomous energy management agent.
Your goal: Reduce energy waste in buildings.

Follow this exact loop:
1. PLAN: Check room status
2. ACT: Use tools to execute decisions
3. OBSERVE: Check results
4. REFLECT: Evaluate using evaluate_decision tool

Rules:
- Always start with check_room_status
- Always end with evaluate_decision
- Always call store_to_memory before evaluate_decision
- Be specific and narrow"""

        messages = [{
            "role": "user",
            "content": f"""Analyze room: {state['room_id']}
Scenario: {state.get('scenario', '')}
Empty: {state['is_empty']} | Duration: {state['empty_duration']}min
AC: {state['ac_level']}% | Lights: {state['lights_on']}
Temperature: {state['temperature']}C | Next booking: {state['next_booking']}min

Memory context:
{memory.retrieve_for_llm(state['room_id'])}

Start Plan -> Act -> Observe -> Reflect loop."""
        }]

        loop_count = 0

        while loop_count < 6:
            loop_count += 1

            yield f"data: {json.dumps({'type': 'loop', 'loop': loop_count, 'phase': 'PLAN'})}\n\n"

            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1024,
                system=system_prompt,
                tools=SARAB_TOOLS,
                messages=messages
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":

                        yield f"data: {json.dumps({'type': 'tool_call', 'tool': block.name, 'input': block.input})}\n\n"

                        result = execute_tool(block.name, block.input, state, memory)

                        yield f"data: {json.dumps({'type': 'tool_result', 'tool': block.name, 'result': result})}\n\n"

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result)
                        })

                        if block.name == "evaluate_decision":
                            if state.get("is_correct") and loop_count >= 2:
                                yield f"data: {json.dumps({'type': 'complete', 'savings': state['current_savings'], 'loops': loop_count, 'reason': state.get('evaluation_result', '')})}\n\n"
                                return

                messages.append({"role": "user", "content": tool_results})

            elif response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, 'text'):
                        yield f"data: {json.dumps({'type': 'llm_text', 'text': block.text[:300]})}\n\n"
                break

        yield f"data: {json.dumps({'type': 'done', 'savings': state['current_savings']})}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)