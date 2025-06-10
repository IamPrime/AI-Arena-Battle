from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

class DatabaseManager:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.client = None
        self.db = None
        self.logger = logging.getLogger(__name__)
        self._connect()
    
    def _connect(self):
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=10,
                minPoolSize=1
            )
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client.get_database()
            self.logger.info("Successfully connected to MongoDB")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def store_vote(self, vote_data: Dict[str, Any]) -> bool:
        try:
            vote_data["timestamp"] = datetime.now(timezone.utc)
            result = self.db.votes.insert_one(vote_data)
            return result.acknowledged
        except Exception as e:
            self.logger.error(f"Failed to store vote: {e}")
            return False
    
    def get_vote_stats(self) -> Optional[Dict[str, Any]]:
        try:
            pipeline = [
                {"$group": {
                    "_id": "$vote",
                    "count": {"$sum": 1}
                }}
            ]
            return list(self.db.votes.aggregate(pipeline))
        except Exception as e:
            self.logger.error(f"Failed to get vote stats: {e}")
            return None