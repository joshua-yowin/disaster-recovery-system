"""Tkinter GUI Dashboard for Disaster Recovery Monitoring"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path
import psutil
import datetime
import threading
import time


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

from backup import BackupSystem
from restore import RestoreSystem


class DisasterRecoveryDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ Disaster Recovery Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg="#667eea")
        
        # Initialize systems
        self.backup_system = BackupSystem()
        self.restore_system = RestoreSystem()
        
        # Auto-refresh flag
        self.auto_refresh = True
        
        # Create UI
        self.create_header()
        self.create_stats_section()
        self.create_actions_section()
        self.create_backups_section()
        
        # Start auto-refresh
        self.start_auto_refresh()
        
        # Initial data load
        self.refresh_data()
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.root, bg="white", pady=20)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = tk.Label(
            header_frame,
            text="🛡️ Disaster Recovery Dashboard",
            font=("Helvetica", 24, "bold"),
            bg="white",
            fg="#667eea"
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text="Automated Backup & Recovery System - Real-time Monitoring",
            font=("Helvetica", 12),
            bg="white",
            fg="#666"
        )
        subtitle.pack()
        
        self.status_label = tk.Label(
            header_frame,
            text="🟢 System Operational",
            font=("Helvetica", 10, "bold"),
            bg="#c6f6d5",
            fg="#22543d",
            pady=5,
            padx=15
        )
        self.status_label.pack(pady=(10, 0))
    
    def create_stats_section(self):
        """Create statistics cards"""
        stats_frame = tk.Frame(self.root, bg="#667eea")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Configure grid
        for i in range(4):
            stats_frame.columnconfigure(i, weight=1)
        
        # Stat cards
        self.total_backups_label = self.create_stat_card(
            stats_frame, "TOTAL BACKUPS", "--", "backups created", 0
        )
        
        self.storage_used_label = self.create_stat_card(
            stats_frame, "STORAGE USED", "--", "MB", 1
        )
        
        self.last_backup_label = self.create_stat_card(
            stats_frame, "LAST BACKUP", "--", "timestamp", 2
        )
        
        self.system_health_label = self.create_stat_card(
            stats_frame, "SYSTEM HEALTH", "100%", "all systems operational", 3
        )
    
    def create_stat_card(self, parent, title, value, label, column):
        """Create a statistics card"""
        card = tk.Frame(parent, bg="white", relief="raised", borderwidth=2)
        card.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")
        
        tk.Label(
            card,
            text=title,
            font=("Helvetica", 9, "bold"),
            bg="white",
            fg="#667eea"
        ).pack(pady=(15, 5))
        
        value_label = tk.Label(
            card,
            text=value,
            font=("Helvetica", 24, "bold"),
            bg="white",
            fg="#333"
        )
        value_label.pack()
        
        tk.Label(
            card,
            text=label,
            font=("Helvetica", 8),
            bg="white",
            fg="#999"
        ).pack(pady=(5, 15))
        
        return value_label
    
    def create_actions_section(self):
        """Create action buttons"""
        actions_frame = tk.Frame(self.root, bg="white", pady=20)
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            actions_frame,
            text="🎮 Quick Actions",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#667eea"
        ).pack(anchor="w", padx=20)
        
        button_frame = tk.Frame(actions_frame, bg="white")
        button_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        # Run Backup Button
        self.backup_btn = tk.Button(
            button_frame,
            text="▶️ Run Backup Now",
            font=("Helvetica", 11, "bold"),
            bg="#48bb78",
            fg="white",
            command=self.run_backup,
            cursor="hand2",
            relief="flat",
            padx=20,
            pady=10
        )
        self.backup_btn.pack(side="left", padx=(0, 10))
        
        # Refresh Button
        tk.Button(
            button_frame,
            text="🔄 Refresh Data",
            font=("Helvetica", 11, "bold"),
            bg="#667eea",
            fg="white",
            command=self.refresh_data,
            cursor="hand2",
            relief="flat",
            padx=20,
            pady=10
        ).pack(side="left", padx=(0, 10))
        
        # Test Disaster Button
        tk.Button(
            button_frame,
            text="💥 Test Disaster Recovery",
            font=("Helvetica", 11, "bold"),
            bg="#f56565",
            fg="white",
            command=self.test_disaster,
            cursor="hand2",
            relief="flat",
            padx=20,
            pady=10
        ).pack(side="left")
    
    def create_backups_section(self):
        """Create backups list section"""
        backups_frame = tk.Frame(self.root, bg="white")
        backups_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        tk.Label(
            backups_frame,
            text="📦 Recent Backups",
            font=("Helvetica", 14, "bold"),
            bg="white",
            fg="#667eea"
        ).pack(anchor="w", padx=20, pady=(20, 10))
        
        # Scrollable frame for backups
        canvas = tk.Canvas(backups_frame, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(backups_frame, orient="vertical", command=canvas.yview)
        self.backups_container = tk.Frame(canvas, bg="white")
        
        self.backups_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.backups_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
        scrollbar.pack(side="right", fill="y", pady=(0, 20))
    
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            # Get statistics
            stats = self.backup_system.get_backup_stats()
            
            # Update stat cards
            self.total_backups_label.config(text=str(stats.get('total_backups', 0)))
            self.storage_used_label.config(text=f"{stats.get('total_size_mb', 0):.2f}")
            self.last_backup_label.config(
                text=stats.get('latest_backup', 'No backups yet')[:20],
                font=("Helvetica", 12, "bold")
            )
            
            # Get backups list
            backups = self.backup_system.list_backups()
            
            # Clear previous backups
            for widget in self.backups_container.winfo_children():
                widget.destroy()
            
            # Display backups
            if not backups:
                no_backups = tk.Label(
                    self.backups_container,
                    text="No backups found. Click 'Run Backup Now' to create your first backup.",
                    font=("Helvetica", 10),
                    bg="#f7fafc",
                    fg="#666",
                    pady=20
                )
                no_backups.pack(fill="x", pady=5)
            else:
                for backup in backups:
                    self.create_backup_item(backup)
            
            self.status_label.config(text="🟢 System Operational", bg="#c6f6d5", fg="#22543d")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data: {str(e)}")
            self.status_label.config(text="🔴 Error Loading Data", bg="#fed7d7", fg="#742a2a")
    
    def create_backup_item(self, backup):
        """Create a backup item in the list"""
        item_frame = tk.Frame(self.backups_container, bg="#f7fafc", relief="solid", borderwidth=1)
        item_frame.pack(fill="x", pady=5, padx=5)
        
        # Info section
        info_frame = tk.Frame(item_frame, bg="#f7fafc")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        tk.Label(
            info_frame,
            text=f"📦 {backup.get('backup_name', 'Unknown')}",
            font=("Helvetica", 11, "bold"),
            bg="#f7fafc",
            fg="#333",
            anchor="w"
        ).pack(anchor="w")
        
        tk.Label(
            info_frame,
            text=f"{backup.get('total_files', 0)} files • {backup.get('total_size_mb', 0):.2f} MB • {backup.get('timestamp', 'Unknown')}",
            font=("Helvetica", 9),
            bg="#f7fafc",
            fg="#666",
            anchor="w"
        ).pack(anchor="w")
        
        # Restore button
        tk.Button(
            item_frame,
            text="♻️ Restore",
            font=("Helvetica", 10, "bold"),
            bg="#667eea",
            fg="white",
            command=lambda: self.restore_backup(backup.get('backup_name')),
            cursor="hand2",
            relief="flat",
            padx=15,
            pady=5
        ).pack(side="right", padx=15)
    
    def run_backup(self):
        """Run backup in background thread"""
        def backup_thread():
            try:
                self.backup_btn.config(state="disabled", text="⏳ Creating backup...")
                self.root.update()
                
                success, backup_name, metadata = self.backup_system.create_backup()
                
                if success:
                    messagebox.showinfo("Success", f"✅ Backup created successfully!\n\n{backup_name}")
                else:
                    messagebox.showerror("Error", "❌ Backup failed!")
                
                self.backup_btn.config(state="normal", text="▶️ Run Backup Now")
                self.refresh_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"❌ Backup failed: {str(e)}")
                self.backup_btn.config(state="normal", text="▶️ Run Backup Now")
        
        threading.Thread(target=backup_thread, daemon=True).start()
    
    def restore_backup(self, backup_name):
        """Restore a backup"""
        if messagebox.askyesno(
            "Confirm Restore",
            f"⚠️ Restore backup: {backup_name}?\n\nThis will overwrite current files."
        ):
            def restore_thread():
                try:
                    success = self.restore_system.restore_backup(backup_name)
                    
                    if success:
                        messagebox.showinfo("Success", "✅ Restore completed successfully!")
                    else:
                        messagebox.showerror("Error", "❌ Restore failed!")
                        
                except Exception as e:
                    messagebox.showerror("Error", f"❌ Restore failed: {str(e)}")
            
            threading.Thread(target=restore_thread, daemon=True).start()
    
    def test_disaster(self):
        """Test disaster recovery"""
        if messagebox.askyesno(
            "Test Disaster",
            "⚠️ This will simulate a disaster scenario and create a backup.\n\nContinue?"
        ):
            messagebox.showinfo("Disaster Simulated", "💥 Disaster simulated! Automatic backup triggered.")
            self.run_backup()
    
    def start_auto_refresh(self):
        """Auto-refresh data every 30 seconds"""
        def auto_refresh_thread():
            while self.auto_refresh:
                time.sleep(30)
                if self.auto_refresh:
                    try:
                        self.root.after(0, self.refresh_data)
                    except:
                        break
        
        threading.Thread(target=auto_refresh_thread, daemon=True).start()
    
    def on_closing(self):
        """Handle window closing"""
        self.auto_refresh = False
        self.root.destroy()


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = DisasterRecoveryDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == '__main__':
    print("=" * 60)
    print("🛡️ Starting Disaster Recovery Dashboard (GUI)")
    print("=" * 60)
    print("📊 Loading Tkinter interface...")
    print("=" * 60)
    main()
