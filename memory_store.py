import json
import os
import uuid
from datetime import datetime
from typing import Optional, List, Dict

MEMORY_FILE = "memory_store.json"

VALID_TYPES = [
    "core_rule", "operational_rule", "commercial_rule", "pricing_rule",
    "risk_rule", "regional_rule", "document_rule", "conversion_rule",
    "followup_rule", "admin_command_rule", "faq_rule", "case_pattern",
    "forbidden_behavior"
]

PRIORITY_ORDER = [
    "admin_command_rule", "operational_rule", "regional_rule",
    "commercial_rule", "core_rule", "faq_rule"
]

def load_memory() -> List[Dict]:
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memories: List[Dict]):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

def add_rule(tipo: str, titulo: str, contenido: str, ambito: dict = None, 
             prioridad: str = "media", confianza: float = 0.9, 
             fuente: str = "admin", tags: list = None) -> Dict:
    memories = load_memory()
    rule = {
        "memory_id": str(uuid.uuid4()),
        "tipo": tipo,
        "titulo": titulo,
        "contenido": contenido,
        "ambito": ambito or {},
        "prioridad": prioridad,
        "confianza": confianza,
        "fuente": fuente,
        "creado_por": "admin",
        "fecha_creacion": datetime.utcnow().isoformat() + "Z",
        "fecha_actualizacion": datetime.utcnow().isoformat() + "Z",
        "activa": True,
        "version": 1,
        "tags": tags or []
    }
    memories.append(rule)
    save_memory(memories)
    return rule

def get_active_rules(tramite: str = None, ccaa: str = None, modo: str = None) -> List[Dict]:
    memories = load_memory()
    active = [m for m in memories if m.get("activa", True)]
    if tramite:
        active = [m for m in active if not m.get("ambito", {}).get("tramite") or tramite in m["ambito"]["tramite"]]
    if ccaa:
        active = [m for m in active if not m.get("ambito", {}).get("ccaa") or ccaa in m["ambito"]["ccaa"]]
    if modo:
        active = [m for m in active if not m.get("ambito", {}).get("modo") or modo in m["ambito"]["modo"]]
    # Ordenar por prioridad
    def priority_key(m):
        tipo = m.get("tipo", "")
        try:
            return PRIORITY_ORDER.index(tipo)
        except ValueError:
            return len(PRIORITY_ORDER)
    active.sort(key=priority_key)
    return active

def deactivate_rule(memory_id_or_title: str) -> bool:
    memories = load_memory()
    for m in memories:
        if m["memory_id"] == memory_id_or_title or m["titulo"].lower() == memory_id_or_title.lower():
            m["activa"] = False
            m["fecha_actualizacion"] = datetime.utcnow().isoformat() + "Z"
            save_memory(memories)
            return True
    return False

def update_rule(memory_id_or_title: str, nuevo_contenido: str) -> bool:
    memories = load_memory()
    for m in memories:
        if m["memory_id"] == memory_id_or_title or m["titulo"].lower() == memory_id_or_title.lower():
            m["contenido"] = nuevo_contenido
            m["version"] = m.get("version", 1) + 1
            m["fecha_actualizacion"] = datetime.utcnow().isoformat() + "Z"
            save_memory(memories)
            return True
    return False

def get_recent_rules(limit: int = 10) -> List[Dict]:
    memories = load_memory()
    active = [m for m in memories if m.get("activa", True)]
    active.sort(key=lambda m: m.get("fecha_actualizacion", ""), reverse=True)
    return active[:limit]

def find_rule(query: str) -> List[Dict]:
    memories = load_memory()
    query_lower = query.lower()
    results = []
    for m in memories:
        if (query_lower in m.get("titulo", "").lower() or 
            query_lower in m.get("contenido", "").lower() or
            any(query_lower in tag.lower() for tag in m.get("tags", []))):
            results.append(m)
    return results
