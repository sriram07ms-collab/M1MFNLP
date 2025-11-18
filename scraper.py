"""
Web scraper for ICICI Prudential AMC fund data from Groww website.
Extracts: expense ratio, exit load, minimum SIP, lock-in, riskometer, benchmark, statement download info.
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, Optional
from urllib.parse import urljoin, urlparse
import time


class GrowwFundScraper:
    """Scraper for extracting fund information from Groww website."""
    
    def __init__(self):
        self.base_url = "https://groww.in"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def validate_url(self, url: str) -> bool:
        """Validate that URL is from groww.in domain."""
        parsed = urlparse(url)
        return parsed.netloc in ['groww.in', 'www.groww.in'] and parsed.scheme in ['http', 'https']
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse HTML page."""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}. Must be from groww.in domain.")
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_expense_ratio(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract expense ratio from the page."""
        # Method 1: Look for expense ratio in various possible locations
        expense_patterns = [
            r'expense\s*ratio[:\s]*([\d.]+)\s*%',
            r'expense\s*ratio[:\s]*([\d.]+)',
            r'([\d.]+)\s*%\s*expense\s*ratio',
        ]
        
        text = soup.get_text()
        for pattern in expense_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                return {
                    'value': value,
                    'unit': '%',
                    'display': f"{value}%"
                }
        
        # Method 2: Look for in structured data sections (table cells, divs)
        details_sections = soup.find_all(['div', 'span', 'td', 'th'], string=re.compile(r'expense\s*ratio', re.I))
        for section in details_sections:
            parent = section.find_parent()
            if parent:
                # Look for percentage in same element or siblings
                text = parent.get_text()
                match = re.search(r'([\d.]+)\s*%', text)
                if match:
                    value = float(match.group(1))
                    return {
                        'value': value,
                        'unit': '%',
                        'display': f"{value}%"
                    }
                # Check next sibling
                next_sibling = section.find_next_sibling()
                if next_sibling:
                    text = next_sibling.get_text()
                    match = re.search(r'([\d.]+)\s*%', text)
                    if match:
                        value = float(match.group(1))
                        return {
                            'value': value,
                            'unit': '%',
                            'display': f"{value}%"
                        }
        
        # Method 3: Look in meta tags or JSON-LD structured data
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # Search in JSON structure
                json_str = json.dumps(data)
                match = re.search(r'expense[^"]*ratio[^"]*([\d.]+)', json_str, re.I)
                if match:
                    value = float(match.group(1))
                    return {
                        'value': value,
                        'unit': '%',
                        'display': f"{value}%"
                    }
            except:
                pass
        
        return None
    
    def extract_exit_load(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract exit load information."""
        exit_load_patterns = [
            r'exit\s*load\s*of\s*([\d.]+)\s*%\s*(?:if\s*redeemed\s*(?:upto|within|before)\s*(\d+)\s*(?:year|yr))',
            r'exit\s*load[:\s]*([\d.]+)\s*%\s*(?:if\s*redeemed\s*(?:upto|within|before)\s*(\d+)\s*(?:year|yr|month|mo|day|d))',
            r'exit\s*load[:\s]*([\d.]+)\s*%',
            r'([\d.]+)\s*%\s*exit\s*load',
        ]
        
        text = soup.get_text()
        for pattern in exit_load_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                percentage = float(match.group(1))
                period = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                if period:
                    return {
                        'value': percentage,
                        'unit': '%',
                        'period': period,
                        'display': f"{percentage}% if redeemed within {period} year(s)"
                    }
                else:
                    return {
                        'value': percentage,
                        'unit': '%',
                        'display': f"{percentage}%"
                    }
        
        # Also check for "No exit load" or "Nil exit load"
        if re.search(r'(?:no|nil|zero)\s*exit\s*load', text, re.I):
            return {
                'value': 0,
                'unit': '%',
                'display': "No exit load"
            }
        
        return None
    
    def extract_minimum_sip(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract minimum SIP amount."""
        sip_patterns = [
            r'min\.?\s*sip\s*amount[:\s]*₹?\s*(\d+(?:,\d+)*)',
            r'min\.?\s*sip[:\s]*₹?\s*(\d+(?:,\d+)*)',
            r'minimum\s*sip[:\s]*₹?\s*(\d+(?:,\d+)*)',
            r'sip[:\s]*₹?\s*(\d+(?:,\d+)*)',
            r'₹?\s*(\d+(?:,\d+)*)\s*min\.?\s*sip',
        ]
        
        text = soup.get_text()
        for pattern in sip_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = int(amount_str)
                return {
                    'value': amount,
                    'unit': 'INR',
                    'display': f"₹{amount}"
                }
        
        # Look for "Min. SIP amount" in structured format (like in tables)
        sip_elements = soup.find_all(string=re.compile(r'min\.?\s*sip', re.I))
        for elem in sip_elements:
            parent = elem.find_parent()
            if parent:
                # Check parent and siblings for amount
                text = parent.get_text()
                match = re.search(r'₹?\s*(\d+(?:,\d+)*)', text)
                if match:
                    amount_str = match.group(1).replace(',', '')
                    amount = int(amount_str)
                    return {
                        'value': amount,
                        'unit': 'INR',
                        'display': f"₹{amount}"
                    }
                # Check next sibling
                next_sibling = elem.find_next_sibling()
                if next_sibling:
                    text = next_sibling.get_text()
                    match = re.search(r'₹?\s*(\d+(?:,\d+)*)', text)
                    if match:
                        amount_str = match.group(1).replace(',', '')
                        amount = int(amount_str)
                        return {
                            'value': amount,
                            'unit': 'INR',
                            'display': f"₹{amount}"
                        }
        
        return None
    
    def extract_lock_in(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract lock-in period (especially for ELSS funds)."""
        lock_in_patterns = [
            r'lock[-\s]*in[:\s]*(\d+)\s*(?:year|yr)',
            r'lock[-\s]*in\s*period[:\s]*(\d+)\s*(?:year|yr)',
            r'(\d+)\s*(?:year|yr)\s*lock[-\s]*in',
            r'elss[:\s]*(\d+)\s*(?:year|yr)',
        ]
        
        text = soup.get_text()
        for pattern in lock_in_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = int(match.group(1))
                return {
                    'value': years,
                    'unit': 'years',
                    'display': f"{years} years",
                    'is_elss': 'elss' in text.lower()
                }
        
        # Check if it's an ELSS fund (which typically has 3-year lock-in)
        if 'elss' in text.lower() or 'tax saver' in text.lower():
            return {
                'value': 3,
                'unit': 'years',
                'display': "3 years (ELSS)",
                'is_elss': True
            }
        
        return None
    
    def extract_rating(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract fund rating (e.g., 5 stars)."""
        rating_patterns = [
            r'rating[:\s]*(\d+)',
            r'(\d+)\s*(?:star|rating)',
            r'rating\s*(\d+)',
        ]
        
        text = soup.get_text()
        for pattern in rating_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                rating_value = int(match.group(1))
                # Validate rating is between 1-5
                if 1 <= rating_value <= 5:
                    return {
                        'value': rating_value,
                        'display': f"{rating_value}",
                        'max_rating': 5
                    }
        
        # Look for rating in structured elements
        rating_elements = soup.find_all(string=re.compile(r'rating', re.I))
        for elem in rating_elements:
            parent = elem.find_parent()
            if parent:
                text = parent.get_text()
                match = re.search(r'(\d+)', text)
                if match:
                    rating_value = int(match.group(1))
                    if 1 <= rating_value <= 5:
                        return {
                            'value': rating_value,
                            'display': f"{rating_value}",
                            'max_rating': 5
                        }
        
        return None
    
    def extract_riskometer(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract riskometer/risk rating."""
        risk_patterns = [
            r'riskometer[:\s]*(very\s*high|high|moderate|low|very\s*low)',
            r'risk[:\s]*(very\s*high|high|moderate|low|very\s*low)',
            r'(very\s*high|high|moderate|low|very\s*low)\s*risk',
        ]
        
        text = soup.get_text()
        for pattern in risk_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                risk_level = match.group(1).strip().lower()
                return {
                    'value': risk_level,
                    'display': risk_level.title()
                }
        
        return None
    
    def extract_benchmark(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract benchmark information."""
        benchmark_patterns = [
            r'benchmark[:\s]*([^\.\n]+)',
            r'fund\s*benchmark[:\s]*([^\.\n]+)',
        ]
        
        text = soup.get_text()
        for pattern in benchmark_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                benchmark = match.group(1).strip()
                # Clean up the benchmark text
                benchmark = re.sub(r'\s+', ' ', benchmark)
                return {
                    'value': benchmark,
                    'display': benchmark
                }
        
        # Look for benchmark in structured table format
        benchmark_elements = soup.find_all(string=re.compile(r'benchmark', re.I))
        for elem in benchmark_elements:
            parent = elem.find_parent()
            if parent:
                # Look for next sibling or parent text
                text = parent.get_text()
                match = re.search(r'benchmark[:\s]*([^\.\n]+)', text, re.I)
                if match:
                    benchmark = match.group(1).strip()
                    benchmark = re.sub(r'\s+', ' ', benchmark)
                    return {
                        'value': benchmark,
                        'display': benchmark
                    }
        
        return None
    
    def extract_statement_download_info(self, soup: BeautifulSoup) -> Optional[Dict]:
        """Extract information about how to download statements."""
        # Look for statement download information
        statement_keywords = ['statement', 'download', 'account statement', 'consolidated account statement']
        
        text = soup.get_text().lower()
        has_statement_info = any(keyword in text for keyword in statement_keywords)
        
        if has_statement_info:
            # Try to find specific instructions or links
            statement_sections = soup.find_all(['div', 'section', 'p'], string=re.compile(r'statement|download', re.I))
            
            instructions = []
            for section in statement_sections[:3]:  # Limit to first 3 matches
                text = section.get_text().strip()
                if text and len(text) < 500:  # Reasonable length
                    instructions.append(text)
            
            return {
                'available': True,
                'instructions': instructions[:2] if instructions else ["Statements can be downloaded from the fund house website or registrar portal"],
                'display': "Available - Check fund house website or registrar portal (CAMS/Karvy)"
            }
        
        return {
            'available': True,
            'instructions': ["Statements can be downloaded from ICICI Prudential AMC website or registrar portal (CAMS/Karvy)"],
            'display': "Available - Check ICICI Prudential AMC website or registrar portal"
        }
    
    def extract_fund_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract fund name from the page."""
        # Try to find in title or h1
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            # Extract fund name from title
            match = re.search(r'ICICI Prudential[^|]+', title_text)
            if match:
                return match.group(0).strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return None
    
    def scrape_fund(self, url: str) -> Dict:
        """Main method to scrape all fund information."""
        if not self.validate_url(url):
            raise ValueError(f"Invalid URL: {url}")
        
        print(f"Scraping fund data from: {url}")
        soup = self.fetch_page(url)
        
        if not soup:
            raise Exception(f"Failed to fetch page: {url}")
        
        fund_name = self.extract_fund_name(soup) or "Unknown Fund"
        
        data = {
            'fund_name': fund_name,
            'source_url': url,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'expense_ratio': self.extract_expense_ratio(soup),
            'exit_load': self.extract_exit_load(soup),
            'minimum_sip': self.extract_minimum_sip(soup),
            'lock_in': self.extract_lock_in(soup),
            'rating': self.extract_rating(soup),
            'riskometer': self.extract_riskometer(soup),
            'benchmark': self.extract_benchmark(soup),
            'statement_download': self.extract_statement_download_info(soup),
        }
        
        return data


if __name__ == "__main__":
    scraper = GrowwFundScraper()
    
    # Test URLs
    test_urls = [
        "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
        "https://groww.in/mutual-funds/icici-prudential-midcap-fund-direct-growth"
    ]
    
    for url in test_urls:
        try:
            data = scraper.scrape_fund(url)
            print(f"\n{'='*60}")
            print(f"Fund: {data['fund_name']}")
            print(f"Source: {data['source_url']}")
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error scraping {url}: {e}")

