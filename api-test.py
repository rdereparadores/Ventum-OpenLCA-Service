from fastapi import FastAPI
from olca_client import OLCAClient
from pydantic import BaseModel
from VentumACVOutput import VentumACVOutput
import olca_schema as o

app = FastAPI()
client = OLCAClient(port=8080)

class PostProcessImpact(BaseModel):
    impact_method_uid: str
    amount: int = 1

@app.get("/unit-group")
def get_all_unit_groups():
    return client.get_all_unit_groups()

@app.get("/flow")
def get_all_flows():
    return client.get_all_flows()

@app.get("/product-flow")
def get_all_product_flows():
    return client.get_all_product_flows()

@app.get("/elementary-flow")
def get_all_elementary_flows():
    return client.get_all_elementary_flows()

@app.get("/waste-flow")
def get_all_waste_flows():
    return client.get_all_waste_flows()

@app.get("/process")
def get_all_processes():
    return client.get_all_processes()

@app.post("/process/{uid}/impact")
def post_process_impact(uid: str, params: PostProcessImpact):
    process = client.get_process(uid=uid)
    result = client.calculate_process_impact(process_uid=uid, impact_method_uid=params.impact_method_uid, amount=params.amount)
    impacts = result.get_total_impacts()
    return {
        "data": {
            "process": {
                "name": process.name,
                "category": process.category,
                "description": process.description
            },
            "impact_result": [
                {
                    "category": i.impact_category.name,
                    "amount": i.amount,
                    "unit": i.impact_category.ref_unit
                } for i in impacts
            ]
        }
    }

class FlowDict():
    inputs: dict[str, float]
    outputs: dict[str, float]

@app.post("/ventum-acv")
def post_ventum_acv(output: VentumACVOutput):
    fertilizantes = FlowDict()
    fertilizantes.inputs = {
        "Ammonium nitrate phosphate, as N, at regional storehouse {RER}": output.fertilizantes.kg_N,
        "Ammonium nitrate phosphate, as P2O5, at regional storehouse {RER}": output.fertilizantes.kg_P2O5,
        "Diesel, burned in agricultural machine {CH}": output.fertilizantes.transporte_fert_UF_1,
        "Potassium nitrate, as K2O, at regional storehouse {RER}": output.fertilizantes.kg_K2O
    }
    fertilizantes.outputs = {
        "Fertilizantes T": 1,
        "Ammonia": output.fertilizantes.kg_NH3,
        "Dinitrogen monoxide": output.fertilizantes.kg_N2O,
        "Nitrate": output.fertilizantes.kg_NO3,
        "Nitrogen oxides, ES": output.fertilizantes.kg_NOX
    }

    manejo_de_cultivo = FlowDict()
    manejo_de_cultivo.inputs = {
        "Agricultural machinery, general, production {CH}": output.manejo_cultivo.application_of_plant_protection_product.UF_1_kg_produccion,
        "Agricultural machinery, tillage, production {CH}": 0,
        "Application of plant protection products, by field sprayer {CH}": output.manejo_cultivo.application_of_plant_protection_product.rendimiento_h_ha,
        "Combine harvesting {CH}": 0,
        "Diesel, burned in agricultural machine {CH}": output.maquinaria.cosechadora.UF_kg, # Algunos podrían ser arrays puesto que hay elementos con mismo nombre
        "Harvester, production {CH}": output.maquinaria.cosechadora.UF_kg_fabricacion,
        "Planting {CH}": 0,
        "Tillage, cultivating, chiselling {CH}": 0,
        "Tillage, harrowing, by rotary harrow {CH}": 0,
        "Tractor, production {CH}": output.maquinaria.cosechadora.UF_kg_fabricacion_produccion,
        "xx Tillage, rotary cultivator {CH}": 0,
        "Occupation, annual crop, irrigated": output.manejo_cultivo.ocupacion_suelo,
        "Transformation, to annual crop, irrigated": 0,
        "Water, unspecified natural origin, ES": output.manejo_cultivo.uso_de_agua
    }
    manejo_de_cultivo.outputs = {
        "Manejo de cultivo T": 1
    }

    pesticidas = FlowDict()
    pesticidas.inputs = {
        "Acetamide-anillide-compounds, at regional storehouse {RER}": output.fitosanitarios["Acetamide-anillide-compound, unspecified {RER}| production"],
        "Cyclic N-compounds, at regional storehouse {RER}": 0,
        "Dinitroaniline-compounds, at regional storehouse {RER}": 0,
        "Glyphosate, at regional storehouse {RER}": 0,
        "Metolachlor, at regional storehouse {RER}": 0,
        "Nitrile-compounds, at regional storehouse {RER}": 0,
        "Organophosphorus-compounds, at regional storehouse {RER}": 0,
        "Pendimethalin, at regional storage {RER}": 0,
        "Pesticide unspecified, at regional storehouse {RER}": output.fitosanitarios["Pesticice, unspecified {RER}| pesticice, unspecified production"],
        "Phenoxy-compounds, at regional storehouse {RER}": 0,
        "Pyretroid-compounds, at regional storehouse {RER}": 0,
        "Triazine-compounds, at regional storehouse {RER}": 0,
        "xx Captan, at regional storage {RER}": 0,
        "xx Diazole-compounds, at regional storehouse {RER}": 0,
        "xx Folpet, at regional storage {RER}": 0,
        "xx Pyridine-compounds, at regional storehouse {RER}": output.fitosanitarios[" Pyridine-compound {RER}|  pyridine-compound production"]
    }
    pesticidas.outputs = {
        "Pesticidas T": 1,
        "Pendimethalin, at regional storage {RER}": 0,
        "Chlorpyrifos": 0,
        "Metalaxyl-M": 0,
        "Imidacloprid": 0,
        "Alpha-cypermethrin": 0,
        "Abamectin": 0,
        "Folpet": 0,
        "PYRIDINE": 0,
        "Pesticides, unspecified": 0,
        "Tebuconazole": 0,
        "Metribuzin": 0,
        "Lambda-cyhalothrin": 0,
        "Pesticides, unspecified": 0,
        "Tebuconazole": 0,
        "Pendimethalin": 0,
        "Metribuzin": 0,
        "Lambda-cyhalothrin": 0
    }

    sistema_de_riego = FlowDict()
    sistema_de_riego.inputs = {
        "Water, well, RER": output.manejo_cultivo.uso_de_agua,
        "Steel, low alloyed, secondary production (100% Rec.) {CH}": 0,
        "Steel product manufacturing, average metal working {RER}": output.bombeo.kg_acero_ha_produccion,
        "Polypropylene, granulate, at plant {RER}": output.riegos.kg_PP_produccion,
        "Stretch blow moulding {RER}": 0,
        "Extrusion, plastic pipes {RER}": 0,
        "Polystyrene, expandable, at plant {RER}": output.riegos.kg_PE_produccion,
        "Polyvinylchloride, emulsion polymerised, at plant {RER}": output.riegos.kg_PVC_produccion,
        "Tractor, production {CH}": 0,
        "Diesel, burned in agricultural machine {CH}": 0,
        "Transport, freight, lorry, 7.5t-16t gross weight, fleet average {RER}": 0,
        "Polyethylene, HDPE, granulate, at plant {RER}": 0,
        "Electricity, low voltage, production from oil, at grid {CH}": 0
    }
    sistema_de_riego.outputs = {
        "Sistema de riego T": 1,
        "xx Recycling PVC {RER}": output.riegos.kg_PVC_ha_anio,
        "xx Recycling PP {RER}": output.riegos.kg_PP_ha_anio,
        "xx Recycling PE {RER}": output.riegos.kg_PE_ha_anio,
        "Recycling steel and iron {RER}": 0
    }

    product_system = client.get_product_system(name="TOMATE")
    fertilizantes_process = client.get_process(name="Fertilizantes T")
    manejo_de_cultivo_process = client.get_process(name="Manejo de cultivo T")
    pesticidas_process = client.get_process(name="Pesticidas T")
    sistema_de_riego_process = client.get_process(name="Sistema de riego T")

    def update_process_exchanges(process, flow_dict: FlowDict) -> None:
        for exchange in process.exchanges:
            if exchange.is_input:
                exchange.amount = flow_dict.inputs[exchange.flow.name]
            else:
                exchange.amount = flow_dict.outputs[exchange.flow.name]
        client.update_process(process)

    update_process_exchanges(fertilizantes_process, fertilizantes)
    update_process_exchanges(manejo_de_cultivo_process, manejo_de_cultivo)
    update_process_exchanges(pesticidas_process, pesticidas)
    update_process_exchanges(sistema_de_riego_process, sistema_de_riego)

    result = client.calculate_product_system_impact(product_system_uid=product_system.id, impact_method_uid="2f995579-06bd-4681-b07c-cee3b1805b0d", amount=0.001)
    impacts = result.get_total_impacts()

    tech_flows = result.get_total_requirements()
    
    fertilizantes_tech_flow = next((tf.tech_flow for tf in tech_flows if tf.tech_flow.flow.name == "Fertilizantes T"), None)
    manejo_cultivo_tech_flow = next((tf.tech_flow for tf in tech_flows if tf.tech_flow.flow.name == "Manejo de cultivo T"), None)
    pesticidas_tech_flow = next((tf.tech_flow for tf in tech_flows if tf.tech_flow.flow.name == "Pesticidas T"), None)
    sistema_riego_tech_flow = next((tf.tech_flow for tf in tech_flows if tf.tech_flow.flow.name == "Sistema de riego T"), None)
    
    impact_fertilizantes = result.get_total_impacts_of(tech_flow=fertilizantes_tech_flow)
    impact_manejo_cultivo = result.get_total_impacts_of(tech_flow=manejo_cultivo_tech_flow)
    impact_pesticidas = result.get_total_impacts_of(tech_flow=pesticidas_tech_flow)
    impact_sistema_riego = result.get_total_impacts_of(tech_flow=sistema_riego_tech_flow)

    result.dispose()

    return {
        "impacto_fertilizantes": [
            {
                "category": i.impact_category.name,
                "amount": i.amount,
                "unit": i.impact_category.ref_unit
            } for i in impact_fertilizantes
        ],
        "impacto_manejo_cultivo": [
            {
                "category": i.impact_category.name,
                "amount": i.amount,
                "unit": i.impact_category.ref_unit
            } for i in impact_manejo_cultivo
        ],
        "impacto_pesticidas": [
            {
                "category": i.impact_category.name,
                "amount": i.amount,
                "unit": i.impact_category.ref_unit
            } for i in impact_pesticidas
        ],
        "impacto_sistema_riego": [
            {
                "category": i.impact_category.name,
                "amount": i.amount,
                "unit": i.impact_category.ref_unit
            } for i in impact_sistema_riego
        ],
        "impacto_total": [
            {
                "category": i.impact_category.name,
                "amount": i.amount,
                "unit": i.impact_category.ref_unit
            } for i in impacts
        ]
    }