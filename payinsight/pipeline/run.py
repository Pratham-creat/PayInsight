from payinsight.generator.seeded import generate_events
from payinsight.pipeline.stages import normalize, validate
from payinsight.warehouse.duckdb import Warehouse


def run(n: int = 1000, seed: int = 42, warehouse: Warehouse | None = None) -> Warehouse:
    target = warehouse or Warehouse()
    for chunk in generate_events(n, seed):
        target.load(normalize(validate(chunk)))
    return target
