from pydantic import BaseModel, RootModel, Field
from typing import Dict, Literal

class VentumACVOutput_Riegos(BaseModel):
    tipo: str
    entre_arboles: str
    entre_calles: str
    n_goteros_arbol: int | None
    n_arboles: float
    n_calles: int
    m_portagotero: int
    peso_portagoteros_16mm: int
    n_enganches: int
    peso_enganches: float
    metros_principal: float
    peso_principal_32mm: float
    peso_llaves: float
    kg_PP: float
    peso_tira_pollo: float
    peso_principal_17mm: float
    deposito_abono: float
    kg_PP_ha_anio: float
    kg_PE_1_ha_anio: float
    kg_PE_2_ha_anio: float
    kg_PE_deposito_ha_anio: float
    kg_PE_ha_anio: float
    kg_PVC_ha_anio: float
    kg_PVC_produccion: float
    kg_PP_produccion: float
    kg_PE_produccion: float

class VentumACVOutput_Caseta(BaseModel):
    alto: str
    largo: str
    ancho: str
    largo_tejado: str
    ancho_tejado: str
    superficie_tejado: float
    kg_hormigon_m2: float
    kg_hormigon: float
    peso_m2_chapas_acero: float
    kg_poliuretano: float
    kg_acero: float
    kg_hor: float
    kg_PU: float
    kg_acero_ha_anio: float

class VentumACVOutput_Bombeo(BaseModel):
    cabeas: float
    potencia: str
    consumo_l_h: str
    kg_acero_ha_produccion: float

class VentumACVOutput_Fertilizantes(BaseModel):
    kg_N: float
    kg_K2O: float
    kg_P2O5: float
    kg_NH3: float
    kg_N2O: float
    kg_NOX: float
    kg_NO3: float
    transporte_fert_UF_1: float

class VentumACVOutput_ManejoCultivo_Item(BaseModel):
    rendimiento_h_ha: float = Field(alias="rendimeinto_h_ha")
    UF_1_ha: float
    UF_1_ha_produccion: float
    fabricacion: float
    reparacion: float
    UF_1_kg: float
    UF_1_kg_produccion: float

class VentumACVOutput_ManejoCultivo(BaseModel):
    application_of_plant_protection_product: VentumACVOutput_ManejoCultivo_Item = Field(
        alias="Application of plant protection product, by field sprayer [CH]"
    )
    ocupacion_suelo: float
    uso_de_agua: float

class VentumACVOutput_Maquinaria_Cosechadora(BaseModel):
    UF_kg: float
    UF_kg_produccion: float
    UF_kg_fabricacion: float
    UF_kg_fabricacion_produccion: float

class VentumACVOutput_Maquinaria(BaseModel):
    cosechadora: VentumACVOutput_Maquinaria_Cosechadora

class VentumACVOutput(BaseModel):
    riegos: VentumACVOutput_Riegos
    caseta: VentumACVOutput_Caseta
    bombeo: VentumACVOutput_Bombeo
    fitosanitarios: Dict[str, float]
    fertilizantes: VentumACVOutput_Fertilizantes
    manejo_cultivo: VentumACVOutput_ManejoCultivo
    maquinaria: VentumACVOutput_Maquinaria