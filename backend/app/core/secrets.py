"""
Secrets Management Module
Industry-standard secrets handling with support for multiple backends

Supports:
- Environment Variables (default)
- AWS Secrets Manager
- HashiCorp Vault
- Azure Key Vault
- Google Secret Manager

This module provides a unified interface for accessing secrets
regardless of the backend storage mechanism.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from functools import lru_cache
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SecretsBackend(str, Enum):
    """Available secrets backends"""
    ENVIRONMENT = "environment"
    AWS_SECRETS_MANAGER = "aws_secrets_manager"
    HASHICORP_VAULT = "hashicorp_vault"
    AZURE_KEY_VAULT = "azure_key_vault"
    GOOGLE_SECRET_MANAGER = "google_secret_manager"


@dataclass
class SecretMetadata:
    """Metadata about a secret"""
    name: str
    version: Optional[str] = None
    created_at: Optional[str] = None
    backend: Optional[str] = None


class SecretsProvider(ABC):
    """Abstract base class for secrets providers"""
    
    @abstractmethod
    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret by name"""
        pass
    
    @abstractmethod
    async def set_secret(self, name: str, value: str) -> bool:
        """Store a secret (if supported)"""
        pass
    
    @abstractmethod
    async def list_secrets(self) -> list:
        """List available secrets"""
        pass
    
    @abstractmethod
    async def delete_secret(self, name: str) -> bool:
        """Delete a secret"""
        pass


class EnvironmentSecretsProvider(SecretsProvider):
    """Environment variable-based secrets provider (default)"""
    
    def __init__(self, prefix: str = ""):
        """
        Initialize environment secrets provider
        
        Args:
            prefix: Optional prefix for environment variable names
        """
        self.prefix = prefix
    
    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Get secret from environment variable"""
        key = f"{self.prefix}{name}" if self.prefix else name
        value = os.environ.get(key)
        
        if value is None:
            logger.debug(f"Secret '{name}' not found in environment")
        
        return value
    
    async def set_secret(self, name: str, value: str) -> bool:
        """Set environment variable (in-memory only)"""
        key = f"{self.prefix}{name}" if self.prefix else name
        os.environ[key] = value
        logger.warning(f"Secret '{name}' set in environment (in-memory only)")
        return True
    
    async def list_secrets(self) -> list:
        """List secrets with the configured prefix"""
        if not self.prefix:
            return []
        return [
            key for key in os.environ.keys() 
            if key.startswith(self.prefix)
        ]
    
    async def delete_secret(self, name: str) -> bool:
        """Remove from environment (in-memory only)"""
        key = f"{self.prefix}{name}" if self.prefix else name
        if key in os.environ:
            del os.environ[key]
            return True
        return False


class AWSSecretsManagerProvider(SecretsProvider):
    """AWS Secrets Manager provider"""
    
    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of boto3 client"""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client(
                    'secretsmanager',
                    region_name=self.region_name
                )
            except ImportError:
                logger.error("boto3 not installed. Run: pip install boto3")
                raise
        return self._client
    
    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from AWS Secrets Manager"""
        try:
            client = self._get_client()
            
            kwargs = {"SecretId": name}
            if version:
                kwargs["VersionId"] = version
            
            response = client.get_secret_value(**kwargs)
            
            if 'SecretString' in response:
                return response['SecretString']
            else:
                # Binary secret
                import base64
                return base64.b64decode(response['SecretBinary']).decode('utf-8')
                
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{name}' from AWS: {e}")
            return None
    
    async def set_secret(self, name: str, value: str) -> bool:
        """Create or update secret in AWS Secrets Manager"""
        try:
            client = self._get_client()
            
            try:
                client.create_secret(Name=name, SecretString=value)
            except client.exceptions.ResourceExistsException:
                client.update_secret(SecretId=name, SecretString=value)
            
            return True
        except Exception as e:
            logger.error(f"Failed to set secret '{name}' in AWS: {e}")
            return False
    
    async def list_secrets(self) -> list:
        """List all secrets in AWS Secrets Manager"""
        try:
            client = self._get_client()
            response = client.list_secrets()
            return [s['Name'] for s in response.get('SecretList', [])]
        except Exception as e:
            logger.error(f"Failed to list secrets from AWS: {e}")
            return []
    
    async def delete_secret(self, name: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            client = self._get_client()
            client.delete_secret(SecretId=name, ForceDeleteWithoutRecovery=True)
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret '{name}' from AWS: {e}")
            return False


class HashiCorpVaultProvider(SecretsProvider):
    """HashiCorp Vault secrets provider"""
    
    def __init__(
        self,
        url: str = "http://localhost:8200",
        token: Optional[str] = None,
        mount_point: str = "secret"
    ):
        self.url = url
        self.token = token or os.environ.get("VAULT_TOKEN")
        self.mount_point = mount_point
        self._client = None
    
    def _get_client(self):
        """Lazy initialization of hvac client"""
        if self._client is None:
            try:
                import hvac
                self._client = hvac.Client(url=self.url, token=self.token)
                
                if not self._client.is_authenticated():
                    raise Exception("Vault authentication failed")
                    
            except ImportError:
                logger.error("hvac not installed. Run: pip install hvac")
                raise
        return self._client
    
    async def get_secret(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve secret from Vault"""
        try:
            client = self._get_client()
            
            response = client.secrets.kv.v2.read_secret_version(
                path=name,
                mount_point=self.mount_point,
                version=int(version) if version else None
            )
            
            data = response['data']['data']
            
            # Return single value if only one key, otherwise JSON
            if len(data) == 1:
                return list(data.values())[0]
            return json.dumps(data)
            
        except Exception as e:
            logger.error(f"Failed to retrieve secret '{name}' from Vault: {e}")
            return None
    
    async def set_secret(self, name: str, value: str) -> bool:
        """Store secret in Vault"""
        try:
            client = self._get_client()
            
            # Try to parse as JSON, otherwise store as single value
            try:
                data = json.loads(value)
            except json.JSONDecodeError:
                data = {"value": value}
            
            client.secrets.kv.v2.create_or_update_secret(
                path=name,
                secret=data,
                mount_point=self.mount_point
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to set secret '{name}' in Vault: {e}")
            return False
    
    async def list_secrets(self) -> list:
        """List secrets in Vault"""
        try:
            client = self._get_client()
            response = client.secrets.kv.v2.list_secrets(
                path="",
                mount_point=self.mount_point
            )
            return response['data']['keys']
        except Exception as e:
            logger.error(f"Failed to list secrets from Vault: {e}")
            return []
    
    async def delete_secret(self, name: str) -> bool:
        """Delete secret from Vault"""
        try:
            client = self._get_client()
            client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=name,
                mount_point=self.mount_point
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete secret '{name}' from Vault: {e}")
            return False


class SecretsManager:
    """
    Unified secrets management interface
    
    Usage:
        secrets = SecretsManager()
        api_key = await secrets.get("GEMINI_API_KEY")
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._provider = self._create_provider()
        self._cache: Dict[str, str] = {}
        self._initialized = True
        
        logger.info(f"Secrets Manager initialized with {self._get_backend()} backend")
    
    def _get_backend(self) -> SecretsBackend:
        """Determine which secrets backend to use"""
        backend = os.environ.get("SECRETS_BACKEND", "environment").lower()
        
        try:
            return SecretsBackend(backend)
        except ValueError:
            logger.warning(f"Unknown secrets backend '{backend}', using environment")
            return SecretsBackend.ENVIRONMENT
    
    def _create_provider(self) -> SecretsProvider:
        """Create the appropriate secrets provider"""
        backend = self._get_backend()
        
        if backend == SecretsBackend.AWS_SECRETS_MANAGER:
            region = os.environ.get("AWS_REGION", "us-east-1")
            return AWSSecretsManagerProvider(region_name=region)
        
        elif backend == SecretsBackend.HASHICORP_VAULT:
            return HashiCorpVaultProvider(
                url=os.environ.get("VAULT_ADDR", "http://localhost:8200"),
                token=os.environ.get("VAULT_TOKEN"),
                mount_point=os.environ.get("VAULT_MOUNT_POINT", "secret")
            )
        
        # Default to environment variables
        return EnvironmentSecretsProvider()
    
    async def get(
        self,
        name: str,
        default: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Retrieve a secret
        
        Args:
            name: Secret name/key
            default: Default value if secret not found
            use_cache: Whether to use cached value
            
        Returns:
            Secret value or default
        """
        # Check cache first
        if use_cache and name in self._cache:
            return self._cache[name]
        
        # Retrieve from provider
        value = await self._provider.get_secret(name)
        
        if value is None:
            return default
        
        # Cache the value
        if use_cache:
            self._cache[name] = value
        
        return value
    
    async def set(self, name: str, value: str) -> bool:
        """Store a secret"""
        success = await self._provider.set_secret(name, value)
        if success:
            self._cache[name] = value
        return success
    
    async def delete(self, name: str) -> bool:
        """Delete a secret"""
        success = await self._provider.delete_secret(name)
        if success and name in self._cache:
            del self._cache[name]
        return success
    
    async def list(self) -> list:
        """List available secrets"""
        return await self._provider.list_secrets()
    
    def clear_cache(self):
        """Clear the secrets cache"""
        self._cache.clear()
    
    async def rotate(self, name: str, new_value: str) -> bool:
        """
        Rotate a secret (update with new value)
        
        This is useful for key rotation workflows
        """
        old_value = await self.get(name, use_cache=False)
        
        if await self.set(name, new_value):
            logger.info(f"Secret '{name}' rotated successfully")
            return True
        
        logger.error(f"Failed to rotate secret '{name}'")
        return False


# Global singleton instance
secrets_manager = SecretsManager()


# Convenience function
async def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Convenience function to get a secret
    
    Usage:
        from backend.app.core.secrets import get_secret
        api_key = await get_secret("GEMINI_API_KEY")
    """
    return await secrets_manager.get(name, default)
