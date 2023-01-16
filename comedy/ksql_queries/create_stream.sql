CREATE STREAM YT_VIDEOS (
  id VARCHAR KEY,
  title VARCHAR,
  description VARCHAR,
  published_at VARCHAR

) WITH (
 KAFKA_TOPIC = 'YT_VIDEOS',
  PARTITIONS =1,
  VALUE_FORMAT = 'avro',
  TIMESTAMP='published_at',
  TIMESTAMP_FORMAT='yyyy-MM-ddTHH:mm:ss'
);