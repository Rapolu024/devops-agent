"""
DevOps Agentic AI - Main Agent Class
Orchestrates all components for autonomous DevOps operations
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio

from repository_analyzer import RepositoryAnalyzer
from code_understanding import CodeUnderstandingEngine
from decision_engine import DecisionEngine
from action_executor import ActionExecutor
from monitoring_system import MonitoringSystem
from learning_module import LearningModule
from infrastructure_manager import InfrastructureManager

@dataclass
class ProjectContext:
    """Holds all context about the analyzed project"""
    repo_url: str
    project_type: str
    languages: List[str]
    frameworks: List[str]
    dependencies: Dict[str, Any]
    structure: Dict[str, Any]
    deployment_requirements: Dict[str, Any]
    security_requirements: List[str]
    performance_requirements: Dict[str, Any]
    database_usage: List[str]
    api_endpoints: List[Dict[str, Any]]
    environment_variables: List[str]
    build_tools: List[str]

class DevOpsAgent:
    """
    Main DevOps Agent that coordinates all subsystems
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logging()
        
        # Initialize all subsystems
        self.repo_analyzer = RepositoryAnalyzer(self.config)
        self.code_engine = CodeUnderstandingEngine(self.config)
        self.decision_engine = DecisionEngine(self.config)
        self.action_executor = ActionExecutor(self.config)
        self.monitoring_system = MonitoringSystem(self.config)
        self.learning_module = LearningModule(self.config)
        self.infra_manager = InfrastructureManager(self.config)
        
        self.project_context: Optional[ProjectContext] = None
        self.is_running = False
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "logging_level": "INFO",
            "max_analysis_time": 3600,  # 1 hour
            "supported_languages": ["python", "javascript", "java", "go", "rust"],
            "cloud_providers": ["aws", "gcp", "azure"],
            "default_cloud": "aws",
            "monitoring_interval": 60,  # seconds
            "auto_scale": True,
            "auto_heal": True,
            "security_scan": True
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config["logging_level"]),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    async def analyze_repository(self, repo_url: str) -> ProjectContext:
        """
        Analyze a repository and understand its structure and requirements
        """
        self.logger.info(f"Starting analysis of repository: {repo_url}")
        
        try:
            # Step 1: Download and analyze repository structure
            repo_data = await self.repo_analyzer.analyze(repo_url)
            
            # Step 2: Understand code and extract insights
            code_insights = await self.code_engine.analyze_codebase(repo_data)
            
            # Step 3: Create project context
            self.project_context = ProjectContext(
                repo_url=repo_url,
                project_type=code_insights.project_type,
                languages=code_insights.languages,
                frameworks=code_insights.frameworks,
                dependencies=code_insights.dependencies,
                structure=repo_data.structure,
                deployment_requirements=code_insights.deployment_requirements,
                security_requirements=code_insights.security_requirements,
                performance_requirements=code_insights.performance_requirements,
                database_usage=code_insights.database_usage,
                api_endpoints=code_insights.api_endpoints,
                environment_variables=code_insights.environment_variables,
                build_tools=code_insights.build_tools
            )
            
            self.logger.info("Repository analysis completed successfully")
            return self.project_context
            
        except Exception as e:
            self.logger.error(f"Failed to analyze repository: {str(e)}")
            raise
    
    async def setup_infrastructure(self) -> Dict[str, Any]:
        """
        Setup required infrastructure based on project analysis
        """
        if not self.project_context:
            raise ValueError("Must analyze repository first")
        
        self.logger.info("Setting up infrastructure")
        
        # Generate infrastructure plan
        infra_plan = await self.decision_engine.create_infrastructure_plan(
            self.project_context
        )
        
        # Execute infrastructure setup
        infra_result = await self.infra_manager.create_infrastructure(infra_plan)
        
        self.logger.info("Infrastructure setup completed")
        return infra_result
    
    async def deploy(self) -> Dict[str, Any]:
        """
        Deploy the application with CI/CD pipeline
        """
        if not self.project_context:
            raise ValueError("Must analyze repository first")
        
        self.logger.info("Starting deployment process")
        
        # Create deployment plan
        deployment_plan = await self.decision_engine.create_deployment_plan(
            self.project_context
        )
        
        # Execute deployment
        deployment_result = await self.action_executor.execute_deployment(
            deployment_plan
        )
        
        self.logger.info("Deployment completed successfully")
        return deployment_result
    
    async def start_monitoring(self) -> None:
        """
        Start continuous monitoring and autonomous operations
        """
        if not self.project_context:
            raise ValueError("Must deploy application first")
        
        self.logger.info("Starting autonomous monitoring")
        self.is_running = True
        
        # Start monitoring loop
        await self.monitoring_system.start_monitoring(self.project_context)
        
        # Start decision loop
        asyncio.create_task(self._autonomous_decision_loop())
    
    async def _autonomous_decision_loop(self) -> None:
        """
        Main autonomous decision-making loop
        """
        while self.is_running:
            try:
                # Get current system state
                system_state = await self.monitoring_system.get_system_state()
                
                # Make decisions based on current state
                decisions = await self.decision_engine.make_decisions(
                    system_state, self.project_context
                )
                
                # Execute decisions
                for decision in decisions:
                    await self.action_executor.execute_action(decision)
                
                # Learn from outcomes
                await self.learning_module.update_from_actions(
                    decisions, system_state
                )
                
                # Wait before next iteration
                await asyncio.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                self.logger.error(f"Error in decision loop: {str(e)}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def stop(self) -> None:
        """
        Stop all autonomous operations
        """
        self.logger.info("Stopping DevOps Agent")
        self.is_running = False
        await self.monitoring_system.stop()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of all systems
        """
        return {
            "is_running": self.is_running,
            "project_context": self.project_context.__dict__ if self.project_context else None,
            "monitoring_status": self.monitoring_system.get_status(),
            "infrastructure_status": self.infra_manager.get_status(),
            "last_decisions": self.decision_engine.get_recent_decisions()
        }

# Example usage
async def main():
    agent = DevOpsAgent()
    
    # Analyze repository
    context = await agent.analyze_repository("https://github.com/user/repo")
    
    # Setup infrastructure
    infra = await agent.setup_infrastructure()
    
    # Deploy application
    deployment = await agent.deploy()
    
    # Start autonomous monitoring
    await agent.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
