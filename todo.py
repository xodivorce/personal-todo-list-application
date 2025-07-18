import json
import os
import datetime
import customtkinter as ctk
from tkinter import messagebox
import darkdetect

class Task:
    def __init__(self, title, description, category, due_date=None, completed=False):
        self.title = title
        self.description = description
        self.category = category
        self.due_date = due_date
        self.completed = completed

    def toggle_complete(self):
        self.completed = not self.completed

def load_tasks():
    if os.path.exists('tasks.json'):
        try:
            with open('tasks.json', 'r') as f:
                return [Task(**task) for task in json.load(f)]
        except (json.JSONDecodeError, TypeError):
            return []
    return []

def save_tasks(tasks):
    with open('tasks.json', 'w') as f:
        json.dump([task.__dict__ for task in tasks], f, indent=4)

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal To-Do List Application")
        ctk.set_appearance_mode("Dark" if darkdetect.isDark() else "Light")
        self.theme = ctk.get_appearance_mode()
        self.bg_color = "#1D1D1F" if self.theme == "Dark" else "#f1f1f1"
        self.fg_color = "#f1f1f1" if self.theme == "Dark" else "#1D1D1F"
        self.font = ("TkDefaultFont", 13)
        self.font_bold = ("TkDefaultFont", 13, "bold")
        self.root.configure(bg=self.bg_color)
        self.tasks = load_tasks()
        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=15, pady=(8, 0), sticky="ew")
        
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=75)
        self.header_frame.grid_columnconfigure(1, weight=2, minsize=170)
        self.header_frame.grid_columnconfigure(2, weight=1, minsize=95)
        self.header_frame.grid_columnconfigure(3, weight=1, minsize=125)
        self.header_frame.grid_columnconfigure(4, weight=3, minsize=210)
        self.header_frame.grid_columnconfigure(5, weight=0, minsize=145)

        headers = ["Status", "Task Name", "Task Group", "Due Date", "Details", "Delete Task"]
        header_anchors = ["center", "w", "w", "w", "w", "w"]
        for i, text in enumerate(headers):
            ctk.CTkLabel(self.header_frame, text=text, text_color=self.fg_color, font=self.font_bold, anchor=header_anchors[i]).grid(
                row=0, column=i, padx=20, pady=5, sticky="ew"
            )

        self.task_list_frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.task_list_frame.grid(row=1, column=0, padx=15, pady=3, sticky="nsew")
        self.task_list_frame.grid_columnconfigure(0, weight=1)
        
        add_button = ctk.CTkButton(
            self.root,
            text="Add Task",
            font=("TkDefaultFont", 13, "bold"),
            command=self.add_task,
            fg_color="#4F70F0",
            hover_color="#3D5EDC",
            text_color="white",
            corner_radius=6,
            height=40,
            width=130,
            border_width=0
        )
        add_button.grid(row=2, column=0, pady=12, padx=0) 
        
        self.refresh_tasks()

    def refresh_tasks(self):
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        
        def truncate(text, max_len=30):
            return text if len(text) <= max_len else text[:max_len - 3] + "..."
        
        for i, task in enumerate(self.tasks):
            row_frame = ctk.CTkFrame(self.task_list_frame, fg_color="transparent", height=48)
            row_frame.grid(row=i, column=0, padx=0, pady=(2, 0), sticky="ew")
            row_frame.grid_propagate(False)
            
            row_frame.grid_columnconfigure(0, weight=0, minsize=75)
            row_frame.grid_columnconfigure(1, weight=2, minsize=180)
            row_frame.grid_columnconfigure(2, weight=1, minsize=150)
            row_frame.grid_columnconfigure(3, weight=1, minsize=132)
            row_frame.grid_columnconfigure(4, weight=3, minsize=210)
            row_frame.grid_columnconfigure(5, weight=0, minsize=130)
            
            checkbox = ctk.CTkCheckBox(
                row_frame, text="", variable=ctk.BooleanVar(value=task.completed),
                command=lambda index=i: self.toggle_status(index),
                width=20, height=20, checkbox_width=18, checkbox_height=18,
                fg_color="#506eec", hover_color="#3757e8",
                border_color="#9098a9",
                border_width=1, corner_radius=3
            )
            checkbox.grid(row=0, column=0, padx=4, pady=4)
            
            font_style = self.font if not task.completed else ("TkDefaultFont", 13, "overstrike")

            title_color = "#888888" if task.completed else self.fg_color
            title_label = ctk.CTkLabel(
                row_frame, text=truncate(task.title, 32), font=font_style, text_color=title_color,
                anchor="w"
            )
            title_label.grid(row=0, column=1, padx=25, pady=5, sticky="ew")
            
            cat_color = "#888888" if task.completed else self.fg_color
            cat_label = ctk.CTkLabel(
                row_frame, text=truncate(task.category, 15), font=font_style, text_color=cat_color,
                anchor="w"
            )
            cat_label.grid(row=0, column=2, padx=28, pady=5, sticky="ew")

            due_color = "#888888" if task.completed else self.fg_color
            due_label = ctk.CTkLabel(
                row_frame, text=task.due_date or "No date.", font=font_style, text_color=due_color,
                anchor="w"
            )
            due_label.grid(row=0, column=3, padx=0, pady=5, sticky="ew")
               
            def format_multiline_desc(text, chars_per_line=30, max_lines=3):
                if len(text) <= chars_per_line:
                    return text
                lines, remaining = [], text
                for line_num in range(max_lines):
                    if len(remaining) <= chars_per_line:
                        lines.append(remaining)
                        break
                    break_point = chars_per_line
                    for i in range(chars_per_line - 1, chars_per_line - 10, -1):
                        if i < len(remaining) and remaining[i] in ' .-,':
                            break_point = i
                            break
                    lines.append(remaining[:break_point])
                    remaining = remaining[break_point:].lstrip()
                    if line_num == max_lines - 1 and remaining:
                        lines[-1] = lines[-1][:45] + "..."
                return '\n'.join(lines)
            
            desc_display = format_multiline_desc(task.description or "")
            desc_color = "#888888" if task.completed else self.fg_color
            desc_label = ctk.CTkLabel(
                row_frame, text=desc_display or "—", font=font_style, text_color=desc_color,
                anchor="nw", justify="left"
            )
            desc_label.grid(row=0, column=4, padx=0, pady=5, sticky="new")
            
            delete_btn = ctk.CTkButton(
                row_frame, text="Remove",
                font=("TkDefaultFont", 13),
                width=80, height=30,
                fg_color="#506eec",
                hover_color="#3757e8",
                text_color="white",
                corner_radius=6,
                border_width=0,
                command=lambda index=i: self.delete_task(index)
            )
            delete_btn.grid(row=0, column=5, padx=(0, 10), pady=4, sticky="ew")


    def toggle_status(self, index):
        self.tasks[index].toggle_complete()
        save_tasks(self.tasks)
        self.refresh_tasks()

    def delete_task(self, index):
        del self.tasks[index]
        save_tasks(self.tasks)
        self.refresh_tasks()

    def add_task(self):
        win = ctk.CTkToplevel(self.root)
        win.title("Add New Task")
        win.configure(fg_color=self.bg_color)
        win.transient(self.root)
        win.grab_set()
        win.grid_columnconfigure(1, weight=1)
        win.geometry("450x350")
        win.resizable(False, False)
        
        ctk.CTkLabel(
            win, text="Add New Task",
            font=("TkDefaultFont", 13, "bold"),
            text_color=self.fg_color
        ).grid(row=0, column=0, columnspan=2, pady=20)
        
        labels = ["Task Name", "Details", "Task Group", "Due Date"]
        entries = []
        category_options = [
            "Work", "Finance", "Projects", "Meetings",
            "Health", "Fitness", "Learning", "Reading",
            "Writing", "Music"
        ]

        for i, label_text in enumerate(labels):
            ctk.CTkLabel(win, text=label_text, text_color=self.fg_color, font=("TkDefaultFont", 13)).grid(
                row=i + 1, column=0, padx=20, pady=8, sticky="e"
            )
            if i == 2:
                option = ctk.CTkOptionMenu(win, values=category_options, width=300, height=32, font=self.font)
                option.set("Work")
                option.grid(row=i + 1, column=1, padx=40, pady=5, sticky="ew")
                entries.append(option)
            elif i == 3:
                entry = ctk.CTkEntry(
                    win,
                    width=300,
                    height=32,
                    font=self.font,
                    corner_radius=6,
                    border_width=1,
                    placeholder_text="DD.MM.YYYY"
                )
                entry.grid(row=i + 1, column=1, padx=40, pady=5, sticky="ew")
                entries.append(entry)
            else:
                placeholder = "Enter Your Task Name" if i == 0 else "Enter Your Task Details"
                entry = ctk.CTkEntry(
                    win, width=300, height=32,
                    font=self.font,
                    corner_radius=6,
                    border_width=1,
                    placeholder_text=placeholder
                )
                entry.grid(row=i + 1, column=1, padx=40, pady=5, sticky="ew")
                entries.append(entry)
        
        entries[0].focus()
        
        def save():
            title = entries[0].get().strip()
            desc = entries[1].get().strip()
            cat = entries[2].get().strip()
            raw_due = entries[3].get().strip()

            if not title or not cat:
                messagebox.showwarning("Missing Information", "Task name and Category are required.", parent=win)
                return

            if title:
                title = title.capitalize()

            if desc:
                desc = desc.capitalize()
                if desc[-1] not in ".!?":
                    desc += "."

            due = ""
            if raw_due:
                try:
                    parsed = datetime.datetime.strptime(raw_due, "%d.%m.%Y")
                    due = parsed.strftime("%b %d, %Y").replace(" 0", " ")
                except ValueError:
                    messagebox.showwarning("Invalid Date Format", "Please enter date as DD.MM.YYYY", parent=win)
                    return

            self.tasks.append(Task(title, desc, cat, due))
            save_tasks(self.tasks)
            self.refresh_tasks()
            win.destroy()

        def cancel():
            win.destroy()
        
        button_frame = ctk.CTkFrame(win, fg_color="transparent")
        button_frame.grid(row=len(labels) + 2, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(
            button_frame, text="Cancel",
            command=cancel,
            fg_color=("#6B7280", "#4B5563"),
            hover_color=("#4B5563", "#374151"),
            text_color="white",
            font=("TkDefaultFont", 13),
            width=100, height=36,
            corner_radius=6
        ).grid(row=0, column=0, padx=10)
        
        ctk.CTkButton(
            button_frame, text="Save Task",
            command=save,
            fg_color="#506EEC",
            hover_color="#3E5CE1",
            text_color="white",
            font=("TkDefaultFont", 13),
            width=100, height=36,
            corner_radius=6
        ).grid(row=0, column=1, padx=10)
        
        win.bind("<Return>", lambda event: save())
        win.bind("<Escape>", lambda event: cancel())

if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1020x420")
    app = ToDoApp(root)
    root.mainloop()
