"""
Test script to validate scraper against known values.
"""

from scraper import GrowwFundScraper
from data_validator import DataValidator
import json


def test_large_cap_fund():
    """Test scraping large cap fund with known values."""
    scraper = GrowwFundScraper()
    validator = DataValidator()
    
    url = "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth"
    
    print("Testing Large Cap Fund Scraper")
    print("=" * 60)
    
    try:
        fund_data = scraper.scrape_fund(url)
        
        print(f"\nFund Name: {fund_data['fund_name']}")
        print(f"Source URL: {fund_data['source_url']}")
        
        # Expected values (based on user's example)
        expected_expense_ratio = 0.85
        
        print("\n" + "-" * 60)
        print("Extracted Data:")
        print("-" * 60)
        
        # Expense Ratio
        if fund_data.get('expense_ratio'):
            er = fund_data['expense_ratio']
            print(f"Expense Ratio: {er.get('display', 'N/A')}")
            if abs(er.get('value', 0) - expected_expense_ratio) < 0.1:
                print(f"  ✓ Matches expected value (~{expected_expense_ratio}%)")
            else:
                print(f"  ✗ Does not match expected value ({expected_expense_ratio}%)")
        else:
            print("Expense Ratio: NOT FOUND")
        
        # Exit Load
        if fund_data.get('exit_load'):
            el = fund_data['exit_load']
            print(f"Exit Load: {el.get('display', 'N/A')}")
        else:
            print("Exit Load: NOT FOUND")
        
        # Minimum SIP
        if fund_data.get('minimum_sip'):
            sip = fund_data['minimum_sip']
            print(f"Minimum SIP: {sip.get('display', 'N/A')}")
        else:
            print("Minimum SIP: NOT FOUND")
        
        # Lock-in
        if fund_data.get('lock_in'):
            lock = fund_data['lock_in']
            print(f"Lock-in: {lock.get('display', 'N/A')}")
        else:
            print("Lock-in: None (not an ELSS fund)")
        
        # Riskometer
        if fund_data.get('riskometer'):
            risk = fund_data['riskometer']
            print(f"Riskometer: {risk.get('display', 'N/A')}")
        else:
            print("Riskometer: NOT FOUND")
        
        # Benchmark
        if fund_data.get('benchmark'):
            bench = fund_data['benchmark']
            print(f"Benchmark: {bench.get('display', 'N/A')}")
        else:
            print("Benchmark: NOT FOUND")
        
        # Statement Download
        if fund_data.get('statement_download'):
            stmt = fund_data['statement_download']
            print(f"Statement Download: {stmt.get('display', 'N/A')}")
        else:
            print("Statement Download: NOT FOUND")
        
        # Validation
        print("\n" + "-" * 60)
        print("Validation Results:")
        print("-" * 60)
        
        is_valid, errors, warnings = validator.validate_fund_data(fund_data)
        
        if is_valid:
            print("✓ All validations passed")
        else:
            print("✗ Validation errors found:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("\n⚠ Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        # Save test output
        with open('test_output.json', 'w', encoding='utf-8') as f:
            json.dump(fund_data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Test output saved to test_output.json")
        
        return fund_data
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_midcap_fund():
    """Test scraping midcap fund."""
    scraper = GrowwFundScraper()
    validator = DataValidator()
    
    url = "https://groww.in/mutual-funds/icici-prudential-midcap-fund-direct-growth"
    
    print("\n\nTesting Midcap Fund Scraper")
    print("=" * 60)
    
    try:
        fund_data = scraper.scrape_fund(url)
        
        print(f"\nFund Name: {fund_data['fund_name']}")
        print(f"Source URL: {fund_data['source_url']}")
        
        print("\n" + "-" * 60)
        print("Extracted Data:")
        print("-" * 60)
        
        # Expense Ratio
        if fund_data.get('expense_ratio'):
            er = fund_data['expense_ratio']
            print(f"Expense Ratio: {er.get('display', 'N/A')}")
        else:
            print("Expense Ratio: NOT FOUND")
        
        # Exit Load
        if fund_data.get('exit_load'):
            el = fund_data['exit_load']
            print(f"Exit Load: {el.get('display', 'N/A')}")
        else:
            print("Exit Load: NOT FOUND")
        
        # Minimum SIP
        if fund_data.get('minimum_sip'):
            sip = fund_data['minimum_sip']
            print(f"Minimum SIP: {sip.get('display', 'N/A')}")
        else:
            print("Minimum SIP: NOT FOUND")
        
        # Validation
        is_valid, errors, warnings = validator.validate_fund_data(fund_data)
        
        if is_valid:
            print("\n✓ All validations passed")
        else:
            print("\n✗ Validation errors found:")
            for error in errors:
                print(f"  - {error}")
        
        return fund_data
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("ICICI Prudential AMC Fund Scraper - Test Suite")
    print("=" * 60)
    
    # Test large cap fund
    large_cap_data = test_large_cap_fund()
    
    # Test midcap fund
    midcap_data = test_midcap_fund()
    
    print("\n\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Large Cap Fund: {'✓ PASSED' if large_cap_data else '✗ FAILED'}")
    print(f"Midcap Fund: {'✓ PASSED' if midcap_data else '✗ FAILED'}")


