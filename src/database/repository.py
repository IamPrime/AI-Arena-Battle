from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import (
    ConnectionFailure, 
    ServerSelectionTimeoutError,
    DuplicateKeyError,
    WriteError
)
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import logging
from contextlib import contextmanager

class DatabaseRepository:
    def __init__(self, connection_string: str, database_name: str = "complexflow_arena"):
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.logger = logging.getLogger(__name__)
        self._initialize_connection()
        self._create_indexes()
    
    def _initialize_connection(self):
        """Initialize MongoDB connection with proper configuration"""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
                maxPoolSize=50,
                minPoolSize=5,
                maxIdleTimeMS=30000,
                retryWrites=True,
                retryReads=True
            )
            
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.logger.info("Successfully connected to MongoDB")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Create necessary database indexes for performance"""
        try:
            # Index for vote queries
            self.db.votes.create_index([
                ("timestamp", DESCENDING),
                ("model_a", ASCENDING),
                ("model_b", ASCENDING)
            ])
            
            # Index for prompt-based queries
            self.db.votes.create_index([
                ("prompt_hash", ASCENDING)
            ])
            
            # Compound index for analytics
            self.db.votes.create_index([
                ("vote", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            
            self.logger.info("Database indexes created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create indexes: {e}")
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.client.start_session()
        try:
            yield session
        finally:
            session.end_session()
    
    def store_vote(self, prompt: str, model_a: str, model_b: str, vote: str, user_ip: str = "unknown") -> bool:
        """Store vote with transaction support"""
        print(f"DEBUG: store_vote called with prompt={prompt}, model_a={model_a}, model_b={model_b}, vote={vote}, user_ip={user_ip}")
        
        try:
            # Add metadata
            vote_document = {
                "ip_hash": hash(user_ip),  # For rate limiting
                "timestamp": datetime.now(timezone.utc),
                "prompt": prompt,
                "prompt_hash": hash(prompt),  # Add prompt hash for indexing
                "model_a": model_a,
                "model_b": model_b,
                "vote": vote,
            }
            
            # Insert vote document
            result = self.db.votes.insert_one(vote_document)
            
            if result.acknowledged and result.inserted_id:
                self.logger.info(f"✅ Vote inserted with ID: {result.inserted_id}")
                
                # Update model statistics
                self._update_model_stats_simple(vote_document)
                
                return True
            else:
                self.logger.error("❌ Vote insertion not acknowledged")
                return False
                    
        except DuplicateKeyError:
            self.logger.warning("Duplicate vote attempt detected")
            return False
        except WriteError as e:
            self.logger.error(f"Database write error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error storing vote: {e}")
            return False

    def _update_model_stats_simple(self, vote_data: Dict[str, Any]):
        """Update model statistics without transaction"""
        try:
            model_a = vote_data.get("model_a")
            model_b = vote_data.get("model_b")
            vote = vote_data.get("vote")
            
            # Validate model names before updating
            if not model_a or not model_b:
                self.logger.error(f"Invalid model names: model_a={model_a}, model_b={model_b}")
                return
            
            # Update stats for model A
            if vote == "A":
                # Model A wins
                self.db.model_stats.update_one(
                    {"model": model_a},
                    {"$inc": {"wins": 1, "total_battles": 1}},
                    upsert=True
                )
                # Model B loses
                self.db.model_stats.update_one(
                    {"model": model_b},
                    {"$inc": {"losses": 1, "total_battles": 1}},
                    upsert=True
                )
            elif vote == "B":
                # Model B wins
                self.db.model_stats.update_one(
                    {"model": model_b},
                    {"$inc": {"wins": 1, "total_battles": 1}},
                    upsert=True
                )
                # Model A loses
                self.db.model_stats.update_one(
                    {"model": model_a},
                    {"$inc": {"losses": 1, "total_battles": 1}},
                    upsert=True
                )
            else:  # Tie or Both Bad
                # Both models get a tie
                self.db.model_stats.update_one(
                    {"model": model_a},
                    {"$inc": {"ties": 1, "total_battles": 1}},
                    upsert=True
                )
                self.db.model_stats.update_one(
                    {"model": model_b},
                    {"$inc": {"ties": 1, "total_battles": 1}},
                    upsert=True
                )
            
            self.logger.info(f"✅ Model stats updated for vote: {vote}")
            
        except Exception as e:
            self.logger.error(f"Error updating model stats: {e}")

    def _update_model_stats(self, vote_data: Dict[str, Any], session):
        """Update model statistics in transaction"""
        model_a = vote_data.get("model_a")
        model_b = vote_data.get("model_b")
        vote = vote_data.get("vote")
        
        # Update stats for model A
        if vote == "A":
            self.db.model_stats.update_one(
                {"model": model_a},
                {"$inc": {"wins": 1, "total_battles": 1}},
                upsert=True,
                session=session
            )
            self.db.model_stats.update_one(
                {"model": model_b},
                {"$inc": {"losses": 1, "total_battles": 1}},
                upsert=True,
                session=session
            )
        elif vote == "B":
            self.db.model_stats.update_one(
                {"model": model_b},
                {"$inc": {"wins": 1, "total_battles": 1}},
                upsert=True,
                session=session
            )
            self.db.model_stats.update_one(
                {"model": model_a},
                {"$inc": {"losses": 1, "total_battles": 1}},
                upsert=True,
                session=session
            )
        else:  # Tie or Both Bad
            self.db.model_stats.update_one(
                {"model": model_a},
                {"$inc": {"ties": 1, "total_battles": 1}},
                upsert=True,
                session=session
            )
            self.db.model_stats.update_one(
                {"model": model_b},
                {"$inc": {"ties": 1, "total_battles": 1}},
                upsert=True,
                session=session
            )
    
    def cleanup_model_stats(self):
        """Clean up model stats with null/missing model names"""
        try:
            # Remove entries with null model names
            result1 = self.db.model_stats.delete_many({"model": None})
            self.logger.info(f"Removed {result1.deleted_count} entries with null model names")
            
            # Remove entries with empty string model names
            result2 = self.db.model_stats.delete_many({"model": ""})
            self.logger.info(f"Removed {result2.deleted_count} entries with empty model names")
            
            # Remove entries where model field doesn't exist
            result3 = self.db.model_stats.delete_many({"model": {"$exists": False}})
            self.logger.info(f"Removed {result3.deleted_count} entries with missing model field")
            
            total_removed = result1.deleted_count + result2.deleted_count + result3.deleted_count
            self.logger.info(f"Total cleanup: removed {total_removed} invalid entries")
            
            return True
        except Exception as e:
            self.logger.error(f"Error cleaning up model stats: {e}")
            return False
    
    def get_model_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get model leaderboard with win rates - improved with null handling"""
        try:
            pipeline = [
                # Filter out null/empty model names
                {"$match": {"model": {"$ne": None, "$ne": "", "$exists": True}}},
                {
                    "$addFields": {
                        "total_votes": "$total_battles",
                        "win_rate": {
                            "$cond": {
                                "if": {"$eq": ["$total_battles", 0]},
                                "then": 0,
                                "else": {"$divide": ["$wins", "$total_battles"]}
                            }
                        }
                    }
                },
                {"$sort": {"win_rate": -1, "total_battles": -1}},
                {"$limit": limit}
            ]
            
            result = list(self.db.model_stats.aggregate(pipeline))
            self.logger.info(f"Retrieved {len(result)} models for leaderboard")
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting model leaderboard: {e}")
            return []
    
    def get_vote_count(self) -> int:
        """Get total number of votes"""
        try:
            count = self.db.votes.count_documents({})
            self.logger.info(f"Total votes in database: {count}")
            return count
        except Exception as e:
            self.logger.error(f"Error getting vote count: {e}")
            return 0
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            self.client.admin.command('ping')
            self.logger.info("Database connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics for debugging"""
        try:
            stats = {
                "votes_count": self.db.votes.count_documents({}),
                "model_stats_count": self.db.model_stats.count_documents({}),
                "collections": self.db.list_collection_names(),
                "recent_votes": list(self.db.votes.find().sort("timestamp", -1).limit(5)),
                "model_stats_sample": list(self.db.model_stats.find().limit(5))
            }
            return stats
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {}
