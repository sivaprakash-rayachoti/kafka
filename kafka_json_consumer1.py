import argparse

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONDeserializer


API_KEY = 'FXBQOYMN6BPLQATD'
ENDPOINT_SCHEMA_URL  = 'https://psrc-mw0d1.us-east-2.aws.confluent.cloud'
API_SECRET_KEY = 'DfRYczELBQNScQ8KomEyhH51nif/knENFjGMGAmUMslFRzzr4TroJ21DCdCynOro'
BOOTSTRAP_SERVER = 'pkc-ymrq7.us-east-2.aws.confluent.cloud:9092'
SECURITY_PROTOCOL = 'SASL_SSL'
SSL_MACHENISM = 'PLAIN'
SCHEMA_REGISTRY_API_KEY = 'TBNO7C6GKSK3Q2ZD'
SCHEMA_REGISTRY_API_SECRET = '4ZrAK4hsnPqFBSitTlJ4aqKBX/TJEuCPItHbyz6WnddplTeZMcynE/fZw50HPH5S'


def sasl_conf():

    sasl_conf = {'sasl.mechanism': SSL_MACHENISM,
                 # Set to SASL_SSL to enable TLS support.
                #  'security.protocol': 'SASL_PLAINTEXT'}
                'bootstrap.servers':BOOTSTRAP_SERVER,
                'security.protocol': SECURITY_PROTOCOL,
                'sasl.username': API_KEY,
                'sasl.password': API_SECRET_KEY
                }
    return sasl_conf



def schema_config():
    return {'url':ENDPOINT_SCHEMA_URL,
    
    'basic.auth.user.info':f"{SCHEMA_REGISTRY_API_KEY}:{SCHEMA_REGISTRY_API_SECRET}"

    }


class Order:   
    def __init__(self,record:dict):
        for k,v in record.items():
            setattr(self,k,v)
        
        self.record=record
   
    @staticmethod
    def dict_to_order(data:dict,ctx):
        return Order(record=data)

    def __str__(self):
        return f"{self.record}"


def main(topic):

    schema_registry_conf = schema_config()
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)
    schema_str = schema_registry_client.get_latest_version('rest-topic-value').schema.schema_str
    json_deserializer = JSONDeserializer(schema_str,
                                         from_dict=Order.dict_to_order)

    consumer_conf = sasl_conf()
    consumer_conf.update({
                     'group.id': 'group1',
                     'auto.offset.reset': "earliest"})

    consumer = Consumer(consumer_conf)
    consumer.subscribe([topic])

    count = 0
    while True:
        try:
            # SIGINT can't be handled when polling, limit timeout to 1 second.
            msg = consumer.poll(1.0)
            
            if msg is None:
                print('No of records consumed by consumer 1 :' + str(count))
                
                continue

            order = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))

            if order is not None:
                print("User record {}: order: {}\n"
                      .format(msg.key(), order))
                count += 1

        except KeyboardInterrupt:
            break

    consumer.close()

main("rest-topic")

# python /Users/DELL/Desktop/BigData/kafka/assignment/kafka_json_consumer1.py