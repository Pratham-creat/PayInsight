#!/usr/bin/env python
from payinsight.generator.seeded import generate_events
from payinsight.warehouse.duckdb import Warehouse

warehouse = Warehouse("payinsight.duckdb")
count = sum(warehouse.load(chunk) for chunk in generate_events(10000))
print(f"loaded {count} events")
warehouse.close()
