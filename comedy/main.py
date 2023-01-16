from confluent_kafka.error import KafkaError, KafkaException
from sources.youtube import YoutubeSource
from content_models.channel import YoutubeChanel
from confluent_kafka import Consumer
import sys



if __name__ == '__main__':
    ...
    #from sources.youtube import youtube_source
    # print()
    #
    #
    # consumer = Consumer(KAFKA_SETUP | {
    #     'group.id': 'mygroup2',
    #     'auto.offset.reset': 'earliest',
    #     'enable.auto.commit': False,
    # })
    #
    #
    # i = KafkaInterface(
    #     kafka_admin=MyKafkaAdminClient(setup=KAFKA_SETUP),
    #     kafka_producer=MyKafkaProducer(setup=KAFKA_SETUP)
    # )
    # topic = "YT_subscriptions"
    # if True:
    #     # OK, tohle je feeed ehm
    #     my_subs = YoutubeSource().get_my_subs()
    #
    #     subs_formatted = []
    #     for s in my_subs:
    #         snippet = s["snippet"]
    #         subs_formatted.append(
    #             YoutubeChanel(
    #                 _id=snippet["channelId"],
    #                 title=snippet["title"],
    #                 description=snippet.get("description", None)
    #
    #             )
    #         )
    #
    #     i.produce(
    #         topic, data=subs_formatted
    #     )
    #
    #
    # running = True
    # msgs = []
    # try:
    #     consumer.subscribe([topic])
    #
    #     while running:
    #         msg = consumer.poll(timeout=1.0)
    #         if msg is None:
    #             continue
    #
    #         if msg.error():
    #             if msg.error().code() == KafkaError._PARTITION_EOF:
    #                 # End of partition event
    #                 sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
    #                                  (msg.topic(), msg.partition(), msg.offset()))
    #             elif msg.error():
    #                 raise KafkaException(msg.error())
    #         else:
    #             if msg.key():
    #                 msgs.append(
    #                     YoutubeChanel.make_instance_of_self(msg.value().decode())
    #                 )
    # finally:
    #     # Close down consumer to commit final offsets.
    #     consumer.close()
    # print()