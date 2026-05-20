import requests
from typing import Dict, Any, Optional

class ClouDNSClient:
    """
    Low-level API client for ClouDNS. Handles request authentication,
    methods (GET/POST), and error handling.
    """
    def __init__(self, auth_id: str, auth_password: str, api_base_url: str = "https://api.cloudns.net/"):
        self.auth_id = auth_id
        self.auth_password = auth_password
        self.api_base_url = api_base_url.rstrip("/")

    def request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sends an HTTP request to ClouDNS API.
        Authentication details are automatically appended to each request.
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        
        # Build authentication payload
        payload = {
            "auth-id": self.auth_id,
            "auth-password": self.auth_password
        }
        
        if params:
            payload.update(params)
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=payload, timeout=15)
            else:
                # ClouDNS API expects POST data as application/x-www-form-urlencoded
                if data:
                    payload.update(data)
                response = requests.post(url, data=payload, timeout=15)
                
            response.raise_for_status()
            
            try:
                res_json = response.json()
            except ValueError:
                # Fallback for non-JSON responses
                return {"success": True, "raw": True, "data": response.text}
                
            # Check for API level failures
            if isinstance(res_json, dict) and res_json.get("status") == "Failed":
                return {"success": False, "message": res_json.get("statusDescription", "未知API错误")}
                
            return {"success": True, "data": res_json}
            
        except Exception as e:
            return {"success": False, "message": f"网络或系统异常: {str(e)}"}
