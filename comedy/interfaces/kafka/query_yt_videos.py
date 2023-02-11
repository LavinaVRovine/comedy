if __name__ == '__main__':
    from ksql import KSQLAPI
    import ksql
    ksql.builder.string_types
    from my_kafka.kafka_globals import KAFKA_SETUP
    client = KSQLAPI('http://localhost:8088')
    tables = client.ksql("show tables")
    client
    client.create_stream(
        "YT_videos",columns_type={
            "ID BIGINT, title varchar, description VARCHAR, thumbnails VARCHAR"
        },topic="YT_videos"
    )

    print()