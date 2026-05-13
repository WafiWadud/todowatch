import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import time
import os


class TodoMonitor:
    def __init__(self, root: tk.Tk):
        self.root: tk.Tk = root
        self.root.title("TODO/FIXME Monitor")
        self.root.geometry("900x600")

        self.directory: str | None = None
        self.monitoring = False
        self.monitor_thread: threading.Thread | None = None
        self.file_timestamps: dict[str, float] = {}
        self.ignore_patterns: list[str] = [
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".next",
            ".nuxt",
            "target",
            "vendor",
        ]

        self.setup_ui()

    def setup_ui(self):
        # Top frame for controls
        control_frame: ttk.Frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)

        # Directory selection
        ttk.Label(control_frame, text="Directory:").pack(side=tk.LEFT, padx=5)

        self.dir_label: ttk.Label = ttk.Label(
            control_frame, text="No directory selected", relief=tk.SUNKEN, width=50
        )
        self.dir_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Browse", command=self.select_directory).pack(
            side=tk.LEFT, padx=5
        )

        self.toggle_btn: ttk.Button = ttk.Button(
            control_frame, text="Start Monitoring", command=self.toggle_monitoring
        )
        self.toggle_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="Refresh", command=self.scan_todos).pack(
            side=tk.LEFT, padx=5
        )

        ttk.Button(
            control_frame, text="Ignore List", command=self.show_ignore_list
        ).pack(side=tk.LEFT, padx=5)

        # Status label
        status_frame: ttk.Frame = ttk.Frame(self.root, padding="5")
        status_frame.pack(fill=tk.X)

        self.status_label: ttk.Label = ttk.Label(status_frame, text="Status: Idle")
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.count_label: ttk.Label = ttk.Label(status_frame, text="Total: 0")
        self.count_label.pack(side=tk.LEFT, padx=10)

        # Create treeview with scrollbar
        tree_frame: ttk.Frame = ttk.Frame(self.root, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        vsb: ttk.Scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb: ttk.Scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Treeview
        self.tree: ttk.Treeview = ttk.Treeview(
            tree_frame,
            columns=("Type", "File", "Line", "Content"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure columns
        self.tree.heading("Type", text="Type")
        self.tree.heading("File", text="File")
        self.tree.heading("Line", text="Line")
        self.tree.heading("Content", text="Content")

        self.tree.column("Type", width=80)
        self.tree.column("File", width=250)
        self.tree.column("Line", width=60)
        self.tree.column("Content", width=450)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Tag colors
        self.tree.tag_configure("TODO", foreground="#0066cc")
        self.tree.tag_configure("FIXME", foreground="#cc0000")

        # Double-click to copy
        self.tree.bind("<Double-Button-1>", self.on_double_click)

    def show_ignore_list(self):
        dialog: tk.Toplevel = tk.Toplevel(self.root)
        dialog.title("Ignore List")
        dialog.geometry("400x400")
        dialog.transient(self.root)

        ttk.Label(dialog, text="Ignored directories and patterns:", padding=10).pack()

        # Frame for listbox and scrollbar
        list_frame: ttk.Frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        scrollbar: ttk.Scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        listbox: tk.Listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)

        # Populate listbox
        for pattern in self.ignore_patterns:
            listbox.insert(tk.END, pattern)

        # Entry and buttons frame
        entry_frame: ttk.Frame = ttk.Frame(dialog, padding=10)
        entry_frame.pack(fill=tk.X)

        entry: ttk.Entry = ttk.Entry(entry_frame)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def add_pattern():
            pattern: str = entry.get().strip()
            if pattern and pattern not in self.ignore_patterns:
                self.ignore_patterns.append(pattern)
                listbox.insert(tk.END, pattern)
                entry.delete(0, tk.END)

        def remove_pattern():
            selection: list[str | int] = listbox.curselection()
            if selection:
                idx: str | int = selection[0]
                pattern: str = listbox.get(idx)
                self.ignore_patterns.remove(pattern)
                listbox.delete(idx)

        ttk.Button(entry_frame, text="Add", command=add_pattern).pack(
            side=tk.LEFT, padx=2
        )

        button_frame: ttk.Frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)

        ttk.Button(button_frame, text="Remove Selected", command=remove_pattern).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="Close", command=dialog.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def select_directory(self):
        directory: str = filedialog.askdirectory(title="Select Directory to Monitor")
        if directory:
            self.directory = directory
            self.dir_label.config(text=directory)
            self.file_timestamps.clear()
            self.scan_todos()

    def toggle_monitoring(self):
        if not self.directory:
            messagebox.showwarning("No Directory", "Please select a directory first")
            return

        self.monitoring: bool = not self.monitoring

        if self.monitoring:
            self.toggle_btn.config(text="Stop Monitoring")
            self.status_label.config(text="Status: Monitoring...")
            self.monitor_thread = threading.Thread(
                target=self.monitor_loop, daemon=True
            )
            self.monitor_thread.start()
        else:
            self.toggle_btn.config(text="Start Monitoring")
            self.status_label.config(text="Status: Stopped")

    def monitor_loop(self):
        while self.monitoring:
            if self.check_for_changes():
                self.root.after(0, self.scan_todos)
            time.sleep(2)  # Check every 2 seconds

    def check_for_changes(self):
        if not self.directory:
            return False

        changed: bool = False
        current_timestamps: dict[str, float] = {}

        try:
            for root_dir, dirs, files in os.walk(self.directory):
                # Filter out ignored directories
                dirs[:] = [d for d in dirs if d not in self.ignore_patterns]

                for file in files:
                    filepath: str = os.path.join(root_dir, file)
                    try:
                        mtime: float = os.path.getmtime(filepath)
                        current_timestamps[filepath] = mtime

                        if (
                            filepath not in self.file_timestamps
                            or self.file_timestamps[filepath] != mtime
                        ):
                            changed = True
                    except (OSError, PermissionError):
                        continue

            self.file_timestamps = current_timestamps

        except Exception as e:
            print(f"Error checking timestamps: {e}")

        return changed

    def scan_todos(self):
        if not self.directory:
            return

        self.status_label.config(text="Status: Scanning...")

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            # Build ripgrep command with ignore patterns
            cmd: list[str] = ["rg", "-n", "--no-heading", ".*(TODO|FIXME):.*"]

            # Add glob patterns to exclude ignored directories
            for pattern in self.ignore_patterns:
                cmd.extend(["--glob", f"!{pattern}"])

            cmd.append(self.directory)

            # Run ripgrep command
            result: subprocess.CompletedProcess[str] = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10
            )

            lines: list[str] = result.stdout.strip().split("\n")
            count: int = 0

            for line in lines:
                if not line:
                    continue

                # Parse ripgrep output: filepath:line_number:content
                parts: list[str] = line.split(":", 2)
                if len(parts) >= 3:
                    filepath: str = parts[0]
                    line_num: str = parts[1]
                    content: str = parts[2].strip()

                    # Determine type
                    if "TODO:" in content or "TODO :" in content:
                        tag_type: str = "TODO"
                    elif "FIXME:" in content or "FIXME :" in content:
                        tag_type: str = "FIXME"
                    else:
                        tag_type: str = "OTHER"

                    # Get relative path
                    rel_path: str = os.path.relpath(filepath, self.directory)

                    # Insert into tree
                    self.tree.insert(
                        "",
                        tk.END,
                        values=(tag_type, rel_path, line_num, content),
                        tags=(tag_type,),
                    )
                    count += 1

            self.count_label.config(text=f"Total: {count}")
            status_text: str = (
                "Status: Monitoring..." if self.monitoring else "Status: Idle"
            )
            self.status_label.config(text=status_text)

        except FileNotFoundError:
            messagebox.showerror(
                "Error", "ripgrep (rg) not found. Please install it first."
            )
            self.status_label.config(text="Status: Error - ripgrep not found")
        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Scan timed out")
            self.status_label.config(text="Status: Error - Timeout")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Status: Error")

    def on_double_click(self, _):
        item: str = self.tree.selection()[0]
        values: tuple[str, ...] = tuple(
            str(item) for item in self.tree.item(item, "values")
        )

        # Copy file path and line number to clipboard
        if len(values) >= 3:
            filepath: str = os.path.join(str(self.directory), values[1])
            line_num: int = int(values[2])
            copy_text: str = f"{filepath}:{line_num}"
            self.root.clipboard_clear()
            self.root.clipboard_append(copy_text)
            self.status_label.config(text=f"Copied: {copy_text}")


if __name__ == "__main__":
    root: tk.Tk = tk.Tk()
    app: TodoMonitor = TodoMonitor(root)
    root.mainloop()
