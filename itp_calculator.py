import datetime
from config import HONORARIOS_BASE, RECARGO_URGENCIA

# Tipos impositivos de ITP por CCAA para vehículos usados
TIPOS_ITP_CCAA = {
    "Andalucía": 0.04,
    "Aragón": 0.04,
    "Asturias": 0.08,
    "Baleares": 0.04,
    "Canarias": 0.065, # IGIC
    "Cantabria": 0.06,
    "Castilla-La Mancha": 0.04,
    "Castilla y León": 0.04,
    "Cataluña": 0.05,
    "Comunidad Valenciana": 0.04,
    "Extremadura": 0.07,
    "Galicia": 0.07,
    "La Rioja": 0.04,
    "Madrid": 0.04,
    "Murcia": 0.04,
    "Navarra": 0.06,
    "País Vasco": 0.04,
    "Ceuta": 0.0, # Exento
    "Melilla": 0.0 # Exento
}

def estimar_valor_vehiculo(ano_matriculacion: int) -> float:
    """
    Estima el valor del vehículo basado en su antigüedad.
    Tabla simplificada de depreciación (valor base 15.000€).
    """
    ano_actual = datetime.datetime.now().year
    antiguedad = ano_actual - ano_matriculacion
    
    valor_base = 15000.0
    
    if antiguedad <= 1:
        porcentaje = 1.0
    elif antiguedad == 2:
        porcentaje = 0.84
    elif antiguedad == 3:
        porcentaje = 0.67
    elif antiguedad == 4:
        porcentaje = 0.56
    elif antiguedad == 5:
        porcentaje = 0.47
    elif antiguedad == 6:
        porcentaje = 0.39
    elif antiguedad == 7:
        porcentaje = 0.34
    elif antiguedad == 8:
        porcentaje = 0.28
    elif antiguedad == 9:
        porcentaje = 0.24
    elif antiguedad == 10:
        porcentaje = 0.19
    elif antiguedad == 11:
        porcentaje = 0.17
    elif antiguedad == 12:
        porcentaje = 0.13
    else:
        porcentaje = 0.10
        
    return valor_base * porcentaje

def calcular_precio(marca: str, modelo: str, ano: int, ccaa: str, valor_venta: float = None, urgente: bool = False) -> dict:
    """
    Calcula el desglose de precio para el trámite.
    """
    # 1. Determinar base imponible
    valor_estimado = estimar_valor_vehiculo(ano)
    if valor_venta and valor_venta > valor_estimado:
        base_imponible = valor_venta
    else:
        base_imponible = valor_estimado
        
    # 2. Calcular ITP
    # Normalizar CCAA para evitar problemas de mayúsculas/tildes en la búsqueda
    ccaa_normalizada = next((k for k in TIPOS_ITP_CCAA.keys() if k.lower() == ccaa.lower()), "Madrid") # Default a Madrid si no se encuentra
    tipo_itp = TIPOS_ITP_CCAA.get(ccaa_normalizada, 0.04)
    
    itp = round(base_imponible * tipo_itp, 2)
    
    # 3. Tasas y honorarios
    tasas_dgt = 55.70
    honorarios = HONORARIOS_BASE
    recargo = RECARGO_URGENCIA if urgente else 0.0
    
    # 4. Total
    total = round(itp + tasas_dgt + honorarios + recargo, 2)
    
    return {
        "itp": itp,
        "tasas_dgt": tasas_dgt,
        "honorarios": honorarios,
        "recargo_urgencia": recargo,
        "total": total
    }
