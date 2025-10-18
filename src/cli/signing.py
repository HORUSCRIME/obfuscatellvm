#!/usr/bin/env python3
"""Build signing and manifest verification for ObfuscateLLVM."""

import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature


class BuildSigner:
    """Handles build signing and manifest generation."""
    
    def __init__(self, private_key_path: Optional[str] = None):
        self.private_key = None
        self.public_key = None
        
        if private_key_path and Path(private_key_path).exists():
            self.load_private_key(private_key_path)
        else:
            self.generate_key_pair()
    
    def generate_key_pair(self):
        """Generate RSA key pair for signing."""
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()
    
    def load_private_key(self, key_path: str, password: Optional[bytes] = None):
        """Load private key from file."""
        with open(key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=password
            )
        self.public_key = self.private_key.public_key()
    
    def save_keys(self, private_path: str, public_path: str):
        """Save key pair to files."""
        # Save private key
        private_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(private_path, 'wb') as f:
            f.write(private_pem)
        
        # Save public key
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(public_path, 'wb') as f:
            f.write(public_pem)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def create_manifest(self, 
                       input_file: str, 
                       output_file: str, 
                       config: Dict[str, Any],
                       watermark: Optional[str] = None) -> Dict[str, Any]:
        """Create obfuscation manifest."""
        
        manifest = {
            "version": "1.0.0",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "input": {
                "file": input_file,
                "hash": self.calculate_file_hash(input_file),
                "size": Path(input_file).stat().st_size
            },
            "output": {
                "file": output_file,
                "hash": self.calculate_file_hash(output_file) if Path(output_file).exists() else None,
                "size": Path(output_file).stat().st_size if Path(output_file).exists() else 0
            },
            "configuration": config,
            "watermark": watermark,
            "tool_version": "ObfuscateLLVM-1.0.0"
        }
        
        return manifest
    
    def sign_manifest(self, manifest: Dict[str, Any]) -> str:
        """Sign manifest with private key."""
        if not self.private_key:
            raise ValueError("No private key available for signing")
        
        # Convert manifest to canonical JSON
        manifest_json = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
        manifest_bytes = manifest_json.encode('utf-8')
        
        # Sign the manifest
        signature = self.private_key.sign(
            manifest_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature.hex()
    
    def verify_manifest(self, manifest: Dict[str, Any], signature: str, public_key_path: str) -> bool:
        """Verify manifest signature."""
        try:
            # Load public key
            with open(public_key_path, 'rb') as f:
                public_key = serialization.load_pem_public_key(f.read())
            
            # Convert manifest to canonical JSON
            manifest_json = json.dumps(manifest, sort_keys=True, separators=(',', ':'))
            manifest_bytes = manifest_json.encode('utf-8')
            
            # Verify signature
            signature_bytes = bytes.fromhex(signature)
            public_key.verify(
                signature_bytes,
                manifest_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except (InvalidSignature, Exception):
            return False
    
    def create_signed_manifest(self, 
                              input_file: str, 
                              output_file: str, 
                              config: Dict[str, Any],
                              watermark: Optional[str] = None) -> Dict[str, Any]:
        """Create and sign manifest."""
        
        manifest = self.create_manifest(input_file, output_file, config, watermark)
        signature = self.sign_manifest(manifest)
        
        signed_manifest = {
            "manifest": manifest,
            "signature": signature,
            "public_key_fingerprint": self.get_public_key_fingerprint()
        }
        
        return signed_manifest
    
    def get_public_key_fingerprint(self) -> str:
        """Get public key fingerprint for identification."""
        if not self.public_key:
            return ""
        
        public_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return hashlib.sha256(public_pem).hexdigest()[:16]


def embed_watermark(binary_path: str, watermark: str) -> bool:
    """Embed watermark in binary file."""
    try:
        # Simple watermark embedding in a comment section
        watermark_data = f"OBFUSCATE_WATERMARK:{watermark}".encode('utf-8')
        
        with open(binary_path, 'ab') as f:
            f.write(b'\x00' * 16)  # Padding
            f.write(watermark_data)
            f.write(b'\x00' * 16)  # Padding
        
        return True
    except Exception:
        return False


def extract_watermark(binary_path: str) -> Optional[str]:
    """Extract watermark from binary file."""
    try:
        with open(binary_path, 'rb') as f:
            content = f.read()
        
        marker = b"OBFUSCATE_WATERMARK:"
        start = content.find(marker)
        if start == -1:
            return None
        
        start += len(marker)
        end = content.find(b'\x00', start)
        if end == -1:
            return None
        
        return content[start:end].decode('utf-8')
    except Exception:
        return None


if __name__ == "__main__":
    # Test signing functionality
    signer = BuildSigner()
    
    # Create test manifest
    config = {"profile": "balanced", "cycles": 2}
    manifest = signer.create_manifest("test_input.c", "test_output", config, "test@example.com")
    
    # Sign manifest
    signature = signer.sign_manifest(manifest)
    
    print("Manifest created and signed successfully!")
    print(f"Signature: {signature[:32]}...")
    print(f"Public key fingerprint: {signer.get_public_key_fingerprint()}")