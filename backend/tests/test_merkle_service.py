import pytest
from services.merkle_service import MerkleService


@pytest.fixture
def merkle():
    return MerkleService()


def test_build_tree_single_chunk(merkle):
    tree = merkle.build_tree(["hello world"])
    assert tree["root"]
    assert len(tree["leaves"]) == 2  # Padded to even


def test_build_tree_multiple_chunks(merkle):
    chunks = ["chunk one", "chunk two", "chunk three", "chunk four"]
    tree = merkle.build_tree(chunks)
    assert tree["root"]
    assert len(tree["leaves"]) == 4


def test_build_tree_empty_raises(merkle):
    with pytest.raises(ValueError):
        merkle.build_tree([])


def test_generate_and_verify_proof(merkle):
    chunks = ["alpha", "beta", "gamma", "delta"]
    tree = merkle.build_tree(chunks)

    for i in range(len(chunks)):
        proof = merkle.generate_proof(tree, i)
        # Proof should verify correctly for the original leaf
        valid = merkle.verify_proof(chunks[i], proof, tree["root"])
        assert valid, f"Proof failed for leaf {i}"


def test_verify_proof_tampered_fails(merkle):
    chunks = ["alpha", "beta", "gamma", "delta"]
    tree = merkle.build_tree(chunks)
    proof = merkle.generate_proof(tree, 0)

    # Tamper with the leaf data
    valid = merkle.verify_proof("TAMPERED", proof, tree["root"])
    assert not valid


def test_root_consistency(merkle):
    chunks = ["a", "b", "c", "d"]
    tree1 = merkle.build_tree(chunks[:])
    tree2 = merkle.build_tree(chunks[:])
    assert tree1["root"] == tree2["root"]


def test_different_content_different_root(merkle):
    t1 = merkle.build_tree(["hello"])
    t2 = merkle.build_tree(["world"])
    assert t1["root"] != t2["root"]
