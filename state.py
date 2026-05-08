from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # بيانات الغرفة
    room_id: str
    is_empty: bool
    empty_duration: int
    ac_level: int
    lights_on: bool
    next_booking: int
    temperature: float

    # Short-term Memory
    current_observations: List[str]
    current_actions: List[str]
    current_savings: float

    # Long-term Memory
    long_term_memory: List[dict]

    # نتائج الـ Loop
    llm_decision: Optional[str]
    tools_executed: List[str]
    evaluation_result: Optional[str]
    is_correct: bool
    loop_count: int