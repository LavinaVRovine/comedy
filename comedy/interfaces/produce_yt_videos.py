if __name__ == '__main__':
    from typing import List
    from comedy.sources.youtube import YoutubeSource
    from comedy.content_models.videos import YoutubeVideo
    from confluent_kafka import Producer, SerializingProducer
    from comedy.kafka_helpers import topic, serializing_config
    from comedy.config import CONFLUENT_CONFIG

    serializing_config["value.serializer"]._to_dict = YoutubeVideo.to_avro
    producer = SerializingProducer(CONFLUENT_CONFIG | serializing_config)

    youtube_source = YoutubeSource()
    bittersteel_playlist_id = "UU4tWW-toq9KKo-HL3S8D23A"
    bitterstel_channel_id = 'UC4tWW-toq9KKo-HL3S8D23A'  # = "UC_x5XG1OV2P6uZZ5FSM9Ttw"
    # uploads_playilis = youtube_source.get_channels_uploaded_playlist_id(channel_id=bitterstel_channel_id)
    def on_delivery(err, record):

        print(f"{record}: {err}")
        ...
    vs:List[YoutubeVideo] = youtube_source.get_videos(bittersteel_playlist_id)
    for v in vs:

        producer.produce(bitterstel_channel_id, key=v.id, value=v, )# on_delivery=on_delivery)
    producer.flush()
    # print()
    #
    # # OK, tohle je feeed ehm
    # my_subs = YoutubeSource().get_my_subs()
    #
    # subs_formatted = []
    # for s in my_subs:
    #     snippet = s["snippet"]
    #     subs_formatted.append(
    #         YoutubeChanel(
    #             _id=snippet["channelId"],
    #             title=snippet["title"],
    #             description=snippet.get("description", None)
    #
    #         )
    #     )
    #
    # i.produce(
    #     topic, data=subs_formatted
    # )