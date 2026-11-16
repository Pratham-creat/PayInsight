from payinsight.models import PaymentEvent
from payinsight.pipeline.stages import payments_frame
from payinsight.warehouse.duckdb import PaymentWarehouse


def load_events(events: list[PaymentEvent], warehouse: PaymentWarehouse | None = None):
    warehouse = warehouse or PaymentWarehouse()
    warehouse.load(payments_frame(events))
    return warehouse
