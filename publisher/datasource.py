from pymongo import MongoClient
from abc import ABCMeta
from lxml import etree
import xmljson

class DataSource:
    __metaclass__ = ABCMeta

    def get_data(self, xpath: str):
        raise NotImplementedError("This is only an interface")

    def get_data_when_changed(self, xpath: str):
        raise NotImplementedError("This is only an interface")

    def xpath_exists(self, xpath: str):
        raise NotImplementedError("This is only an interface")


class MongoDataSource(DataSource):

    def get_data_when_changed(self, xpath: str):
        pass

    def __init__(self, host: str, port: int, database: str, collection: str, timeout_ms: int = 2000):
        self.client = MongoClient(
            f"mongodb://{host}:{port}/?readPreference=primary&appname=netconf-publisher",
            serverSelectionTimeoutMS=timeout_ms)

        # Test MongoDB connection. Fails if could not connect to any mongodb server and raises an exception.
        self.client.server_info()
        self.collection = self.client[database][collection]

    def get_data(self, xpath: str):
        base_doc_name = xpath.split("/")[0]
        if base_doc_name.startswith("/"):
            base_doc_name = base_doc_name[1:]

        json_doc = self.collection.find_one({base_doc_name: {"$exists": True}})

        xml_doc = xmljson.parker.etree(json_doc, root=etree.Element("root"))
        xpath_real = "/root/" + xpath
        return xml_doc.xpath(xpath_real)

    def xpath_exists(self, xpath: str) -> bool:
        if xpath.startswith("/"):
            xpath = xpath[1:]

        base_doc_name: str = xpath.split("/")[0]

        json_doc = self.collection.find_one({base_doc_name: {"$exists": True}})

        if not json_doc:
            return False

        xml_doc = xmljson.parker.etree(json_doc, root=etree.Element("root"))
        xpath_real = "/root/" + xpath
        data = xml_doc.xpath(xpath_real)

        return True if data else False
