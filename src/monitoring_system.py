"""
Monitoring System - Tracks system health, metrics, and performance
"""

import asyncio
import random
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from decision_engine import SystemState
# from .devops_agent import ProjectContext
# Import will be resolved at runtime

@dataclass
class MetricData:
    timestamp: datetime
    value: float
    metric_name: str
    tags: Dict[str, str]

class MonitoringSystem:
    """Monitors system health and collects performance metrics"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_monitoring = False
        self.metrics_history: List[MetricData] = []
        self.current_alerts: List[Dict[str, Any]] = []
        self.monitoring_interval = config.get("monitoring_interval", 60)
        
    async def start_monitoring(self, context: 'ProjectContext') -> None:
        """Start continuous monitoring"""
        self.logger.info("Starting monitoring system")
        self.is_monitoring = True
        self.project_context = context
        
        # Start monitoring tasks
        asyncio.create_task(self._collect_metrics())
        asyncio.create_task(self._check_alerts())
        asyncio.create_task(self._health_checks())
    
    async def stop(self) -> None:
        """Stop monitoring"""
        self.logger.info("Stopping monitoring system")
        self.is_monitoring = False
    
    async def get_system_state(self) -> SystemState:
        """Get current system state"""
        # Simulate collecting real metrics
        current_time = datetime.now()
        
        # Generate realistic metrics with some variation
        cpu_usage = self._generate_cpu_metric()
        memory_usage = self._generate_memory_metric()
        disk_usage = self._generate_disk_metric()
        network_usage = self._generate_network_metric()
        response_time = self._generate_response_time_metric()
        error_rate = self._generate_error_rate_metric()
        request_count = self._generate_request_count_metric()
        
        # Service health simulation
        service_health = self._check_service_health()
        
        # Get current alerts
        alerts = self.current_alerts.copy()
        
        # Deployment status
        deployment_status = "stable"
        last_deployment = current_time - timedelta(hours=2)  # Simulate last deployment
        
        return SystemState(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage,
            network_usage=network_usage,
            response_time=response_time,
            error_rate=error_rate,
            request_count=request_count,
            service_health=service_health,
            alerts=alerts,
            deployment_status=deployment_status,
            last_deployment=last_deployment
        )
    
    async def _collect_metrics(self) -> None:
        """Continuously collect system metrics"""
        while self.is_monitoring:
            try:
                timestamp = datetime.now()
                
                # Collect various metrics
                metrics = [
                    MetricData(timestamp, self._generate_cpu_metric(), "cpu_usage", {"host": "web-1"}),
                    MetricData(timestamp, self._generate_memory_metric(), "memory_usage", {"host": "web-1"}),
                    MetricData(timestamp, self._generate_disk_metric(), "disk_usage", {"host": "web-1"}),
                    MetricData(timestamp, self._generate_response_time_metric(), "response_time", {"service": "api"}),
                    MetricData(timestamp, self._generate_error_rate_metric(), "error_rate", {"service": "api"}),
                ]
                
                # Store metrics
                self.metrics_history.extend(metrics)
                
                # Keep only recent metrics (last 24 hours)
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_time]
                
                # Log metrics periodically
                if len(self.metrics_history) % 10 == 0:
                    self.logger.debug(f"Collected {len(metrics)} metrics")
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error collecting metrics: {str(e)}")
                await asyncio.sleep(10)
    
    async def _check_alerts(self) -> None:
        """Check for alert conditions"""
        while self.is_monitoring:
            try:
                current_state = await self.get_system_state()
                new_alerts = []
                
                # CPU usage alerts
                if current_state.cpu_usage > 90:
                    new_alerts.append({
                        "id": f"cpu-alert-{datetime.now().timestamp()}",
                        "type": "performance",
                        "severity": "high",
                        "message": f"High CPU usage: {current_state.cpu_usage}%",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Memory usage alerts
                if current_state.memory_usage > 90:
                    new_alerts.append({
                        "id": f"memory-alert-{datetime.now().timestamp()}",
                        "type": "performance",
                        "severity": "high",
                        "message": f"High memory usage: {current_state.memory_usage}%",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Disk usage alerts
                if current_state.disk_usage > 85:
                    new_alerts.append({
                        "id": f"disk-alert-{datetime.now().timestamp()}",
                        "type": "storage",
                        "severity": "medium",
                        "message": f"High disk usage: {current_state.disk_usage}%",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Response time alerts
                if current_state.response_time > 3.0:
                    new_alerts.append({
                        "id": f"response-alert-{datetime.now().timestamp()}",
                        "type": "performance",
                        "severity": "medium",
                        "message": f"Slow response time: {current_state.response_time}s",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Error rate alerts
                if current_state.error_rate > 5:
                    new_alerts.append({
                        "id": f"error-alert-{datetime.now().timestamp()}",
                        "type": "error",
                        "severity": "high",
                        "message": f"High error rate: {current_state.error_rate}%",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Security alerts (simulated)
                if random.random() < 0.01:  # 1% chance of security alert
                    new_alerts.append({
                        "id": f"security-alert-{datetime.now().timestamp()}",
                        "type": "security",
                        "severity": "high",
                        "message": "Suspicious login attempts detected",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # SSL certificate expiry (simulated)
                if random.random() < 0.005:  # 0.5% chance
                    new_alerts.append({
                        "id": f"ssl-alert-{datetime.now().timestamp()}",
                        "type": "security",
                        "severity": "medium",
                        "message": "SSL certificate expiring in 7 days",
                        "timestamp": datetime.now().isoformat()
                    })
                
                # Add new alerts
                self.current_alerts.extend(new_alerts)
                
                # Remove old alerts (older than 1 hour)
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.current_alerts = [
                    alert for alert in self.current_alerts 
                    if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
                ]
                
                if new_alerts:
                    self.logger.info(f"Generated {len(new_alerts)} new alerts")
                
                await asyncio.sleep(30)  # Check alerts every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error checking alerts: {str(e)}")
                await asyncio.sleep(10)
    
    async def _health_checks(self) -> None:
        """Perform health checks on services"""
        while self.is_monitoring:
            try:
                # Simulate health checks for various services
                services = ["web", "api", "database", "cache", "queue"]
                
                for service in services:
                    is_healthy = await self._check_service_health_individual(service)
                    
                    if not is_healthy:
                        alert = {
                            "id": f"health-alert-{service}-{datetime.now().timestamp()}",
                            "type": "health",
                            "severity": "critical",
                            "message": f"Service {service} is unhealthy",
                            "timestamp": datetime.now().isoformat()
                        }
                        self.current_alerts.append(alert)
                        self.logger.warning(f"Service {service} health check failed")
                
                await asyncio.sleep(60)  # Health checks every minute
                
            except Exception as e:
                self.logger.error(f"Error in health checks: {str(e)}")
                await asyncio.sleep(10)
    
    def _generate_cpu_metric(self) -> float:
        """Generate realistic CPU usage metric"""
        # Base CPU usage with some randomness
        base_cpu = 45.0
        variation = random.gauss(0, 15)  # Normal distribution
        cpu_usage = max(0, min(100, base_cpu + variation))
        
        # Simulate occasional spikes
        if random.random() < 0.05:  # 5% chance of spike
            cpu_usage = min(100, cpu_usage + random.uniform(20, 40))
        
        return round(cpu_usage, 2)
    
    def _generate_memory_metric(self) -> float:
        """Generate realistic memory usage metric"""
        base_memory = 60.0
        variation = random.gauss(0, 10)
        memory_usage = max(0, min(100, base_memory + variation))
        
        # Simulate memory leaks (gradual increase)
        if random.random() < 0.02:  # 2% chance
            memory_usage = min(100, memory_usage + random.uniform(10, 25))
        
        return round(memory_usage, 2)
    
    def _generate_disk_metric(self) -> float:
        """Generate realistic disk usage metric"""
        base_disk = 35.0
        variation = random.gauss(0, 5)
        disk_usage = max(0, min(100, base_disk + variation))
        
        return round(disk_usage, 2)
    
    def _generate_network_metric(self) -> float:
        """Generate realistic network usage metric"""
        base_network = 25.0
        variation = random.gauss(0, 20)
        network_usage = max(0, min(100, base_network + variation))
        
        return round(network_usage, 2)
    
    def _generate_response_time_metric(self) -> float:
        """Generate realistic response time metric"""
        base_response = 0.8
        variation = random.gauss(0, 0.3)
        response_time = max(0.1, base_response + variation)
        
        # Simulate occasional slow responses
        if random.random() < 0.03:  # 3% chance
            response_time += random.uniform(1, 4)
        
        return round(response_time, 3)
    
    def _generate_error_rate_metric(self) -> float:
        """Generate realistic error rate metric"""
        base_error = 1.5
        variation = random.gauss(0, 1)
        error_rate = max(0, base_error + variation)
        
        # Simulate error spikes
        if random.random() < 0.02:  # 2% chance
            error_rate += random.uniform(3, 8)
        
        return round(error_rate, 2)
    
    def _generate_request_count_metric(self) -> int:
        """Generate realistic request count metric"""
        base_requests = 150
        variation = random.gauss(0, 50)
        request_count = max(0, int(base_requests + variation))
        
        return request_count
    
    def _check_service_health(self) -> Dict[str, bool]:
        """Check health of all services"""
        services = ["web", "api", "database", "cache", "queue"]
        health_status = {}
        
        for service in services:
            # Simulate service health (95% uptime)
            health_status[service] = random.random() > 0.05
        
        return health_status
    
    async def _check_service_health_individual(self, service: str) -> bool:
        """Check health of individual service"""
        # Simulate health check delay
        await asyncio.sleep(0.1)
        
        # Simulate service health (98% uptime for individual checks)
        return random.random() > 0.02
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            "is_monitoring": self.is_monitoring,
            "metrics_collected": len(self.metrics_history),
            "active_alerts": len(self.current_alerts),
            "monitoring_interval": self.monitoring_interval,
            "last_collection": datetime.now().isoformat()
        }
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get summary of metrics for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {"message": "No metrics available"}
        
        # Group metrics by name
        metrics_by_name = {}
        for metric in recent_metrics:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = []
            metrics_by_name[metric.metric_name].append(metric.value)
        
        # Calculate statistics
        summary = {}
        for name, values in metrics_by_name.items():
            summary[name] = {
                "avg": round(sum(values) / len(values), 2),
                "min": round(min(values), 2),
                "max": round(max(values), 2),
                "count": len(values)
            }
        
        return {
            "period_hours": hours,
            "metrics": summary,
            "total_datapoints": len(recent_metrics)
        }
