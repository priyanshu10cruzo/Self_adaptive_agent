import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import inspect

logger = logging.getLogger(__name__)

class Tool:
    """Represents a tool that an agent can use"""
    
    def __init__(self, name: str, description: str, function: Callable, 
                 parameters: Dict[str, Any], category: str):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
        self.category = category
        self.created_at = datetime.now()
        self.usage_count = 0
        self.success_rate = 1.0
        self.last_used = None
        
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        try:
            self.usage_count += 1
            self.last_used = datetime.now()
            
            # Validate parameters
            validated_params = self._validate_parameters(kwargs)
            
            # Execute the function
            if asyncio.iscoroutinefunction(self.function):
                result = await self.function(**validated_params)
            else:
                result = self.function(**validated_params)
                
            # Update success rate
            self.success_rate = (self.success_rate * (self.usage_count - 1) + 1.0) / self.usage_count
            
            return result
            
        except Exception as e:
            # Update success rate on failure
            self.success_rate = (self.success_rate * (self.usage_count - 1) + 0.0) / self.usage_count
            logger.error(f"Tool {self.name} execution failed: {str(e)}")
            raise
    
    def _validate_parameters(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare parameters for tool execution"""
        validated = {}
        
        for param_name, param_info in self.parameters.items():
            if param_name in kwargs:
                value = kwargs[param_name]
                
                # Type validation
                expected_type = param_info.get("type", str)
                if not isinstance(value, expected_type):
                    try:
                        if expected_type == int:
                            value = int(value)
                        elif expected_type == float:
                            value = float(value)
                        elif expected_type == bool:
                            value = bool(value)
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid type for parameter {param_name}")
                
                # Range validation
                if "min" in param_info and value < param_info["min"]:
                    raise ValueError(f"Parameter {param_name} must be >= {param_info['min']}")
                if "max" in param_info and value > param_info["max"]:
                    raise ValueError(f"Parameter {param_name} must be <= {param_info['max']}")
                
                # Enum validation
                if "enum" in param_info and value not in param_info["enum"]:
                    raise ValueError(f"Parameter {param_name} must be one of {param_info['enum']}")
                
                validated[param_name] = value
            elif param_info.get("required", False):
                raise ValueError(f"Required parameter {param_name} is missing")
            else:
                validated[param_name] = param_info.get("default")
        
        return validated

class ToolManager:
    """Manages tools available to agents"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.tool_categories = {}
        self.agent_tools: Dict[str, List[str]] = {}  # agent_id -> list of tool names
        
    async def initialize(self):
        """Initialize the tool manager with default tools"""
        logger.info("Initializing tool manager...")
        
        # Register default tools
        await self._register_default_tools()
        logger.info("Tool manager initialized")
    
    async def register_tool(self, tool: Tool, agent_id: Optional[str] = None):
        """Register a new tool"""
        if tool.name in self.tools:
            logger.warning(f"Tool {tool.name} already exists, updating...")
        
        self.tools[tool.name] = tool
        
        # Add to category
        if tool.category not in self.tool_categories:
            self.tool_categories[tool.category] = []
        self.tool_categories[tool.category].append(tool.name)
        
        # Assign to agent if specified
        if agent_id:
            if agent_id not in self.agent_tools:
                self.agent_tools[agent_id] = []
            if tool.name not in self.agent_tools[agent_id]:
                self.agent_tools[agent_id].append(tool.name)
        
        logger.info(f"Tool {tool.name} registered successfully")
    
    async def unregister_tool(self, tool_name: str):
        """Unregister a tool"""
        if tool_name in self.tools:
            tool = self.tools[tool_name]
            
            # Remove from category
            if tool.category in self.tool_categories:
                if tool_name in self.tool_categories[tool.category]:
                    self.tool_categories[tool.category].remove(tool_name)
            
            # Remove from agent assignments
            for agent_id, tools in self.agent_tools.items():
                if tool_name in tools:
                    tools.remove(tool_name)
            
            # Remove the tool
            del self.tools[tool_name]
            logger.info(f"Tool {tool_name} unregistered successfully")
    
    async def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    async def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a specific category"""
        if category not in self.tool_categories:
            return []
        
        return [self.tools[name] for name in self.tool_categories[category] 
                if name in self.tools]
    
    async def get_agent_tools(self, agent_id: str) -> List[Tool]:
        """Get all tools available to a specific agent"""
        if agent_id not in self.agent_tools:
            return []
        
        return [self.tools[name] for name in self.agent_tools[agent_id] 
                if name in self.tools]
    
    async def assign_tool_to_agent(self, tool_name: str, agent_id: str):
        """Assign a tool to an agent"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} does not exist")
        
        if agent_id not in self.agent_tools:
            self.agent_tools[agent_id] = []
        
        if tool_name not in self.agent_tools[agent_id]:
            self.agent_tools[agent_id].append(tool_name)
            logger.info(f"Tool {tool_name} assigned to agent {agent_id}")
    
    async def remove_tool_from_agent(self, tool_name: str, agent_id: str):
        """Remove a tool from an agent"""
        if agent_id in self.agent_tools and tool_name in self.agent_tools[agent_id]:
            self.agent_tools[agent_id].remove(tool_name)
            logger.info(f"Tool {tool_name} removed from agent {agent_id}")
    
    async def execute_tool(self, tool_name: str, agent_id: str, **kwargs) -> Any:
        """Execute a tool for a specific agent"""
        # Check if agent has access to the tool
        if agent_id not in self.agent_tools or tool_name not in self.agent_tools[agent_id]:
            raise PermissionError(f"Agent {agent_id} does not have access to tool {tool_name}")
        
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        return await tool.execute(**kwargs)
    
    async def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """Get statistics for a specific tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return {}
        
        return {
            "name": tool.name,
            "category": tool.category,
            "usage_count": tool.usage_count,
            "success_rate": tool.success_rate,
            "last_used": tool.last_used.isoformat() if tool.last_used else None,
            "created_at": tool.created_at.isoformat()
        }
    
    async def get_agent_tool_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get tool usage statistics for a specific agent"""
        if agent_id not in self.agent_tools:
            return {"total_tools": 0, "tool_usage": {}}
        
        tool_stats = {}
        total_usage = 0
        
        for tool_name in self.agent_tools[agent_id]:
            tool = self.tools.get(tool_name)
            if tool:
                stats = await self.get_tool_stats(tool_name)
                tool_stats[tool_name] = stats
                total_usage += stats["usage_count"]
        
        return {
            "total_tools": len(self.agent_tools[agent_id]),
            "total_usage": total_usage,
            "tool_usage": tool_stats
        }
    
    async def _register_default_tools(self):
        """Register default tools available to all agents"""
        
        # Data Analysis Tools
        data_analysis_tool = Tool(
            name="analyze_data",
            description="Analyze data and generate insights",
            function=self._analyze_data,
            parameters={
                "data": {"type": list, "required": True, "description": "Data to analyze"},
                "analysis_type": {"type": str, "required": True, "enum": ["summary", "trends", "anomalies"]},
                "output_format": {"type": str, "default": "json", "enum": ["json", "csv", "table"]}
            },
            category="data_analysis"
        )
        await self.register_tool(data_analysis_tool)
        
        # Report Generation Tools
        report_tool = Tool(
            name="generate_report",
            description="Generate business reports",
            function=self._generate_report,
            parameters={
                "report_type": {"type": str, "required": True, "enum": ["performance", "financial", "operational"]},
                "data_source": {"type": str, "required": True, "description": "Data source for report"},
                "format": {"type": str, "default": "pdf", "enum": ["pdf", "html", "excel"]}
            },
            category="report_generation"
        )
        await self.register_tool(report_tool)
        
        # Task Automation Tools
        automation_tool = Tool(
            name="automate_task",
            description="Automate repetitive tasks",
            function=self._automate_task,
            parameters={
                "task_type": {"type": str, "required": True, "enum": ["data_processing", "email", "file_management"]},
                "parameters": {"type": dict, "required": True, "description": "Task parameters"},
                "schedule": {"type": str, "default": "immediate", "enum": ["immediate", "daily", "weekly"]}
            },
            category="task_automation"
        )
        await self.register_tool(automation_tool)
    
    async def _analyze_data(self, data: list, analysis_type: str, output_format: str = "json") -> Dict[str, Any]:
        """Default data analysis tool implementation"""
        # This is a placeholder implementation
        return {
            "analysis_type": analysis_type,
            "data_points": len(data),
            "insights": f"Generated {analysis_type} analysis for {len(data)} data points",
            "output_format": output_format,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_report(self, report_type: str, data_source: str, format: str = "pdf") -> Dict[str, Any]:
        """Default report generation tool implementation"""
        return {
            "report_type": report_type,
            "data_source": data_source,
            "format": format,
            "status": "generated",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _automate_task(self, task_type: str, parameters: dict, schedule: str = "immediate") -> Dict[str, Any]:
        """Default task automation tool implementation"""
        return {
            "task_type": task_type,
            "parameters": parameters,
            "schedule": schedule,
            "status": "automated",
            "timestamp": datetime.now().isoformat()
        } 