from app.database.mongo import MongoDatabase 
from app.database.base import BaseDatabase


storage: BaseDatabase = MongoDatabase() 