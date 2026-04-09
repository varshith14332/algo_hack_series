from beaker import *
from pyteal import *


class ReputationState:
    oracle_address = GlobalStateVar(TealType.bytes, key="oracle")


app = Application(
    "AgentReputation",
    state=ReputationState(),
    descr="Manages agent reputation scores as on-chain state",
)

SCORE_KEY_PREFIX = "agent_score_"
TASKS_KEY_PREFIX = "agent_tasks_"


@app.create
def create(oracle: abi.Address) -> Expr:
    return app.state.oracle_address.set(oracle.get())


@app.external
def update_score(
    agent_address: abi.Address,
    success: abi.Bool,
    *,
    output: abi.Uint64,
):
    score_key = Concat(Bytes(SCORE_KEY_PREFIX), agent_address.get())
    tasks_key = Concat(Bytes(TASKS_KEY_PREFIX), agent_address.get())

    current_score = App.globalGetEx(Int(0), score_key)
    current_tasks = App.globalGetEx(Int(0), tasks_key)

    return Seq([
        Assert(
            Txn.sender() == app.state.oracle_address.get(),
            comment="Only oracle can update reputation",
        ),
        current_score,
        current_tasks,

        (score := ScratchVar(TealType.uint64)),
        score.store(
            If(current_score.hasValue())
            .Then(current_score.value())
            .Else(Int(500))
        ),

        If(success.get())
        .Then(
            score.store(
                If(score.load() + Int(10) <= Int(1000))
                .Then(score.load() + Int(10))
                .Else(Int(1000))
            )
        )
        .Else(
            score.store(
                If(score.load() >= Int(20))
                .Then(score.load() - Int(20))
                .Else(Int(0))
            )
        ),

        App.globalPut(score_key, score.load()),
        App.globalPut(
            tasks_key,
            If(current_tasks.hasValue())
            .Then(current_tasks.value() + Int(1))
            .Else(Int(1)),
        ),

        output.set(score.load()),
    ])


@app.external(read_only=True)
def get_score(agent_address: abi.Address, *, output: abi.Uint64):
    score_key = Concat(Bytes(SCORE_KEY_PREFIX), agent_address.get())
    score = App.globalGetEx(Int(0), score_key)
    return Seq([
        score,
        output.set(
            If(score.hasValue()).Then(score.value()).Else(Int(500))
        ),
    ])
