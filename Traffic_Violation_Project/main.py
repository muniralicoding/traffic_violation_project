"""
Smart Traffic Violation Analysis and Reporting System (GUI Dashboard)
Course: Python Programming (MCA 1st Semester)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import os

class TrafficDatabase:
    """Class to handle file operations and data cleaning."""
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.DataFrame()
        self.load_data()

    def load_data(self):
        """Loads data from the CSV file into a Pandas DataFrame."""
        try:
            self.df = pd.read_csv(self.filename)
            self.clean_data()
        except FileNotFoundError:
            # We initialize an empty structure if no file is found
            cols = ["Violation_ID", "Date", "Time", "Location", "Vehicle_Type", "Vehicle_Number", "Violation_Type", "Fine_Amount", "Payment_Status", "Repeat_Offender", "Officer_ID"]
            self.df = pd.DataFrame(columns=cols)

    def clean_data(self):
        """Cleans the dataset by handling missing values and correcting types."""
        if not self.df.empty:
            # Drop completely empty rows and duplicates
            self.df.dropna(how='all', inplace=True)
            self.df.drop_duplicates(inplace=True)
            # Convert Fine_Amount to numeric, handling errors
            self.df['Fine_Amount'] = pd.to_numeric(self.df['Fine_Amount'], errors='coerce')
            # Drop rows where critical fields are NaN
            self.df.dropna(subset=['Fine_Amount', 'Violation_ID'], inplace=True)
            # Fill remaining NaNs with empty strings for a cleaner UI
            self.df.fillna('', inplace=True)

    def get_dataframe(self):
        return self.df


class TrafficAnalyzer:
    """Class to perform data analysis, searching, and filtering."""
    def __init__(self, database):
        self.database = database

    def get_statistics(self):
        """Calculates basic statistics using NumPy and Pandas."""
        df = self.database.get_dataframe()
        if df.empty:
            return None
        return {
            "Total Violations Recorded": len(df),
            "Total Fines Collected": df[df['Payment_Status'].str.capitalize() == 'Paid']['Fine_Amount'].sum(),
            "Total Fines Pending": df[df['Payment_Status'].str.capitalize() == 'Unpaid']['Fine_Amount'].sum(),
            "Average Fine Amount": np.mean(df['Fine_Amount']),
            "Maximum Fine Imposed": np.max(df['Fine_Amount']),
            "Ratio (Paid vs Unpaid)": f"{len(df[df['Payment_Status'].str.capitalize() == 'Paid'])} Paid / {len(df[df['Payment_Status'].str.capitalize() == 'Unpaid'])} Unpaid",
            "Most Common Violation": df['Violation_Type'].mode()[0] if not df['Violation_Type'].empty else "N/A",
            "Highest-Risk Location": df['Location'].mode()[0] if not df['Location'].empty else "N/A",
            "Identified Repeat Offenders": len(df[df['Repeat_Offender'].str.capitalize() == 'Yes'])
        }


class DashboardApp:
    """Tkinter Application for the Dashboard Interface."""
    def __init__(self, root, db, analyzer):
        self.root = root
        self.db = db
        self.analyzer = analyzer
        
        # Configure Main Window
        self.root.title("Smart Traffic Violation Dashboard")
        self.root.geometry("1100x700")
        self.root.configure(bg="#f4f4f4")
        
        # Configure modern looking styles
        style = ttk.Style()
        try:
            style.theme_use('clam') # 'clam' looks cleaner than default windows theme
        except:
            pass
        style.configure("TButton", font=("Arial", 10, "bold"), padding=6)
        style.configure("TLabel", background="#f4f4f4", font=("Arial", 11))
        
        self.create_layout()
        self.show_data_table(self.db.get_dataframe())

    def create_layout(self):
        """Constructs the sidebar and main content areas."""
        # Top Header
        header = tk.Frame(self.root, bg="#2c3e50", height=70)
        header.pack(fill=tk.X)
        tk.Label(header, text="Smart Traffic Violation Dashboard", fg="white", bg="#2c3e50", font=("Arial", 18, "bold")).pack(pady=15)
        
        # Main Body Split (Sidebar + Content Area)
        body = tk.Frame(self.root, bg="#f4f4f4")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sidebar (Left)
        sidebar = tk.Frame(body, width=220, bg="#e0e0e0", relief=tk.RAISED, borderwidth=1)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Label(sidebar, text="Navigation Panel", bg="#e0e0e0", font=("Arial", 12, "bold")).pack(pady=15)
        
        # Sidebar Buttons
        ttk.Button(sidebar, text="View All Records", command=lambda: self.show_data_table(self.db.get_dataframe())).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(sidebar, text="Filter: Unpaid Fines", command=self.filter_unpaid).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(sidebar, text="Filter: Repeat Offenders", command=self.filter_repeat).pack(fill=tk.X, padx=10, pady=5)
        
        # Spacer
        tk.Frame(sidebar, height=2, bg="#c0c0c0").pack(fill=tk.X, padx=10, pady=15)
        
        ttk.Button(sidebar, text="View Statistics", command=self.show_statistics).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(sidebar, text="Interactive Charts", command=self.show_charts).pack(fill=tk.X, padx=10, pady=5)
        
        # Exit Button at bottom of sidebar
        ttk.Button(sidebar, text="Exit Application", command=self.root.quit).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=15)
        
        # Content Area (Right)
        self.content_area = tk.Frame(body, bg="white", relief=tk.SUNKEN, borderwidth=1)
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def clear_content_area(self):
        """Destroys all widgets in the content area to load a new view."""
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_data_table(self, df):
        """Renders the Pandas DataFrame into a Tkinter Treeview table."""
        self.clear_content_area()
        tk.Label(self.content_area, text=f"Traffic Violation Records (Count: {len(df)})", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        if df.empty:
            tk.Label(self.content_area, text="No records available.", bg="white", fg="red").pack(pady=20)
            return

        # Treeview Configuration
        tree_frame = tk.Frame(self.content_area)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        tree_scroll_y = tk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(tree_frame, orient='horizontal')
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        cols = list(df.columns)
        tree = ttk.Treeview(tree_frame, columns=cols, show='headings', 
                            yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        tree_scroll_y.config(command=tree.yview)
        tree_scroll_x.config(command=tree.xview)
        
        for col in cols:
            tree.heading(col, text=col)
            # Adjust specific column widths
            width = 120
            if col == "Location": width = 180
            elif col == "Violation_Type": width = 150
            elif col == "Time" or col == "Repeat_Offender": width = 80
            tree.column(col, width=width, anchor=tk.CENTER)
        
        for _, row in df.iterrows():
            tree.insert("", tk.END, values=list(row))
            
        tree.pack(fill=tk.BOTH, expand=True)

    def show_statistics(self):
        """Renders a clean statistical summary panel."""
        self.clear_content_area()
        tk.Label(self.content_area, text="Key Statistical Findings", font=("Arial", 16, "bold"), bg="white").pack(pady=20)
        
        stats = self.analyzer.get_statistics()
        if not stats:
            tk.Label(self.content_area, text="No data available for statistics.", bg="white").pack()
            return
            
        stat_frame = tk.Frame(self.content_area, bg="white")
        stat_frame.pack(pady=10)
        
        row_idx = 0
        for key, val in stats.items():
            tk.Label(stat_frame, text=f"{key}:", font=("Arial", 12, "bold"), bg="white", anchor="e", width=25, fg="#2c3e50").grid(row=row_idx, column=0, pady=8, padx=10)
            
            # Format numerical values beautifully
            if isinstance(val, float):
                val = f"₹ {val:,.2f}"
            elif "Fine" in key and isinstance(val, (int, float)):
                val = f"₹ {val:,}"
                
            tk.Label(stat_frame, text=str(val), font=("Arial", 12), bg="white", anchor="w", width=30).grid(row=row_idx, column=1, pady=8, padx=10)
            row_idx += 1

    def show_charts(self):
        """Embeds Matplotlib figures directly inside the Tkinter Dashboard."""
        self.clear_content_area()
        tk.Label(self.content_area, text="Visual Insights", font=("Arial", 14, "bold"), bg="white").pack(pady=5)
        
        df = self.db.get_dataframe()
        if df.empty:
            tk.Label(self.content_area, text="No data for charts.", bg="white").pack()
            return

        # Create Matplotlib Figure
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        fig.patch.set_facecolor('white')

        # 1. Bar chart: Violations by type
        ax1 = fig.add_subplot(221)
        df['Violation_Type'].value_counts().plot(kind='bar', ax=ax1, color='#3498db')
        ax1.set_title('Violations by Type')
        ax1.tick_params(axis='x', rotation=12, labelsize=8)

        # 2. Pie chart: Payment Status
        ax2 = fig.add_subplot(222)
        df['Payment_Status'].value_counts().plot(kind='pie', ax=ax2, autopct='%1.1f%%', colors=['#2ecc71', '#e74c3c'])
        ax2.set_title('Payment Status Distribution')
        ax2.set_ylabel('')

        # 3. Bar chart: Top Locations
        ax3 = fig.add_subplot(223)
        df['Location'].value_counts().head(4).plot(kind='bar', ax=ax3, color='#e67e22')
        ax3.set_title('Top High-Risk Locations')
        ax3.tick_params(axis='x', rotation=10, labelsize=8)

        # 4. Histogram: Fines
        ax4 = fig.add_subplot(224)
        ax4.hist(df['Fine_Amount'], bins=8, color='#1abc9c', edgecolor='black')
        ax4.set_title('Fine Amount Distribution')
        ax4.set_xlabel('Fine (₹)', fontsize=8)

        fig.tight_layout(pad=2.0)

        # Embed into Tkinter Canvas
        canvas = FigureCanvasTkAgg(fig, master=self.content_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def filter_unpaid(self):
        """Quick filter action for Unpaid status."""
        df = self.db.get_dataframe()
        filtered = df[df['Payment_Status'].str.capitalize() == 'Unpaid']
        self.show_data_table(filtered)

    def filter_repeat(self):
        """Quick filter action for Repeat Offenders."""
        df = self.db.get_dataframe()
        filtered = df[df['Repeat_Offender'].str.capitalize() == 'Yes']
        self.show_data_table(filtered)


def main():
    root = tk.Tk()
    db_file = 'traffic_violations.csv'
    
    # Verify file existence and warn if missing
    if not os.path.exists(db_file):
        messagebox.showwarning(
            "Dataset Missing", 
            f"Dataset '{db_file}' not found in the current directory.\n\nPlease ensure 'dataset_generator.py' was executed."
        )
        
    db = TrafficDatabase(db_file)
    analyzer = TrafficAnalyzer(db)
    
    # Initialize and run the application
    app = DashboardApp(root, db, analyzer)
    root.mainloop()

if __name__ == "__main__":
    main()
