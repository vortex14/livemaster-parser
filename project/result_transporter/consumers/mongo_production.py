from typhoon.components.result_transporter.executions.base_consumer import BaseConsumer

from typhoon.extensions.elogger.typhoon_logger import typhoon_logger
class MongoProduction(BaseConsumer):

    def __init__(self, config, loop):

        super().__init__(config, loop)
        self.log = typhoon_logger(name="MongoProduction", component="transporter")
        self.collection = self.get_mongo_collection(collection_name="books", client_name="main")

    async def sync_send(self, task):
        await self.collection.update_one({"id": task.result["id"]}, {"$set": task.result}, upsert=True)

    async def send(self, task):
        # self.log.debug(task.result)
        await self.collection.update_one({"id": task.result["id"]}, {"$set": task.result}, upsert=True)

    async def send_many(self, bucket):
        bulk = self.collection.initialize_ordered_bulk_op()
        for task in bucket:
            bulk.find({"upc": task.result["upc"]}).upsert().update({"$set": task.result})
        await bulk.execute()
