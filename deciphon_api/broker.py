from kombu import Connection, Exchange, Queue

__all__ = ["broker_publish_hmm"]


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
