from pymongo import MongoClient
from abc import ABCMeta
from lxml import etree
import xmljson
import logging
from threading import Lock, Thread, Condition

logger = logging.getLogger("publisher")

class DataSource:
    __metaclass__ = ABCMeta

    def get_data(self, xpath: str):
        raise NotImplementedError("This is only an interface")

    def get_data_when_changed(self, xpath: str):
        raise NotImplementedError("This is only an interface")

    def xpath_exists(self, xpath: str):
        raise NotImplementedError("This is only an interface")

    def register_change_listener(self, xpath:str):
        raise NotImplementedError("This is only an interface")



class MongoDataSource(DataSource):

    @staticmethod
    def get_base_doc_name(xpath: str) -> str:
        if xpath.startswith("/"):
            xpath = xpath[1:]

        return xpath.split("/")[0]


    def get_data_when_changed(self, xpath: str):
        pass

    def __init__(self, host: str, port: int, database: str, collection: str, timeout_ms: int = 2000):
        self.client = MongoClient(
            f"mongodb://{host}:{port}/?readPreference=primary&appname=netconf-publisher",
            serverSelectionTimeoutMS=timeout_ms)

        # Test MongoDB connection. Fails if could not connect to any mongodb server and raises an exception.
        self.client.server_info()
        self.collection = self.client[database][collection]
        self.add_change_listener_lock = Lock()
        self.change_listeners = {}

    def get_data(self, xpath: str):
        json_doc = self.collection.find_one({self.get_base_doc_name(xpath): {"$exists": True}})

        xml_doc = xmljson.parker.etree(json_doc, root=etree.Element("root"))
        xpath_real = "/root/" + xpath
        return xml_doc.xpath(xpath_real)

    def xpath_exists(self, xpath: str) -> bool:
        json_doc = self.collection.find_one({self.get_base_doc_name(xpath): {"$exists": True}})

        if not json_doc:
            return False

        xml_doc = xmljson.parker.etree(json_doc, root=etree.Element("root"))
        xpath_real = "/root/" + xpath
        data = xml_doc.xpath(xpath_real)

        return True if data else False

    def register_change_listener(self, xpath:str):
        with self.add_change_listener_lock:
            base_doc_name = self.get_base_doc_name(xpath)
            
            if base_doc_name in self.change_listeners:
                # If we already have a listener on that document
                # we only have to add a sub-listener for the xpath
                pass
            else:
                tmp_lock = Condition()
                Thread(target=self.document_change_listener, args=(xpath, tmp_lock), name=f"{base_doc_name}-listener-thread", daemon=True).start()
                tmp_lock.wait()
    
    def document_change_listener(self, base_doc_name, wait_for_listener_to_be_created_lock: Condition):
        with self.collection.watch() as stream:
            wait_for_listener_to_be_created_lock.notify()
            # This will trigger every time a document document is changed
            for change in stream:
                print(change)
                # For each sub-xpath related to this document, check if there is a change by
                # comparing the new value to an old stored value. If changed, notify all waiting threads.
