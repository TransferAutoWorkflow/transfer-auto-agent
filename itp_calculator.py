import json
import os
import math
from datetime import datetime
from typing import Optional, Dict, Tuple

# Cargar tablas del BOE
def _load_json(filename: str) -> list:
    path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _load_coeficientes() -> dict:
    path = os.path.join(os.path.dirname(__file__), "coeficientes.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

TABLAS_BOE = _load_json("tablas_boe_full.json")
ITP_CCAA = _load_json("itp_ccaa.json")
COEFICIENTES = _load_coeficientes()

def get_depreciation_percentage(anos_uso: float) -> int:
    """Obtiene el porcentaje de depreciación según los tramos del BOE"""
    tramos = COEFICIENTES.get("turismos_todoterreno", {}).get("tramos", [])
    for tramo in tramos:
        limite_inf = tramo.get("limite_inferior", 0)
        limite_sup = tramo.get("limite_superior", 999)
        if limite_inf < anos_uso <= limite_sup:
            return tramo["porcentaje"]
    # Si supera todos los tramos, usar el último
    if tramos:
        return tramos[-1]["porcentaje"]
    # Fallback manual si no hay datos
    if anos_uso <= 1: return 100
    elif anos_uso <= 2: return 84
    elif anos_uso <= 3: return 67
    elif anos_uso <= 4: return 56
    elif anos_uso <= 5: return 47
    elif anos_uso <= 6: return 39
    elif anos_uso <= 7: return 34
    elif anos_uso <= 8: return 28
    elif anos_uso <= 9: return 24
    elif anos_uso <= 10: return 19
    elif anos_uso <= 11: return 17
    elif anos_uso <= 12: return 15
    else: return 10

def find_vehicle_value(marca: str, modelo: str, ano: int) -> Tuple[Optional[float], str]:
    """
    Busca el valor del vehículo en las tablas del BOE.
    Retorna (valor, descripcion_version) o (None, "no encontrado")
    """
    marca_upper = marca.upper().strip()
    modelo_upper = modelo.upper().strip()
    ano_str = str(ano)
    
    best_match = None
    best_score = 0
    
    for entry in TABLAS_BOE:
        entry_marca = entry.get("marca", "").upper()
        entry_modelo = entry.get("modelo", "").upper()
        entry_periodo = entry.get("periodo", "")
        entry_valor = entry.get("valor", 0)
        
        # Verificar marca
        if entry_marca != marca_upper:
            continue
            
        # Verificar que el año está en el periodo
        periodo_match = False
        if "-" in entry_periodo:
            parts = entry_periodo.split("-")
            try:
                year_start = int(parts[0])
                year_end = int(parts[1]) if parts[1] != "actualidad" else 2030
                if year_start <= ano <= year_end:
                    periodo_match = True
            except:
                pass
        elif ano_str in entry_periodo:
            periodo_match = True
            
        if not periodo_match:
            continue
        
        # Verificar modelo (búsqueda flexible)
        entry_modelo_clean = entry_modelo.replace("-", " ").replace("_", " ")
        modelo_clean = modelo_upper.replace("-", " ").replace("_", " ")
        
        score = 0
        if modelo_clean in entry_modelo_clean or entry_modelo_clean.startswith(modelo_clean):
            score = 10
        elif any(word in entry_modelo_clean for word in modelo_clean.split() if len(word) > 2):
            score = 5
            
        if score > best_score:
            best_score = score
            best_match = entry
    
    if best_match:
        return best_match["valor"], best_match.get("version", best_match.get("modelo", ""))
    
    return None, "no encontrado en tablas BOE"

def get_itp_rate(ccaa: str) -> Tuple[float, str]:
    """Obtiene el tipo impositivo del ITP para una CCAA"""
    ccaa_lower = ccaa.lower().strip()
    
    # Mapeo de nombres comunes a códigos
    ccaa_map = {
        "andalucia": "AN", "andalucía": "AN",
        "aragon": "AR", "aragón": "AR",
        "asturias": "AS",
        "baleares": "IB", "islas baleares": "IB", "illes balears": "IB",
        "canarias": "CN",
        "cantabria": "CB",
        "castilla la mancha": "CM", "castilla-la mancha": "CM",
        "castilla leon": "CL", "castilla y leon": "CL", "castilla y león": "CL", "castilla-leon": "CL",
        "cataluna": "CT", "cataluña": "CT", "catalunya": "CT",
        "extremadura": "EX",
        "galicia": "GA",
        "la rioja": "RI", "rioja": "RI",
        "madrid": "MD", "comunidad de madrid": "MD",
        "murcia": "MC", "region de murcia": "MC", "región de murcia": "MC",
        "navarra": "NC", "comunidad foral de navarra": "NC",
        "pais vasco": "PV", "país vasco": "PV", "euskadi": "PV",
        "valencia": "VC", "comunidad valenciana": "VC", "comunitat valenciana": "VC",
        "ceuta": "CE",
        "melilla": "ML"
    }
    
    codigo = ccaa_map.get(ccaa_lower)
    
    for entry in ITP_CCAA:
        if (entry.get("codigo_iso") == codigo or 
            entry.get("comunidad", "").lower() == ccaa_lower):
            return entry.get("tipo_general_pct", 4.0), entry.get("comunidad", ccaa)
    
    # Default si no se encuentra
    return 4.0, ccaa

def calculate_itp(marca: str, modelo: str, ano: int, ccaa: str) -> Dict:
    """
    Calcula el ITP completo con desglose según tablas BOE.
    
    Retorna dict con:
    - valor_venal: valor de referencia BOE
    - anos_uso: antigüedad del vehículo
    - porcentaje_depreciacion: % aplicado
    - base_imponible: valor_venal * porcentaje_depreciacion / 100
    - tipo_itp_pct: tipo impositivo de la CCAA
    - ccaa_nombre: nombre de la CCAA
    - importe_itp: base_imponible * tipo_itp_pct / 100
    - desglose_texto: texto formateado para mostrar al cliente
    - encontrado_en_boe: bool
    - version_encontrada: descripción de la versión encontrada
    """
    ano_actual = datetime.now().year
    anos_uso = ano_actual - ano
    
    # Obtener valor del BOE
    valor_venal, version_encontrada = find_vehicle_value(marca, modelo, ano)
    encontrado_en_boe = valor_venal is not None
    
    if not encontrado_en_boe:
        # Valor estimado si no está en tablas
        valor_venal = 15000  # valor conservador por defecto
        version_encontrada = "estimado (no encontrado en tablas BOE)"
    
    # Calcular depreciación
    porcentaje_depreciacion = get_depreciation_percentage(anos_uso)
    base_imponible = round(valor_venal * porcentaje_depreciacion / 100, 2)
    
    # Obtener tipo ITP de la CCAA
    tipo_itp_pct, ccaa_nombre = get_itp_rate(ccaa)
    
    # Calcular importe ITP
    importe_itp = round(base_imponible * tipo_itp_pct / 100, 2)
    
    # Construir desglose
    desglose = {
        "marca": marca,
        "modelo": modelo,
        "ano": ano,
        "anos_uso": anos_uso,
        "version_boe": version_encontrada,
        "valor_venal_boe": valor_venal,
        "porcentaje_depreciacion": porcentaje_depreciacion,
        "base_imponible": base_imponible,
        "ccaa": ccaa_nombre,
        "tipo_itp_pct": tipo_itp_pct,
        "importe_itp": importe_itp,
        "encontrado_en_boe": encontrado_en_boe,
        "fuente": "Orden HAC/1501/2025 - BOE 23/12/2025"
    }
    
    return desglose

def format_itp_desglose(itp_data: Dict) -> str:
    """Formatea el desglose del ITP para mostrar al cliente"""
    encontrado = itp_data.get("encontrado_en_boe", False)
    
    lines = [
        f"📋 *Cálculo del ITP — {itp_data['marca']} {itp_data['modelo']} {itp_data['ano']}*",
        f"",
        f"• Valor de referencia BOE: {itp_data['valor_venal_boe']:,.0f}€",
        f"• Antigüedad: {itp_data['anos_uso']} años → depreciación del {100 - itp_data['porcentaje_depreciacion']}%",
        f"• Base imponible: {itp_data['base_imponible']:,.2f}€",
        f"• Tipo ITP {itp_data['ccaa']}: {itp_data['tipo_itp_pct']}%",
        f"• *ITP a pagar: {itp_data['importe_itp']:,.2f}€*",
        f"",
        f"_(Fuente: {itp_data['fuente']})_"
    ]
    
    if not encontrado:
        lines.append(f"_⚠️ Vehículo no encontrado en tablas BOE. Valor estimado orientativo._")
    
    return "\n".join(lines)
