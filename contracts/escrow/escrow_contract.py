from beaker import *
from pyteal import *


class EscrowState:
    oracle_address = GlobalStateVar(TealType.bytes, key="oracle")
    total_received = GlobalStateVar(TealType.uint64, key="total")


app = Application(
    "NeuralLedgerEscrow",
    state=EscrowState(),
    descr="Receives x402 payments and releases with revenue split",
)


@app.create
def create(oracle: abi.Address) -> Expr:
    return Seq([
        app.state.oracle_address.set(oracle.get()),
        app.state.total_received.set(Int(0)),
    ])


@app.external
def release_payment(
    task_hash: abi.String,
    recipient: abi.Address,
    platform_account: abi.Address,
    platform_share_bps: abi.Uint64,
    *,
    output: abi.Bool,
):
    """
    Split payment: platform_share_bps basis points to platform,
    remainder to original requester. Oracle-only.
    """
    return Seq([
        Assert(
            Txn.sender() == app.state.oracle_address.get(),
            comment="Only oracle can release payments",
        ),
        Assert(Txn.type_enum() == TxnType.ApplicationCall),
        Assert(Gtxn[0].type_enum() == TxnType.Payment),

        (total := ScratchVar(TealType.uint64)),
        total.store(Gtxn[0].amount()),

        (platform_amt := ScratchVar(TealType.uint64)),
        platform_amt.store(
            WideRatio([total.load(), platform_share_bps.get()], [Int(10000)])
        ),

        (requester_amt := ScratchVar(TealType.uint64)),
        requester_amt.store(total.load() - platform_amt.load()),

        InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: platform_account.get(),
            TxnField.amount: platform_amt.load(),
            TxnField.fee: Int(0),
        }),

        InnerTxnBuilder.Execute({
            TxnField.type_enum: TxnType.Payment,
            TxnField.receiver: recipient.get(),
            TxnField.amount: requester_amt.load(),
            TxnField.fee: Int(0),
        }),

        app.state.total_received.set(
            app.state.total_received.get() + total.load()
        ),

        output.set(Bool(True)),
    ])


@app.external(read_only=True)
def get_total_received(*, output: abi.Uint64):
    return output.set(app.state.total_received.get())
