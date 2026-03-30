from typing import Dict, Any, List

class StateManager:
    def __init__(self):
        # TODO: Migrar a Redis o PostgreSQL en fase 2 para persistencia real
        self._states: Dict[str, Dict[str, Any]] = {}

    def _get_default_state(self, phone: str) -> Dict[str, Any]:
        return {
            "expediente_estado": "inicio",
            "tramite_principal": None,
            "subtipo_tramite": None,
            "nombre_cliente": None,
            "telefono": phone,
            "marca": None,
            "modelo": None,
            "ano_matriculacion": None,
            "comunidad_autonoma": None,
            "urgencia": "normal",
            "pago_estado": "pendiente",
            "canal_origen": "whatsapp_directo",
            "documentos_recibidos": [],
            "precio_desglose": {},
            "notas_internas": "",
            "history": []
        }

    def get_state(self, phone: str) -> Dict[str, Any]:
        if phone not in self._states:
            self._states[phone] = self._get_default_state(phone)
        return self._states[phone]

    def update_state(self, phone: str, state_data: Dict[str, Any]) -> None:
        if phone not in self._states:
            self._states[phone] = self._get_default_state(phone)
        
        # Actualizar solo los campos proporcionados
        for key, value in state_data.items():
            if key in self._states[phone] and value is not None:
                self._states[phone][key] = value

    def get_history(self, phone: str) -> List[Dict[str, str]]:
        state = self.get_state(phone)
        return state.get("history", [])

    def add_message(self, phone: str, role: str, content: str) -> None:
        state = self.get_state(phone)
        if "history" not in state:
            state["history"] = []
        state["history"].append({"role": role, "content": content})

    def reset(self, phone: str) -> None:
        self._states[phone] = self._get_default_state(phone)

# Instancia global para uso en la app
state_manager = StateManager()
