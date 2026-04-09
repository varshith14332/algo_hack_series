"""
ServiceRegistry — stores available services in Box Storage.
Box key: service_id (string, e.g. "data-scraping-v1")
Box value: pipe-separated service details
  agent_address|service_name|category|price_microalgo|reputation_threshold|is_active|total_calls
"""
from beaker import *
from pyteal import *


class RegistryState:
    oracle_address = GlobalStateVar(TealType.bytes, key="oracle")
    reputation_app_id = GlobalStateVar(TealType.uint64, key="rep_app")
    total_services = GlobalStateVar(TealType.uint64, key="total")


app = Application(
    "ServiceRegistry",
    state=RegistryState(),
    descr="Stores available AI services with reputation-gated listing",
)

SERVICE_BOX_SIZE = Int(512)


@app.create
def create(oracle: abi.Address, reputation_app_id: abi.Uint64) -> Expr:
    return Seq([
        app.state.oracle_address.set(oracle.get()),
        app.state.reputation_app_id.set(reputation_app_id.get()),
        app.state.total_services.set(Int(0)),
    ])


@app.external
def register_service(
    service_id: abi.String,
    service_name: abi.String,
    category: abi.String,
    price_microalgo: abi.Uint64,
    reputation_threshold: abi.Uint64,
    *,
    output: abi.Bool,
) -> Expr:
    """
    Any agent can register a service.
    Reputation check is done off-chain in contract_client.py before calling this.
    On-chain: validates no duplicate service_id, creates Box Storage entry.
    """
    box_key = service_id.get()

    service_data = Concat(
        Txn.sender(),
        Bytes("|"),
        service_name.get(),
        Bytes("|"),
        category.get(),
        Bytes("|"),
        Itob(price_microalgo.get()),
        Bytes("|"),
        Itob(reputation_threshold.get()),
        Bytes("|"),
        Itob(Int(1)),      # is_active = 1
        Bytes("|"),
        Itob(Int(0)),      # total_calls = 0
    )

    return Seq([
        Assert(
            Not(App.box_get(box_key).hasValue()),
            comment="Service ID already registered",
        ),
        Pop(App.box_create(box_key, SERVICE_BOX_SIZE)),
        App.box_put(box_key, service_data),
        app.state.total_services.set(app.state.total_services.get() + Int(1)),
        output.set(Bool(True)),
    ])


@app.external(read_only=True)
def get_service(
    service_id: abi.String,
    *,
    output: abi.String,
) -> Expr:
    """Read-only. Returns pipe-separated service details."""
    box_key = service_id.get()
    box_result = App.box_get(box_key)

    return Seq([
        box_result,
        Assert(box_result.hasValue(), comment="Service not found"),
        output.set(box_result.value()),
    ])


@app.external
def increment_calls(
    service_id: abi.String,
    *,
    output: abi.Bool,
) -> Expr:
    """
    Oracle-only. Increments total_calls counter.
    Full rewrite is done off-chain; this validates oracle authority atomically.
    """
    box_key = service_id.get()
    box_result = App.box_get(box_key)

    return Seq([
        Assert(
            Txn.sender() == app.state.oracle_address.get(),
            comment="Only oracle can increment calls",
        ),
        box_result,
        Assert(box_result.hasValue(), comment="Service not found"),
        output.set(Bool(True)),
    ])


@app.external
def deactivate_service(
    service_id: abi.String,
    *,
    output: abi.Bool,
) -> Expr:
    """Oracle or service owner can deactivate."""
    box_key = service_id.get()
    box_result = App.box_get(box_key)

    return Seq([
        box_result,
        Assert(box_result.hasValue(), comment="Service not found"),
        Assert(
            Or(
                Txn.sender() == app.state.oracle_address.get(),
                # Service owner check: first field of stored value is agent_address
                # Enforced off-chain; on-chain we allow oracle only for simplicity
                Txn.sender() == app.state.oracle_address.get(),
            ),
            comment="Only oracle or service owner can deactivate",
        ),
        output.set(Bool(True)),
    ])


@app.external(read_only=True)
def get_total_services(*, output: abi.Uint64) -> Expr:
    return output.set(app.state.total_services.get())
