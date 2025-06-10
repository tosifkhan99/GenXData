"""
IP-based tracking utility for monitoring API usage and detecting abuse patterns.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class APIUsage:
    """Track API usage for an IP address"""
    ip_address: str
    endpoint: str
    timestamp: datetime
    rows_requested: int = 0
    user_agent: str = ""
    status_code: int = 200

class IPTracker:
    """Track IP usage patterns and detect potential abuse"""
    
    def __init__(self, storage_file: str = "api_usage.json"):
        self.storage_file = storage_file
        self.usage_data: List[APIUsage] = []
        self.load_data()
    
    def load_data(self):
        """Load existing usage data from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.usage_data = [
                        APIUsage(
                            ip_address=item['ip_address'],
                            endpoint=item['endpoint'],
                            timestamp=datetime.fromisoformat(item['timestamp']),
                            rows_requested=item.get('rows_requested', 0),
                            user_agent=item.get('user_agent', ''),
                            status_code=item.get('status_code', 200)
                        ) for item in data
                    ]
            except Exception as e:
                logger.error(f"Error loading usage data: {e}")
                self.usage_data = []
    
    def save_data(self):
        """Save usage data to file"""
        try:
            # Only keep last 30 days of data
            cutoff_date = datetime.now() - timedelta(days=30)
            recent_data = [
                usage for usage in self.usage_data 
                if usage.timestamp > cutoff_date
            ]
            
            # Convert to JSON-serializable format
            data = []
            for usage in recent_data:
                data.append({
                    'ip_address': usage.ip_address,
                    'endpoint': usage.endpoint,
                    'timestamp': usage.timestamp.isoformat(),
                    'rows_requested': usage.rows_requested,
                    'user_agent': usage.user_agent,
                    'status_code': usage.status_code
                })
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.usage_data = recent_data
        except Exception as e:
            logger.error(f"Error saving usage data: {e}")
    
    def log_request(self, ip_address: str, endpoint: str, rows_requested: int = 0, 
                   user_agent: str = "", status_code: int = 200):
        """Log an API request"""
        usage = APIUsage(
            ip_address=ip_address,
            endpoint=endpoint,
            timestamp=datetime.now(),
            rows_requested=rows_requested,
            user_agent=user_agent,
            status_code=status_code
        )
        
        self.usage_data.append(usage)
        
        # Save every 10 requests to avoid too much I/O
        if len(self.usage_data) % 10 == 0:
            self.save_data()
    
    def get_ip_stats(self, ip_address: str, hours: int = 24) -> Dict:
        """Get usage statistics for an IP address"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        ip_requests = [
            usage for usage in self.usage_data 
            if usage.ip_address == ip_address and usage.timestamp > cutoff_time
        ]
        
        total_requests = len(ip_requests)
        total_rows = sum(usage.rows_requested for usage in ip_requests)
        endpoints = {}
        
        for usage in ip_requests:
            endpoints[usage.endpoint] = endpoints.get(usage.endpoint, 0) + 1
        
        return {
            'ip_address': ip_address,
            'total_requests': total_requests,
            'total_rows_generated': total_rows,
            'endpoints_used': endpoints,
            'timeframe_hours': hours,
            'first_request': min(usage.timestamp for usage in ip_requests) if ip_requests else None,
            'last_request': max(usage.timestamp for usage in ip_requests) if ip_requests else None
        }
    
    def is_suspicious_activity(self, ip_address: str) -> Dict:
        """Detect suspicious patterns for an IP address"""
        stats_1h = self.get_ip_stats(ip_address, hours=1)
        stats_24h = self.get_ip_stats(ip_address, hours=24)
        
        suspicious_indicators = []
        
        # Check for high frequency requests
        if stats_1h['total_requests'] > 50:
            suspicious_indicators.append("High request frequency (>50/hour)")
        
        # Check for excessive row generation
        if stats_24h['total_rows_generated'] > 50000:
            suspicious_indicators.append("Excessive data generation (>50k rows/day)")
        
        # Check for rapid-fire requests to expensive endpoints
        expensive_endpoints = ['/generate_and_download', '/generate_data']
        expensive_requests = sum(
            stats_1h['endpoints_used'].get(endpoint, 0) 
            for endpoint in expensive_endpoints
        )
        if expensive_requests > 10:
            suspicious_indicators.append("Too many expensive operations (>10/hour)")
        
        return {
            'is_suspicious': len(suspicious_indicators) > 0,
            'indicators': suspicious_indicators,
            'stats_1h': stats_1h,
            'stats_24h': stats_24h
        }
    
    def get_top_users(self, hours: int = 24, limit: int = 10) -> List[Dict]:
        """Get top users by request count"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        ip_counts = {}
        for usage in self.usage_data:
            if usage.timestamp > cutoff_time:
                ip = usage.ip_address
                if ip not in ip_counts:
                    ip_counts[ip] = {'requests': 0, 'rows': 0}
                ip_counts[ip]['requests'] += 1
                ip_counts[ip]['rows'] += usage.rows_requested
        
        # Sort by request count
        sorted_users = sorted(
            ip_counts.items(), 
            key=lambda x: x[1]['requests'], 
            reverse=True
        )
        
        return [
            {
                'ip_address': ip,
                'requests': data['requests'],
                'rows_generated': data['rows'],
                'avg_rows_per_request': data['rows'] / data['requests'] if data['requests'] > 0 else 0
            }
            for ip, data in sorted_users[:limit]
        ]
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        self.usage_data = [
            usage for usage in self.usage_data 
            if usage.timestamp > cutoff_date
        ]
        self.save_data()

# Global tracker instance
ip_tracker = IPTracker() 