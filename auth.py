"""
Week 7: Security & File Persistence (Hashing)
Authentication module with bcrypt password hashing and file-based storage.
"""

import bcrypt
import os
from datetime import datetime


class AuthManager:
    """Handles user authentication with secure password hashing."""
    
    def __init__(self, users_file: str = "users.txt"):
        """Initialize AuthManager with the path to users file."""
        self.users_file = users_file
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create the users file if it doesn't exist."""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                # Write header
                f.write("username|password_hash|role|created_at\n")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt with automatic salt generation.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password as string
        """
        # Generate salt and hash the password
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored hash to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def _read_users(self) -> dict:
        """
        Read all users from the file.
        
        Returns:
            Dictionary of username -> user data
        """
        users = {}
        try:
            with open(self.users_file, 'r') as f:
                lines = f.readlines()
                # Skip header
                for line in lines[1:]:
                    line = line.strip()
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 4:
                            username = parts[0]
                            users[username] = {
                                'username': username,
                                'password_hash': parts[1],
                                'role': parts[2],
                                'created_at': parts[3]
                            }
        except FileNotFoundError:
            self._ensure_file_exists()
        return users
    
    def _write_user(self, username: str, password_hash: str, role: str) -> None:
        """
        Append a new user to the file.
        
        Args:
            username: User's username
            password_hash: Hashed password
            role: User's role (admin, cybersecurity, datascience, it_operations)
        """
        created_at = datetime.now().isoformat()
        with open(self.users_file, 'a') as f:
            f.write(f"{username}|{password_hash}|{role}|{created_at}\n")
    
    def register_user(self, username: str, password: str, role: str) -> tuple[bool, str]:
        """
        Register a new user with secure password hashing.
        
        Args:
            username: Desired username
            password: Plain text password
            role: User role (admin, cybersecurity, datascience, it_operations)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Validate inputs
        if not username or not password:
            return False, "Username and password are required."
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        
        valid_roles = ['admin', 'cybersecurity', 'datascience', 'it_operations']
        if role not in valid_roles:
            return False, f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        
        # Check if user already exists
        users = self._read_users()
        if username in users:
            return False, "Username already exists."
        
        # Hash password and store user
        password_hash = self.hash_password(password)
        self._write_user(username, password_hash, role)
        
        return True, f"User '{username}' registered successfully with role '{role}'."
    
    def login(self, username: str, password: str) -> tuple[bool, str, dict | None]:
        """
        Authenticate a user.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Tuple of (success: bool, message: str, user_data: dict or None)
        """
        users = self._read_users()
        
        if username not in users:
            return False, "Invalid username or password.", None
        
        user = users[username]
        if self.verify_password(password, user['password_hash']):
            return True, f"Welcome, {username}!", user
        else:
            return False, "Invalid username or password.", None
    
    def get_user(self, username: str) -> dict | None:
        """Get user data by username."""
        users = self._read_users()
        return users.get(username)
    
    def get_all_users(self) -> list[dict]:
        """Get all users (without password hashes for security)."""
        users = self._read_users()
        return [
            {
                'username': u['username'],
                'role': u['role'],
                'created_at': u['created_at']
            }
            for u in users.values()
        ]


def cli_main():
    """Command-line interface for testing authentication."""
    auth = AuthManager()
    
    print("=" * 50)
    print("  Multi-Domain Intelligence Platform")
    print("  Authentication System (Week 7)")
    print("=" * 50)
    
    while True:
        print("\n1. Register new user")
        print("2. Login")
        print("3. List all users")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            print("\n--- User Registration ---")
            username = input("Username: ").strip()
            password = input("Password (min 8 chars): ").strip()
            print("\nAvailable roles: admin, cybersecurity, datascience, it_operations")
            role = input("Role: ").strip().lower()
            
            success, message = auth.register_user(username, password, role)
            print(f"\n{'✓' if success else '✗'} {message}")
            
        elif choice == '2':
            print("\n--- User Login ---")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            
            success, message, user = auth.login(username, password)
            print(f"\n{'✓' if success else '✗'} {message}")
            if success and user:
                print(f"   Role: {user['role']}")
            
        elif choice == '3':
            print("\n--- Registered Users ---")
            users = auth.get_all_users()
            if users:
                for user in users:
                    print(f"  • {user['username']} ({user['role']}) - Created: {user['created_at'][:10]}")
            else:
                print("  No users registered yet.")
            
        elif choice == '4':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1-4.")


if __name__ == "__main__":
    cli_main()

