from kombu import Connection, Exchange, Queue

__all__ = ["broker_publish_hmm", "broker_publish_scan"]


def broker_publish_hmm(hmm_id: int, hmm_filename: str, job_id: int):
    exchange = Exchange("hmm", "direct", durable=True)
    queue = Queue("hmm", exchange=exchange, routing_key="hmm")

    with Connection("amqp://guest:guest@localhost//") as conn:
        producer = conn.Producer(serializer="json")
        producer.publish(
            {"hmm_id": hmm_id, "hmm_filename": hmm_filename, "job_id": job_id},
            exchange=exchange,
            routing_key="hmm",
            declare=[queue],
        )


def broker_publish_scan(
    scan_id: int,
    hmm_id: int,
    hmm_filename: str,
    db_id: int,
    db_filename: str,
    job_id: int,
):
    exchange = Exchange("scan", "direct", durable=True)
    queue = Queue("scan", exchange=exchange, routing_key="scan")

    with Connection("amqp://guest:guest@localhost//") as conn:
        producer = conn.Producer(serializer="json")
        producer.publish(
            {
                "scan_id": scan_id,
                "hmm_id": hmm_id,
                "hmm_filename": hmm_filename,
                "db_id": db_id,
                "db_filename": db_filename,
                "job_id": job_id,
            },
            exchange=exchange,
            routing_key="scan",
            declare=[queue],
        )
