"""
Action Executor - Executes DevOps operations and deployment actions
"""

import os
import json
import yaml
import asyncio
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from decision_engine import Decision, ActionType

@dataclass
class ExecutionResult:
    success: bool
    message: str
    details: Dict[str, Any]
    execution_time: float
    timestamp: datetime

class ActionExecutor:
    """Executes DevOps actions and operations"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.execution_history: List[ExecutionResult] = []
        self.cloud_provider = config.get("default_cloud", "aws")
        
    async def execute_deployment(self, deployment_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute deployment based on deployment plan"""
        self.logger.info("Starting deployment execution")
        
        results = {
            "overall_success": True,
            "stage_results": [],
            "deployment_id": f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "start_time": datetime.now().isoformat()
        }
        
        try:
            for stage in deployment_plan["stages"]:
                stage_result = await self._execute_pipeline_stage(stage)
                results["stage_results"].append(stage_result)
                
                if not stage_result.success:
                    results["overall_success"] = False
                    if stage["name"] != "deploy_production":  # Don't fail on production deploy
                        break
            
            results["end_time"] = datetime.now().isoformat()
            self.logger.info(f"Deployment completed: {results['overall_success']}")
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {str(e)}")
            results["overall_success"] = False
            results["error"] = str(e)
        
        return results
    
    async def execute_action(self, decision: Decision) -> ExecutionResult:
        """Execute a single action based on decision"""
        start_time = datetime.now()
        
        try:
            if decision.action_type == ActionType.SCALE_UP:
                result = await self._execute_scale_up(decision)
            elif decision.action_type == ActionType.SCALE_DOWN:
                result = await self._execute_scale_down(decision)
            elif decision.action_type == ActionType.RESTART_SERVICE:
                result = await self._execute_restart_service(decision)
            elif decision.action_type == ActionType.ROLLBACK:
                result = await self._execute_rollback(decision)
            elif decision.action_type == ActionType.HEAL_SERVICE:
                result = await self._execute_heal_service(decision)
            elif decision.action_type == ActionType.OPTIMIZE_PERFORMANCE:
                result = await self._execute_optimize_performance(decision)
            elif decision.action_type == ActionType.UPDATE_SECURITY:
                result = await self._execute_update_security(decision)
            elif decision.action_type == ActionType.UPDATE_CONFIG:
                result = await self._execute_update_config(decision)
            else:
                result = ExecutionResult(
                    success=False,
                    message=f"Unknown action type: {decision.action_type}",
                    details={},
                    execution_time=0,
                    timestamp=datetime.now()
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.execution_history.append(result)
            self.logger.info(f"Action executed: {decision.action_type.value} - {result.success}")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = ExecutionResult(
                success=False,
                message=f"Action execution failed: {str(e)}",
                details={"error": str(e), "action_type": decision.action_type.value},
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            
            self.execution_history.append(result)
            self.logger.error(f"Action execution failed: {str(e)}")
            return result
    
    async def _execute_pipeline_stage(self, stage: Dict[str, Any]) -> ExecutionResult:
        """Execute a single pipeline stage"""
        start_time = datetime.now()
        stage_name = stage["name"]
        stage_type = stage["type"]
        config = stage["config"]
        
        try:
            if stage_type == "source_control":
                result = await self._execute_source_stage(config)
            elif stage_type == "build":
                result = await self._execute_build_stage(config)
            elif stage_type == "test":
                result = await self._execute_test_stage(config)
            elif stage_type == "security":
                result = await self._execute_security_stage(config)
            elif stage_type == "deploy":
                result = await self._execute_deploy_stage(config)
            else:
                result = ExecutionResult(
                    success=False,
                    message=f"Unknown stage type: {stage_type}",
                    details={},
                    execution_time=0,
                    timestamp=datetime.now()
                )
            
            result.execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Stage {stage_name} completed: {result.success}")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ExecutionResult(
                success=False,
                message=f"Stage {stage_name} failed: {str(e)}",
                details={"error": str(e), "stage": stage_name},
                execution_time=execution_time,
                timestamp=datetime.now()
            )
    
    async def _execute_source_stage(self, config: Dict[str, Any]) -> ExecutionResult:
        """Execute source control stage"""
        # Simulate source code checkout
        await asyncio.sleep(2)  # Simulate time
        
        return ExecutionResult(
            success=True,
            message="Source code checked out successfully",
            details={"branch": config.get("branch", "main"), "trigger": config.get("trigger")},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _execute_build_stage(self, config: Dict[str, Any]) -> ExecutionResult:
        """Execute build stage"""
        runtime = config.get("runtime", "docker")
        
        if runtime == "nodejs":
            return await self._build_nodejs(config)
        elif runtime == "python":
            return await self._build_python(config)
        elif runtime == "java":
            return await self._build_java(config)
        elif runtime == "docker":
            return await self._build_docker(config)
        else:
            return ExecutionResult(
                success=False,
                message=f"Unsupported runtime: {runtime}",
                details={},
                execution_time=0,
                timestamp=datetime.now()
            )
    
    async def _build_nodejs(self, config: Dict[str, Any]) -> ExecutionResult:
        """Build Node.js application"""
        commands = [
            config.get("install_cmd", "npm ci"),
            config.get("build_cmd", "npm run build")
        ]
        
        for cmd in commands:
            success, output = await self._run_command(cmd)
            if not success:
                return ExecutionResult(
                    success=False,
                    message=f"Build failed: {cmd}",
                    details={"command": cmd, "output": output},
                    execution_time=0,
                    timestamp=datetime.now()
                )
        
        return ExecutionResult(
            success=True,
            message="Node.js build completed successfully",
            details={"runtime": "nodejs", "artifact_path": config.get("artifact_path")},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _build_python(self, config: Dict[str, Any]) -> ExecutionResult:
        """Build Python application"""
        commands = [
            config.get("install_cmd", "pip install -r requirements.txt"),
            config.get("build_cmd", "python setup.py build")
        ]
        
        for cmd in commands:
            success, output = await self._run_command(cmd)
            if not success:
                return ExecutionResult(
                    success=False,
                    message=f"Build failed: {cmd}",
                    details={"command": cmd, "output": output},
                    execution_time=0,
                    timestamp=datetime.now()
                )
        
        return ExecutionResult(
            success=True,
            message="Python build completed successfully",
            details={"runtime": "python", "artifact_path": config.get("artifact_path")},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _build_java(self, config: Dict[str, Any]) -> ExecutionResult:
        """Build Java application"""
        build_tool = config.get("build_tool", "maven")
        cmd = config.get("build_cmd", "mvn package" if build_tool == "maven" else "./gradlew build")
        
        success, output = await self._run_command(cmd)
        
        if success:
            return ExecutionResult(
                success=True,
                message="Java build completed successfully",
                details={"runtime": "java", "build_tool": build_tool, "artifact_path": config.get("artifact_path")},
                execution_time=0,
                timestamp=datetime.now()
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"Java build failed: {cmd}",
                details={"command": cmd, "output": output},
                execution_time=0,
                timestamp=datetime.now()
            )
    
    async def _build_docker(self, config: Dict[str, Any]) -> ExecutionResult:
        """Build Docker image"""
        dockerfile = config.get("dockerfile", "Dockerfile")
        image_tag = f"app:{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        cmd = f"docker build -f {dockerfile} -t {image_tag} ."
        
        success, output = await self._run_command(cmd)
        
        if success:
            return ExecutionResult(
                success=True,
                message="Docker build completed successfully",
                details={"runtime": "docker", "image_tag": image_tag},
                execution_time=0,
                timestamp=datetime.now()
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"Docker build failed: {cmd}",
                details={"command": cmd, "output": output},
                execution_time=0,
                timestamp=datetime.now()
            )
    
    async def _execute_test_stage(self, config: Dict[str, Any]) -> ExecutionResult:
        """Execute test stage"""
        test_type = config.get("type", "unit")
        environment = config.get("environment", "test")
        
        # Simulate test execution
        await asyncio.sleep(5)  # Simulate test time
        
        # Simulate test results (90% pass rate)
        import random
        success = random.random() > 0.1
        
        if success:
            return ExecutionResult(
                success=True,
                message=f"{test_type.title()} tests passed",
                details={"test_type": test_type, "environment": environment, "coverage": "85%"},
                execution_time=0,
                timestamp=datetime.now()
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"{test_type.title()} tests failed",
                details={"test_type": test_type, "environment": environment, "failed_tests": 3},
                execution_time=0,
                timestamp=datetime.now()
            )
    
    async def _execute_security_stage(self, config: Dict[str, Any]) -> ExecutionResult:
        """Execute security scanning stage"""
        scans = []
        
        if config.get("sast", False):
            scans.append("SAST")
        if config.get("dependency_check", False):
            scans.append("Dependency Check")
        
        # Simulate security scan
        await asyncio.sleep(3)
        
        # Simulate scan results
        import random
        vulnerabilities = random.randint(0, 2)
        
        if vulnerabilities == 0:
            return ExecutionResult(
                success=True,
                message="Security scans passed - no vulnerabilities found",
                details={"scans": scans, "vulnerabilities": 0},
                execution_time=0,
                timestamp=datetime.now()
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"Security scans found {vulnerabilities} vulnerabilities",
                details={"scans": scans, "vulnerabilities": vulnerabilities},
                execution_time=0,
                timestamp=datetime.now()
            )
    
    async def _execute_deploy_stage(self, config: Dict[str, Any]) -> ExecutionResult:
        """Execute deployment stage"""
        environment = config.get("environment", "staging")
        auto_approve = config.get("auto_approve", False)
        
        if not auto_approve and environment == "production":
            # In real implementation, this would wait for manual approval
            await asyncio.sleep(1)
        
        # Simulate deployment
        await asyncio.sleep(10)  # Simulate deployment time
        
        # Simulate deployment success (95% success rate)
        import random
        success = random.random() > 0.05
        
        if success:
            return ExecutionResult(
                success=True,
                message=f"Deployment to {environment} successful",
                details={"environment": environment, "version": "1.0.0", "instances": 2},
                execution_time=0,
                timestamp=datetime.now()
            )
        else:
            return ExecutionResult(
                success=False,
                message=f"Deployment to {environment} failed",
                details={"environment": environment, "error": "Connection timeout"},
                execution_time=0,
                timestamp=datetime.now()
            )
    
    async def _execute_scale_up(self, decision: Decision) -> ExecutionResult:
        """Execute scale up action"""
        target = decision.target
        parameters = decision.parameters
        
        if self.cloud_provider == "aws":
            return await self._aws_scale_up(target, parameters)
        elif self.cloud_provider == "gcp":
            return await self._gcp_scale_up(target, parameters)
        elif self.cloud_provider == "azure":
            return await self._azure_scale_up(target, parameters)
        else:
            return await self._generic_scale_up(target, parameters)
    
    async def _execute_scale_down(self, decision: Decision) -> ExecutionResult:
        """Execute scale down action"""
        target = decision.target
        parameters = decision.parameters
        
        if self.cloud_provider == "aws":
            return await self._aws_scale_down(target, parameters)
        elif self.cloud_provider == "gcp":
            return await self._gcp_scale_down(target, parameters)
        elif self.cloud_provider == "azure":
            return await self._azure_scale_down(target, parameters)
        else:
            return await self._generic_scale_down(target, parameters)
    
    async def _aws_scale_up(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Scale up AWS resources"""
        metric = parameters.get("metric", "instances")
        increase = parameters.get("increase", "1")
        
        if metric == "instances":
            cmd = f"aws autoscaling set-desired-capacity --auto-scaling-group-name {target} --desired-capacity +{increase}"
        elif metric == "cpu":
            cmd = f"aws ec2 modify-instance-attribute --instance-id {target} --instance-type t3.large"
        else:
            cmd = f"aws autoscaling update-auto-scaling-group --auto-scaling-group-name {target}"
        
        success, output = await self._run_command(cmd)
        
        return ExecutionResult(
            success=success,
            message=f"AWS scale up {'completed' if success else 'failed'}",
            details={"target": target, "metric": metric, "increase": increase, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _aws_scale_down(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Scale down AWS resources"""
        metric = parameters.get("metric", "instances")
        decrease = parameters.get("decrease", "1")
        
        if metric == "instances":
            cmd = f"aws autoscaling set-desired-capacity --auto-scaling-group-name {target} --desired-capacity -{decrease}"
        elif metric == "cpu":
            cmd = f"aws ec2 modify-instance-attribute --instance-id {target} --instance-type t3.small"
        else:
            cmd = f"aws autoscaling update-auto-scaling-group --auto-scaling-group-name {target}"
        
        success, output = await self._run_command(cmd)
        
        return ExecutionResult(
            success=success,
            message=f"AWS scale down {'completed' if success else 'failed'}",
            details={"target": target, "metric": metric, "decrease": decrease, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _generic_scale_up(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Generic scale up (for simulation)"""
        await asyncio.sleep(2)  # Simulate scaling time
        
        return ExecutionResult(
            success=True,
            message=f"Scaled up {target} successfully",
            details={"target": target, "parameters": parameters},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _generic_scale_down(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Generic scale down (for simulation)"""
        await asyncio.sleep(2)  # Simulate scaling time
        
        return ExecutionResult(
            success=True,
            message=f"Scaled down {target} successfully",
            details={"target": target, "parameters": parameters},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _gcp_scale_up(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Scale up GCP resources"""
        metric = parameters.get("metric", "instances")
        increase = parameters.get("increase", "1")
        
        cmd = f"gcloud compute instance-groups managed resize {target} --size +{increase}"
        success, output = await self._run_command(cmd)
        
        return ExecutionResult(
            success=success,
            message=f"GCP scale up {'completed' if success else 'failed'}",
            details={"target": target, "metric": metric, "increase": increase, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _gcp_scale_down(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Scale down GCP resources"""
        metric = parameters.get("metric", "instances")
        decrease = parameters.get("decrease", "1")
        
        cmd = f"gcloud compute instance-groups managed resize {target} --size -{decrease}"
        success, output = await self._run_command(cmd)
        
        return ExecutionResult(
            success=success,
            message=f"GCP scale down {'completed' if success else 'failed'}",
            details={"target": target, "metric": metric, "decrease": decrease, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _azure_scale_up(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Scale up Azure resources"""
        metric = parameters.get("metric", "instances")
        increase = parameters.get("increase", "1")
        
        cmd = f"az vmss scale --name {target} --new-capacity +{increase}"
        success, output = await self._run_command(cmd)
        
        return ExecutionResult(
            success=success,
            message=f"Azure scale up {'completed' if success else 'failed'}",
            details={"target": target, "metric": metric, "increase": increase, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _azure_scale_down(self, target: str, parameters: Dict[str, Any]) -> ExecutionResult:
        """Scale down Azure resources"""
        metric = parameters.get("metric", "instances")
        decrease = parameters.get("decrease", "1")
        
        cmd = f"az vmss scale --name {target} --new-capacity -{decrease}"
        success, output = await self._run_command(cmd)
        
        return ExecutionResult(
            success=success,
            message=f"Azure scale down {'completed' if success else 'failed'}",
            details={"target": target, "metric": metric, "decrease": decrease, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _execute_restart_service(self, decision: Decision) -> ExecutionResult:
        """Execute service restart"""
        target = decision.target
        parameters = decision.parameters
        graceful = parameters.get("graceful", True)
        timeout = parameters.get("timeout", "30s")
        
        if graceful:
            cmd = f"systemctl reload {target}"
        else:
            cmd = f"systemctl restart {target}"
        
        success, output = await self._run_command(cmd)
        
        return ExecutionResult(
            success=success,
            message=f"Service restart {'completed' if success else 'failed'}",
            details={"target": target, "graceful": graceful, "timeout": timeout, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _execute_rollback(self, decision: Decision) -> ExecutionResult:
        """Execute deployment rollback"""
        target = decision.parameters.get("target", "previous_stable")
        
        # Simulate rollback process
        await asyncio.sleep(5)
        
        return ExecutionResult(
            success=True,
            message="Rollback completed successfully",
            details={"target": target, "rollback_version": "v1.2.3"},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _execute_heal_service(self, decision: Decision) -> ExecutionResult:
        """Execute service healing"""
        target = decision.target
        action = decision.parameters.get("action", "restart")
        max_attempts = decision.parameters.get("max_attempts", 3)
        
        for attempt in range(max_attempts):
            if action == "restart":
                success, output = await self._run_command(f"systemctl restart {target}")
                if success:
                    return ExecutionResult(
                        success=True,
                        message=f"Service {target} healed successfully",
                        details={"target": target, "action": action, "attempts": attempt + 1},
                        execution_time=0,
                        timestamp=datetime.now()
                    )
            
            await asyncio.sleep(5)  # Wait between attempts
        
        return ExecutionResult(
            success=False,
            message=f"Failed to heal service {target} after {max_attempts} attempts",
            details={"target": target, "action": action, "attempts": max_attempts},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _execute_optimize_performance(self, decision: Decision) -> ExecutionResult:
        """Execute performance optimization"""
        target = decision.target
        action = decision.parameters.get("action")
        
        if action == "increase_cache_size":
            amount = decision.parameters.get("amount", "50%")
            success, output = await self._run_command(f"redis-cli CONFIG SET maxmemory +{amount}")
        elif action == "cleanup_logs":
            retention = decision.parameters.get("retention", "7d")
            success, output = await self._run_command(f"find /var/log -name '*.log' -mtime +{retention[:-1]} -delete")
        elif action == "identify_unused":
            success, output = await self._run_command("docker system prune -f")
        else:
            success = True
            output = "Performance optimization completed"
        
        return ExecutionResult(
            success=success,
            message=f"Performance optimization {'completed' if success else 'failed'}",
            details={"target": target, "action": action, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _execute_update_security(self, decision: Decision) -> ExecutionResult:
        """Execute security updates"""
        target = decision.target
        action = decision.parameters.get("action")
        
        if action == "block_suspicious_ips":
            alert_id = decision.parameters.get("alert_id")
            success, output = await self._run_command("iptables -A INPUT -s suspicious_ip -j DROP")
        elif action == "renew_certificates":
            success, output = await self._run_command("certbot renew --quiet")
        else:
            success = True
            output = "Security update completed"
        
        return ExecutionResult(
            success=success,
            message=f"Security update {'completed' if success else 'failed'}",
            details={"target": target, "action": action, "output": output},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _execute_update_config(self, decision: Decision) -> ExecutionResult:
        """Execute configuration updates"""
        target = decision.target
        config_changes = decision.parameters.get("changes", {})
        
        # Simulate configuration update
        await asyncio.sleep(2)
        
        return ExecutionResult(
            success=True,
            message=f"Configuration updated for {target}",
            details={"target": target, "changes": config_changes},
            execution_time=0,
            timestamp=datetime.now()
        )
    
    async def _run_command(self, command: str) -> tuple[bool, str]:
        """Run shell command and return success status and output"""
        try:
            # For demo purposes, simulate command execution
            await asyncio.sleep(1)  # Simulate execution time
            
            # Simulate success/failure (90% success rate)
            import random
            success = random.random() > 0.1
            
            if success:
                output = f"Command executed successfully: {command}"
            else:
                output = f"Command failed: {command}"
            
            return success, output
            
        except Exception as e:
            return False, str(e)
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history for reporting"""
        return [
            {
                "success": result.success,
                "message": result.message,
                "execution_time": result.execution_time,
                "timestamp": result.timestamp.isoformat()
            }
            for result in self.execution_history[-10:]  # Last 10 executions
        ]
