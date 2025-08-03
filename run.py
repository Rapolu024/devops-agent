#!/usr/bin/env python3
"""
DevOps Agentic AI - Main Execution Script
Run this to start the complete autonomous DevOps system
"""

import asyncio
import sys
import os
import logging
import signal
import json
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from devops_agent import DevOpsAgent

class DevOpsAgentRunner:
    """Main runner for the DevOps Agentic AI system"""
    
    def __init__(self):
        self.agent = None
        self.running = False
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        self.running = False
        if self.agent:
            asyncio.create_task(self.agent.stop())
    
    async def run_interactive_mode(self):
        """Run in interactive mode - prompt user for repository URL"""
        print("=" * 60)
        print("DevOps Agentic AI System - Interactive Mode")
        print("=" * 60)
        print()
        
        # Get repository URL from user
        while True:
            repo_url = input("Enter repository URL (or 'demo' for demo mode): ").strip()
            if repo_url:
                break
            print("Please enter a valid repository URL.")
        
        if repo_url.lower() == 'demo':
            repo_url = "https://github.com/example/demo-app"
            print(f"Using demo repository: {repo_url}")
        
        print(f"\nStarting analysis of repository: {repo_url}")
        print("This may take a few minutes...")
        
        try:
            # Initialize agent
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            self.agent = DevOpsAgent(config_path)
            self.running = True
            
            print("\n1. Analyzing repository...")
            context = await self.agent.analyze_repository(repo_url)
            
            print("✓ Repository analysis completed!")
            print(f"  - Project type: {context.project_type}")
            print(f"  - Languages: {', '.join(context.languages)}")
            print(f"  - Frameworks: {', '.join(context.frameworks)}")
            
            print("\n2. Setting up infrastructure...")
            infra_result = await self.agent.setup_infrastructure()
            
            if infra_result['success']:
                print("✓ Infrastructure setup completed!")
                print(f"  - Resources created: {len(infra_result['created_resources'])}")
                print(f"  - Estimated monthly cost: ${infra_result['total_cost_estimate']:.2f}")
            else:
                print("✗ Infrastructure setup failed!")
                return
            
            print("\n3. Deploying application...")
            deployment_result = await self.agent.deploy()
            
            if deployment_result['overall_success']:
                print("✓ Deployment completed successfully!")
                print(f"  - Deployment ID: {deployment_result['deployment_id']}")
            else:
                print("✗ Deployment failed!")
                return
            
            print("\n4. Starting autonomous monitoring...")
            await self.agent.start_monitoring()
            print("✓ Monitoring system active!")
            
            print("\n" + "=" * 60)
            print("System is now running autonomously!")
            print("=" * 60)
            print("\nMonitoring and managing your application...")
            print("Press Ctrl+C to stop the agent gracefully.")
            print()
            
            # Keep running and show periodic status
            iteration = 0
            while self.running:
                await asyncio.sleep(30)  # Wait 30 seconds between status updates
                
                iteration += 1
                if iteration % 2 == 0:  # Show status every minute
                    status = self.agent.get_status()
                    monitoring_status = status['monitoring_status']
                    
                    print(f"Status Update - Active alerts: {monitoring_status['active_alerts']}, "
                          f"Metrics collected: {monitoring_status['metrics_collected']}")
                
        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Shutting down...")
        except Exception as e:
            print(f"\nError: {str(e)}")
            logging.error(f"Error in interactive mode: {str(e)}")
        finally:
            if self.agent:
                await self.agent.stop()
                print("DevOps Agent stopped.")
    
    async def run_batch_mode(self, repo_url: str):
        """Run in batch mode with provided repository URL"""
        print("=" * 60)
        print("DevOps Agentic AI System - Batch Mode")
        print("=" * 60)
        print(f"Repository: {repo_url}")
        print()
        
        try:
            # Initialize agent
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            self.agent = DevOpsAgent(config_path)
            
            # Run the full pipeline
            print("Analyzing repository...")
            context = await self.agent.analyze_repository(repo_url)
            print(f"✓ Project type: {context.project_type}")
            
            print("Setting up infrastructure...")
            infra_result = await self.agent.setup_infrastructure()
            print(f"✓ Infrastructure cost: ${infra_result['total_cost_estimate']:.2f}/month")
            
            print("Deploying application...")
            deployment_result = await self.agent.deploy()
            print(f"✓ Deployment: {deployment_result['deployment_id']}")
            
            print("Starting monitoring (running for 5 minutes)...")
            await self.agent.start_monitoring()
            
            # Run for 5 minutes in batch mode
            await asyncio.sleep(300)
            
            print("Batch run completed. Stopping agent...")
            await self.agent.stop()
            
            # Show final status
            status = self.agent.get_status()
            print("\nFinal Status:")
            print(json.dumps(status, indent=2, default=str))
            
        except Exception as e:
            print(f"Error in batch mode: {str(e)}")
            logging.error(f"Error in batch mode: {str(e)}")
    
    async def run_status_check(self):
        """Run a quick status check without full deployment"""
        print("=" * 60)
        print("DevOps Agentic AI System - Status Check")
        print("=" * 60)
        
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            self.agent = DevOpsAgent(config_path)
            
            # Check system configuration
            print("Configuration Status:")
            print(f"  - Default cloud: {self.agent.config['default_cloud']}")
            print(f"  - Monitoring interval: {self.agent.config['monitoring_interval']}s")
            print(f"  - Auto-scaling: {self.agent.config['auto_scale']}")
            print(f"  - Auto-healing: {self.agent.config['auto_heal']}")
            
            print("\nSystem Components:")
            print("  ✓ Repository Analyzer")
            print("  ✓ Code Understanding Engine")
            print("  ✓ Decision Engine")
            print("  ✓ Action Executor")
            print("  ✓ Monitoring System")
            print("  ✓ Learning Module")
            print("  ✓ Infrastructure Manager")
            
            print("\nSystem ready for deployment!")
            
        except Exception as e:
            print(f"Status check failed: {str(e)}")
            logging.error(f"Status check failed: {str(e)}")

def print_usage():
    """Print usage information"""
    print("DevOps Agentic AI System")
    print("Usage:")
    print("  python run.py                          # Interactive mode")
    print("  python run.py <repository_url>         # Batch mode")
    print("  python run.py --status                 # Status check")
    print("  python run.py --help                   # Show this help")
    print()
    print("Examples:")
    print("  python run.py")
    print("  python run.py https://github.com/user/repo")
    print("  python run.py --status")

async def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('devops_agent.log'),
            logging.StreamHandler()
        ]
    )
    
    runner = DevOpsAgentRunner()
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # Interactive mode
        await runner.run_interactive_mode()
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if arg in ['--help', '-h']:
            print_usage()
        elif arg == '--status':
            await runner.run_status_check()
        elif arg.startswith('http'):
            # Batch mode with repository URL
            await runner.run_batch_mode(arg)
        else:
            print("Invalid argument. Use --help for usage information.")
    else:
        print("Too many arguments. Use --help for usage information.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)
