"""
Main entry point for running the DevOps Agentic AI System
"""

import asyncio
import logging
from devops_agent import DevOpsAgent

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    agent = DevOpsAgent("config.json")
    
    # Analyze the repository
    context = await agent.analyze_repository("https://github.com/user/repo")
    
    # Setup infrastructure
    infra_result = await agent.setup_infrastructure()
    
    # Deploy the application
    deployment_result = await agent.deploy()
    
    # Start monitoring
    await agent.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
