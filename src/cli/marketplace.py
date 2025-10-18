#!/usr/bin/env python3
"""Profile marketplace for sharing and downloading obfuscation configurations."""

import json
import requests
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional


class ProfileMarketplace:
    """Handles profile sharing and marketplace operations."""
    
    def __init__(self, base_url: str = "https://api.obfuscatellvm.org"):
        self.base_url = base_url
        self.local_profiles_dir = Path(__file__).parent.parent.parent / "profiles"
        self.cache_dir = Path.home() / ".obfuscatellvm" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def upload_profile(self, profile_path: str, author: str, description: str = "") -> Dict[str, Any]:
        """Upload profile to marketplace."""
        
        profile_file = Path(profile_path)
        if not profile_file.exists():
            raise FileNotFoundError(f"Profile not found: {profile_path}")
        
        with open(profile_file) as f:
            profile_data = json.load(f)
        
        # Calculate profile hash for integrity
        profile_json = json.dumps(profile_data, sort_keys=True)
        profile_hash = hashlib.sha256(profile_json.encode()).hexdigest()
        
        upload_data = {
            "name": profile_file.stem,
            "author": author,
            "description": description or profile_data.get("description", ""),
            "profile": profile_data,
            "hash": profile_hash,
            "version": "1.0.0"
        }
        
        try:
            # Simulate API call (would be real HTTP request in production)
            print(f"Uploading profile '{profile_file.stem}' to marketplace...")
            print(f"Author: {author}")
            print(f"Hash: {profile_hash[:16]}...")
            
            # In real implementation, this would be:
            # response = requests.post(f"{self.base_url}/profiles", json=upload_data)
            # return response.json()
            
            return {
                "success": True,
                "profile_id": f"mp_{profile_file.stem}_{profile_hash[:8]}",
                "message": "Profile uploaded successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def download_profile(self, profile_id: str, install: bool = True) -> Dict[str, Any]:
        """Download profile from marketplace."""
        
        try:
            # Simulate API call
            print(f"Downloading profile: {profile_id}")
            
            # Mock profile data
            mock_profiles = {
                "enterprise_secure": {
                    "name": "enterprise_secure",
                    "description": "Enterprise-grade security profile",
                    "author": "security_team",
                    "passes": {
                        "string_encryption": True,
                        "junk_insertion": True,
                        "symbol_renaming": True
                    },
                    "config": {
                        "junk_density": 0.15,
                        "cycles": 3,
                        "cfg_flatten": True,
                        "opaque_predicates": True,
                        "virtualize": True
                    }
                },
                "performance_optimized": {
                    "name": "performance_optimized",
                    "description": "Balanced protection with minimal overhead",
                    "author": "perf_team",
                    "passes": {
                        "string_encryption": True,
                        "junk_insertion": True,
                        "symbol_renaming": True
                    },
                    "config": {
                        "junk_density": 0.05,
                        "cycles": 1,
                        "cfg_flatten": False,
                        "opaque_predicates": True,
                        "virtualize": False
                    }
                }
            }
            
            if profile_id not in mock_profiles:
                return {"success": False, "error": "Profile not found"}
            
            profile_data = mock_profiles[profile_id]
            
            if install:
                # Install to local profiles directory
                profile_path = self.local_profiles_dir / f"{profile_id}.json"
                with open(profile_path, 'w') as f:
                    json.dump(profile_data, f, indent=2)
                
                print(f"Profile installed to: {profile_path}")
            
            return {
                "success": True,
                "profile": profile_data,
                "message": f"Profile '{profile_id}' downloaded successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_profiles(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        """Search marketplace profiles."""
        
        # Mock search results
        all_profiles = [
            {
                "id": "enterprise_secure",
                "name": "Enterprise Secure",
                "author": "security_team",
                "description": "Enterprise-grade security profile with maximum protection",
                "category": "security",
                "downloads": 1250,
                "rating": 4.8,
                "tags": ["enterprise", "security", "maximum"]
            },
            {
                "id": "performance_optimized",
                "name": "Performance Optimized",
                "author": "perf_team", 
                "description": "Balanced protection with minimal performance impact",
                "category": "performance",
                "downloads": 890,
                "rating": 4.6,
                "tags": ["performance", "balanced", "minimal-overhead"]
            },
            {
                "id": "mobile_friendly",
                "name": "Mobile Friendly",
                "author": "mobile_dev",
                "description": "Optimized for mobile applications with size constraints",
                "category": "mobile",
                "downloads": 567,
                "rating": 4.4,
                "tags": ["mobile", "size-optimized", "lightweight"]
            },
            {
                "id": "research_experimental",
                "name": "Research Experimental",
                "author": "research_lab",
                "description": "Cutting-edge obfuscation techniques for research",
                "category": "research",
                "downloads": 234,
                "rating": 4.2,
                "tags": ["research", "experimental", "advanced"]
            }
        ]
        
        # Filter by query and category
        results = all_profiles
        
        if query:
            query_lower = query.lower()
            results = [p for p in results if 
                      query_lower in p["name"].lower() or 
                      query_lower in p["description"].lower() or
                      any(query_lower in tag for tag in p["tags"])]
        
        if category:
            results = [p for p in results if p["category"] == category]
        
        return results
    
    def list_installed_profiles(self) -> List[Dict[str, Any]]:
        """List locally installed profiles."""
        
        profiles = []
        
        for profile_file in self.local_profiles_dir.glob("*.json"):
            try:
                with open(profile_file) as f:
                    profile_data = json.load(f)
                
                profiles.append({
                    "name": profile_file.stem,
                    "description": profile_data.get("description", ""),
                    "path": str(profile_file),
                    "source": "marketplace" if profile_file.stem.startswith("mp_") else "builtin"
                })
                
            except Exception as e:
                print(f"Error reading profile {profile_file}: {e}")
        
        return profiles
    
    def remove_profile(self, profile_name: str) -> bool:
        """Remove installed profile."""
        
        profile_path = self.local_profiles_dir / f"{profile_name}.json"
        
        if not profile_path.exists():
            return False
        
        # Don't allow removal of builtin profiles
        builtin_profiles = {"minimal", "balanced", "maximum", "av-safe"}
        if profile_name in builtin_profiles:
            print(f"Cannot remove builtin profile: {profile_name}")
            return False
        
        try:
            profile_path.unlink()
            print(f"Profile '{profile_name}' removed successfully")
            return True
        except Exception as e:
            print(f"Error removing profile: {e}")
            return False


def main():
    """CLI interface for marketplace operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ObfuscateLLVM Profile Marketplace")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload profile to marketplace')
    upload_parser.add_argument('profile', help='Path to profile file')
    upload_parser.add_argument('--author', required=True, help='Author name')
    upload_parser.add_argument('--description', help='Profile description')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download profile from marketplace')
    download_parser.add_argument('profile_id', help='Profile ID to download')
    download_parser.add_argument('--no-install', action='store_true', help='Download without installing')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search marketplace profiles')
    search_parser.add_argument('--query', help='Search query')
    search_parser.add_argument('--category', help='Filter by category')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List installed profiles')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove installed profile')
    remove_parser.add_argument('profile_name', help='Profile name to remove')
    
    args = parser.parse_args()
    marketplace = ProfileMarketplace()
    
    if args.command == 'upload':
        result = marketplace.upload_profile(args.profile, args.author, args.description or "")
        print(json.dumps(result, indent=2))
    
    elif args.command == 'download':
        result = marketplace.download_profile(args.profile_id, not args.no_install)
        print(json.dumps(result, indent=2))
    
    elif args.command == 'search':
        results = marketplace.search_profiles(args.query or "", args.category or "")
        print(f"Found {len(results)} profiles:")
        for profile in results:
            print(f"  {profile['id']}: {profile['name']} by {profile['author']}")
            print(f"    {profile['description']}")
            print(f"    Downloads: {profile['downloads']}, Rating: {profile['rating']}")
            print()
    
    elif args.command == 'list':
        profiles = marketplace.list_installed_profiles()
        print(f"Installed profiles ({len(profiles)}):")
        for profile in profiles:
            print(f"  {profile['name']}: {profile['description']} [{profile['source']}]")
    
    elif args.command == 'remove':
        success = marketplace.remove_profile(args.profile_name)
        if not success:
            exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()