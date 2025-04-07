import requests
from typing import Dict, List, Optional
import random
import time

class ProxyManager:
    def __init__(self, proxy_list: List[str]):
        self.proxies = proxy_list
        self.working_proxies = []
        self.failed_proxies = set()
        self.verify_proxies()
    
    def verify_proxies(self):
        """Test each proxy and build initial working proxy list"""
        for proxy in self.proxies:
            try:
                response = requests.get(
                    'https://httpbin.org/ip',
                    proxies={'http': proxy, 'https': proxy},
                    timeout=10,
                    verify=False  # Disable SSL verification for testing
                )
                if response.status_code == 200:
                    self.working_proxies.append(proxy)
                else:
                    print(f"Proxy {proxy} failed with status code {response.status_code}")
            except Exception as e:
                print(f"Proxy {proxy} failed with error: {e}")
                self.failed_proxies.add(proxy)
                continue
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get working proxy or None if none available"""
        if not self.working_proxies:
            self.verify_proxies()  # Try to recover failed proxies
            if not self.working_proxies:
                return None
                
        proxy = random.choice(self.working_proxies)
        return {
            'http': proxy,
            'https': proxy
        }
    
    def mark_proxy_failed(self, proxy: Dict[str, str]):
        """Mark proxy as failed and remove from working list"""
        if proxy and 'https' in proxy:
            proxy_url = proxy['https']
            if proxy_url in self.working_proxies:
                self.working_proxies.remove(proxy_url)
            self.failed_proxies.add(proxy_url)