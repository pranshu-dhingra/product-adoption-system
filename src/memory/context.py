"""
Memory system for storing customer context and historical patterns.
In production, this would integrate with persistent storage.
"""
from typing import Dict, List, Optional
from datetime import datetime
from ..data.models import Customer, Recommendation, ChurnRiskAssessment


class MemoryStore:
    """
    In-memory store for customer context and historical intelligence.
    In production, this would be backed by a database or vector store.
    """
    
    def __init__(self):
        """Initialize empty memory store."""
        self._customer_contexts: Dict[str, Dict] = {}
        self._historical_recommendations: Dict[str, List[Recommendation]] = {}
        self._historical_assessments: Dict[str, List[ChurnRiskAssessment]] = {}
    
    def store_customer_context(
        self,
        customer_id: str,
        context: Dict
    ):
        """Store customer context for future reference."""
        if customer_id not in self._customer_contexts:
            self._customer_contexts[customer_id] = {}
        
        self._customer_contexts[customer_id].update(context)
        self._customer_contexts[customer_id]["last_updated"] = datetime.now()
    
    def get_customer_context(self, customer_id: str) -> Dict:
        """Retrieve stored customer context."""
        return self._customer_contexts.get(customer_id, {})
    
    def store_recommendations(
        self,
        customer_id: str,
        recommendations: List[Recommendation]
    ):
        """Store historical recommendations for trend analysis."""
        if customer_id not in self._historical_recommendations:
            self._historical_recommendations[customer_id] = []
        
        self._historical_recommendations[customer_id].append({
            "timestamp": datetime.now(),
            "recommendations": recommendations
        })
    
    def get_recommendation_history(
        self,
        customer_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get recent recommendation history."""
        history = self._historical_recommendations.get(customer_id, [])
        return history[-limit:]
    
    def store_churn_assessment(
        self,
        customer_id: str,
        assessment: ChurnRiskAssessment
    ):
        """Store historical churn risk assessments."""
        if customer_id not in self._historical_assessments:
            self._historical_assessments[customer_id] = []
        
        self._historical_assessments[customer_id].append({
            "timestamp": datetime.now(),
            "assessment": assessment
        })
    
    def get_churn_history(
        self,
        customer_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """Get recent churn risk history."""
        history = self._historical_assessments.get(customer_id, [])
        return history[-limit:]
    
    def get_risk_trend(self, customer_id: str) -> Optional[str]:
        """Analyze risk trend over time."""
        history = self.get_churn_history(customer_id, limit=3)
        if len(history) < 2:
            return None
        
        # Compare most recent with previous
        recent = history[-1]["assessment"].risk_score
        previous = history[-2]["assessment"].risk_score
        
        if recent > previous + 0.1:
            return "increasing"
        elif recent < previous - 0.1:
            return "decreasing"
        else:
            return "stable"

