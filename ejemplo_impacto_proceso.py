from olca_client import OLCAClient
import olca_schema as o
import pandas as pd

client = OLCAClient(port=8080)

process_uid = input("Escribe el UUID del proceso a evaluar: ") # 0dc3d65b-7ff8-4c92-a694-748fb28070a9 89863fcc-3306-11dd-bd11-0800200c9a66 67829cd7-53f8-3b8c-acd5-5d441d8eeae3
impact_method_uid = input("Escribe el UUID del método de impacto a usar: ") # be749018-2f47-3c25-819e-6e0c6fca1cb5 4e4dee04-079f-4feb-96f4-6d042138b31b 2f995579-06bd-4681-b07c-cee3b1805b0d

product_system = client.add_product_system(process_uid)
impact_method = client.get_impact_method(impact_method_uid)

setup = o.CalculationSetup(
    target = o.Ref(
        ref_type=o.RefType.ProductSystem,
        id=product_system.id,
    ),
    impact_method=o.Ref(id=impact_method.id),
    amount=100
)

result = client.client.calculate(setup)
result.wait_until_ready()

impacts = result.get_total_impacts()

print(
    pd.DataFrame(
        data=[(
            i.impact_category.name,
            i.amount,
            i.impact_category.ref_unit
        ) for i in impacts],
        columns=["Categoría", "Cantidad", "Unidad"]
    )
)

result.dispose()