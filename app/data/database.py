"""
Week 8: Data Pipeline & CRUD (SQL)
Database Manager class for SQLite operations.
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import Optional, List, Tuple, Any
from contextlib import contextmanager

# Import OOP entity classes
from models import (
    User, SecurityIncident, Dataset, ITTicket,
    create_user_from_row, create_incident_from_row,
    create_dataset_from_row, create_ticket_from_row
)


class DatabaseManager:
    """Manages SQLite database connections and CRUD operations."""
    
    def __init__(self, db_path: str = "intelligence_platform.db"):
        """Initialize database manager with path to SQLite database."""
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self) -> None:
        """Initialize database with all required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Cyber Incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cyber_incidents (
                    incident_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    threat_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    assigned_to TEXT,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT,
                    resolution_time_hours REAL,
                    source_ip TEXT,
                    target_system TEXT
                )
            ''')
            
            # Datasets Metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets_metadata (
                    dataset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    source_department TEXT,
                    file_format TEXT,
                    size_mb REAL,
                    row_count INTEGER,
                    column_count INTEGER,
                    uploaded_by TEXT,
                    upload_date TEXT,
                    last_accessed TEXT,
                    quality_score REAL,
                    status TEXT DEFAULT 'Active',
                    storage_location TEXT
                )
            ''')
            
            # IT Tickets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS it_tickets (
                    ticket_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    status TEXT NOT NULL,
                    requester TEXT,
                    assigned_to TEXT,
                    created_at TEXT NOT NULL,
                    first_response_at TEXT,
                    resolved_at TEXT,
                    resolution_time_hours REAL,
                    sla_met TEXT,
                    department TEXT,
                    satisfaction_rating INTEGER
                )
            ''')
            
            conn.commit()
    
    # ==================== USER CRUD ====================
    
    def create_user(self, username: str, password_hash: str, role: str) -> bool:
        """Create a new user."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (username, password_hash, role, datetime.now().isoformat()))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_user(self, username: str) -> Optional[Tuple]:
        """Get user by username."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            return tuple(row) if row else None
    
    def get_all_users(self) -> List[Tuple]:
        """Get all users."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return [tuple(row) for row in cursor.fetchall()]
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Update user fields."""
        if not kwargs:
            return False
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [username]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE users SET {set_clause} WHERE username = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_user(self, username: str) -> bool:
        """Delete a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE username = ?', (username,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ==================== CYBER INCIDENTS CRUD ====================
    
    def create_incident(self, incident_data: dict) -> bool:
        """Create a new security incident."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO cyber_incidents 
                    (incident_id, title, description, threat_type, severity, status,
                     assigned_to, created_at, resolved_at, resolution_time_hours, source_ip, target_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    incident_data.get('incident_id'),
                    incident_data.get('title'),
                    incident_data.get('description'),
                    incident_data.get('threat_type'),
                    incident_data.get('severity'),
                    incident_data.get('status'),
                    incident_data.get('assigned_to'),
                    incident_data.get('created_at'),
                    incident_data.get('resolved_at'),
                    incident_data.get('resolution_time_hours'),
                    incident_data.get('source_ip'),
                    incident_data.get('target_system')
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_incident(self, incident_id: str) -> Optional[Tuple]:
        """Get incident by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cyber_incidents WHERE incident_id = ?', (incident_id,))
            row = cursor.fetchone()
            return tuple(row) if row else None
    
    def get_all_incidents(self) -> List[Tuple]:
        """Get all incidents."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM cyber_incidents ORDER BY created_at DESC')
            return [tuple(row) for row in cursor.fetchall()]
    
    def get_incidents_dataframe(self) -> pd.DataFrame:
        """Get all incidents as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query('SELECT * FROM cyber_incidents ORDER BY created_at DESC', conn)
    
    def update_incident(self, incident_id: str, **kwargs) -> bool:
        """Update incident fields."""
        if not kwargs:
            return False
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [incident_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE cyber_incidents SET {set_clause} WHERE incident_id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_incident(self, incident_id: str) -> bool:
        """Delete an incident."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cyber_incidents WHERE incident_id = ?', (incident_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ==================== DATASETS METADATA CRUD ====================
    
    def create_dataset(self, dataset_data: dict) -> bool:
        """Create a new dataset entry."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO datasets_metadata 
                    (dataset_id, name, description, source_department, file_format, size_mb,
                     row_count, column_count, uploaded_by, upload_date, last_accessed,
                     quality_score, status, storage_location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    dataset_data.get('dataset_id'),
                    dataset_data.get('name'),
                    dataset_data.get('description'),
                    dataset_data.get('source_department'),
                    dataset_data.get('file_format'),
                    dataset_data.get('size_mb'),
                    dataset_data.get('row_count'),
                    dataset_data.get('column_count'),
                    dataset_data.get('uploaded_by'),
                    dataset_data.get('upload_date'),
                    dataset_data.get('last_accessed'),
                    dataset_data.get('quality_score'),
                    dataset_data.get('status', 'Active'),
                    dataset_data.get('storage_location')
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_dataset(self, dataset_id: str) -> Optional[Tuple]:
        """Get dataset by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM datasets_metadata WHERE dataset_id = ?', (dataset_id,))
            row = cursor.fetchone()
            return tuple(row) if row else None
    
    def get_all_datasets(self) -> List[Tuple]:
        """Get all datasets."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM datasets_metadata ORDER BY upload_date DESC')
            return [tuple(row) for row in cursor.fetchall()]
    
    def get_datasets_dataframe(self) -> pd.DataFrame:
        """Get all datasets as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query('SELECT * FROM datasets_metadata ORDER BY upload_date DESC', conn)
    
    def update_dataset(self, dataset_id: str, **kwargs) -> bool:
        """Update dataset fields."""
        if not kwargs:
            return False
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [dataset_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE datasets_metadata SET {set_clause} WHERE dataset_id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM datasets_metadata WHERE dataset_id = ?', (dataset_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ==================== IT TICKETS CRUD ====================
    
    def create_ticket(self, ticket_data: dict) -> bool:
        """Create a new IT ticket."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO it_tickets 
                    (ticket_id, title, description, category, priority, status,
                     requester, assigned_to, created_at, first_response_at, resolved_at,
                     resolution_time_hours, sla_met, department, satisfaction_rating)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticket_data.get('ticket_id'),
                    ticket_data.get('title'),
                    ticket_data.get('description'),
                    ticket_data.get('category'),
                    ticket_data.get('priority'),
                    ticket_data.get('status'),
                    ticket_data.get('requester'),
                    ticket_data.get('assigned_to'),
                    ticket_data.get('created_at'),
                    ticket_data.get('first_response_at'),
                    ticket_data.get('resolved_at'),
                    ticket_data.get('resolution_time_hours'),
                    ticket_data.get('sla_met'),
                    ticket_data.get('department'),
                    ticket_data.get('satisfaction_rating')
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_ticket(self, ticket_id: str) -> Optional[Tuple]:
        """Get ticket by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM it_tickets WHERE ticket_id = ?', (ticket_id,))
            row = cursor.fetchone()
            return tuple(row) if row else None
    
    def get_all_tickets(self) -> List[Tuple]:
        """Get all tickets."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM it_tickets ORDER BY created_at DESC')
            return [tuple(row) for row in cursor.fetchall()]
    
    def get_tickets_dataframe(self) -> pd.DataFrame:
        """Get all tickets as a pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query('SELECT * FROM it_tickets ORDER BY created_at DESC', conn)
    
    def update_ticket(self, ticket_id: str, **kwargs) -> bool:
        """Update ticket fields."""
        if not kwargs:
            return False
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [ticket_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                UPDATE it_tickets SET {set_clause} WHERE ticket_id = ?
            ''', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_ticket(self, ticket_id: str) -> bool:
        """Delete a ticket."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM it_tickets WHERE ticket_id = ?', (ticket_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ==================== DATA MIGRATION & LOADING ====================
    
    def migrate_users_from_file(self, users_file: str = "users.txt") -> int:
        """Migrate users from text file to database (Week 7 -> Week 8)."""
        if not os.path.exists(users_file):
            return 0
        
        migrated = 0
        with open(users_file, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:  # Skip header
                line = line.strip()
                if line:
                    parts = line.split('|')
                    if len(parts) >= 4:
                        if self.create_user(parts[0], parts[1], parts[2]):
                            migrated += 1
        return migrated
    
    def load_csv_data(self, csv_path: str, table_name: str) -> int:
        """Load data from CSV file into specified table."""
        if not os.path.exists(csv_path):
            return 0
        
        df = pd.read_csv(csv_path)
        
        with self.get_connection() as conn:
            # Clear existing data
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table_name}')
            
            # Insert new data
            df.to_sql(table_name, conn, if_exists='append', index=False)
            conn.commit()
            
        return len(df)
    
    def load_all_sample_data(self, data_dir: str = "data") -> dict:
        """Load all sample CSV data into the database."""
        results = {}
        
        csv_mappings = {
            'cyber_incidents.csv': 'cyber_incidents',
            'datasets_metadata.csv': 'datasets_metadata',
            'it_tickets.csv': 'it_tickets'
        }
        
        for csv_file, table_name in csv_mappings.items():
            csv_path = os.path.join(data_dir, csv_file)
            if os.path.exists(csv_path):
                count = self.load_csv_data(csv_path, table_name)
                results[table_name] = count
            else:
                results[table_name] = 0
        
        return results
    
    # ==================== OOP ENTITY METHODS ====================
    # These methods return proper OOP entity objects instead of raw tuples
    
    def get_user_object(self, username: str) -> Optional[User]:
        """Get user as OOP User object."""
        row = self.get_user(username)
        if row:
            return create_user_from_row(row)
        return None
    
    def get_all_users_objects(self) -> List[User]:
        """Get all users as OOP User objects."""
        rows = self.get_all_users()
        return [create_user_from_row(row) for row in rows]
    
    def get_incident_object(self, incident_id: str) -> Optional[SecurityIncident]:
        """Get incident as OOP SecurityIncident object."""
        row = self.get_incident(incident_id)
        if row:
            return create_incident_from_row(row)
        return None
    
    def get_all_incidents_objects(self) -> List[SecurityIncident]:
        """Get all incidents as OOP SecurityIncident objects."""
        rows = self.get_all_incidents()
        return [create_incident_from_row(row) for row in rows]
    
    def get_dataset_object(self, dataset_id: str) -> Optional[Dataset]:
        """Get dataset as OOP Dataset object."""
        row = self.get_dataset(dataset_id)
        if row:
            return create_dataset_from_row(row)
        return None
    
    def get_all_datasets_objects(self) -> List[Dataset]:
        """Get all datasets as OOP Dataset objects."""
        rows = self.get_all_datasets()
        return [create_dataset_from_row(row) for row in rows]
    
    def get_ticket_object(self, ticket_id: str) -> Optional[ITTicket]:
        """Get ticket as OOP ITTicket object."""
        row = self.get_ticket(ticket_id)
        if row:
            return create_ticket_from_row(row)
        return None
    
    def get_all_tickets_objects(self) -> List[ITTicket]:
        """Get all tickets as OOP ITTicket objects."""
        rows = self.get_all_tickets()
        return [create_ticket_from_row(row) for row in rows]
    
    # ==================== ANALYTICS QUERIES ====================
    
    def get_incident_stats(self) -> dict:
        """Get cybersecurity incident statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total incidents
            cursor.execute('SELECT COUNT(*) FROM cyber_incidents')
            total = cursor.fetchone()[0]
            
            # By status
            cursor.execute('SELECT status, COUNT(*) FROM cyber_incidents GROUP BY status')
            by_status = dict(cursor.fetchall())
            
            # By severity
            cursor.execute('SELECT severity, COUNT(*) FROM cyber_incidents GROUP BY severity')
            by_severity = dict(cursor.fetchall())
            
            # By threat type
            cursor.execute('SELECT threat_type, COUNT(*) FROM cyber_incidents GROUP BY threat_type')
            by_threat = dict(cursor.fetchall())
            
            # Average resolution time
            cursor.execute('SELECT AVG(resolution_time_hours) FROM cyber_incidents WHERE resolved_at IS NOT NULL')
            avg_resolution = cursor.fetchone()[0] or 0
            
            return {
                'total': total,
                'by_status': by_status,
                'by_severity': by_severity,
                'by_threat_type': by_threat,
                'avg_resolution_hours': round(avg_resolution, 2)
            }
    
    def get_dataset_stats(self) -> dict:
        """Get dataset catalog statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total datasets
            cursor.execute('SELECT COUNT(*) FROM datasets_metadata')
            total = cursor.fetchone()[0]
            
            # Total size
            cursor.execute('SELECT SUM(size_mb) FROM datasets_metadata')
            total_size = cursor.fetchone()[0] or 0
            
            # By department
            cursor.execute('SELECT source_department, COUNT(*), SUM(size_mb) FROM datasets_metadata GROUP BY source_department')
            by_dept = {row[0]: {'count': row[1], 'size_mb': row[2]} for row in cursor.fetchall()}
            
            # By status
            cursor.execute('SELECT status, COUNT(*) FROM datasets_metadata GROUP BY status')
            by_status = dict(cursor.fetchall())
            
            # Average quality score
            cursor.execute('SELECT AVG(quality_score) FROM datasets_metadata')
            avg_quality = cursor.fetchone()[0] or 0
            
            return {
                'total': total,
                'total_size_mb': round(total_size, 2),
                'total_size_gb': round(total_size / 1024, 2),
                'by_department': by_dept,
                'by_status': by_status,
                'avg_quality_score': round(avg_quality, 2)
            }
    
    def get_ticket_stats(self) -> dict:
        """Get IT ticket statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total tickets
            cursor.execute('SELECT COUNT(*) FROM it_tickets')
            total = cursor.fetchone()[0]
            
            # By status
            cursor.execute('SELECT status, COUNT(*) FROM it_tickets GROUP BY status')
            by_status = dict(cursor.fetchall())
            
            # By category
            cursor.execute('SELECT category, COUNT(*) FROM it_tickets GROUP BY category')
            by_category = dict(cursor.fetchall())
            
            # By assigned technician
            cursor.execute('SELECT assigned_to, COUNT(*), AVG(resolution_time_hours) FROM it_tickets GROUP BY assigned_to')
            by_assignee = {row[0]: {'count': row[1], 'avg_resolution': round(row[2] or 0, 2)} for row in cursor.fetchall()}
            
            # SLA compliance
            cursor.execute("SELECT COUNT(*) FROM it_tickets WHERE sla_met = 'Yes'")
            sla_met = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM it_tickets WHERE sla_met IS NOT NULL")
            sla_total = cursor.fetchone()[0]
            
            # Average resolution time
            cursor.execute('SELECT AVG(resolution_time_hours) FROM it_tickets WHERE resolved_at IS NOT NULL')
            avg_resolution = cursor.fetchone()[0] or 0
            
            return {
                'total': total,
                'by_status': by_status,
                'by_category': by_category,
                'by_assignee': by_assignee,
                'sla_compliance': round(sla_met / sla_total * 100, 2) if sla_total > 0 else 0,
                'avg_resolution_hours': round(avg_resolution, 2)
            }


def cli_main():
    """Command-line interface for database operations."""
    db = DatabaseManager()
    
    print("=" * 50)
    print("  Multi-Domain Intelligence Platform")
    print("  Database Manager (Week 8)")
    print("=" * 50)
    
    while True:
        print("\n1. Load sample data from CSV files")
        print("2. Migrate users from users.txt")
        print("3. View incident statistics")
        print("4. View dataset statistics")
        print("5. View ticket statistics")
        print("6. List all incidents")
        print("7. List all datasets")
        print("8. List all tickets")
        print("9. Exit")
        
        choice = input("\nEnter choice (1-9): ").strip()
        
        if choice == '1':
            results = db.load_all_sample_data()
            print("\n✓ Data loaded successfully:")
            for table, count in results.items():
                print(f"  • {table}: {count} records")
                
        elif choice == '2':
            count = db.migrate_users_from_file()
            print(f"\n✓ Migrated {count} users from users.txt")
            
        elif choice == '3':
            stats = db.get_incident_stats()
            print("\n--- Cybersecurity Incident Statistics ---")
            print(f"Total incidents: {stats['total']}")
            print(f"By status: {stats['by_status']}")
            print(f"By severity: {stats['by_severity']}")
            print(f"Average resolution time: {stats['avg_resolution_hours']} hours")
            
        elif choice == '4':
            stats = db.get_dataset_stats()
            print("\n--- Dataset Catalog Statistics ---")
            print(f"Total datasets: {stats['total']}")
            print(f"Total size: {stats['total_size_gb']} GB")
            print(f"Average quality score: {stats['avg_quality_score']}")
            
        elif choice == '5':
            stats = db.get_ticket_stats()
            print("\n--- IT Ticket Statistics ---")
            print(f"Total tickets: {stats['total']}")
            print(f"By status: {stats['by_status']}")
            print(f"SLA compliance: {stats['sla_compliance']}%")
            print(f"Average resolution time: {stats['avg_resolution_hours']} hours")
            
        elif choice == '6':
            incidents = db.get_all_incidents()
            print(f"\n--- All Incidents ({len(incidents)}) ---")
            for inc in incidents[:10]:
                print(f"  {inc[0]}: {inc[1]} [{inc[4]}] - {inc[5]}")
            if len(incidents) > 10:
                print(f"  ... and {len(incidents) - 10} more")
                
        elif choice == '7':
            datasets = db.get_all_datasets()
            print(f"\n--- All Datasets ({len(datasets)}) ---")
            for ds in datasets[:10]:
                print(f"  {ds[0]}: {ds[1]} [{ds[5]} MB] - {ds[12]}")
            if len(datasets) > 10:
                print(f"  ... and {len(datasets) - 10} more")
                
        elif choice == '8':
            tickets = db.get_all_tickets()
            print(f"\n--- All Tickets ({len(tickets)}) ---")
            for tkt in tickets[:10]:
                print(f"  {tkt[0]}: {tkt[1]} [{tkt[4]}] - {tkt[5]}")
            if len(tickets) > 10:
                print(f"  ... and {len(tickets) - 10} more")
                
        elif choice == '9':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please enter 1-9.")


if __name__ == "__main__":
    cli_main()

