"""
Data access tools for the agent.
Provides clean interfaces to customer and feature data.
"""
from typing import Dict, Optional, List
from datetime import datetime
from ..data.models import Customer, Feature, FeatureUsage
from ..data.mock_data import generate_mock_customers, get_feature_catalog


class DataAccessTool:
    """
    Tool for accessing customer and feature data.
    In production, this would connect to databases, APIs, etc.
    """
    
    def __init__(self):
        """Initialize with mock data."""
        self._customers = generate_mock_customers()
        self._feature_catalog = get_feature_catalog()
    
    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Retrieve customer by ID."""
        return self._customers.get(customer_id)
    
    def get_feature(self, feature_id: str) -> Optional[Feature]:
        """Retrieve feature definition by ID."""
        return self._feature_catalog.get(feature_id)
    
    def get_all_features(self) -> Dict[str, Feature]:
        """Get all available features."""
        return self._feature_catalog.copy()
    
    def get_customer_feature_usage(
        self, 
        customer_id: str, 
        feature_id: str
    ) -> Optional[FeatureUsage]:
        """Get usage data for a specific customer-feature combination."""
        customer = self.get_customer(customer_id)
        if not customer:
            return None
        return customer.features.get(feature_id)
    
    def list_customers(self) -> List[str]:
        """List all customer IDs."""
        return list(self._customers.keys())
    
    def get_customers_by_account_manager(self, account_manager: str) -> List[Customer]:
        """Get all customers for a specific account manager."""
        return [
            customer for customer in self._customers.values()
            if customer.account_manager == account_manager
        ]

