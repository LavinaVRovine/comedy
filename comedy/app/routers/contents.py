from fastapi import APIRouter
from comedy.config import CONFLUENT_CONFIG
# noinspection PyUnresolvedReferences
from confluent_kafka.error import KafkaError, KafkaException
from content_models.videos import YoutubeVideo
from confluent_kafka import Consumer
import sys

from confluent_kafka.serialization import SerializationContext, MessageField

from confluent_kafka.schema_registry.avro import AvroDeserializer

from kafka_helpers import topic, schema_registry_client, youtube_videos_value_schema

router = APIRouter(prefix="/contents", responses={404: {"description": "Not found"}})
import random
import uuid
gid_ = str(uuid.uuid4())
import datetime
def get_n_thingis(n=3):
    start =datetime.datetime.now()
    consumer = Consumer(CONFLUENT_CONFIG | {
        'group.id': gid_,
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True,
    })
    print(f"{datetime.datetime.now() - start}")

    deserializer = AvroDeserializer(schema_registry_client, youtube_videos_value_schema.schema.schema_str,
                                    from_dict=YoutubeVideo.from_avro)

    msgs = []
    try:
        consumer.subscribe([topic])
        failed_counter = 0
        while True:
            if failed_counter >= 4 or len(msgs) >= n:
                print("Failed 4 times")
                break
            if len(msgs) > n:
                break
            msg = consumer.poll(timeout=0.5, )
            if msg is None:
                failed_counter += 1
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                if msg.key():
                    video = deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
                    msgs.append(
                        video
                    )
                    failed_counter = 0

    finally:
        # Close down consumer to commit final offsets.
        consumer.close()
    return msgs


@router.get("/latest-contents/", tags=["latest-contents"])
async def get_latest_contents():
    return get_n_thingis()


if __name__ == '__main__':
    m = get_n_thingis()
    print()
