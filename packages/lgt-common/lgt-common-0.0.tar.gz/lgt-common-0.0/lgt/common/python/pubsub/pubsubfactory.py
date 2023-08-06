import time
import env

from google.cloud import pubsub_v1
from google.api_core.exceptions import GoogleAPICallError
from google.auth.transport.grpc import *
from google.auth import jwt


class PubSubFactory:

    __cred: jwt.Credentials
    __delay: 3

    def __init__(self):
        self.cred = jwt.Credentials.from_service_account_file(env.google_application_credential)

    def create_publisher(self):
        return pubsub_v1.PublisherClient(credentials=self.cred)

    def create_subscriber(self):
        return pubsub_v1.SubscriberClient(credentials=self.cred)

    def get_topic_path(self, project_id, topic_name):
        topic = self.create_topic_if_doesnt_exist(topic_name)
        return pubsub_v1.PublisherClient.api.topic_path(project_id, topic)

    def create_topic_if_doesnt_exist(self, topic_name):
        time.sleep(self.__delay)
        publisher = pubsub_v1.PublisherClient(credentials=self.cred)
        try:
            return publisher.api.get_topic(topic_name)
        except GoogleAPICallError as ex:
            if ex.grpc_status_code == grpc.StatusCode.NOT_FOUND:
                return publisher.api.create_topic(name=topic_name)
            else:
                raise

    def create_subscription_if_doesnt_exist(self, subscriber_name, topic_name):
        time.sleep(self.__delay)
        subscriber = pubsub_v1.SubscriberClient(credentials=self.cred)
        try:
            return subscriber.api.get_subscription(subscriber_name)
        except GoogleAPICallError as ex:
            if ex.grpc_status_code == grpc.StatusCode.NOT_FOUND:
                return subscriber.api.create_subscription(name=subscriber_name, topic=topic_name,
                                                          push_config=None, ack_deadline_seconds=60)
            else:
                raise
