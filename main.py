import olca_ipc as ipc
import olca_schema as o
import pandas as pd
import numpy as np
import olca_client

from typing import Callable

technosphere = pd.DataFrame(
    data=[
        [1.0, -50.0, -1.0, 0.0],
        [-0.01, 1.0, -1.0, 0.0],
        [0.0, 0.0, 1.0, -1.0],
        [0.0, 0.0, 0.0, 100.0]
    ],
    columns=[
        "electricity production",
        "aliminium production",
        "aliminium foil production",
        "sandwitch package production"
    ],
    index=[
        "electricity [MJ]",
        "aluminium [kg]",
        "aluminium foil [kg]",
        "sandwitch package [Item(s)]"
    ],
)

interventions = pd.DataFrame(
    data=[
        [0.0, -5.0, 0.0, 0.0],
        [-0.5, 0.0, 0.0, 0.0],
        [3.0, 0.0, 0.0, 0.0],
        [2.0, 10.0, 0.0, 1.0]
    ],
    columns=technosphere.columns,
    index=[
        "bauxite [kg]",
        "crude oil [kg]",
        "CO2 [kg]",
        "solid waste [kg]"
    ]
)

client = olca_client.OLCAClient()

# Añadir unidades
client.add_unit_group("Mass units", "kg")
client.add_unit_group("Energy units", "MJ")
client.add_unit_group("Counting units", "Item(s)")

# Añadir propiedades de un flujo (flow)
client.add_flow_property("Mass", "Mass units")
client.add_flow_property("Energy", "Energy units")
client.add_flow_property("Number of items", "Counting units")

product_flows = []
for index, name in enumerate(technosphere.index):
    parts = name.split("[")
    name = parts[0].strip()
    unit = parts[1][0:-1].strip()
    match unit:
        case "kg":
            prop = "Mass"
        case "MJ":
            prop = "Energy"
        case "Item(s)":
            prop = "Number of items"

    product_flows.append(client.add_product_flow(name, prop))

elementary_flows = []
for index, name in enumerate(interventions.index):
    parts = name.split("[")
    name = parts[0].strip()
    unit = parts[1][0:-1].strip()
    match unit:
        case "kg":
            prop = "Mass"
        case "MJ":
            prop = "Energy"
        case "Item(s)":
            prop = "Number of items"

    elementary_flows.append(client.add_elementary_flow(name, prop))

for index, name in enumerate(technosphere.columns):
    product_exchanges = {product_flow.name: technosphere.iat[i, index] for i, product_flow in enumerate(product_flows)}
    elementary_exchanges = {elementary_flow.name: interventions.iat[i, index] for i, elementary_flow in enumerate(elementary_flows)}

    client.add_process(
        name=name,
        product_exchanges=product_exchanges,
        elementary_exchanges=elementary_exchanges,
        quantitative_ref_name=technosphere.index[index]
    )

setup = o.CalculationSetup(
    # "sandwitch package production"
    target=o.Ref(ref_type=o.RefType.Process, id=client.get_process("sandwitch package production").id),
    unit=o.Ref(ref_type=o.RefType.FlowProperty, id=client.get_flow_property("Number of items").id),
    amount=10
)
result = client.client.calculate(setup)
result.wait_until_ready()

inventory = result.get_total_flows()
print(
    pd.DataFrame(
        data=[
            (
                i.envi_flow.flow.name,
                i.envi_flow.is_input,
                i.amount,
                i.envi_flow.flow.ref_unit
            )
            for i in inventory
        ],
        columns=["Flow", "Is input?", "Amount", "Unit"],
    )
)
print(result.get_total_costs())

result.dispose()