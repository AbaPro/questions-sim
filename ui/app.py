import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List
import sys
import os
import threading
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_loader import DataLoader
from utils.similarity import SimilarityCalculator
from ui.similarity_matrix_tab import SimilarityMatrixTab
from ui.settings_dialog import SettingsDialog

class QuestionsSim:
    def __init__(self, root):
        self.root = root
        self.root.title("Arabic Questions Similarity Finder")
        self.root.geometry("1400x800")
        
        self.ids = []
        self.questions = []
        self.similarity_calc = SimilarityCalculator()
        self.min_similarity = 30.0  # القيمة الافتراضية
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Top frame for file selection ONLY
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="📁 Load Excel File", command=self.load_file, 
                   style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        self.file_label = ttk.Label(top_frame, text="No file loaded", 
                                    font=('Arial', 10))
        self.file_label.pack(side=tk.LEFT, padx=10)
        
        # Add settings button
        ttk.Button(top_frame, text="⚙️ Settings", 
                  command=self.open_settings).pack(side=tk.RIGHT, padx=5)
        
        # Remove the similarity control from here - it will be in each tab
        
        # Progress bar frame
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(fill=tk.X, padx=10)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_label = ttk.Label(self.progress_frame, text="")
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Single Question Similarity
        self.single_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.single_tab, text="🔍 Single Question")
        self.setup_single_question_tab()
        
        # Tab 2: Similarity Matrix
        self.matrix_tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.matrix_tab_frame, text="📊 All Questions Matrix")
        self.matrix_tab = SimilarityMatrixTab(self.matrix_tab_frame, 
                                             self.similarity_calc,
                                             self.ids,
                                             self.questions,
                                             30.0)  # Default min similarity

    def setup_single_question_tab(self):
        """إعداد تاب السؤال الواحد"""
        # Add similarity control at the top of THIS tab
        control_frame = ttk.Frame(self.single_tab, padding="10")
        control_frame.pack(fill=tk.X)
        
        ttk.Label(control_frame, text="Minimum Similarity:", 
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        self.single_similarity_var = tk.DoubleVar(value=30.0)
        similarity_spinbox = ttk.Spinbox(control_frame, 
                                        from_=0, 
                                        to=100, 
                                        increment=5,
                                        textvariable=self.single_similarity_var,
                                        width=10,
                                        command=self.on_single_similarity_change)
        similarity_spinbox.pack(side=tk.LEFT, padx=5)
        similarity_spinbox.bind('<Return>', lambda e: self.on_single_similarity_change())
        
        ttk.Label(control_frame, text="%", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="Apply", 
                  command=self.on_single_similarity_change).pack(side=tk.LEFT, padx=5)
        
        # Main container
        main_container = ttk.PanedWindow(self.single_tab, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Questions list
        left_frame = ttk.Frame(main_container)
        main_container.add(left_frame, weight=1)
        
        # Header with count
        header_frame = ttk.Frame(left_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(header_frame, text="📋 All Questions", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        self.count_label = ttk.Label(header_frame, text="(0)", 
                                     font=('Arial', 10, 'italic'))
        self.count_label.pack(side=tk.LEFT, padx=5)
        
        # Search box
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="🔍", font=('Arial', 12)).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_questions)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, 
                                font=('Arial', 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Questions treeview
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.questions_tree = ttk.Treeview(list_frame, 
                                          columns=('ID', 'Question'),
                                          show='tree headings',
                                          yscrollcommand=y_scrollbar.set,
                                          xscrollcommand=x_scrollbar.set,
                                          selectmode='browse')
        
        self.questions_tree.heading('ID', text='ID', anchor=tk.W)
        self.questions_tree.heading('Question', text='Question', anchor=tk.W)
        
        self.questions_tree.column('#0', width=0, stretch=False)
        self.questions_tree.column('ID', width=80, anchor=tk.W)
        self.questions_tree.column('Question', width=500, anchor=tk.W)
        
        self.questions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scrollbar.config(command=self.questions_tree.yview)
        x_scrollbar.config(command=self.questions_tree.xview)
        
        self.questions_tree.bind('<<TreeviewSelect>>', self.on_question_select)
        
        self.questions_tree.tag_configure('oddrow', background='#f0f0f0')
        self.questions_tree.tag_configure('evenrow', background='white')
        
        # Right panel - Similar questions
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=1)
        
        # Header with count and export button
        header_right_frame = ttk.Frame(right_frame)
        header_right_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_right_frame, text="🔗 Similar Questions", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        self.similar_count_label = ttk.Label(header_right_frame, text="(0)", 
                                            font=('Arial', 10, 'italic'))
        self.similar_count_label.pack(side=tk.LEFT, padx=5)
        
        # Export button
        self.export_button = ttk.Button(header_right_frame, 
                                       text="📥 Export to Excel", 
                                       command=self.export_results,
                                       state=tk.DISABLED)
        self.export_button.pack(side=tk.RIGHT, padx=5)
        
        # Selected question display
        selected_frame = ttk.LabelFrame(right_frame, text="Selected Question", padding=10)
        selected_frame.pack(fill=tk.X, pady=5)
        
        self.selected_label = tk.Text(selected_frame, height=3, wrap=tk.WORD, 
                                      font=('Arial', 10), bg='#e8f4f8', 
                                      relief=tk.FLAT)
        self.selected_label.pack(fill=tk.X)
        self.selected_label.insert('1.0', "Select a question from the left to see similar ones")
        self.selected_label.config(state=tk.DISABLED)
        
        # Similar questions treeview
        similar_frame = ttk.Frame(right_frame)
        similar_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Scrollbars
        y_scrollbar2 = ttk.Scrollbar(similar_frame, orient=tk.VERTICAL)
        y_scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        x_scrollbar2 = ttk.Scrollbar(similar_frame, orient=tk.HORIZONTAL)
        x_scrollbar2.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.similar_tree = ttk.Treeview(similar_frame,
                                        columns=('Similarity', 'ID', 'Question'),
                                        show='tree headings',
                                        yscrollcommand=y_scrollbar2.set,
                                        xscrollcommand=x_scrollbar2.set,
                                        selectmode='browse')
        
        self.similar_tree.heading('Similarity', text='Match %', anchor=tk.CENTER)
        self.similar_tree.heading('ID', text='ID', anchor=tk.W)
        self.similar_tree.heading('Question', text='Question', anchor=tk.W)
        
        self.similar_tree.column('#0', width=0, stretch=False)
        self.similar_tree.column('Similarity', width=80, anchor=tk.CENTER)
        self.similar_tree.column('ID', width=80, anchor=tk.W)
        self.similar_tree.column('Question', width=450, anchor=tk.W)
        
        self.similar_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        y_scrollbar2.config(command=self.similar_tree.yview)
        x_scrollbar2.config(command=self.similar_tree.xview)
        
        # Color tags for similarity levels
        self.similar_tree.tag_configure('high', background='#c8e6c9')  # Green
        self.similar_tree.tag_configure('medium', background='#fff9c4')  # Yellow
        self.similar_tree.tag_configure('low', background='#ffccbc')  # Orange
    
    def on_single_similarity_change(self):
        """Update minimum similarity for single question tab"""
        try:
            new_value = self.single_similarity_var.get()
            
            if new_value < 0:
                new_value = 0
                self.single_similarity_var.set(0)
            elif new_value > 100:
                new_value = 100
                self.single_similarity_var.set(100)
            
            # Refresh current selection
            selection = self.questions_tree.selection()
            if selection and len(self.questions) > 0:
                actual_idx = int(selection[0])
                self.display_similar_questions(actual_idx)
        
        except tk.TclError:
            self.single_similarity_var.set(30.0)

    def show_progress(self, message):
        """Show progress bar"""
        self.progress_label.config(text=message)
        self.progress_label.pack(side=tk.LEFT, padx=10)
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_bar.start(10)
        self.root.update()
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
        self.root.update()
    
    def load_file(self):
        """Load Excel file"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Disable button during loading
        self.show_progress("Loading Excel file...")
        
        def load_thread():
            try:
                self.ids, self.questions = DataLoader.load_excel(file_path)
                
                self.root.after(0, lambda: self.progress_label.config(text="Processing questions..."))
                self.similarity_calc.fit(self.questions)
                
                # Update UI in main thread
                self.root.after(0, self.on_load_complete, file_path)
            
            except Exception as e:
                self.root.after(0, self.on_load_error, str(e))
        
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
    
    def on_load_complete(self, file_path):
        """Called when loading is complete"""
        self.hide_progress()
        filename = file_path.split('/')[-1]
        self.file_label.config(text=f"✓ {filename} ({len(self.questions)} questions)")
        self.count_label.config(text=f"({len(self.questions)})")
        self.populate_questions_list()
        
        # Update matrix tab with default min similarity
        self.matrix_tab.update_data(self.ids, self.questions, 30.0)
        
        messagebox.showinfo("Success", f"Loaded {len(self.questions)} questions successfully!")
    
    def on_load_error(self, error_message):
        """Called when loading fails"""
        self.hide_progress()
        messagebox.showerror("Error", error_message)
    
    def populate_questions_list(self, filter_text=""):
        """Populate the questions treeview"""
        self.questions_tree.delete(*self.questions_tree.get_children())
        
        count = 0
        for i, (qid, question) in enumerate(zip(self.ids, self.questions)):
            if filter_text.lower() in question.lower() or filter_text.lower() in str(qid).lower():
                tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                self.questions_tree.insert('', tk.END, values=(qid, question), 
                                          tags=(tag,), iid=str(i))
                count += 1
    
    def filter_questions(self, *args):
        """Filter questions based on search text"""
        self.populate_questions_list(self.search_var.get())
    
    def on_question_select(self, event):
        """Handle question selection"""
        selection = self.questions_tree.selection()
        if not selection:
            return
        
        # Get actual index
        actual_idx = int(selection[0])
        
        # Update selected question label
        self.selected_label.config(state=tk.NORMAL)
        self.selected_label.delete('1.0', tk.END)
        self.selected_label.insert('1.0', f"[{self.ids[actual_idx]}] {self.questions[actual_idx]}")
        self.selected_label.config(state=tk.DISABLED)
        
        # Find and display similar questions
        self.display_similar_questions(actual_idx)
    
    def export_results(self):
        """تصدير النتائج إلى ملف Excel"""
        # التحقق من وجود نتائج
        if not self.similar_tree.get_children():
            messagebox.showwarning("تحذير", "لا توجد نتائج للتصدير!")
            return
        
        # الحصول على السؤال المحدد
        selection = self.questions_tree.selection()
        if not selection:
            messagebox.showwarning("تحذير", "الرجاء تحديد سؤال أولاً!")
            return
        
        actual_idx = int(selection[0])
        selected_question = self.questions[actual_idx]
        selected_id = self.ids[actual_idx]
        
        # جمع البيانات من الجدول
        export_data = []
        for item in self.similar_tree.get_children():
            values = self.similar_tree.item(item)['values']
            if values[0] != "N/A":  # تجاهل رسالة "لا توجد نتائج"
                export_data.append({
                    'Similarity %': values[0],
                    'Question ID': values[1],
                    'Question': values[2]
                })
        
        if not export_data:
            messagebox.showwarning("تحذير", "لا توجد بيانات صالحة للتصدير!")
            return
        
        # إنشاء DataFrame
        df = pd.DataFrame(export_data)
        
        # إضافة معلومات السؤال الأصلي في الأعلى
        header_df = pd.DataFrame({
            'Similarity %': ['Original Question:', f'ID: {selected_id}', ''],
            'Question ID': ['', '', ''],
            'Question': ['', selected_question, '']
        })
        
        # دمج البيانات
        final_df = pd.concat([header_df, df], ignore_index=True)
        
        # اختيار مكان الحفظ
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"similar_questions_{selected_id}_{timestamp}.xlsx"
        
        file_path = filedialog.asksaveasfilename(
            title="حفظ النتائج",
            defaultextension=".xlsx",
            initialfile=default_filename,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # حفظ الملف
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                final_df.to_excel(writer, index=False, sheet_name='Similar Questions')
                
                # تنسيق العمود
                worksheet = writer.sheets['Similar Questions']
                worksheet.column_dimensions['A'].width = 15
                worksheet.column_dimensions['B'].width = 15
                worksheet.column_dimensions['C'].width = 80
            
            messagebox.showinfo("نجح", 
                              f"تم تصدير {len(export_data)} سؤال بنجاح!\n\nالملف: {file_path}")
        
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل التصدير:\n{str(e)}")

    def display_similar_questions(self, query_idx: int):
        """Display similar questions"""
        self.similar_tree.delete(*self.similar_tree.get_children())
        
        similar = self.similarity_calc.get_similar_questions(query_idx, top_n=100)
        
        # Use the tab-specific minimum similarity
        min_similarity = self.single_similarity_var.get()
        filtered_similar = [(idx, score) for idx, score in similar 
                           if score * 100 >= min_similarity]
        
        if not filtered_similar:
            self.similar_tree.insert('', tk.END, 
                                    values=("N/A", "N/A", 
                                           f"No similar questions with ≥{min_similarity}%"))
            self.similar_count_label.config(text="(0 results)")
            self.export_button.config(state=tk.DISABLED)
            return
        
        # تحديث عداد النتائج
        result_text = f"({len(filtered_similar)} result{'s' if len(filtered_similar) > 1 else ''})"
        self.similar_count_label.config(text=result_text)
        self.export_button.config(state=tk.NORMAL)
        
        for idx, score in filtered_similar:
            similarity_percent = score * 100
            
            # Determine color tag based on similarity
            if similarity_percent >= 70:
                tag = 'high'
            elif similarity_percent >= 40:
                tag = 'medium'
            else:
                tag = 'low'
            
            self.similar_tree.insert('', tk.END, 
                                    values=(f"{similarity_percent:.1f}%", 
                                           self.ids[idx], 
                                           self.questions[idx]),
                                    tags=(tag,))
    
    def open_settings(self):
        """Open settings dialog"""
        def on_settings_saved():
            """Called when settings are saved"""
            if self.ids and self.questions:
                result = messagebox.askyesno("Recalculate?",
                                            "Stop words have been changed.\n"
                                            "Do you want to recalculate similarities now?")
                if result:
                    # Recalculate similarity matrix
                    if hasattr(self, 'matrix_tab'):
                        self.matrix_tab.calculate_all_similarities()
        
        SettingsDialog(self.root, on_save_callback=on_settings_saved)