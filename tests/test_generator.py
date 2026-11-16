from payinsight.generator.seeded import generate_events


def test_generator_is_deterministic_and_chunked():
    a = list(generate_events(11, seed=7, chunk_size=4))
    b = list(generate_events(11, seed=7, chunk_size=4))
    assert [e.model_dump() for c in a for e in c] == [e.model_dump() for c in b for e in c]
    assert [len(c) for c in a] == [4, 4, 3]
