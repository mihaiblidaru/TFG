import pymongo

from pymongo import MongoClient
client = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0-zrkqn.mongodb.net/test?retryWrites=true&w=majority")
db = client['testdb']
try:
    print("Listening for notifications")
    with db['test_notifications'].watch() as stream:
        for change in stream:
            print(change)
except pymongo.errors.PyMongoError:
    # The ChangeStream encountered an unrecoverable error or the
    # resume attempt failed to recreate the cursor.
    logging.error('...')