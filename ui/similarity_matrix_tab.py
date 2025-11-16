import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from datetime import datetime
import threading

class SimilarityMatrixTab:
    """Tab for displaying complete similarity matrix of all questions"""
    
    def __init__(self, parent, similarity_calc, ids, questions, min_similarity):
        self.parent = parent
        self.similarity_calc = similarity_calc
        self.ids = ids
        self.questions = questions
        self.min_similarity = min_similarity
        self.matrix_data = []
        self.filtered_data = []
        self.current_sort_column = None
        self.current_sort_reverse = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup user interface"""
        # Header frame
        header_frame = ttk.Frame(self.parent, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(header_frame, text="📊 Similarity Matrix - All Questions", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        self.count_label = ttk.Label(header_frame, text="(0 pairs)", 
                                     font=('Arial', 10, 'italic'))
        self.count_label.pack(side=tk.LEFT, padx=10)
        
        # Buttons frame
        buttons_frame = ttk.Frame(header_frame)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.calculate_button = ttk.Button(buttons_frame, 
                                          text="🔄 Calculate All Similarities",
                                          command=self.calculate_all_similarities)
        self.calculate_button.pack(side=tk.LEFT, padx=5)
        
        self.export_button = ttk.Button(buttons_frame, 
                                       text="📥 Export Current View",
                                       command=self.export_matrix,
                                       state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_frame = ttk.Frame(self.parent)
        self.progress_frame.pack(fill=tk.X, padx=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_label = ttk.Label(self.progress_frame, text="")
        
        # Search and filter frame
        filter_frame = ttk.Frame(self.parent, padding="10")
        filter_frame.pack(fill=tk.X)
        
        ttk.Label(filter_frame, text="🔍 Search:", 
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.on_filter_change)
        search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, 
                                font=('Arial', 10), width=40)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(filter_frame, text="Min %:", 
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.filter_similarity_var = tk.DoubleVar(value=self.min_similarity)
        filter_spinbox = ttk.Spinbox(filter_frame, 
                                    from_=0, 
                                    to=100, 
                                    increment=5,
                                    textvariable=self.filter_similarity_var,
                                    width=10)
        filter_spinbox.pack(side=tk.LEFT, padx=5)
        filter_spinbox.bind('<Return>', lambda e: self.apply_new_percentage())
        
        ttk.Label(filter_frame, text="%", 
                 font=('Arial', 10)).pack(side=tk.LEFT)
        
        ttk.Button(filter_frame, text="Apply", 
                  command=self.apply_new_percentage).pack(side=tk.LEFT, padx=5)
        
        # Sort options
        ttk.Separator(filter_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Label(filter_frame, text="Sort by:", 
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        self.sort_var = tk.StringVar(value="similarity_desc")
        sort_options = [
            ("Similarity ↓", "similarity_desc"),
            ("Similarity ↑", "similarity_asc"),
            ("ID ↓", "id_desc"),
            ("ID ↑", "id_asc"),
        ]
        
        for text, value in sort_options:
            ttk.Radiobutton(filter_frame, text=text, 
                           variable=self.sort_var, 
                           value=value,
                           command=self.apply_sort).pack(side=tk.LEFT, padx=2)
        
        # Table frame
        table_frame = ttk.Frame(self.parent)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.matrix_tree = ttk.Treeview(table_frame,
                                       columns=('Similarity', 'ID1', 'Question1', 'ID2', 'Question2'),
                                       show='tree headings',
                                       yscrollcommand=y_scrollbar.set,
                                       xscrollcommand=x_scrollbar.set,
                                       selectmode='browse')
        
        # Clickable headers for sorting
        self.matrix_tree.heading('Similarity', text='Similarity % ⇅', anchor=tk.CENTER,
                                command=lambda: self.sort_by_column('similarity'))
        self.matrix_tree.heading('ID1', text='ID ⇅', anchor=tk.W,
                                command=lambda: self.sort_by_column('id1'))
        self.matrix_tree.heading('Question1', text='Question', anchor=tk.W)
        self.matrix_tree.heading('ID2', text='Similar ID ⇅', anchor=tk.W,
                                command=lambda: self.sort_by_column('id2'))
        self.matrix_tree.heading('Question2', text='Similar Question', anchor=tk.W)
        
        self.matrix_tree.column('#0', width=0, stretch=False)
        self.matrix_tree.column('Similarity', width=100, anchor=tk.CENTER)
        self.matrix_tree.column('ID1', width=60, anchor=tk.W)
        self.matrix_tree.column('Question1', width=300, anchor=tk.W)
        self.matrix_tree.column('ID2', width=60, anchor=tk.W)
        self.matrix_tree.column('Question2', width=300, anchor=tk.W)
        
        self.matrix_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.matrix_tree.yview)
        x_scrollbar.config(command=self.matrix_tree.xview)
        
        # Color tags
        self.matrix_tree.tag_configure('high', background='#c8e6c9')
        self.matrix_tree.tag_configure('medium', background='#fff9c4')
        self.matrix_tree.tag_configure('low', background='#ffccbc')
    
    def sort_by_column(self, column):
        """Sort table by clicking column header"""
        if self.current_sort_column == column:
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            self.current_sort_column = column
            self.current_sort_reverse = False
        
        self.apply_sort()
    
    def apply_sort(self):
        """Apply sorting to filtered data"""
        if not self.filtered_data:
            return
        
        sort_option = self.sort_var.get()
        
        if sort_option == "similarity_desc":
            self.filtered_data.sort(key=lambda x: x['similarity'], reverse=True)
        elif sort_option == "similarity_asc":
            self.filtered_data.sort(key=lambda x: x['similarity'], reverse=False)
        elif sort_option == "id_desc":
            self.filtered_data.sort(key=lambda x: (x['id1'], x['id2']), reverse=True)
        elif sort_option == "id_asc":
            self.filtered_data.sort(key=lambda x: (x['id1'], x['id2']), reverse=False)
        
        # Also handle column header clicks
        if self.current_sort_column:
            if self.current_sort_column == 'similarity':
                self.filtered_data.sort(key=lambda x: x['similarity'], 
                                       reverse=self.current_sort_reverse)
            elif self.current_sort_column in ['id1', 'id2']:
                self.filtered_data.sort(key=lambda x: x[self.current_sort_column], 
                                       reverse=self.current_sort_reverse)
        
        self.populate_table(self.filtered_data)
    
    def on_filter_change(self, *args):
        """Handle filter text change"""
        self.apply_filters()
    
    def apply_new_percentage(self):
        """Recalculate with new minimum percentage"""
        new_min = self.filter_similarity_var.get()
        
        if new_min < 0:
            new_min = 0
            self.filter_similarity_var.set(0)
        elif new_min > 100:
            new_min = 100
            self.filter_similarity_var.set(100)
        
        if not self.matrix_data:
            messagebox.showinfo("Info", "Please calculate similarities first!")
            return
        
        # Check if we need to recalculate or just filter
        if new_min < self.min_similarity:
            # Need to recalculate with lower threshold
            result = messagebox.askyesno("Recalculate?", 
                                        f"New minimum ({new_min}%) is lower than original ({self.min_similarity}%).\n"
                                        "Do you want to recalculate all similarities?")
            if result:
                self.min_similarity = new_min
                self.calculate_all_similarities()
            else:
                self.filter_similarity_var.set(self.min_similarity)
        else:
            # Just filter existing data
            self.apply_filters()
    
    def apply_filters(self):
        """Apply all filters to matrix data"""
        if not self.matrix_data:
            return
        
        search_text = self.search_var.get().lower()
        min_sim = self.filter_similarity_var.get()
        
        self.filtered_data = []
        for item in self.matrix_data:
            # Filter by percentage
            if item['similarity'] < min_sim:
                continue
            
            # Filter by search text
            if search_text:
                if (search_text not in item['question1'].lower() and 
                    search_text not in item['question2'].lower() and
                    search_text not in str(item['id1']).lower() and
                    search_text not in str(item['id2']).lower()):
                    continue
            
            self.filtered_data.append(item)
        
        self.apply_sort()
    
    def show_progress(self, message, value=0):
        """Show progress bar"""
        try:
            self.progress_label.config(text=message)
            self.progress_label.pack(side=tk.LEFT, padx=10)
            self.progress_bar.pack(fill=tk.X, pady=5)
            self.progress_bar['value'] = value
            self.parent.update_idletasks()
        except:
            pass
    
    def hide_progress(self):
        """Hide progress bar"""
        try:
            self.progress_bar.pack_forget()
            self.progress_label.pack_forget()
            self.parent.update_idletasks()
        except:
            pass
    
    def calculate_all_similarities(self):
        """Calculate all similarities between questions"""
        if not self.ids or not self.questions:
            messagebox.showwarning("Warning", "Please load an Excel file first!")
            return
        
        result = messagebox.askyesno("Confirm", 
                                    f"Calculate similarities for {len(self.questions)} questions?\n"
                                    "This may take some time.")
        
        if not result:
            return
        
        self.calculate_button.config(state=tk.DISABLED)
        self.calculate_button.config(text="⏳ Calculating...")
        
        def calculate_thread():
            try:
                self.matrix_data = []
                total = len(self.questions)
                
                for i in range(total):
                    similar = self.similarity_calc.get_similar_questions(i, top_n=100)
                    
                    for similar_idx, score in similar:
                        similarity_percent = score * 100
                        
                        if similarity_percent >= self.min_similarity:
                            self.matrix_data.append({
                                'similarity': similarity_percent,
                                'id1': self.ids[i],
                                'question1': self.questions[i],
                                'id2': self.ids[similar_idx],
                                'question2': self.questions[similar_idx]
                            })
                    
                    if i % 10 == 0 or i == total - 1:
                        progress = (i + 1) / total * 100
                        message = f"Processing question {i + 1}/{total}..."
                        self.parent.after(0, self.update_progress, message, progress)
                
                self.parent.after(0, self.on_calculation_complete)
            
            except Exception as e:
                self.parent.after(0, lambda: self.on_calculation_error(str(e)))
        
        thread = threading.Thread(target=calculate_thread)
        thread.daemon = True
        thread.start()

    def update_progress(self, message, value):
        """Update progress bar safely"""
        try:
            self.progress_label.config(text=message)
            self.progress_bar['value'] = value
            self.parent.update_idletasks()
        except:
            pass
    
    def on_calculation_complete(self):
        """After calculation is complete"""
        self.hide_progress()
        self.calculate_button.config(state=tk.NORMAL)
        self.calculate_button.config(text="🔄 Calculate All Similarities")
        
        # Apply initial filters
        self.apply_filters()
        
        self.export_button.config(state=tk.NORMAL)
        messagebox.showinfo("Complete", 
                          f"Calculated {len(self.matrix_data)} similar question pairs!\n"
                          f"Minimum similarity: {self.min_similarity}%")
    
    def on_calculation_error(self, error_message):
        """On error"""
        self.hide_progress()
        self.calculate_button.config(state=tk.NORMAL)
        self.calculate_button.config(text="🔄 Calculate All Similarities")
        messagebox.showerror("Error", f"Calculation failed:\n{error_message}")
    
    def populate_table(self, data_to_show):
        """Populate table with data"""
        self.matrix_tree.delete(*self.matrix_tree.get_children())
        
        if not data_to_show:
            self.count_label.config(text="(0 pairs)")
            return
        
        total_pairs = len(self.matrix_data)
        shown_pairs = len(data_to_show)
        
        if shown_pairs < total_pairs:
            self.count_label.config(text=f"({shown_pairs}/{total_pairs} pairs)")
        else:
            self.count_label.config(text=f"({shown_pairs} pairs)")
        
        # Limit display
        max_display = 5000
        if len(data_to_show) > max_display:
            messagebox.showwarning("Warning", 
                                 f"Too many results ({len(data_to_show)}). "
                                 f"Showing first {max_display} only.")
            data_to_show = data_to_show[:max_display]
        
        for idx, item in enumerate(data_to_show):
            try:
                similarity = float(item['similarity'])
                
                if similarity >= 70:
                    tag = ('high',)
                elif similarity >= 40:
                    tag = ('medium',)
                else:
                    tag = ('low',)
                
                self.matrix_tree.insert('', 'end',
                                       values=(f"{similarity:.1f}%",
                                              str(item['id1']),
                                              str(item['question1'])[:200],
                                              str(item['id2']),
                                              str(item['question2'])[:200]),
                                       tags=tag)
            except Exception as e:
                print(f"Error inserting row {idx}: {e}")
                continue
    
    def export_matrix(self):
        """Export current view to Excel"""
        if not self.filtered_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        # Prepare data from current view
        export_data = []
        for item in self.filtered_data:
            export_data.append({
                'Similarity %': f"{item['similarity']:.1f}%",
                'ID': item['id1'],
                'Question': item['question1'],
                'Similar ID': item['id2'],
                'Similar Question': item['question2']
            })
        
        df = pd.DataFrame(export_data)
        
        # Choose save location
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        min_sim = self.filter_similarity_var.get()
        default_filename = f"similarity_matrix_min{min_sim}_{timestamp}.xlsx"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Similarity Matrix",
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Similarity Matrix')
                
                # Format columns
                worksheet = writer.sheets['Similarity Matrix']
                worksheet.column_dimensions['A'].width = 15
                worksheet.column_dimensions['B'].width = 10
                worksheet.column_dimensions['C'].width = 60
                worksheet.column_dimensions['D'].width = 15
                worksheet.column_dimensions['E'].width = 60
            
            total = len(self.matrix_data)
            exported = len(export_data)
            messagebox.showinfo("Success", 
                              f"Exported {exported} pairs successfully!\n"
                              f"(Filtered from {total} total pairs)\n"
                              f"Min similarity: {min_sim}%\n\n"
                              f"File: {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def update_data(self, ids, questions, min_similarity):
        """Update data"""
        self.ids = ids
        self.questions = questions
        self.min_similarity = min_similarity
        self.matrix_data = []
        self.filtered_data = []
        self.filter_similarity_var.set(min_similarity)
        self.matrix_tree.delete(*self.matrix_tree.get_children())
        self.count_label.config(text="(0 pairs)")
        self.export_button.config(state=tk.DISABLED)