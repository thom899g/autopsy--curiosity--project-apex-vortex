"""
Firebase Firestore integration for state persistence and real-time data management.
Implements CRITICAL ecosystem rule: Firebase Priority for all state management.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List, Union
from pathlib import Path

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1.base_client import BaseClient
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("firebase-admin not installed. State persistence will be limited.")

class FirebaseHandler:
    """Robust Firebase Firestore handler with error recovery and connection management."""
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        """
        Initialize Firebase connection with proper error handling.
        
        Args:
            project_id: Firebase project ID from environment
            credentials_path: Path to Firebase service account credentials
            
        Raises:
            FileNotFoundError: If credentials file doesn't exist
            ValueError: If Firebase admin initialization fails
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin package not installed. Install with: pip install firebase-admin")
            
        self.project_id = project_id
        self.credentials_path = credentials_path
        self._client: Optional[BaseClient] = None
        self._initialized = False
        
        self._initialize_firebase()
        
    def _initialize_firebase(self) -> None:
        """Initialize Firebase app with proper error handling and validation."""
        try:
            # Verify credentials file exists if provided
            if self.credentials_path:
                cred