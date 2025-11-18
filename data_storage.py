"""
Data storage module for saving and retrieving fund data.
Follows the precompute architecture - stores data with source URLs.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class DataStorage:
    """Manages storage and retrieval of fund data."""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.funds_file = os.path.join(storage_dir, "funds_data.json")
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist."""
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def _generate_fund_id(self, url: str) -> str:
        """Generate a unique ID for a fund based on its URL."""
        # Extract fund name from URL
        fund_slug = url.split('/')[-1]
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def save_fund_data(self, fund_data: Dict, overwrite: bool = True) -> str:
        """Save fund data to storage."""
        fund_id = self._generate_fund_id(fund_data['source_url'])
        
        # Load existing data
        all_funds = self.load_all_funds()
        
        # Check if fund already exists
        existing_index = None
        for i, fund in enumerate(all_funds):
            if fund.get('source_url') == fund_data['source_url']:
                existing_index = i
                break
        
        # Add metadata
        fund_data['fund_id'] = fund_id
        fund_data['last_updated'] = datetime.now().isoformat()
        
        if existing_index is not None:
            if overwrite:
                all_funds[existing_index] = fund_data
                print(f"Updated existing fund: {fund_data['fund_name']}")
            else:
                print(f"Fund already exists: {fund_data['fund_name']}. Skipping (overwrite=False).")
                return fund_id
        else:
            all_funds.append(fund_data)
            print(f"Added new fund: {fund_data['fund_name']}")
        
        # Save to file
        with open(self.funds_file, 'w', encoding='utf-8') as f:
            json.dump(all_funds, f, indent=2, ensure_ascii=False)
        
        # Update metadata
        self._update_metadata(len(all_funds))
        
        return fund_id
    
    def load_all_funds(self) -> List[Dict]:
        """Load all fund data from storage."""
        if not os.path.exists(self.funds_file):
            return []
        
        try:
            with open(self.funds_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading funds data: {e}")
            return []
    
    def load_fund_by_url(self, url: str) -> Optional[Dict]:
        """Load fund data by source URL."""
        all_funds = self.load_all_funds()
        for fund in all_funds:
            if fund.get('source_url') == url:
                return fund
        return None
    
    def load_fund_by_id(self, fund_id: str) -> Optional[Dict]:
        """Load fund data by fund ID."""
        all_funds = self.load_all_funds()
        for fund in all_funds:
            if fund.get('fund_id') == fund_id:
                return fund
        return None
    
    def _update_metadata(self, total_funds: int):
        """Update metadata file."""
        metadata = {
            'total_funds': total_funds,
            'last_updated': datetime.now().isoformat(),
            'storage_version': '1.0'
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    def get_metadata(self) -> Dict:
        """Get storage metadata."""
        if not os.path.exists(self.metadata_file):
            return {
                'total_funds': 0,
                'last_updated': None,
                'storage_version': '1.0'
            }
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {
                'total_funds': 0,
                'last_updated': None,
                'storage_version': '1.0'
            }
    
    def export_for_rag(self, output_file: str = None) -> str:
        """Export data in a format suitable for RAG (Retrieval-Augmented Generation)."""
        if output_file is None:
            output_file = os.path.join(self.storage_dir, "rag_data.json")
        
        all_funds = self.load_all_funds()
        rag_data = []
        
        for fund in all_funds:
            # Create structured facts for RAG
            facts = []
            
            if fund.get('expense_ratio'):
                facts.append({
                    'fact': f"Expense ratio: {fund['expense_ratio'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'expense_ratio'
                })
            
            if fund.get('exit_load'):
                facts.append({
                    'fact': f"Exit load: {fund['exit_load'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'exit_load'
                })
            
            if fund.get('minimum_sip'):
                facts.append({
                    'fact': f"Minimum SIP: {fund['minimum_sip'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'minimum_sip'
                })
            
            if fund.get('lock_in'):
                facts.append({
                    'fact': f"Lock-in period: {fund['lock_in'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'lock_in'
                })
            
            if fund.get('rating'):
                facts.append({
                    'fact': f"Rating: {fund['rating'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'rating'
                })
            
            if fund.get('riskometer'):
                facts.append({
                    'fact': f"Riskometer: {fund['riskometer'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'riskometer'
                })
            
            if fund.get('benchmark'):
                facts.append({
                    'fact': f"Benchmark: {fund['benchmark'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'benchmark'
                })
            
            if fund.get('statement_download'):
                facts.append({
                    'fact': f"Statement download: {fund['statement_download'].get('display', 'N/A')}",
                    'source_url': fund['source_url'],
                    'category': 'statement_download'
                })
            
            rag_data.append({
                'fund_name': fund.get('fund_name'),
                'fund_id': fund.get('fund_id'),
                'source_url': fund.get('source_url'),
                'facts': facts
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rag_data, f, indent=2, ensure_ascii=False)
        
        print(f"Exported {len(rag_data)} funds to {output_file}")
        return output_file


if __name__ == "__main__":
    storage = DataStorage()
    
    # Test data
    test_fund = {
        'fund_name': 'ICICI Prudential Large Cap Fund Direct Growth',
        'source_url': 'https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth',
        'expense_ratio': {'value': 0.85, 'unit': '%', 'display': '0.85%'},
        'exit_load': {'value': 1.0, 'unit': '%', 'display': '1% if redeemed within 1 year'},
        'minimum_sip': {'value': 100, 'unit': 'INR', 'display': '₹100'},
        'riskometer': {'value': 'very high', 'display': 'Very High'},
        'benchmark': {'value': 'NIFTY 100 Total Return Index', 'display': 'NIFTY 100 Total Return Index'},
        'statement_download': {'available': True, 'display': 'Available'}
    }
    
    fund_id = storage.save_fund_data(test_fund)
    print(f"Saved fund with ID: {fund_id}")
    
    # Export for RAG
    storage.export_for_rag()

