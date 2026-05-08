import json
import os
import faiss
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer

# ══════════════════════════════
# MEMORY MANAGER
# ══════════════════════════════

STRUCTURED_MEMORY_FILE = "sarab_structured.json"

class SarabMemory:
    def __init__(self):
        # Short-term: conversation buffer
        self.short_term = []
        
        # Long-term: FAISS vector store
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.long_term_texts = []
        
        # Structured: JSON
        self.structured = self._load_structured()

    # ── SHORT-TERM ──
    def add_to_short_term(self, role: str, content: str):
        """يضيف للـ conversation buffer"""
        self.short_term.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_short_term_context(self) -> str:
        """يرجع للـ LLM السياق الحالي"""
        if not self.short_term:
            return "No previous context in this session."
        context = "\n".join([
            f"{m['role']}: {m['content']}" 
            for m in self.short_term[-5:]
        ])
        return f"Short-term memory:\n{context}"

    # ── LONG-TERM ──
    def add_to_long_term(self, text: str):
        """يحفظ في FAISS vector store"""
        vector = self.encoder.encode([text])
        self.index.add(np.array(vector, dtype=np.float32))
        self.long_term_texts.append({
            "text": text,
            "timestamp": datetime.now().isoformat()
        })

    def retrieve_from_long_term(self, query: str, k: int = 3) -> str:
        """يسترجع أقرب ذكريات للـ LLM"""
        if self.index.ntotal == 0:
            return "No long-term memory yet."
        vector = self.encoder.encode([query])
        distances, indices = self.index.search(
            np.array(vector, dtype=np.float32), k
        )
        results = []
        for idx in indices[0]:
            if idx < len(self.long_term_texts):
                results.append(self.long_term_texts[idx]["text"])
        return "Long-term memory:\n" + "\n".join(results)

    # ── STRUCTURED ──
    def _load_structured(self) -> dict:
        """يقرأ الذاكرة المنظمة"""
        if os.path.exists(STRUCTURED_MEMORY_FILE):
            with open(STRUCTURED_MEMORY_FILE, "r") as f:
                return json.load(f)
        return {"decisions": [], "total_saved": 0}

    def save_structured(self, room_id: str, decision: str, savings: float):
        """يحفظ قرار منظم"""
        self.structured["decisions"].append({
            "room_id": room_id,
            "decision": decision,
            "savings_sar": savings,
            "timestamp": datetime.now().isoformat()
        })
        self.structured["total_saved"] += savings
        with open(STRUCTURED_MEMORY_FILE, "w") as f:
            json.dump(self.structured, f, indent=2)

    # ── RETRIEVE ALL FOR LLM ──
    def retrieve_for_llm(self, query: str) -> str:
        """
        يجمع كل أنواع الذاكرة ويرجعها للـ LLM
        هذا هو سهم الرجوع من Memory للـ LLM
        """
        short = self.get_short_term_context()
        long = self.retrieve_from_long_term(query)
        structured = f"Total saved so far: {self.structured['total_saved']} SAR"
        
        return f"""
{short}

{long}

{structured}
"""