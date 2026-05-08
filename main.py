from agent import run_sarab_agent

if __name__ == "__main__":
    
    print("\n" + "="*60)
    print("SARAB — Smart Autonomous Resource & Building Management")
    print("سَرَب — نظام إدارة الطاقة الذكي")
    print("="*60)

    # ── الغرفة الأولى — فاضية وتهدر طاقة ──
    room_4B = {
        "room_id": "Conference Room 4B",
        "is_empty": True,
        "empty_duration": 52,
        "ac_level": 80,
        "lights_on": True,
        "next_booking": 90,
        "temperature": 22.0
    }

    # ── الغرفة الثانية — مجاورة ومشغولة ──
    room_4A = {
        "room_id": "Conference Room 4A",
        "is_empty": False,
        "empty_duration": 0,
        "ac_level": 65,
        "lights_on": True,
        "next_booking": 0,
        "temperature": 23.0
    }

    print("\n🏢 Analyzing Room 4B...")
    result_4B = run_sarab_agent(room_4B)

    print("\n🏢 Analyzing Room 4A...")
    result_4A = run_sarab_agent(room_4A)

    print("\n" + "="*60)
    print("BUILDING SUMMARY")
    print(f"Room 4B savings: {result_4B['current_savings']} SAR")
    print(f"Room 4A savings: {result_4A['current_savings']} SAR")
    print(f"Total saved: {result_4B['current_savings'] + result_4A['current_savings']} SAR")
    print("="*60)