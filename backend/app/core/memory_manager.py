import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages agent memory, knowledge, and learning patterns"""
    
    def __init__(self):
        self.memory_store = {}
        self.knowledge_base = {}
        self.learning_patterns = {}
        self.memory_limit = 10000  # Default memory limit
        
    async def initialize(self):
        """Initialize the memory manager"""
        logger.info("Memory manager initialized")
        
    async def store_memory(self, agent_id: str, memory_data: Dict[str, Any]) -> str:
        """Store a new memory for an agent"""
        memory_id = self._generate_memory_id(memory_data)
        
        if agent_id not in self.memory_store:
            self.memory_store[agent_id] = {}
            
        memory_entry = {
            "id": memory_id,
            "data": memory_data,
            "timestamp": datetime.now(),
            "access_count": 0,
            "importance": memory_data.get("importance", 0.5)
        }
        
        self.memory_store[agent_id][memory_id] = memory_entry
        
        # Check memory limits and cleanup if necessary
        await self._cleanup_memory(agent_id)
        
        return memory_id
    
    async def retrieve_memory(self, agent_id: str, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory"""
        if agent_id in self.memory_store and memory_id in self.memory_store[agent_id]:
            memory = self.memory_store[agent_id][memory_id]
            memory["access_count"] += 1
            return memory["data"]
        return None
    
    async def search_memories(self, agent_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories based on query"""
        if agent_id not in self.memory_store:
            return []
        
        # Simple keyword-based search (in production, use vector search)
        results = []
        for memory_id, memory in self.memory_store[agent_id].items():
            if self._matches_query(memory["data"], query):
                results.append({
                    "id": memory_id,
                    "data": memory["data"],
                    "relevance": self._calculate_relevance(memory["data"], query),
                    "timestamp": memory["timestamp"]
                })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]
    
    async def update_knowledge(self, agent_id: str, knowledge_domain: str, knowledge_data: Dict[str, Any]):
        """Update agent knowledge in a specific domain"""
        if agent_id not in self.knowledge_base:
            self.knowledge_base[agent_id] = {}
            
        if knowledge_domain not in self.knowledge_base[agent_id]:
            self.knowledge_base[agent_id][knowledge_domain] = {}
            
        self.knowledge_base[agent_id][knowledge_domain].update(knowledge_data)
        
        # Store as memory for future reference
        await self.store_memory(agent_id, {
            "type": "knowledge_update",
            "domain": knowledge_domain,
            "data": knowledge_data,
            "importance": 0.8
        })
    
    async def get_knowledge(self, agent_id: str, knowledge_domain: str) -> Dict[str, Any]:
        """Retrieve knowledge for a specific domain"""
        if (agent_id in self.knowledge_base and 
            knowledge_domain in self.knowledge_base[agent_id]):
            return self.knowledge_base[agent_id][knowledge_domain]
        return {}
    
    async def learn_pattern(self, agent_id: str, pattern_type: str, pattern_data: Dict[str, Any]):
        """Learn and store a new pattern"""
        if agent_id not in self.learning_patterns:
            self.learning_patterns[agent_id] = {}
            
        if pattern_type not in self.learning_patterns[agent_id]:
            self.learning_patterns[agent_id][pattern_type] = []
            
        pattern_entry = {
            "data": pattern_data,
            "timestamp": datetime.now(),
            "confidence": pattern_data.get("confidence", 0.5),
            "usage_count": 0
        }
        
        self.learning_patterns[agent_id][pattern_type].append(pattern_entry)
        
        # Store as memory
        await self.store_memory(agent_id, {
            "type": "pattern_learning",
            "pattern_type": pattern_type,
            "data": pattern_data,
            "importance": 0.7
        })
    
    async def get_patterns(self, agent_id: str, pattern_type: str) -> List[Dict[str, Any]]:
        """Retrieve learned patterns of a specific type"""
        if (agent_id in self.learning_patterns and 
            pattern_type in self.learning_patterns[agent_id]):
            return self.learning_patterns[agent_id][pattern_type]
        return []
    
    async def _cleanup_memory(self, agent_id: str):
        """Clean up old or less important memories to stay within limits"""
        if agent_id not in self.memory_store:
            return
            
        memories = self.memory_store[agent_id]
        if len(memories) <= self.memory_limit:
            return
            
        # Sort by importance and access count
        sorted_memories = sorted(
            memories.items(),
            key=lambda x: (x[1]["importance"], x[1]["access_count"]),
            reverse=True
        )
        
        # Keep only the most important memories
        memories_to_keep = sorted_memories[:self.memory_limit]
        self.memory_store[agent_id] = dict(memories_to_keep)
        
        logger.info(f"Cleaned up memory for agent {agent_id}, kept {len(memories_to_keep)} memories")
    
    def _generate_memory_id(self, memory_data: Dict[str, Any]) -> str:
        """Generate a unique memory ID"""
        data_string = json.dumps(memory_data, sort_keys=True, default=str)
        return hashlib.md5(data_string.encode()).hexdigest()[:8]
    
    def _matches_query(self, memory_data: Dict[str, Any], query: str) -> bool:
        """Check if memory matches the search query"""
        query_lower = query.lower()
        data_string = json.dumps(memory_data).lower()
        return query_lower in data_string
    
    def _calculate_relevance(self, memory_data: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for search results"""
        # Simple relevance calculation (in production, use more sophisticated methods)
        query_terms = query.lower().split()
        data_string = json.dumps(memory_data).lower()
        
        matches = sum(1 for term in query_terms if term in data_string)
        return matches / len(query_terms) if query_terms else 0.0
    
    async def get_memory_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get memory statistics for an agent"""
        if agent_id not in self.memory_store:
            return {
                "total_memories": 0,
                "memory_usage": 0,
                "knowledge_domains": 0,
                "pattern_types": 0
            }
            
        memories = self.memory_store[agent_id]
        knowledge_domains = len(self.knowledge_base.get(agent_id, {}))
        pattern_types = len(self.learning_patterns.get(agent_id, {}))
        
        return {
            "total_memories": len(memories),
            "memory_usage": len(memories) / self.memory_limit,
            "knowledge_domains": knowledge_domains,
            "pattern_types": pattern_types
        } 