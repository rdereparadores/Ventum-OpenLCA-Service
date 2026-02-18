import olca_ipc as ipc
import olca_schema as o

class OLCAClient:
    def __init__(self, port=3000):
        self.client = ipc.Client(port)
    
    # Group unit
    def get_all_unit_groups(self) -> list[o.UnitGroup]:
        return self.client.get_all(o.UnitGroup)
    
    def get_unit_group(self, name: str) -> o.UnitGroup:
        return self.client.get(o.UnitGroup, name=name)

    def add_unit_group(self, name: str, ref_unit: str) -> o.UnitGroup:
        unit_group = o.new_unit_group(name, ref_unit)
        self.client.put(unit_group)
        return unit_group
    
    # Flow property
    def get_all_flow_properties(self) -> list[o.UnitGroup]:
        return self.client.get_all(o.FlowProperty)

    def get_flow_property(self, name: str) -> o.FlowProperty:
        return self.client.get(o.FlowProperty, name=name)
    
    def add_flow_property(self, name: str, unit_group: o.UnitGroup | str) -> o.FlowProperty:
        if isinstance(unit_group, str):
            unit_group = self.get_unit_group(unit_group)

        flow_property = o.new_flow_property(name, unit_group)
        self.client.put(flow_property)
        return flow_property
    
    # Flow
    def get_all_flows(self) -> list[o.Flow]:
        return self.client.get_all(o.Flow)

    def get_flow(self, name: str) -> o.Flow:
        return self.client.get(o.Flow, name=name)

    # Product flow
    def get_all_product_flows(self) -> list[o.Flow]:
        return [f for f in self.get_all_flows() if f.flow_type == o.FlowType.PRODUCT_FLOW]

    def add_product_flow(self, name: str, flow_property_name: str) -> o.Flow:
        flow_property = self.get_flow_property(flow_property_name)
        product_flow = o.new_product(name, flow_property)
        self.client.put(product_flow)
        return product_flow

    # Elementary flow
    def get_all_elementary_flows(self) -> list[o.Flow]:
        return [f for f in self.get_all_flows() if f.flow_type == o.FlowType.ELEMENTARY_FLOW]

    def add_elementary_flow(self, name: str, flow_property_name: str) -> o.Flow:
        flow_property = self.get_flow_property(flow_property_name)
        elementary_flow = o.new_elementary_flow(name, flow_property)
        self.client.put(elementary_flow)
        return elementary_flow

    # Waste flow
    def get_all_waste_flows(self) -> list[o.Flow]:
        return [f for f in self.get_all_flows() if f.flow_type == o.FlowType.WASTE_FLOW]

    def add_waste_flow(self, name: str, flow_property_name: str) -> o.Flow:
        flow_property = self.get_flow_property(flow_property_name)
        waste_flow = o.new_waste(name, flow_property)
        self.client.put(waste_flow)
        return waste_flow
    
    # Process
    def get_all_processes(self) -> list[o.Process]:
        return self.client.get_all(o.Process)

    def get_process(self, name: str | None = None, uid: str | None = None) -> o.Process:
        return self.client.get(o.Process, name=name, uid=uid)

    def add_process(
        self,
        name: str,
        product_exchanges: dict[str, float] = None,
        elementary_exchanges: dict[str, float] = None,
        waste_exchanges: dict[str, float] = None,
        quantitative_ref_name: str | None = None
    ) -> o.Process:
        process = o.new_process(name)

        def add_exchange(flow: o.Flow, value: float, is_product_exchange: bool) -> o.Exchange | None:
            if value == 0:
                return None
            
            if value < 0:
                exchange = o.new_input(process, flow, abs(value))
            else:
                exchange = o.new_output(process, flow, value)
            
            if is_product_exchange and quantitative_ref_name and flow.name == quantitative_ref_name:
                exchange.is_quantitative_reference = True
            
            return exchange
        
        if product_exchanges:
            for flow_name, amount in product_exchanges.items():
                flow = self.get_flow(flow_name)
                add_exchange(flow, amount, is_product_exchange=True)
        
        if elementary_exchanges:
            for flow_name, amount in elementary_exchanges.items():
                flow = self.get_flow(flow_name)
                add_exchange(flow, amount, is_product_exchange=False)

        if waste_exchanges:
            for flow_name, amount in waste_exchanges.items():
                flow = self.get_flow(flow_name)
                add_exchange(flow, amount, is_product_exchange=True) # Un waste exchange puede ser referencia cuantitativa
        
        self.client.put(process)
        return process
    
    def update_process(self, process: o.Process) -> None:
        self.client.put(process)
    
    # Product system

    def add_product_system(self, process_uid: str) -> o.Ref:
        process = self.get_process(uid=process_uid)
        config = o.LinkingConfig(
            prefer_unit_processes=True,
            provider_linking=o.ProviderLinking.PREFER_DEFAULTS
        )

        return self.client.create_product_system(process=process, config=config)
    
    def get_product_system(self, uid: str | None = None, name: str | None = None) -> o.ProductSystem:
        return self.client.get(o.ProductSystem, uid=uid, name=name)
    
    def remove_product_system(self, uid: str) -> None:
        self.client.delete(o.Ref(ref_type=o.RefType.ProductSystem, id=uid))
    
    # Impact assesment methods

    def get_impact_method(self, uid: str) -> o.ImpactMethod:
        return self.client.get(o.ImpactMethod, uid=uid)
    
    # Calculations
    def calculate_process_impact(self, process_uid: str, impact_method_uid: str, amount: int) -> ipc.Result:
        product_system = self.add_product_system(process_uid=process_uid)

        setup = o.CalculationSetup(
            target=o.Ref(
                ref_type=o.RefType.ProductSystem,
                id=product_system.id
            ),
            impact_method=o.Ref(id=impact_method_uid),
            amount=amount
        )

        result = self.client.calculate(setup)
        result.wait_until_ready()
        #result.dispose()
        self.remove_product_system(product_system.id)
        return result
    
    def calculate_product_system_impact(self, product_system_uid: str, impact_method_uid: str, amount: int) -> ipc.Result:
        product_system = self.get_product_system(uid=product_system_uid)

        setup = o.CalculationSetup(
            target=o.Ref(
                ref_type=o.RefType.ProductSystem,
                id=product_system.id
            ),
            impact_method=o.Ref(id=impact_method_uid),
            amount=amount
        )

        result = self.client.calculate(setup)
        result.wait_until_ready()
        return result
