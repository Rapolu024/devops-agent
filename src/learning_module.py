"""
Learning Module - Learns from actions and outcomes to improve decision making
"""

import json
import pickle
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict

from decision_engine import Decision, SystemState

@dataclass
class ActionOutcome:
    decision: Decision
    execution_success: bool
    system_state_before: SystemState
    system_state_after: Optional[SystemState]
    outcome_metrics: Dict[str, float]
    timestamp: datetime

class LearningModule:
    """Learns from past actions to improve future decisions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.action_history: List[ActionOutcome] = []
        self.performance_patterns: Dict[str, Any] = {}
        self.decision_effectiveness: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.learned_thresholds: Dict[str, float] = {}
        
    async def update_from_actions(self, decisions: List[Decision], system_state: SystemState) -> None:
        """Update learning from executed actions"""
        try:
            for decision in decisions:
                # Simulate action outcome (in real implementation, this would come from monitoring)
                outcome = await self._simulate_action_outcome(decision, system_state)
                self.action_history.append(outcome)
                
                # Update decision effectiveness
                await self._update_decision_effectiveness(outcome)
                
                # Learn patterns
                await self._learn_patterns(outcome)
                
            # Cleanup old history
            await self._cleanup_old_data()
            
            self.logger.debug(f"Updated learning from {len(decisions)} decisions")
            
        except Exception as e:
            self.logger.error(f"Error updating learning module: {str(e)}")
    
    async def _simulate_action_outcome(self, decision: Decision, system_state: SystemState) -> ActionOutcome:
        """Simulate the outcome of an action (in real implementation, measure actual results)"""
        import random
        
        # Simulate execution success (90% success rate)
        execution_success = random.random() > 0.1
        
        # Simulate system state after action
        system_state_after = await self._simulate_system_state_after_action(decision, system_state)
        
        # Calculate outcome metrics
        outcome_metrics = self._calculate_outcome_metrics(system_state, system_state_after)
        
        return ActionOutcome(
            decision=decision,
            execution_success=execution_success,
            system_state_before=system_state,
            system_state_after=system_state_after,
            outcome_metrics=outcome_metrics,
            timestamp=datetime.now()
        )
    
    async def _simulate_system_state_after_action(self, decision: Decision, before_state: SystemState) -> SystemState:
        """Simulate how system state changes after an action"""
        import random
        
        # Copy the before state
        after_state = SystemState(
            cpu_usage=before_state.cpu_usage,
            memory_usage=before_state.memory_usage,
            disk_usage=before_state.disk_usage,
            network_usage=before_state.network_usage,
            response_time=before_state.response_time,
            error_rate=before_state.error_rate,
            request_count=before_state.request_count,
            service_health=before_state.service_health.copy(),
            alerts=before_state.alerts.copy(),
            deployment_status=before_state.deployment_status,
            last_deployment=before_state.last_deployment
        )
        
        # Simulate improvements based on action type
        if decision.action_type.value == "scale_up":
            # Scaling up should reduce CPU and improve response time
            after_state.cpu_usage = max(10, before_state.cpu_usage - random.uniform(10, 25))
            after_state.response_time = max(0.1, before_state.response_time - random.uniform(0.2, 0.8))
            
        elif decision.action_type.value == "scale_down":
            # Scaling down might increase CPU slightly but save costs
            after_state.cpu_usage = min(100, before_state.cpu_usage + random.uniform(5, 15))
            
        elif decision.action_type.value == "restart_service":
            # Restarting should improve error rate and response time
            after_state.error_rate = max(0, before_state.error_rate - random.uniform(2, 5))
            after_state.response_time = max(0.1, before_state.response_time - random.uniform(0.3, 1.0))
            
        elif decision.action_type.value == "heal_service":
            # Healing should restore service health
            for service in after_state.service_health:
                if not before_state.service_health[service]:
                    after_state.service_health[service] = random.random() > 0.2  # 80% healing success
                    
        elif decision.action_type.value == "optimize_performance":
            # Performance optimization should improve multiple metrics
            after_state.cpu_usage = max(5, before_state.cpu_usage - random.uniform(5, 15))
            after_state.memory_usage = max(5, before_state.memory_usage - random.uniform(5, 20))
            after_state.response_time = max(0.1, before_state.response_time - random.uniform(0.1, 0.5))
        
        return after_state
    
    def _calculate_outcome_metrics(self, before: SystemState, after: SystemState) -> Dict[str, float]:
        """Calculate metrics to measure action effectiveness"""
        metrics = {}
        
        # Performance improvements
        metrics['cpu_improvement'] = before.cpu_usage - after.cpu_usage
        metrics['memory_improvement'] = before.memory_usage - after.memory_usage
        metrics['response_time_improvement'] = before.response_time - after.response_time
        metrics['error_rate_improvement'] = before.error_rate - after.error_rate
        
        # Health improvements
        before_healthy_services = sum(1 for h in before.service_health.values() if h)
        after_healthy_services = sum(1 for h in after.service_health.values() if h)
        metrics['health_improvement'] = after_healthy_services - before_healthy_services
        
        # Overall effectiveness score
        effectiveness = 0
        if metrics['cpu_improvement'] > 0:
            effectiveness += 0.3
        if metrics['response_time_improvement'] > 0:
            effectiveness += 0.3
        if metrics['error_rate_improvement'] > 0:
            effectiveness += 0.2
        if metrics['health_improvement'] > 0:
            effectiveness += 0.2
        
        metrics['overall_effectiveness'] = effectiveness
        
        return metrics
    
    async def _update_decision_effectiveness(self, outcome: ActionOutcome) -> None:
        """Update decision effectiveness tracking"""
        action_type = outcome.decision.action_type.value
        target = outcome.decision.target
        
        # Track success rate
        if 'success_rate' not in self.decision_effectiveness[action_type]:
            self.decision_effectiveness[action_type]['success_rate'] = []
        
        self.decision_effectiveness[action_type]['success_rate'].append(
            1.0 if outcome.execution_success else 0.0
        )
        
        # Track effectiveness
        if 'effectiveness' not in self.decision_effectiveness[action_type]:
            self.decision_effectiveness[action_type]['effectiveness'] = []
        
        self.decision_effectiveness[action_type]['effectiveness'].append(
            outcome.outcome_metrics.get('overall_effectiveness', 0.0)
        )
        
        # Keep only recent data (last 100 actions per type)
        for metric_list in self.decision_effectiveness[action_type].values():
            if isinstance(metric_list, list) and len(metric_list) > 100:
                metric_list[:] = metric_list[-100:]
    
    async def _learn_patterns(self, outcome: ActionOutcome) -> None:
        """Learn patterns from action outcomes"""
        try:
            # Learn optimal thresholds
            await self._learn_optimal_thresholds(outcome)
            
            # Learn timing patterns
            await self._learn_timing_patterns(outcome)
            
            # Learn context-specific patterns
            await self._learn_context_patterns(outcome)
            
        except Exception as e:
            self.logger.error(f"Error learning patterns: {str(e)}")
    
    async def _learn_optimal_thresholds(self, outcome: ActionOutcome) -> None:
        """Learn optimal thresholds for triggering actions"""
        action_type = outcome.decision.action_type.value
        before_state = outcome.system_state_before
        effectiveness = outcome.outcome_metrics.get('overall_effectiveness', 0.0)
        
        # Learn CPU thresholds for scaling actions
        if action_type in ['scale_up', 'scale_down']:
            threshold_key = f"{action_type}_cpu_threshold"
            
            if threshold_key not in self.learned_thresholds:
                self.learned_thresholds[threshold_key] = []
            
            # Store successful threshold examples
            if effectiveness > 0.5:  # Action was effective
                self.learned_thresholds[threshold_key].append(before_state.cpu_usage)
                
                # Keep only recent examples
                if len(self.learned_thresholds[threshold_key]) > 50:
                    self.learned_thresholds[threshold_key][:] = self.learned_thresholds[threshold_key][-50:]
    
    async def _learn_timing_patterns(self, outcome: ActionOutcome) -> None:
        """Learn optimal timing for actions"""
        # Learn time-based patterns (e.g., when to scale during day/night)
        hour = outcome.timestamp.hour
        action_type = outcome.decision.action_type.value
        effectiveness = outcome.outcome_metrics.get('overall_effectiveness', 0.0)
        
        pattern_key = f"timing_{action_type}"
        if pattern_key not in self.performance_patterns:
            self.performance_patterns[pattern_key] = {}
        
        if hour not in self.performance_patterns[pattern_key]:
            self.performance_patterns[pattern_key][hour] = []
        
        self.performance_patterns[pattern_key][hour].append(effectiveness)
        
        # Keep only recent data
        if len(self.performance_patterns[pattern_key][hour]) > 20:
            self.performance_patterns[pattern_key][hour][:] = self.performance_patterns[pattern_key][hour][-20:]
    
    async def _learn_context_patterns(self, outcome: ActionOutcome) -> None:
        """Learn context-specific patterns"""
        # Learn which actions work best in different system states
        action_type = outcome.decision.action_type.value
        effectiveness = outcome.outcome_metrics.get('overall_effectiveness', 0.0)
        
        # Categorize system state
        state_category = self._categorize_system_state(outcome.system_state_before)
        
        pattern_key = f"context_{action_type}_{state_category}"
        if pattern_key not in self.performance_patterns:
            self.performance_patterns[pattern_key] = []
        
        self.performance_patterns[pattern_key].append(effectiveness)
        
        # Keep only recent data
        if len(self.performance_patterns[pattern_key]) > 30:
            self.performance_patterns[pattern_key][:] = self.performance_patterns[pattern_key][-30:]
    
    def _categorize_system_state(self, state: SystemState) -> str:
        """Categorize system state for pattern learning"""
        if state.cpu_usage > 80 or state.memory_usage > 80:
            return "high_load"
        elif state.cpu_usage < 30 and state.memory_usage < 40:
            return "low_load"
        elif state.error_rate > 5:
            return "high_errors"
        elif state.response_time > 2.0:
            return "slow_response"
        else:
            return "normal"
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old learning data"""
        # Keep only recent action history (last 7 days)
        cutoff_time = datetime.now() - timedelta(days=7)
        self.action_history = [
            outcome for outcome in self.action_history 
            if outcome.timestamp > cutoff_time
        ]
    
    def get_decision_recommendations(self, action_type: str, system_state: SystemState) -> Dict[str, Any]:
        """Get recommendations based on learned patterns"""
        recommendations = {
            'confidence': 0.0,
            'suggested_threshold': None,
            'best_timing': None,
            'expected_effectiveness': 0.0
        }
        
        try:
            # Get success rate for this action type
            if action_type in self.decision_effectiveness:
                success_rates = self.decision_effectiveness[action_type].get('success_rate', [])
                if success_rates:
                    recommendations['confidence'] = sum(success_rates) / len(success_rates)
                
                effectiveness_scores = self.decision_effectiveness[action_type].get('effectiveness', [])
                if effectiveness_scores:
                    recommendations['expected_effectiveness'] = sum(effectiveness_scores) / len(effectiveness_scores)
            
            # Get optimal threshold recommendations
            threshold_key = f"{action_type}_cpu_threshold"
            if threshold_key in self.learned_thresholds and self.learned_thresholds[threshold_key]:
                thresholds = self.learned_thresholds[threshold_key]
                recommendations['suggested_threshold'] = sum(thresholds) / len(thresholds)
            
            # Get timing recommendations
            timing_key = f"timing_{action_type}"
            if timing_key in self.performance_patterns:
                timing_data = self.performance_patterns[timing_key]
                best_hour = None
                best_effectiveness = 0
                
                for hour, effectiveness_list in timing_data.items():
                    if effectiveness_list:
                        avg_effectiveness = sum(effectiveness_list) / len(effectiveness_list)
                        if avg_effectiveness > best_effectiveness:
                            best_effectiveness = avg_effectiveness
                            best_hour = hour
                
                recommendations['best_timing'] = best_hour
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
        
        return recommendations
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learned patterns and effectiveness"""
        summary = {
            'total_actions_learned': len(self.action_history),
            'action_types_tracked': len(self.decision_effectiveness),
            'patterns_discovered': len(self.performance_patterns),
            'learned_thresholds': len(self.learned_thresholds)
        }
        
        # Action type effectiveness
        action_effectiveness = {}
        for action_type, metrics in self.decision_effectiveness.items():
            if 'effectiveness' in metrics and metrics['effectiveness']:
                avg_effectiveness = sum(metrics['effectiveness']) / len(metrics['effectiveness'])
                action_effectiveness[action_type] = round(avg_effectiveness, 3)
        
        summary['action_effectiveness'] = action_effectiveness
        
        # Most effective actions
        if action_effectiveness:
            best_action = max(action_effectiveness.items(), key=lambda x: x[1])
            summary['most_effective_action'] = {
                'action': best_action[0],
                'effectiveness': best_action[1]
            }
        
        return summary
    
    def save_learning_data(self, filepath: str) -> bool:
        """Save learning data to file"""
        try:
            data = {
                'action_history': self.action_history,
                'performance_patterns': self.performance_patterns,
                'decision_effectiveness': dict(self.decision_effectiveness),
                'learned_thresholds': self.learned_thresholds
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.info(f"Learning data saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving learning data: {str(e)}")
            return False
    
    def load_learning_data(self, filepath: str) -> bool:
        """Load learning data from file"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            self.action_history = data.get('action_history', [])
            self.performance_patterns = data.get('performance_patterns', {})
            self.decision_effectiveness = defaultdict(dict, data.get('decision_effectiveness', {}))
            self.learned_thresholds = data.get('learned_thresholds', {})
            
            self.logger.info(f"Learning data loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading learning data: {str(e)}")
            return False
