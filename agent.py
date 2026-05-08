import anthropic
from memory import SarabMemory
from executor import execute_tool
from tools import SARAB_TOOLS




##set your API KEY HERE 

import os
client = Anthropic(api_key=os.getenv("API_KEY"))

def run_sarab_agent(room_data: dict):
    """
    الـ Agentic Loop الكامل:
    Plan → Act → Observe → Reflect → يعيد حتى يحقق الهدف
    """
    
    memory = SarabMemory()
    state = room_data.copy()
    state["is_correct"] = False
    state["current_savings"] = 0.0
    state["evaluation_result"] = None

    print(f"\n{'='*60}")
    print(f"SARAB AGENT — Goal: Reduce energy waste")
    print(f"Room: {state['room_id']} | Empty: {state['empty_duration']}min | AC: {state['ac_level']}%")
    print(f"{'='*60}\n")

    # السياق الأولي للـ LLM
    system_prompt = """You are SARAB, an autonomous energy management agent.

Your goal: Reduce energy waste in buildings by making smart decisions.

You must follow this exact loop:
1. PLAN: Check room status and retrieve memory context
2. ACT: Use tools to execute decisions  
3. OBSERVE: Check results of your actions
4. REFLECT: Evaluate if your decision was correct using evaluate_decision tool

Rules:
- Always start by calling check_room_status
- Always end by calling evaluate_decision
- Always call store_to_memory before evaluate_decision
- If evaluate_decision returns is_correct=false, adjust and retry
- Every action must leave a trace (observable)
- Be specific and narrow — focus only on this room"""

    messages = [{
        "role": "user",
        "content": f"""Analyze and optimize energy for room: {state['room_id']}

Room data:
- Empty: {state['is_empty']}
- Empty duration: {state['empty_duration']} minutes
- AC level: {state['ac_level']}%
- Lights on: {state['lights_on']}
- Temperature: {state['temperature']}°C
- Next booking: {state['next_booking']} minutes

Memory context:
{memory.retrieve_for_llm(state['room_id'])}

Start the Plan → Act → Observe → Reflect loop now."""
    }]

    loop_count = 0
    max_loops = 10

    while loop_count < max_loops:
        loop_count += 1
        print(f"\n🔄 LOOP #{loop_count} — PLAN")

        # LLM يفكر ويختار Tool
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=system_prompt,
            tools=SARAB_TOOLS,
            messages=messages
        )

        # أضف رد الـ LLM للمحادثة
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        # ACT — ينفذ Tools
        if response.stop_reason == "tool_use":
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n📋 OBSERVE — Tool called: {block.name}")
                    
                    # ينفذ الـ Tool
                    result = execute_tool(
                        block.name,
                        block.input,
                        state,
                        memory
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })

                    # REFLECT — تحقق من evaluate_decision
                    if block.name == "evaluate_decision":
                        if state.get("is_correct"):
                            print(f"\n✅ REFLECT — Decision verified correct!")
                            print(f"   Reason: {state.get('evaluation_result')}")
                            
                            # إذا القرار صح — اطبع النتيجة وانهِ
                            if loop_count >= 2:
                                messages.append({
                                    "role": "user",
                                    "content": tool_results
                                })
                                print(f"\n{'='*60}")
                                print(f"✅ GOAL ACHIEVED")
                                print(f"💰 Savings: {state['current_savings']} SAR")
                                print(f"🔄 Loops completed: {loop_count}")
                                print(f"{'='*60}")
                                return state
                        else:
                            print(f"\n❌ REFLECT — Decision incorrect, adjusting...")
                            print(f"   Reason: {state.get('evaluation_result')}")

            # أرجع نتائج الـ Tools للـ LLM
            messages.append({
                "role": "user",
                "content": tool_results
            })

        # LLM انتهى
        elif response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, 'text'):
                    print(f"\n🧠 LLM Final: {block.text[:200]}")
            break

    print(f"\n{'='*60}")
    print(f"SARAB completed — Savings: {state['current_savings']} SAR")
    print(f"{'='*60}")
    return state