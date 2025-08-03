"""
Decision Engine - Makes autonomous decisions based on system state and context
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

# from .devops_agent import ProjectContext
# Import will be resolved at runtime

class ActionType(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RESTART_SERVICE = "restart_service"
    DEPLOY_UPDATE = "deploy_update"
    ROLLBACK = "rollback"
    UPDATE_CONFIG = "update_config"
    CREATE_ALERT = "create_alert"
    HEAL_SERVICE = "heal_service"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    UPDATE_SECURITY = "update_security"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Decision:
    action_type: ActionType
    priority: Priority
    target: str
    parameters: Dict[str, Any]
    reasoning: str
    timestamp: datetime
    expected_outcome: str
    rollback_plan: Optional[Dict[str, Any]] = None

@dataclass
class SystemState:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_usage: float
    response_time: float
    error_rate: float
    request_count: int
    service_health: Dict[str, bool]
    alerts: List[Dict[str, Any]]
    deployment_status: str
    last_deployment: Optional[datetime]

class DecisionEngine:
    """Makes autonomous decisions based on system state and project context"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.decision_history: List[Decision] = []
        self.rules = self._load_decision_rules()
        self.thresholds = self._load_thresholds()
    
    async def create_infrastructure_plan(self, context: 'ProjectContext') -> Dict[str, Any]:
        """Create infrastructure plan based on project analysis"""
        self.logger.info("Creating infrastructure plan")
        
        plan = {
            "cloud_provider": self.config.get("default_cloud", "aws"),
            "services": [],
            "networking": {},
            "security": {},
            "monitoring": {},
            "scaling": {}
        }
        
        # Determine compute requirements
        compute_req = self._analyze_compute_requirements(context)
        plan["compute"] = compute_req
        
        # Database requirements
        if context.database_usage:
            plan["databases"] = self._plan_database_infrastructure(context.database_usage)
        
        # Load balancing and networking
        if context.performance_requirements.get("estimated_scale") in ["medium", "large"]:
            plan["networking"] = {
                "load_balancer": True,
                "cdn": True,
                "vpc": True
            }
        
        # Security infrastructure
        plan["security"] = self._plan_security_infrastructure(context)
        
        # Monitoring and observability
        plan["monitoring"] = {
            "metrics": True,
            "logs": True,
            "tracing": context.performance_requirements.get("estimated_scale") != "small",
            "alerting": True
        }
        
        # Auto-scaling configuration
        plan["scaling"] = self._plan_scaling_configuration(context)
        
        return plan
    
    async def create_deployment_plan(self, context: 'ProjectContext') -> Dict[str, Any]:
        """Create deployment plan based on project analysis"""
        self.logger.info("Creating deployment plan")
        
        plan = {
            "strategy": "rolling",
            "stages": [],
            "testing": {},
            "rollback": {},
            "notifications": {}
        }
        
        # Determine deployment strategy
        if context.deployment_requirements.get("scaling_requirements") == "high":
            plan["strategy"] = "blue_green"
        elif context.performance_requirements.get("estimated_scale") == "large":
            plan["strategy"] = "canary"
        
        # Build pipeline stages
        stages = self._create_pipeline_stages(context)
        plan["stages"] = stages
        
        # Testing configuration
        plan["testing"] = {
            "unit_tests": True,
            "integration_tests": True,
            "performance_tests": context.performance_requirements.get("estimated_scale") != "small",
            "security_tests": len(context.security_requirements) > 0
        }
        
        # Rollback strategy
        plan["rollback"] = {
            "automatic": True,
            "conditions": ["error_rate > 5%", "response_time > 2s"],
            "max_rollback_time": "5m"
        }
        
        return plan
    
    async def make_decisions(self, system_state: SystemState, context: 'ProjectContext') -> List[Decision]:
        """Make decisions based on current system state"""
        decisions = []
        
        # Performance-based decisions
        perf_decisions = await self._analyze_performance_decisions(system_state, context)
        decisions.extend(perf_decisions)
        
        # Health-based decisions
        health_decisions = await self._analyze_health_decisions(system_state, context)
        decisions.extend(health_decisions)
        
        # Security-based decisions
        security_decisions = await self._analyze_security_decisions(system_state, context)
        decisions.extend(security_decisions)
        
        # Cost optimization decisions
        cost_decisions = await self._analyze_cost_decisions(system_state, context)
        decisions.extend(cost_decisions)
        
        # Sort by priority and limit concurrent actions
        decisions.sort(key=lambda d: d.priority.value, reverse=True)
        
        # Add to history
        self.decision_history.extend(decisions)
        
        # Keep only recent history
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.decision_history = [d for d in self.decision_history if d.timestamp > cutoff_time]
        
        return decisions[:5]  # Limit to 5 concurrent decisions
    
    async def _analyze_performance_decisions(self, state: SystemState, context: 'ProjectContext') -> List[Decision]:
        """Analyze performance metrics and make scaling decisions"""
        decisions = []
        
        # CPU-based scaling
        if state.cpu_usage > self.thresholds["cpu_scale_up"]:
            decisions.append(Decision(
                action_type=ActionType.SCALE_UP,
                priority=Priority.HIGH,
                target="compute",
                parameters={"metric": "cpu", "increase": "25%"},
                reasoning=f"CPU usage at {state.cpu_usage}% exceeds threshold",
                timestamp=datetime.now(),
                expected_outcome="Reduced CPU load and improved response times"
            ))
        elif state.cpu_usage < self.thresholds["cpu_scale_down"]:
            decisions.append(Decision(
                action_type=ActionType.SCALE_DOWN,
                priority=Priority.LOW,
                target="compute",
                parameters={"metric": "cpu", "decrease": "20%"},
                reasoning=f"CPU usage at {state.cpu_usage}% is below threshold",
                timestamp=datetime.now(),
                expected_outcome="Cost optimization while maintaining performance"
            ))
        
        # Memory-based scaling
        if state.memory_usage > self.thresholds["memory_scale_up"]:
            decisions.append(Decision(
                action_type=ActionType.SCALE_UP,
                priority=Priority.HIGH,
                target="memory",
                parameters={"metric": "memory", "increase": "30%"},
                reasoning=f"Memory usage at {state.memory_usage}% exceeds threshold",
                timestamp=datetime.now(),
                expected_outcome="Prevented out-of-memory errors"
            ))
        
        # Response time optimization
        if state.response_time > self.thresholds["response_time"]:
            if context.performance_requirements.get("caching"):
                decisions.append(Decision(
                    action_type=ActionType.OPTIMIZE_PERFORMANCE,
                    priority=Priority.MEDIUM,
                    target="cache",
                    parameters={"action": "increase_cache_size", "amount": "50%"},
                    reasoning=f"Response time {state.response_time}s exceeds threshold",
                    timestamp=datetime.now(),
                    expected_outcome="Improved response times through better caching"
                ))
            else:
                decisions.append(Decision(
                    action_type=ActionType.SCALE_UP,
                    priority=Priority.MEDIUM,
                    target="compute",
                    parameters={"metric": "instances", "increase": "1"},
                    reasoning=f"Response time {state.response_time}s exceeds threshold",
                    timestamp=datetime.now(),
                    expected_outcome="Improved response times through horizontal scaling"
                ))
        
        return decisions
    
    async def _analyze_health_decisions(self, state: SystemState, context: 'ProjectContext') -> List[Decision]:
        """Analyze service health and make healing decisions"""
        decisions = []
        
        # Service health checks
        for service, is_healthy in state.service_health.items():
            if not is_healthy:
                decisions.append(Decision(
                    action_type=ActionType.HEAL_SERVICE,
                    priority=Priority.CRITICAL,
                    target=service,
                    parameters={"action": "restart", "max_attempts": 3},
                    reasoning=f"Service {service} is unhealthy",
                    timestamp=datetime.now(),
                    expected_outcome="Service restoration",
                    rollback_plan={"action": "manual_intervention_required"}
                ))
        
        # Error rate analysis
        if state.error_rate > self.thresholds["error_rate"]:
            # Check if recent deployment might be causing issues
            if (state.last_deployment and 
                datetime.now() - state.last_deployment < timedelta(hours=1)):
                decisions.append(Decision(
                    action_type=ActionType.ROLLBACK,
                    priority=Priority.CRITICAL,
                    target="deployment",
                    parameters={"target": "previous_stable"},
                    reasoning=f"Error rate {state.error_rate}% after recent deployment",
                    timestamp=datetime.now(),
                    expected_outcome="Restored system stability"
                ))
            else:
                decisions.append(Decision(
                    action_type=ActionType.RESTART_SERVICE,
                    priority=Priority.HIGH,
                    target="application",
                    parameters={"graceful": True, "timeout": "30s"},
                    reasoning=f"High error rate {state.error_rate}% detected",
                    timestamp=datetime.now(),
                    expected_outcome="Cleared potential memory leaks or deadlocks"
                ))
        
        # Disk usage monitoring
        if state.disk_usage > self.thresholds["disk_usage"]:
            decisions.append(Decision(
                action_type=ActionType.OPTIMIZE_PERFORMANCE,
                priority=Priority.MEDIUM,
                target="storage",
                parameters={"action": "cleanup_logs", "retention": "7d"},
                reasoning=f"Disk usage at {state.disk_usage}% is critical",
                timestamp=datetime.now(),
                expected_outcome="Free disk space and prevent service interruption"
            ))
        
        return decisions
    
    async def _analyze_security_decisions(self, state: SystemState, context: 'ProjectContext') -> List[Decision]:
        """Analyze security requirements and make security decisions"""
        decisions = []
        
        # Check for security alerts
        security_alerts = [alert for alert in state.alerts if alert.get("type") == "security"]
        
        for alert in security_alerts:
            severity = alert.get("severity", "medium")
            if severity == "high":
                decisions.append(Decision(
                    action_type=ActionType.UPDATE_SECURITY,
                    priority=Priority.CRITICAL,
                    target="firewall",
                    parameters={"action": "block_suspicious_ips", "alert_id": alert["id"]},
                    reasoning=f"High severity security alert: {alert.get('message')}",
                    timestamp=datetime.now(),
                    expected_outcome="Mitigated security threat"
                ))
        
        # SSL certificate expiration
        for alert in state.alerts:
            if "ssl" in alert.get("message", "").lower() and "expir" in alert.get("message", "").lower():
                decisions.append(Decision(
                    action_type=ActionType.UPDATE_SECURITY,
                    priority=Priority.HIGH,
                    target="certificates",
                    parameters={"action": "renew_certificates"},
                    reasoning="SSL certificate expiring soon",
                    timestamp=datetime.now(),
                    expected_outcome="Maintained secure connections"
                ))
        
        return decisions
    
    async def _analyze_cost_decisions(self, state: SystemState, context: 'ProjectContext') -> List[Decision]:
        """Analyze cost optimization opportunities"""
        decisions = []
        
        # Off-hours scaling for non-production environments
        current_hour = datetime.now().hour
        if (current_hour < 8 or current_hour > 18) and context.project_type != "production":
            if state.cpu_usage < 20 and state.memory_usage < 30:
                decisions.append(Decision(
                    action_type=ActionType.SCALE_DOWN,
                    priority=Priority.LOW,
                    target="compute",
                    parameters={"schedule": "off_hours", "reduction": "50%"},
                    reasoning="Low usage during off-hours detected",
                    timestamp=datetime.now(),
                    expected_outcome="Reduced infrastructure costs"
                ))
        
        # Unused resources cleanup
        if state.cpu_usage < 5 and state.memory_usage < 10:
            decisions.append(Decision(
                action_type=ActionType.OPTIMIZE_PERFORMANCE,
                priority=Priority.LOW,
                target="resources",
                parameters={"action": "identify_unused", "threshold": "1h"},
                reasoning="Very low resource utilization detected",
                timestamp=datetime.now(),
                expected_outcome="Cost savings through resource optimization"
            ))
        
        return decisions
    
    def _analyze_compute_requirements(self, context: 'ProjectContext') -> Dict[str, Any]:
        """Analyze compute requirements based on project context"""
        base_requirements = {
            "cpu": 1,
            "memory": "1GB",
            "storage": "10GB",
            "instances": 1
        }
        
        # Scale based on project type and complexity
        if context.project_type in ["web_backend", "backend"]:
            base_requirements["cpu"] = 2
            base_requirements["memory"] = "2GB"
        
        # Scale based on expected load
        scale = context.performance_requirements.get("estimated_scale", "small")
        if scale == "medium":
            base_requirements["cpu"] *= 2
            base_requirements["memory"] = f"{int(base_requirements['memory'][:-2]) * 2}GB"
            base_requirements["instances"] = 2
        elif scale == "large":
            base_requirements["cpu"] *= 4
            base_requirements["memory"] = f"{int(base_requirements['memory'][:-2]) * 4}GB"
            base_requirements["instances"] = 3
        
        # Adjust for specific requirements
        if context.performance_requirements.get("caching"):
            base_requirements["memory"] = f"{int(base_requirements['memory'][:-2]) * 1.5}GB"
        
        return base_requirements
    
    def _plan_database_infrastructure(self, databases: List[str]) -> Dict[str, Any]:
        """Plan database infrastructure"""
        db_plan = {}
        
        for db in databases:
            if db == "postgresql":
                db_plan["postgresql"] = {
                    "instance_type": "db.t3.micro",
                    "storage": "20GB",
                    "backup_retention": "7d",
                    "multi_az": False
                }
            elif db == "redis":
                db_plan["redis"] = {
                    "instance_type": "cache.t3.micro",
                    "memory": "1GB",
                    "backup": True
                }
            elif db == "mongodb":
                db_plan["mongodb"] = {
                    "instance_type": "t3.small",
                    "storage": "20GB",
                    "replica_set": False
                }
        
        return db_plan
    
    def _plan_security_infrastructure(self, context: 'ProjectContext') -> Dict[str, Any]:
        """Plan security infrastructure"""
        security_plan = {
            "firewall": True,
            "waf": False,
            "ssl_certificates": True,
            "secret_management": False,
            "vulnerability_scanning": False
        }
        
        if "authentication" in context.security_requirements:
            security_plan["identity_management"] = True
        
        if "tls_encryption" in context.security_requirements:
            security_plan["ssl_certificates"] = True
            security_plan["force_https"] = True
        
        if "secret_management" in context.security_requirements:
            security_plan["secret_management"] = True
        
        if context.performance_requirements.get("estimated_scale") != "small":
            security_plan["waf"] = True
            security_plan["vulnerability_scanning"] = True
        
        return security_plan
    
    def _plan_scaling_configuration(self, context: 'ProjectContext') -> Dict[str, Any]:
        """Plan auto-scaling configuration"""
        scaling_config = {
            "enabled": True,
            "min_instances": 1,
            "max_instances": 3,
            "target_cpu": 70,
            "target_memory": 80,
            "scale_up_threshold": 2,
            "scale_down_threshold": 5
        }
        
        scale = context.performance_requirements.get("estimated_scale", "small")
        if scale == "medium":
            scaling_config["max_instances"] = 5
        elif scale == "large":
            scaling_config["max_instances"] = 10
            scaling_config["min_instances"] = 2
        
        return scaling_config
    
    def _create_pipeline_stages(self, context: 'ProjectContext') -> List[Dict[str, Any]]:
        """Create CI/CD pipeline stages"""
        stages = [
            {
                "name": "source",
                "type": "source_control",
                "config": {"trigger": "push", "branch": "main"}
            },
            {
                "name": "build",
                "type": "build",
                "config": self._get_build_config(context)
            },
            {
                "name": "test",
                "type": "test",
                "config": {"parallel": True, "coverage_threshold": 80}
            }
        ]
        
        # Add security scanning if required
        if context.security_requirements:
            stages.append({
                "name": "security_scan",
                "type": "security",
                "config": {"sast": True, "dependency_check": True}
            })
        
        # Add deployment stages
        stages.extend([
            {
                "name": "deploy_staging",
                "type": "deploy",
                "config": {"environment": "staging", "auto_approve": True}
            },
            {
                "name": "integration_tests",
                "type": "test",
                "config": {"environment": "staging", "type": "integration"}
            },
            {
                "name": "deploy_production",
                "type": "deploy",
                "config": {"environment": "production", "auto_approve": False}
            }
        ])
        
        return stages
    
    def _get_build_config(self, context: 'ProjectContext') -> Dict[str, Any]:
        """Get build configuration based on project type"""
        if context.project_type == "nodejs" or "npm" in context.build_tools:
            return {
                "runtime": "nodejs",
                "version": "18",
                "install_cmd": "npm ci",
                "build_cmd": "npm run build",
                "artifact_path": "dist/"
            }
        elif context.project_type == "python":
            return {
                "runtime": "python",
                "version": "3.9",
                "install_cmd": "pip install -r requirements.txt",
                "build_cmd": "python setup.py build",
                "artifact_path": "build/"
            }
        elif context.project_type == "java":
            return {
                "runtime": "java",
                "version": "11",
                "build_tool": "maven" if "maven" in context.build_tools else "gradle",
                "build_cmd": "mvn package" if "maven" in context.build_tools else "./gradlew build",
                "artifact_path": "target/" if "maven" in context.build_tools else "build/libs/"
            }
        else:
            return {"runtime": "docker", "dockerfile": "Dockerfile"}
    
    def _load_decision_rules(self) -> Dict[str, Any]:
        """Load decision-making rules"""
        return {
            "scaling": {
                "scale_up_conditions": ["cpu > 80", "memory > 85", "response_time > 2s"],
                "scale_down_conditions": ["cpu < 30", "memory < 40", "low_traffic_period"],
                "max_instances": 10,
                "min_instances": 1
            },
            "health": {
                "restart_conditions": ["error_rate > 5", "memory_leak_detected", "deadlock_detected"],
                "rollback_conditions": ["error_rate > 10", "cascading_failures"],
                "max_restart_attempts": 3
            },
            "security": {
                "immediate_block": ["sql_injection", "xss_attack", "brute_force"],
                "alert_conditions": ["unusual_traffic", "failed_logins", "cert_expiry"]
            }
        }
    
    def _load_thresholds(self) -> Dict[str, float]:
        """Load performance thresholds"""
        return {
            "cpu_scale_up": 80.0,
            "cpu_scale_down": 30.0,
            "memory_scale_up": 85.0,
            "memory_scale_down": 40.0,
            "disk_usage": 90.0,
            "response_time": 2.0,
            "error_rate": 5.0,
            "network_usage": 80.0
        }
    
    def get_recent_decisions(self) -> List[Dict[str, Any]]:
        """Get recent decisions for status reporting"""
        recent = [d for d in self.decision_history if d.timestamp > datetime.now() - timedelta(hours=1)]
        return [
            {
                "action": d.action_type.value,
                "priority": d.priority.name,
                "target": d.target,
                "reasoning": d.reasoning,
                "timestamp": d.timestamp.isoformat()
            }
            for d in recent
        ]
