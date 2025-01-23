import time
import requests
from requests import Session
from .config import BACKEND_API_AUTH_URL, BACKEND_API_URL, API_USERNAME, API_PASSWORD

class BackendClient(Session):
    AUTH_URL = BACKEND_API_AUTH_URL
    BASE_API_URL = BACKEND_API_URL

    def __init__(self):
        super().__init__()
        self.token = None
        self.token_expires_at = 0
        self.refresh_threshold = 30

        # Credentials from environment
        self.username = API_USERNAME
        self.password = API_PASSWORD

    def _authenticate(self):
        """Obtain a new token from the auth endpoint."""
        response = requests.post(self.AUTH_URL, data={
            "username": self.username,
            "password": self.password
        })
        
        response.raise_for_status()
        data = response.json()

        self.token = data["access_token"]
        expires_in = data["expires_in"]
        self.token_expires_at = int(time.time()) + expires_in

    def _ensure_valid_token(self):
        """Refresh the token if it's missing or about to expire."""
        now = time.time()
        if (not self.token) or (now > self.token_expires_at - self.refresh_threshold):
            self._authenticate()

    def request(self, method, url, **kwargs):
        """Override to add Bearer token and handle 401 re-auth."""
        self._ensure_valid_token()

        # Build full URL if not absolute
        if not url.startswith("http"):
            url = f"{self.BASE_API_URL.rstrip('/')}/{url.lstrip('/')}"
        
        # Inject auth header
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.token}"
        kwargs["headers"] = headers

        # Perform the request
        response = super().request(method, url, **kwargs)

        # If token was invalid, try refreshing once and retry
        if response.status_code == 401:
            self._authenticate()
            headers["Authorization"] = f"Bearer {self.token}"
            response = super().request(method, url, **kwargs)

        return response
    
    def check_document_hash(self, doc_hash: str):
        """
        Call the endpoint: GET /api/v1/document/hash/{doc_hash}
        Return a json with a boolean value.
        Raises HTTPError if status code != 200.
        """
        endpoint = f"/document/hash/{doc_hash}"  

        response = self.get(endpoint)
        if response.status_code == 404:
            return {'exists': False}
        return response.json()
    
    def create_document(self, doc_data: dict):
        """
        Call the endpoint: POST /api/v1/document
        Returns the JSON response as a Python dictionary (or list).
        Raises HTTPError if status code != 201.
        """
        endpoint = "/document"
        response = self.post(endpoint, json=doc_data)
        response.raise_for_status()
        return response.json()
    
    def update_document_by_hash(self, doc_hash: str, doc_data: dict):
        """
        Call the endpoint: PUT /api/v1/document/hash/{doc_hash}
        Returns the JSON response as a Python dictionary (or list).
        Raises HTTPError if status code != 200.
        """
        endpoint = f"/document/hash/{doc_hash}"
        response = self.put(endpoint, json=doc_data)
        response.raise_for_status()
        return response.json()