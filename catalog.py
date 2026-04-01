# Catálogo de servicios Transfer Auto
# Precios en euros, IVA incluido (21%)
# Las tasas DGT ya están incluidas en el precio de gestión

CATALOG = {
    "cambio_titularidad_particulares": {
        "nombre": "Cambio de titularidad entre particulares",
        "precio_gestion": 119.79,  # 99€ + IVA
        "precio_base_sin_iva": 99.0,
        "incluye": ["Gestión administrativa completa", "Tasas DGT", "Tramitación ITP en nombre del cliente"],
        "no_incluye": ["ITP (se calcula aparte y lo paga el cliente)"],
        "documentos": ["DNI comprador y vendedor", "Permiso de circulación", "Ficha técnica", "Contrato de compraventa firmado"],
        "plazo": "mismo día hábil si documentación completa antes de las 13h"
    },
    "cambio_titularidad_empresa": {
        "nombre": "Cambio de titularidad con empresa o compraventa profesional",
        "precio_gestion": 119.79,  # 99€ + IVA
        "precio_base_sin_iva": 99.0,
        "incluye": ["Gestión administrativa completa", "Tasas DGT", "Tramitación en nombre del cliente"],
        "no_incluye": ["ITP o IVA según corresponda"],
        "documentos": ["DNI comprador", "CIF empresa vendedora", "Permiso de circulación", "Ficha técnica", "Factura de compraventa"],
        "plazo": "mismo día hábil si documentación completa antes de las 13h"
    },
    "notificacion_venta": {
        "nombre": "Notificación de venta / Comunicación de transmisión",
        "precio_gestion": 119.79,  # 99€ + IVA
        "precio_base_sin_iva": 99.0,
        "incluye": ["Gestión administrativa completa", "Tasas DGT"],
        "no_incluye": [],
        "documentos": ["DNI vendedor", "Permiso de circulación", "Contrato de compraventa o documento de transmisión"],
        "plazo": "mismo día hábil"
    },
    "baja_temporal": {
        "nombre": "Baja temporal de vehículo",
        "precio_gestion": 59.29,  # 49€ + IVA
        "precio_base_sin_iva": 49.0,
        "incluye": ["Gestión administrativa", "Tasas DGT"],
        "no_incluye": [],
        "documentos": ["DNI titular", "Permiso de circulación", "Ficha técnica"],
        "plazo": "mismo día hábil"
    },
    "baja_definitiva": {
        "nombre": "Baja definitiva de vehículo",
        "precio_gestion": 59.29,  # 49€ + IVA
        "precio_base_sin_iva": 49.0,
        "incluye": ["Gestión administrativa", "Tasas DGT"],
        "no_incluye": [],
        "documentos": ["DNI titular", "Permiso de circulación", "Ficha técnica", "Certificado de destrucción si aplica"],
        "plazo": "mismo día hábil"
    },
    "rehabilitacion_baja": {
        "nombre": "Rehabilitación de baja de vehículo",
        "precio_gestion": 59.29,  # 49€ + IVA
        "precio_base_sin_iva": 49.0,
        "incluye": ["Gestión administrativa", "Tasas DGT"],
        "no_incluye": [],
        "documentos": ["DNI titular", "Permiso de circulación", "Ficha técnica", "ITV en vigor"],
        "plazo": "mismo día hábil"
    },
    "cancelacion_embargo": {
        "nombre": "Cancelación de embargo o reserva de dominio",
        "precio_gestion": 156.09,  # 129€ + IVA
        "precio_base_sin_iva": 129.0,
        "incluye": ["Gestión administrativa completa", "Tasas DGT", "Coordinación con entidad financiera"],
        "no_incluye": ["Costes de cancelación de la entidad financiera si los hubiera"],
        "documentos": ["DNI titular", "Permiso de circulación", "Certificado de cancelación del embargo o carta de pago"],
        "plazo": "2-5 días hábiles según entidad"
    },
    "cambio_servicio": {
        "nombre": "Cambio de servicio (particular a taxi, alquiler, etc.)",
        "precio_gestion": 119.79,  # 99€ + IVA
        "precio_base_sin_iva": 99.0,
        "incluye": ["Gestión administrativa", "Tasas DGT"],
        "no_incluye": [],
        "documentos": ["DNI titular", "Permiso de circulación", "Ficha técnica", "Documentación del nuevo servicio"],
        "plazo": "2-3 días hábiles"
    },
    "cambio_domicilio": {
        "nombre": "Cambio de domicilio en permiso de circulación",
        "precio_gestion": 119.79,  # 99€ + IVA
        "precio_base_sin_iva": 99.0,
        "incluye": ["Gestión administrativa", "Tasas DGT"],
        "no_incluye": [],
        "documentos": ["DNI titular con nuevo domicilio", "Permiso de circulación"],
        "plazo": "mismo día hábil"
    },
    "donacion_herencia": {
        "nombre": "Cambio de titularidad por donación o herencia",
        "precio_gestion": 119.79,  # 99€ + IVA (base), puede incrementarse
        "precio_base_sin_iva": 99.0,
        "precio_herencia_sin_iva": 139.0,  # 139€ + IVA para herencias complejas
        "precio_herencia_iva": 168.19,
        "incluye": ["Gestión administrativa completa", "Tasas DGT"],
        "no_incluye": ["Impuesto de donaciones o sucesiones (varía por CCAA y valor)"],
        "documentos": ["DNI donante y donatario / heredero", "Permiso de circulación", "Ficha técnica", "Escritura de donación o testamento/declaración de herederos", "Justificante liquidación impuesto donaciones/sucesiones"],
        "plazo": "2-5 días hábiles",
        "nota": "Caso complejo — requiere validación previa"
    },
    "informe_profesional": {
        "nombre": "Informe con análisis profesional del vehículo o expediente",
        "precio_gestion": 42.35,  # 35€ + IVA
        "precio_base_sin_iva": 35.0,
        "incluye": ["Análisis completo del expediente", "Detección de cargas y embargos", "Valoración de viabilidad", "Informe escrito"],
        "no_incluye": [],
        "documentos": ["Matrícula del vehículo", "DNI del solicitante"],
        "plazo": "mismo día hábil"
    },
    "matriculacion": {
        "nombre": "Matriculación de vehículo",
        "precio_gestion": 242.0,  # 200€ + IVA
        "precio_base_sin_iva": 200.0,
        "incluye": ["Gestión administrativa completa", "Tasas DGT"],
        "no_incluye": ["Impuesto de matriculación si aplica", "IVA del vehículo"],
        "documentos": ["DNI titular", "Factura del vehículo", "Certificado de conformidad", "ITV si aplica"],
        "plazo": "3-7 días hábiles"
    }
}

# Tasas DGT de referencia (para calcular precios de trámites no catalogados)
# Regla: precio Transfer Auto = mínimo 3x la tasa DGT
DGT_TASAS_REFERENCIA = {
    "cambio_titularidad": 55.70,
    "baja_temporal": 16.58,
    "baja_definitiva": 16.58,
    "rehabilitacion": 16.58,
    "duplicado_permiso": 16.58,
    "cambio_domicilio": 16.58,
    "cambio_servicio": 55.70,
    "matriculacion_nueva": 97.84,
    "reforma_vehiculo": 55.70,
}

def get_service(tramite_key: str) -> dict:
    return CATALOG.get(tramite_key, None)

def get_price_for_unknown_service(tasa_dgt: float) -> float:
    """Para trámites no catalogados: mínimo 3x la tasa DGT + IVA"""
    return round(tasa_dgt * 3 * 1.21, 2)
