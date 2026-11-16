from payinsight.generator.seeded import generate_payments


def test_generator_is_deterministic_and_chunked():
    first = list(generate_payments(11, seed=7, chunk_size=4))
    second = list(generate_payments(11, seed=7, chunk_size=4))
    assert [e.model_dump() for c in first for e in c] == [e.model_dump() for c in second for e in c]
    assert [len(c) for c in first] == [4, 4, 3]
    assert first[0][0].payment_id.startswith("pay_")


def test_generator_has_payment_domain_fields():
    payment = next(generate_payments(1))[0]
    assert payment.currency == "INR"
    assert payment.merchant_id.startswith("mer_")
    assert payment.amount > 0
