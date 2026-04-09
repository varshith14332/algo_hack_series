from beaker import *
from pyteal import *


class MarketplaceState:
    oracle_address = GlobalStateVar(TealType.bytes, key="oracle")
    total_results = GlobalStateVar(TealType.uint64, key="total")


app = Application(
    "NeuralLedgerMarketplace",
    state=MarketplaceState(),
    descr="Stores result Merkle roots in Box Storage. Single source of truth for result integrity.",
)


@app.create
def create(oracle: abi.Address) -> Expr:
    return Seq([
        app.state.oracle_address.set(oracle.get()),
        app.state.total_results.set(Int(0)),
    ])


@app.external
def register_result(
    task_hash: abi.String,
    merkle_root: abi.String,
    original_requester: abi.Address,
    price_microalgo: abi.Uint64,
    *,
    output: abi.Bool,
):
    """Store result metadata in Box Storage. Oracle-only."""
    box_key = task_hash.get()
    box_value = Concat(
        merkle_root.get(),
        Bytes("|"),
        original_requester.get(),
        Bytes("|"),
        Itob(price_microalgo.get()),
    )

    return Seq([
        Assert(
            Txn.sender() == app.state.oracle_address.get(),
            comment="Only oracle can register results",
        ),
        Assert(
            Not(App.box_get(box_key).hasValue()),
            comment="Result already registered",
        ),
        Pop(App.box_create(box_key, Int(256))),
        App.box_put(box_key, box_value),
        app.state.total_results.set(
            app.state.total_results.get() + Int(1)
        ),
        output.set(Bool(True)),
    ])


@app.external(read_only=True)
def get_result_proof(task_hash: abi.String, *, output: abi.String):
    """Retrieve Merkle root and metadata for a task hash."""
    box_data = App.box_get(task_hash.get())
    return Seq([
        box_data,
        Assert(box_data.hasValue(), comment="Result not found"),
        output.set(box_data.value()),
    ])


@app.external(read_only=True)
def get_total_results(*, output: abi.Uint64):
    return output.set(app.state.total_results.get())
