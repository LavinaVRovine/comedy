
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringSerializer, StringDeserializer
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer

from comedy.config import CONFLUENT_SCHEMA_REGISTRY_CONFIG

topic = "YT_VIDEOS"
schema_registry_client = SchemaRegistryClient(
    CONFLUENT_SCHEMA_REGISTRY_CONFIG
)
youtube_videos_value_schema = schema_registry_client.get_latest_version(f"{topic}-value")

serializing_config = {
    "key.serializer": StringSerializer(),
    "value.serializer": AvroSerializer(schema_registry_client, youtube_videos_value_schema.schema.schema_str)
}

