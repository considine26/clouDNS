from typing import Dict, Any, List, Optional
from core.api_client import ClouDNSClient

class DNSManager:
    """
    Manages DNS records for ClouDNS master zones.
    """
    def __init__(self, client: ClouDNSClient):
        self.client = client

    def list_records(self, domain_name: str, record_type: Optional[str] = None, host: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieves the DNS record list for a given domain.
        """
        params = {"domain-name": domain_name}
        if record_type:
            params["type"] = record_type.upper()
        if host:
            params["host"] = host

        res = self.client.request("GET", "dns/records.json", params=params)
        
        if res["success"]:
            records_data = res["data"]
            records_list = []
            
            # ClouDNS API returns records as an indexed dictionary (e.g. {"1": {...}, "2": {...}})
            if isinstance(records_data, dict):
                # Extra check in case there was a success true but contains failed status
                if records_data.get("status") == "Failed":
                    return {"success": False, "message": records_data.get("statusDescription", "加载失败")}
                
                for key, val in records_data.items():
                    if isinstance(val, dict) and "id" in val:
                        records_list.append(val)
            elif isinstance(records_data, list):
                records_list = records_data
                
            return {"success": True, "records": records_list}
            
        return res

    def add_record(self, domain_name: str, record_type: str, host: str, record: str, ttl: int = 3600, priority: Optional[int] = None) -> Dict[str, Any]:
        """
        Adds a new DNS resource record.
        """
        data = {
            "domain-name": domain_name,
            "record-type": record_type.upper(),
            "host": host,
            "record": record,
            "ttl": ttl
        }
        if priority is not None:
            data["priority"] = priority

        return self.client.request("POST", "dns/add-record.json", data=data)

    def modify_record(self, domain_name: str, record_id: str, host: str, record: str, ttl: int = 3600, priority: Optional[int] = None) -> Dict[str, Any]:
        """
        Modifies an existing DNS resource record.
        """
        data = {
            "domain-name": domain_name,
            "record-id": record_id,
            "host": host,
            "record": record,
            "ttl": ttl
        }
        if priority is not None:
            data["priority"] = priority

        return self.client.request("POST", "dns/mod-record.json", data=data)

    def delete_record(self, domain_name: str, record_id: str) -> Dict[str, Any]:
        """
        Deletes a DNS record by ID.
        """
        data = {
            "domain-name": domain_name,
            "record-id": record_id
        }
        return self.client.request("POST", "dns/delete-record.json", data=data)
