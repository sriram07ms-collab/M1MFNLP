"""
Data validation module to verify extracted fund data.
"""

import re
from typing import Dict, List, Optional, Tuple


class DataValidator:
    """Validates extracted fund data for correctness and completeness."""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_url(self, url: str) -> Tuple[bool, Optional[str]]:
        """Validate that URL is from groww.in and is well-formed."""
        if not url:
            return False, "URL is empty"
        
        if not url.startswith(('http://', 'https://')):
            return False, "URL must start with http:// or https://"
        
        if 'groww.in' not in url:
            return False, "URL must be from groww.in domain"
        
        return True, None
    
    def validate_expense_ratio(self, expense_ratio: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate expense ratio data."""
        if expense_ratio is None:
            return False, "Expense ratio not found"
        
        if 'value' not in expense_ratio:
            return False, "Expense ratio value missing"
        
        value = expense_ratio.get('value')
        if not isinstance(value, (int, float)):
            return False, "Expense ratio value must be numeric"
        
        if value < 0 or value > 10:
            return False, f"Expense ratio {value}% seems unrealistic (expected 0-10%)"
        
        return True, None
    
    def validate_exit_load(self, exit_load: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate exit load data."""
        if exit_load is None:
            # Exit load can be None (no exit load)
            return True, None
        
        if 'value' not in exit_load:
            return False, "Exit load value missing"
        
        value = exit_load.get('value')
        if not isinstance(value, (int, float)):
            return False, "Exit load value must be numeric"
        
        if value < 0 or value > 5:
            return False, f"Exit load {value}% seems unrealistic (expected 0-5%)"
        
        return True, None
    
    def validate_minimum_sip(self, minimum_sip: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate minimum SIP amount."""
        if minimum_sip is None:
            return False, "Minimum SIP not found"
        
        if 'value' not in minimum_sip:
            return False, "Minimum SIP value missing"
        
        value = minimum_sip.get('value')
        if not isinstance(value, int):
            return False, "Minimum SIP value must be an integer"
        
        if value < 100 or value > 100000:
            return False, f"Minimum SIP ₹{value} seems unrealistic (expected ₹100-₹100,000)"
        
        return True, None
    
    def validate_lock_in(self, lock_in: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate lock-in period."""
        # Lock-in is optional (only for ELSS funds)
        if lock_in is None:
            return True, None  # Not all funds have lock-in
        
        if 'value' not in lock_in:
            return False, "Lock-in value missing"
        
        value = lock_in.get('value')
        if not isinstance(value, int):
            return False, "Lock-in value must be an integer"
        
        if value < 0 or value > 10:
            return False, f"Lock-in {value} years seems unrealistic (expected 0-10 years)"
        
        return True, None
    
    def validate_rating(self, rating: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate fund rating."""
        # Rating is optional
        if rating is None:
            return True, None  # Rating may not be available for all funds
        
        if 'value' not in rating:
            return False, "Rating value missing"
        
        value = rating.get('value')
        if not isinstance(value, int):
            return False, "Rating value must be an integer"
        
        if value < 1 or value > 5:
            return False, f"Rating {value} is out of valid range (1-5)"
        
        return True, None
    
    def validate_riskometer(self, riskometer: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate riskometer/risk rating."""
        if riskometer is None:
            return False, "Riskometer not found"
        
        if 'value' not in riskometer:
            return False, "Riskometer value missing"
        
        valid_risk_levels = ['very low', 'low', 'moderate', 'high', 'very high']
        value = riskometer.get('value', '').lower()
        
        if value not in valid_risk_levels:
            return False, f"Invalid risk level: {value}. Expected one of {valid_risk_levels}"
        
        return True, None
    
    def validate_benchmark(self, benchmark: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate benchmark information."""
        if benchmark is None:
            return False, "Benchmark not found"
        
        if 'value' not in benchmark:
            return False, "Benchmark value missing"
        
        value = benchmark.get('value', '').strip()
        if not value or len(value) < 5:
            return False, "Benchmark value seems too short or empty"
        
        # Check if it contains common benchmark keywords
        benchmark_keywords = ['nifty', 'sensex', 'index', 'total return']
        if not any(keyword in value.lower() for keyword in benchmark_keywords):
            return False, f"Benchmark '{value}' doesn't seem to be a valid index name"
        
        return True, None
    
    def validate_statement_download(self, statement_download: Optional[Dict]) -> Tuple[bool, Optional[str]]:
        """Validate statement download information."""
        if statement_download is None:
            return False, "Statement download info not found"
        
        if 'available' not in statement_download:
            return False, "Statement download availability not specified"
        
        return True, None
    
    def validate_fund_data(self, fund_data: Dict) -> Tuple[bool, List[str], List[str]]:
        """Validate complete fund data structure."""
        errors = []
        warnings = []
        
        # Validate URL
        url = fund_data.get('source_url')
        is_valid, error = self.validate_url(url)
        if not is_valid:
            errors.append(f"URL validation failed: {error}")
        
        # Validate fund name
        fund_name = fund_data.get('fund_name')
        if not fund_name or fund_name == "Unknown Fund":
            warnings.append("Fund name not found or is generic")
        
        # Validate all data fields
        validations = [
            ('expense_ratio', self.validate_expense_ratio),
            ('exit_load', self.validate_exit_load),
            ('minimum_sip', self.validate_minimum_sip),
            ('lock_in', self.validate_lock_in),
            ('rating', self.validate_rating),
            ('riskometer', self.validate_riskometer),
            ('benchmark', self.validate_benchmark),
            ('statement_download', self.validate_statement_download),
        ]
        
        for field_name, validator_func in validations:
            field_data = fund_data.get(field_name)
            is_valid, error = validator_func(field_data)
            if not is_valid:
                errors.append(f"{field_name}: {error}")
        
        return len(errors) == 0, errors, warnings
    
    def compare_with_expected(self, fund_data: Dict, expected_data: Optional[Dict] = None) -> List[str]:
        """Compare extracted data with expected values (for validation)."""
        discrepancies = []
        
        if expected_data is None:
            return discrepancies
        
        # Compare expense ratio (with tolerance)
        if 'expense_ratio' in expected_data:
            expected = expected_data['expense_ratio']
            actual = fund_data.get('expense_ratio', {}).get('value')
            if actual is not None:
                tolerance = 0.1  # 0.1% tolerance
                if abs(actual - expected) > tolerance:
                    discrepancies.append(
                        f"Expense ratio mismatch: expected {expected}%, got {actual}%"
                    )
        
        return discrepancies


if __name__ == "__main__":
    validator = DataValidator()
    
    # Test validation
    test_data = {
        'fund_name': 'ICICI Prudential Large Cap Fund',
        'source_url': 'https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth',
        'expense_ratio': {'value': 0.85, 'unit': '%', 'display': '0.85%'},
        'exit_load': {'value': 1.0, 'unit': '%', 'display': '1% if redeemed within 1 year'},
        'minimum_sip': {'value': 100, 'unit': 'INR', 'display': '₹100'},
        'riskometer': {'value': 'very high', 'display': 'Very High'},
        'benchmark': {'value': 'NIFTY 100 Total Return Index', 'display': 'NIFTY 100 Total Return Index'},
        'statement_download': {'available': True, 'display': 'Available'}
    }
    
    is_valid, errors, warnings = validator.validate_fund_data(test_data)
    print(f"Validation result: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        print(f"Errors: {errors}")
    if warnings:
        print(f"Warnings: {warnings}")

