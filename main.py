"""
Main script to orchestrate data extraction, validation, and storage.
Follows the recommended precompute architecture.
"""

import sys
import json
from scraper import GrowwFundScraper
from data_validator import DataValidator
from data_storage import DataStorage


def scrape_and_store_funds(urls: list, validate: bool = True):
    """
    Scrape fund data from URLs, validate, and store.
    
    Args:
        urls: List of Groww fund URLs to scrape
        validate: Whether to validate data before storing
    """
    scraper = GrowwFundScraper()
    validator = DataValidator()
    storage = DataStorage()
    
    results = {
        'successful': [],
        'failed': [],
        'validation_errors': []
    }
    
    for url in urls:
        print(f"\n{'='*80}")
        print(f"Processing: {url}")
        print('='*80)
        
        try:
            # Scrape data
            fund_data = scraper.scrape_fund(url)
            print(f"\n[OK] Scraped data for: {fund_data['fund_name']}")
            
            # Validate data
            if validate:
                is_valid, errors, warnings = validator.validate_fund_data(fund_data)
                
                if warnings:
                    print(f"\n[WARN] Warnings:")
                    for warning in warnings:
                        print(f"  - {warning}")
                
                if not is_valid:
                    print(f"\n[FAIL] Validation failed:")
                    for error in errors:
                        print(f"  - {error}")
                    results['validation_errors'].append({
                        'url': url,
                        'errors': errors
                    })
                    
                    # In non-interactive mode, skip saving if validation fails
                    # Set SAVE_ON_VALIDATION_ERROR=true to save anyway
                    import os
                    save_anyway = os.getenv('SAVE_ON_VALIDATION_ERROR', 'false').lower() == 'true'
                    
                    if not save_anyway:
                        print("\n[WARN] Skipping save due to validation errors (set SAVE_ON_VALIDATION_ERROR=true to save anyway)")
                        results['failed'].append({
                            'url': url,
                            'reason': 'Validation failed'
                        })
                        continue
                    else:
                        print("\n[WARN] Saving despite validation errors (SAVE_ON_VALIDATION_ERROR=true)")
                else:
                    print(f"\n[OK] Validation passed")
            
            # Store data
            fund_id = storage.save_fund_data(fund_data)
            print(f"[OK] Saved with ID: {fund_id}")
            
            results['successful'].append({
                'url': url,
                'fund_name': fund_data['fund_name'],
                'fund_id': fund_id
            })
            
            # Print summary
            print(f"\nData Summary:")
            print(f"  Fund Name: {fund_data['fund_name']}")
            if fund_data.get('expense_ratio'):
                print(f"  Expense Ratio: {fund_data['expense_ratio'].get('display', 'N/A')}")
            if fund_data.get('exit_load'):
                print(f"  Exit Load: {fund_data['exit_load'].get('display', 'N/A')}")
            if fund_data.get('minimum_sip'):
                print(f"  Minimum SIP: {fund_data['minimum_sip'].get('display', 'N/A')}")
            if fund_data.get('riskometer'):
                print(f"  Riskometer: {fund_data['riskometer'].get('display', 'N/A')}")
            if fund_data.get('benchmark'):
                print(f"  Benchmark: {fund_data['benchmark'].get('display', 'N/A')}")
            
        except Exception as e:
            print(f"\n[ERROR] Error processing {url}: {e}")
            results['failed'].append({
                'url': url,
                'reason': str(e)
            })
    
    # Print final summary
    print(f"\n\n{'='*80}")
    print("FINAL SUMMARY")
    print('='*80)
    print(f"[OK] Successfully processed: {len(results['successful'])}")
    print(f"[FAIL] Failed: {len(results['failed'])}")
    print(f"[WARN] Validation errors: {len(results['validation_errors'])}")
    
    if results['successful']:
        print(f"\nSuccessful funds:")
        for item in results['successful']:
            print(f"  - {item['fund_name']} ({item['fund_id']})")
    
    if results['failed']:
        print(f"\nFailed URLs:")
        for item in results['failed']:
            print(f"  - {item['url']}: {item['reason']}")
    
    # Export for RAG
    if results['successful']:
        print(f"\nExporting data for RAG...")
        rag_file = storage.export_for_rag()
        print(f"[OK] Exported to: {rag_file}")
    
    return results


def main():
    """Main entry point."""
    # Fund URLs to scrape
    fund_urls = [
        "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/icici-prudential-midcap-fund-direct-growth"
    ]
    
    # Check if URLs provided as command line arguments
    if len(sys.argv) > 1:
        fund_urls = sys.argv[1:]
    
    print("ICICI Prudential AMC Fund Data Extractor")
    print("=" * 80)
    print(f"Target URLs: {len(fund_urls)}")
    for url in fund_urls:
        print(f"  - {url}")
    
    # Validate URLs before starting
    validator = DataValidator()
    invalid_urls = []
    for url in fund_urls:
        is_valid, error = validator.validate_url(url)
        if not is_valid:
            invalid_urls.append((url, error))
    
    if invalid_urls:
        print(f"\n✗ Invalid URLs found:")
        for url, error in invalid_urls:
            print(f"  - {url}: {error}")
        print("\nPlease fix the URLs and try again.")
        return
    
    # Scrape and store
    results = scrape_and_store_funds(fund_urls, validate=True)
    
    # Save results summary
    storage = DataStorage()
    results_file = f"{storage.storage_dir}/scraping_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n[OK] Results saved to: {results_file}")


if __name__ == "__main__":
    main()

