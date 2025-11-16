import tkinter as tk
from tkinter import ttk, messagebox
from utils.settings import Settings

class SettingsDialog:
    """Dialog for editing application settings"""
    
    def __init__(self, parent, on_save_callback=None):
        self.parent = parent
        self.on_save_callback = on_save_callback
        self.settings = Settings()
        self.dialog = None
        self.temp_stop_words = self.settings.stop_words.copy()
        
        self.create_dialog()
    
    def create_dialog(self):
        """Create settings dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("⚙️ Settings")
        self.dialog.geometry("700x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="Stop Words Settings", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        ttk.Label(title_frame, 
                 text="(Words that will be ignored during similarity calculation)",
                 font=('Arial', 9, 'italic'),
                 foreground='gray').pack(side=tk.LEFT, padx=10)
        
        # Stop words count
        self.count_label = ttk.Label(title_frame, 
                                     text=f"({len(self.temp_stop_words)} words)",
                                     font=('Arial', 10, 'italic'))
        self.count_label.pack(side=tk.RIGHT)
        
        # Add word frame
        add_frame = ttk.LabelFrame(main_frame, text="Add Stop Word", padding="10")
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="Word:").pack(side=tk.LEFT, padx=5)
        
        self.new_word_var = tk.StringVar()
        self.new_word_entry = ttk.Entry(add_frame, textvariable=self.new_word_var, 
                                        font=('Arial', 11), width=30)
        self.new_word_entry.pack(side=tk.LEFT, padx=5)
        self.new_word_entry.bind('<Return>', lambda e: self.add_word())
        
        ttk.Button(add_frame, text="➕ Add", 
                  command=self.add_word).pack(side=tk.LEFT, padx=5)
        
        # Stop words list frame
        list_frame = ttk.LabelFrame(main_frame, text="Current Stop Words", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Search box
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.filter_list)
        ttk.Entry(search_frame, textvariable=self.search_var, 
                 font=('Arial', 10), width=30).pack(side=tk.LEFT, padx=5)
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.words_listbox = tk.Listbox(list_container, 
                                        font=('Arial', 11),
                                        yscrollcommand=scrollbar.set,
                                        selectmode=tk.EXTENDED)
        self.words_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.words_listbox.yview)
        
        # Buttons for list operations
        list_buttons = ttk.Frame(list_frame)
        list_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(list_buttons, text="🗑️ Remove Selected", 
                  command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(list_buttons, text="🔄 Reset to Defaults", 
                  command=self.reset_to_defaults).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(list_buttons, text="📋 Select All", 
                  command=self.select_all).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="💾 Save & Apply", 
                  command=self.save_settings,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(action_frame, text="❌ Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(action_frame, text="📥 Export to File", 
                  command=self.export_words).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_frame, text="📤 Import from File", 
                  command=self.import_words).pack(side=tk.LEFT, padx=5)
        
        # Populate list
        self.populate_list()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f'+{x}+{y}')
    
    def populate_list(self, filter_text=""):
        """Populate listbox with stop words"""
        self.words_listbox.delete(0, tk.END)
        
        sorted_words = sorted(self.temp_stop_words)
        
        for word in sorted_words:
            if filter_text.lower() in word.lower():
                self.words_listbox.insert(tk.END, word)
        
        self.count_label.config(text=f"({len(self.temp_stop_words)} words)")
    
    def filter_list(self, *args):
        """Filter list based on search"""
        self.populate_list(self.search_var.get())
    
    def add_word(self):
        """Add new stop word"""
        word = self.new_word_var.get().strip()
        
        if not word:
            messagebox.showwarning("Warning", "Please enter a word!")
            return
        
        if word in self.temp_stop_words:
            messagebox.showinfo("Info", f"'{word}' is already in the list!")
            return
        
        self.temp_stop_words.add(word)
        self.populate_list()
        self.new_word_var.set("")
        self.new_word_entry.focus()
    
    def remove_selected(self):
        """Remove selected words from list"""
        selected = self.words_listbox.curselection()
        
        if not selected:
            messagebox.showwarning("Warning", "Please select words to remove!")
            return
        
        words_to_remove = [self.words_listbox.get(i) for i in selected]
        
        result = messagebox.askyesno("Confirm", 
                                    f"Remove {len(words_to_remove)} word(s)?")
        if result:
            for word in words_to_remove:
                self.temp_stop_words.discard(word)
            self.populate_list()
    
    def select_all(self):
        """Select all items in listbox"""
        self.words_listbox.select_set(0, tk.END)
    
    def reset_to_defaults(self):
        """Reset to default stop words"""
        result = messagebox.askyesno("Confirm Reset", 
                                    "Reset to default stop words?\n"
                                    "This will discard all your changes!")
        if result:
            self.temp_stop_words = Settings.DEFAULT_STOP_WORDS.copy()
            self.populate_list()
    
    def save_settings(self):
        """Save settings and close dialog"""
        self.settings.update_stop_words(self.temp_stop_words)
        
        if self.settings.save_settings():
            messagebox.showinfo("Success", 
                              "Settings saved successfully!\n\n"
                              "Note: You may need to recalculate similarities "
                              "for changes to take effect.")
            
            if self.on_save_callback:
                self.on_save_callback()
            
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings!")
    
    def cancel(self):
        """Cancel and close dialog"""
        self.dialog.destroy()
    
    def export_words(self):
        """Export stop words to text file"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Export Stop Words",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for word in sorted(self.temp_stop_words):
                        f.write(word + '\n')
                messagebox.showinfo("Success", f"Exported {len(self.temp_stop_words)} words!")
            except Exception as e:
                messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def import_words(self):
        """Import stop words from text file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Import Stop Words",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    new_words = {line.strip() for line in f if line.strip()}
                
                result = messagebox.askyesno("Confirm Import",
                                           f"Import {len(new_words)} words?\n"
                                           "This will ADD to existing words, not replace them.")
                if result:
                    self.temp_stop_words.update(new_words)
                    self.populate_list()
                    messagebox.showinfo("Success", 
                                      f"Imported {len(new_words)} words!\n"
                                      f"Total: {len(self.temp_stop_words)} words")
            except Exception as e:
                messagebox.showerror("Error", f"Import failed:\n{str(e)}")