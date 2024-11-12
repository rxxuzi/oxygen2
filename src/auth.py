# auth.py

import json
from world import get_config_path


class AuthManager:
    def __init__(self):
        self.auth_dir = get_config_path() / "auth"
        self.cookies_dir = self.auth_dir / "cookies"
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.pass_file = self.auth_dir / "pass.json"
        self.auth_file = self.auth_dir / "auth.json"
        self.credentials = {}
        self.auth_entries = {}
        self.load_credentials()
        self.load_auth_entries()

    def save_cookies(self, domain, cookie_content):
        cookie_file = self.cookies_dir / f"{domain}.cookie"
        with open(cookie_file, 'w', encoding='utf-8') as f:
            f.write(cookie_content)
        # Update auth.json
        self.auth_entries[domain] = {
            "status": "success",
            "type": "cookie",
            "path": str(cookie_file)
        }
        self.save_auth_entries()
        return True

    def get_cookie_file(self, domain):
        cookie_file = self.cookies_dir / f"{domain}.cookie"
        if cookie_file.exists():
            return str(cookie_file)
        else:
            return None

    def save_credentials(self, domain, username, password):
        self.credentials[domain] = {
            "username": username,
            "password": password,
        }
        self.save_credentials_to_file()
        # Update auth.json
        self.auth_entries[domain] = {
            "status": "success",
            "type": "pass",
        }
        self.save_auth_entries()
        return True

    def get_credentials(self, domain):
        return self.credentials.get(domain)

    def load_credentials(self):
        if self.pass_file.exists():
            with open(self.pass_file, 'r', encoding='utf-8') as f:
                self.credentials = json.load(f)
        else:
            self.credentials = {}

    def save_credentials_to_file(self):
        with open(self.pass_file, 'w', encoding='utf-8') as f:
            json.dump(self.credentials, f, ensure_ascii=False, indent=4)

    def delete_auth(self, domain, auth_type):
        if auth_type == "cookie":
            cookie_file = self.cookies_dir / f"{domain}.cookie"
            if cookie_file.exists():
                cookie_file.unlink()
                if domain in self.auth_entries:
                    del self.auth_entries[domain]
                    self.save_auth_entries()
                return True
        elif auth_type == "pass":
            if domain in self.credentials:
                del self.credentials[domain]
                self.save_credentials_to_file()
                if domain in self.auth_entries:
                    del self.auth_entries[domain]
                    self.save_auth_entries()
                return True
        return False

    def list_auth_entries(self):
        entries = []
        for domain, info in self.auth_entries.items():
            entries.append({
                "domain": domain,
                "type": info["type"],
                "status": info["status"],
                "path": info.get("path", "")
            })
        return entries

    def load_auth_entries(self):
        if self.auth_file.exists():
            with open(self.auth_file, 'r', encoding='utf-8') as f:
                self.auth_entries = json.load(f)
        else:
            self.auth_entries = {}

    def save_auth_entries(self):
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(self.auth_entries, f, ensure_ascii=False, indent=4)
