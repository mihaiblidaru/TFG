from abc import ABCMeta
from lxml import etree
from termcolor import colored
import sys


# Classes that handle the notifications received from publishers
# This can be anything, from printing data to the terminal, saving it into a textfile,
# to saving them into a SQL or NoSQL Database

class NotificationHandler:
    """ Interface for notification handlers. Has only one function that will be called
    each time a notification is received.
    """
    __metaclass__ = ABCMeta

    def __call__(self, notification_data, subscription_id: int, path):
        raise NotImplementedError()


class PrintNotificationHandler(NotificationHandler):
    """ Printer handler. just prints the content of the notification
    to a given stream, stdout by default
    """

    def __call__(self, notification_data, subscription_id: int, path: str, out_file=sys.stdout):
        print(f"[{colored(subscription_id, 'green')}] - {colored(path, 'green')}", file=out_file)
        print(etree.tounicode(notification_data, pretty_print=True), end="\n\n", file=out_file)


class MongoNotificationHandler(NotificationHandler):
    """ Saves all notifications into a MongoDB collection. The notification is saved as
    XML string without any conversion to JSON"
    """

    def __init__(self, host: str, port: int, database: str, collection: str):
        """
        :param host: Host of the MongoDB server
        :param port: Port on which the MongoDB server is listening
        :param database: The name of the database where the data will be stored
        :param collection: The name of the collection inside the database where data will be stored
        """
        pass

    def __call__(self, notification_data, subscription_id: int, path):
        pass
