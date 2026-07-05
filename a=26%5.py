import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
class Patient:
    CRITICAL_KEYWORDS = [
        "chest pain",
        "stroke",
        "unconscious",
        "breathing",
        "severe bleeding",
        "seizure"
    ]
    def __init__(self, pid, name, age, gender, symptoms,
                 temperature, heart_rate, oxygen,
                 systolic, diastolic, pain_level,
                 status="Waiting", arrival_time=None):
        self.pid = pid
        self.name = name
        self.age = int(age)
        self.gender = gender
        self.symptoms = symptoms
        self._temperature = float(temperature)
        self._heart_rate = int(heart_rate)
        self._oxygen = int(oxygen)
        self._systolic = int(systolic)
        self._diastolic = int(diastolic)
        self.pain_level = int(pain_level)
        self.status = status
        self.arrival_time = arrival_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.score = self.calculate_score()
        self.priority = self.get_priority()
        self.department = self.assign_department()
        self.category = self.get_patient_category()
    def calculate_score(self):
        score = 0
        if self._oxygen < 90:
            score += 50
        elif self._oxygen < 95:
            score += 20
        if self._heart_rate > 130 or self._heart_rate < 45:
            score += 30
        elif self._heart_rate > 100:
            score += 15
        if self._temperature > 39:
            score += 20
        elif self._temperature > 38:
            score += 10
        if self._systolic >= 180 or self._diastolic >= 120:
            score += 35
        elif self._systolic >= 140 or self._diastolic >= 90:
            score += 15
        if self.pain_level >= 8:
            score += 20
        elif self.pain_level >= 5:
            score += 10
        if self.age >= 65:
            score += 20
        elif self.age <= 5:
            score += 15
        for word in self.CRITICAL_KEYWORDS:
            if word in self.symptoms.lower():
                score += 40
        return score
    def get_priority(self):
        if self.score >= 80:
            return "Critical"
        elif self.score >= 50:
            return "High"
        elif self.score >= 30:
            return "Medium"
        return "Low"
    def assign_department(self):
        symptoms = self.symptoms.lower()
        if "chest pain" in symptoms:
            return "Cardiology"
        elif "stroke" in symptoms or "seizure" in symptoms:
            return "Neurology"
        elif "breathing" in symptoms:
            return "Pulmonology"
        elif "bleeding" in symptoms:
            return "Emergency Surgery"
        elif "fever" in symptoms:
            return "General Medicine"
        else:
            return "Emergency"
    def get_patient_category(self):
        if self.age <= 12:
            return "Child"
        elif self.age >= 65:
            return "Senior"
        return "Adult"
    def bp_text(self):
        return f"{self._systolic}/{self._diastolic}"
    def waiting_time(self):
        try:
            arrival = datetime.strptime(self.arrival_time, "%Y-%m-%d %H:%M:%S")
            diff = datetime.now() - arrival
            minutes = int(diff.total_seconds() // 60)
            return f"{minutes} min"
        except Exception:
            return "N/A"
    def to_list(self):
        return [
            self.pid,
            self.name,
            self.age,
            self.gender,
            self.symptoms,
            self._temperature,
            self._heart_rate,
            self._oxygen,
            self._systolic,
            self._diastolic,
            self.pain_level,
            self.priority,
            self.score,
            self.status,
            self.department,
            self.category,
            self.arrival_time
        ]
class EmergencyPatient(Patient):
    def get_priority(self):
        symptoms = self.symptoms.lower()
        for word in self.CRITICAL_KEYWORDS:
            if word in symptoms:
                return "Critical"
        return super().get_priority()
class TriageSystem:
    def __init__(self):
        self.patients = []
        self.history = []
    def add_patient(self, patient):
        if self.search_patient(patient.pid):
            return False
        self.patients.append(patient)
        self.history.append(
            f"{datetime.now().strftime('%H:%M:%S')} : Added {patient.name} as {patient.priority}"
        )
        return True
    def search_patient(self, pid):
        for patient in self.patients:
            if patient.pid == pid:
                return patient
        return None
    def delete_patient(self, pid):
        patient = self.search_patient(pid)
        if patient:
            self.patients.remove(patient)
            self.history.append(
                f"{datetime.now().strftime('%H:%M:%S')} : Deleted {patient.name}"
            )
            return True
        return False
    def update_status(self, pid, status):
        patient = self.search_patient(pid)
        if patient:
            patient.status = status
            self.history.append(
                f"{datetime.now().strftime('%H:%M:%S')} : Updated {patient.name} status to {status}"
            )
            return True
        return False
    def get_sorted_patients(self, filter_priority="All"):
        order = {
            "Critical": 1,
            "High": 2,
            "Medium": 3,
            "Low": 4
        }
        patients = self.patients
        if filter_priority != "All":
            patients = [p for p in patients if p.priority == filter_priority]
        return sorted(
            patients,
            key=lambda p: (order[p.priority], -p.score)
        )
    def count_priorities(self):
        counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0
        }
        for patient in self.patients:
            counts[patient.priority] += 1
        return counts
    def save_to_csv(self, file_path):
        headings = [
            "Patient ID",
            "Name",
            "Age",
            "Gender",
            "Symptoms",
            "Temperature",
            "Heart Rate",
            "Oxygen",
            "Systolic BP",
            "Diastolic BP",
            "Pain Level",
            "Priority",
            "Score",
            "Status",
            "Department",
            "Category",
            "Arrival Time"
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headings)
            for patient in self.patients:
                writer.writerow(patient.to_list())
    def load_from_csv(self, file_path):
        self.patients.clear()
        self.history.clear()
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                symptoms = row["Symptoms"]
                if any(word in symptoms.lower() for word in Patient.CRITICAL_KEYWORDS):
                    patient = EmergencyPatient(
                        row["Patient ID"],
                        row["Name"],
                        row["Age"],
                        row["Gender"],
                        row["Symptoms"],
                        row["Temperature"],
                        row["Heart Rate"],
                        row["Oxygen"],
                        row["Systolic BP"],
                        row["Diastolic BP"],
                        row["Pain Level"],
                        row["Status"],
                        row["Arrival Time"]
                    )
                else:
                    patient = Patient(
                        row["Patient ID"],
                        row["Name"],
                        row["Age"],
                        row["Gender"],
                        row["Symptoms"],
                        row["Temperature"],
                        row["Heart Rate"],
                        row["Oxygen"],
                        row["Systolic BP"],
                        row["Diastolic BP"],
                        row["Pain Level"],
                        row["Status"],
                        row["Arrival Time"]
                    )
                self.patients.append(patient)
        self.history.append(
            f"{datetime.now().strftime('%H:%M:%S')} : Loaded patient records from file"
        )
    def generate_report(self):
        counts = self.count_priorities()
        total = len(self.patients)
        report = "SMART EMERGENCY ROOM TRIAGE REPORT\n"
        report += "-" * 55 + "\n"
        report += f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Total Patients: {total}\n\n"
        report += "Priority Summary:\n"
        report += f"Critical Patients: {counts['Critical']}\n"
        report += f"High Priority Patients: {counts['High']}\n"
        report += f"Medium Priority Patients: {counts['Medium']}\n"
        report += f"Low Priority Patients: {counts['Low']}\n\n"
        report += "Top Priority Patients:\n"
        report += "-" * 55 + "\n"
        for patient in self.get_sorted_patients()[:10]:
            report += (
                f"{patient.pid} | {patient.name} | {patient.priority} | "
                f"Score: {patient.score} | Status: {patient.status} | "
                f"Department: {patient.department}\n"
            )
        return report
class SmartERGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Emergency Room Triage System")
        self.root.geometry("1450x800")
        self.root.configure(bg="#eef3f8")
        self.system = TriageSystem()
        self.entries = {}
        self.count_labels = {}
        self.filter_var = tk.StringVar(value="All")
        self.setup_style()
        self.create_header()
        self.create_form()
        self.create_buttons()
        self.create_dashboard()
        self.create_filter()
        self.create_table()
        self.create_history()
    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="white",
            foreground="#1f2937",
            rowheight=28,
            fieldbackground="white",
            font=("Arial", 10)
        )
        style.configure(
            "Treeview.Heading",
            background="#1e3a8a",
            foreground="white",
            font=("Arial", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "white")]
        )
    def create_header(self):
        header = tk.Frame(self.root, bg="#1e3a8a", height=85)
        header.pack(fill="x")
        title = tk.Label(
            header,
            text="SMART EMERGENCY ROOM TRIAGE SYSTEM",
            font=("Arial", 24, "bold"),
            bg="#1e3a8a",
            fg="white"
        )
        title.pack(pady=(10, 0))

        subtitle = tk.Label(
            header,
            text="AI-inspired patient prioritization and emergency dashboard",
            font=("Arial", 12),
            bg="#1e3a8a",
            fg="#dbeafe"
        )
        subtitle.pack()
    def create_form(self):
        frame = tk.LabelFrame(
            self.root,
            text="Patient Registration",
            font=("Arial", 12, "bold"),
            bg="#f8fafc",
            fg="#1e3a8a",
            padx=10,
            pady=10
        )
        frame.pack(fill="x", padx=10, pady=8)
        labels = [
            "Patient ID",
            "Name",
            "Age",
            "Gender",
            "Symptoms",
            "Temperature",
            "Heart Rate",
            "Oxygen Level",
            "Systolic BP",
            "Diastolic BP",
            "Pain Level",
            "Status"
        ]
        for i, text in enumerate(labels):
            row = i // 4
            col = (i % 4) * 2
            label = tk.Label(
                frame,
                text=text,
                bg="#f8fafc",
                fg="#111827",
                font=("Arial", 10, "bold")
            )
            label.grid(row=row, column=col, padx=8, pady=6, sticky="w")
            if text == "Gender":
                entry = ttk.Combobox(
                    frame,
                    values=["Male", "Female", "Other"],
                    state="readonly",
                    width=23
                )
                entry.set("Male")
            elif text == "Pain Level":
                entry = tk.Spinbox(
                    frame,
                    from_=0,
                    to=10,
                    width=25
                )
            elif text == "Status":
                entry = ttk.Combobox(
                    frame,
                    values=["Waiting", "Under Treatment", "Discharged"],
                    state="readonly",
                    width=23
                )
                entry.set("Waiting")
            else:
                entry = tk.Entry(frame, width=26)
            entry.grid(row=row, column=col + 1, padx=8, pady=6)
            self.entries[text] = entry
    def create_buttons(self):
        frame = tk.Frame(self.root, bg="#eef3f8")
        frame.pack(pady=8)
        buttons = [
            ("Add Patient", self.add_patient, "#16a34a"),
            ("Search Patient", self.search_patient, "#2563eb"),
            ("Delete Patient", self.delete_patient, "#dc2626"),
            ("Update Status", self.update_status, "#9333ea"),
            ("Discharge", self.discharge_patient, "#0f766e"),
            ("Clear Fields", self.clear_fields, "#64748b"),
            ("Save CSV", self.save_csv, "#0891b2"),
            ("Load CSV", self.load_csv, "#7c3aed"),
            ("Report", self.show_report, "#f97316"),
            ("Export Report", self.export_report, "#ca8a04")
        ]
        for i, (text, command, color) in enumerate(buttons):
            tk.Button(
                frame,
                text=text,
                width=14,
                command=command,
                bg=color,
                fg="white",
                font=("Arial", 9, "bold"),
                relief="raised",
                bd=2
            ).grid(row=0, column=i, padx=4)
    def create_dashboard(self):
        frame = tk.Frame(self.root, bg="#eef3f8")
        frame.pack(fill="x", padx=10, pady=10)
        cards = [
            ("Total Patients", "Total", "#2563eb"),
            ("Critical", "Critical", "#dc2626"),
            ("High Priority", "High", "#f97316"),
            ("Medium Priority", "Medium", "#ca8a04"),
            ("Low Priority", "Low", "#16a34a")
        ]
        for i, (title, key, color) in enumerate(cards):
            card = tk.Frame(
                frame,
                bg=color,
                width=250,
                height=90,
                relief="raised",
                bd=2
            )
            card.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            card.grid_propagate(False)

            title_label = tk.Label(
                card,
                text=title,
                font=("Arial", 11, "bold"),
                bg=color,
                fg="white"
            )
            title_label.pack(pady=(12, 0))
            count_label = tk.Label(
                card,
                text="0",
                font=("Arial", 24, "bold"),
                bg=color,
                fg="white"
            )
            count_label.pack()
            self.count_labels[key] = count_label
        for i in range(5):
            frame.columnconfigure(i, weight=1)
    def create_filter(self):
        frame = tk.Frame(self.root, bg="#eef3f8")
        frame.pack(fill="x", padx=10, pady=2)
        tk.Label(
            frame,
            text="Filter by Priority:",
            bg="#eef3f8",
            fg="#111827",
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=5)
        filter_box = ttk.Combobox(
            frame,
            values=["All", "Critical", "High", "Medium", "Low"],
            state="readonly",
            textvariable=self.filter_var,
            width=18
        )
        filter_box.pack(side="left", padx=5)
        filter_box.bind("<<ComboboxSelected>>", lambda event: self.update_table())
    def create_table(self):
        frame = tk.LabelFrame(
            self.root,
            text="Priority Queue",
            font=("Arial", 12, "bold"),
            bg="#f8fafc",
            fg="#1e3a8a"
        )
        frame.pack(fill="both", expand=True, padx=10, pady=5)
        cols = (
            "ID",
            "Name",
            "Age",
            "Gender",
            "Category",
            "Temp",
            "HR",
            "Oxygen",
            "BP",
            "Pain",
            "Priority",
            "Score",
            "Status",
            "Department",
            "Waiting",
            "Arrival Time"
        )
        self.tree = ttk.Treeview(
            frame,
            columns=cols,
            show="headings",
            height=12
        )
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90)
        self.tree.column("Name", width=130)
        self.tree.column("Department", width=130)
        self.tree.column("Arrival Time", width=160)
        self.tree.tag_configure("Critical", background="#fecaca")
        self.tree.tag_configure("High", background="#fed7aa")
        self.tree.tag_configure("Medium", background="#fef9c3")
        self.tree.tag_configure("Low", background="#bbf7d0")
        scrollbar_y = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
    def create_history(self):
        frame = tk.LabelFrame(
            self.root,
            text="System History",
            font=("Arial", 12, "bold"),
            bg="#f8fafc",
            fg="#1e3a8a"
        )
        frame.pack(fill="x", padx=10, pady=5)
        self.history_box = tk.Text(
            frame,
            height=6,
            bg="#111827",
            fg="#d1fae5",
            font=("Consolas", 10)
        )
        self.history_box.pack(fill="x")
    def validate_inputs(self, age, temp, hr, oxygen, systolic, diastolic, pain):
        age = int(age)
        temp = float(temp)
        hr = int(hr)
        oxygen = int(oxygen)
        systolic = int(systolic)
        diastolic = int(diastolic)
        pain = int(pain)
        if age < 0 or age > 120:
            return False, "Age must be between 0 and 120."
        if temp < 90 or temp > 110:
            return False, "Temperature must be between 30 and 45."
        if hr < 20 or hr > 250:
            return False, "Heart rate must be between 20 and 250."
        if oxygen < 0 or oxygen > 100:
            return False, "Oxygen level must be between 0 and 100."
        if systolic < 50 or systolic > 250:
            return False, "Systolic BP must be between 50 and 250."
        if diastolic < 30 or diastolic > 160:
            return False, "Diastolic BP must be between 30 and 160."
        if pain < 0 or pain > 10:
            return False, "Pain level must be between 0 and 10."
        return True, "Valid"
    def add_patient(self):
        try:
            pid = self.entries["Patient ID"].get().strip()
            name = self.entries["Name"].get().strip()
            age = self.entries["Age"].get().strip()
            gender = self.entries["Gender"].get()
            symptoms = self.entries["Symptoms"].get().strip()
            temp = self.entries["Temperature"].get().strip()
            hr = self.entries["Heart Rate"].get().strip()
            oxygen = self.entries["Oxygen Level"].get().strip()
            systolic = self.entries["Systolic BP"].get().strip()
            diastolic = self.entries["Diastolic BP"].get().strip()
            pain = self.entries["Pain Level"].get()
            status = self.entries["Status"].get()
            if not all([pid, name, age, gender, symptoms, temp, hr, oxygen, systolic, diastolic]):
                messagebox.showerror("Error", "Please fill all fields.")
                return
            valid, message = self.validate_inputs(
                age, temp, hr, oxygen, systolic, diastolic, pain
            )
            if not valid:
                messagebox.showerror("Invalid Data", message)
                return
            if any(word in symptoms.lower() for word in Patient.CRITICAL_KEYWORDS):
                patient = EmergencyPatient(
                    pid, name, age, gender, symptoms,
                    temp, hr, oxygen, systolic, diastolic, pain, status
                )
            else:
                patient = Patient(
                    pid, name, age, gender, symptoms,
                    temp, hr, oxygen, systolic, diastolic, pain, status
                )
            if not self.system.add_patient(patient):
                messagebox.showerror("Error", "Patient ID already exists.")
                return
            self.update_table()
            self.update_dashboard()
            self.update_history()
            messagebox.showinfo(
                "Patient Added",
                f"Priority: {patient.priority}\n"
                f"Risk Score: {patient.score}\n"
                f"Department: {patient.department}"
            )
            self.clear_fields()
        except ValueError:
            messagebox.showerror(
                "Error",
                "Please enter correct numeric values."
            )
    def search_patient(self):
        pid = self.entries["Patient ID"].get().strip()
        if not pid:
            messagebox.showwarning("Missing ID", "Enter Patient ID to search.")
            return
        patient = self.system.search_patient(pid)
        if patient:
            messagebox.showinfo(
                "Patient Found",
                f"ID: {patient.pid}\n"
                f"Name: {patient.name}\n"
                f"Age: {patient.age}\n"
                f"Gender: {patient.gender}\n"
                f"Category: {patient.category}\n"
                f"Symptoms: {patient.symptoms}\n"
                f"Temperature: {patient._temperature}\n"
                f"Heart Rate: {patient._heart_rate}\n"
                f"Oxygen: {patient._oxygen}\n"
                f"BP: {patient.bp_text()}\n"
                f"Pain Level: {patient.pain_level}\n"
                f"Priority: {patient.priority}\n"
                f"Score: {patient.score}\n"
                f"Department: {patient.department}\n"
                f"Status: {patient.status}\n"
                f"Waiting Time: {patient.waiting_time()}"
            )
        else:
            messagebox.showwarning("Not Found", "Patient not found.")
    def delete_patient(self):
        pid = self.entries["Patient ID"].get().strip()
        if not pid:
            messagebox.showwarning("Missing ID", "Enter Patient ID to delete.")
            return
        if self.system.delete_patient(pid):
            self.update_table()
            self.update_dashboard()
            self.update_history()
            messagebox.showinfo("Deleted", "Patient record deleted.")
        else:
            messagebox.showerror("Error", "Patient not found.")
    def update_status(self):
        pid = self.entries["Patient ID"].get().strip()
        status = self.entries["Status"].get()
        if not pid:
            messagebox.showwarning("Missing ID", "Enter Patient ID to update status.")
            return
        if self.system.update_status(pid, status):
            self.update_table()
            self.update_history()
            messagebox.showinfo("Updated", "Patient status updated.")
        else:
            messagebox.showerror("Error", "Patient not found.")
    def discharge_patient(self):
        pid = self.entries["Patient ID"].get().strip()
        if not pid:
            messagebox.showwarning("Missing ID", "Enter Patient ID to discharge.")
            return
        if self.system.update_status(pid, "Discharged"):
            self.update_table()
            self.update_history()
            messagebox.showinfo("Discharged", "Patient marked as discharged.")
        else:
            messagebox.showerror("Error", "Patient not found.")
    def update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        selected_filter = self.filter_var.get()
        for patient in self.system.get_sorted_patients(selected_filter):
            self.tree.insert(
                "",
                "end",
                values=(
                    patient.pid,
                    patient.name,
                    patient.age,
                    patient.gender,
                    patient.category,
                    patient._temperature,
                    patient._heart_rate,
                    patient._oxygen,
                    patient.bp_text(),
                    patient.pain_level,
                    patient.priority,
                    patient.score,
                    patient.status,
                    patient.department,
                    patient.waiting_time(),
                    patient.arrival_time
                ),
                tags=(patient.priority,)
            )
    def update_dashboard(self):
        counts = self.system.count_priorities()
        total = len(self.system.patients)
        self.count_labels["Total"].config(text=str(total))
        self.count_labels["Critical"].config(text=str(counts["Critical"]))
        self.count_labels["High"].config(text=str(counts["High"]))
        self.count_labels["Medium"].config(text=str(counts["Medium"]))
        self.count_labels["Low"].config(text=str(counts["Low"]))
    def update_history(self):
        self.history_box.delete("1.0", tk.END)
        for item in self.system.history:
            self.history_box.insert(tk.END, item + "\n")
    def clear_fields(self):
        for key, entry in self.entries.items():
            if key == "Gender":
                entry.set("Male")
            elif key == "Status":
                entry.set("Waiting")
            elif key == "Pain Level":
                entry.delete(0, tk.END)
                entry.insert(0, "0")
            else:
                entry.delete(0, tk.END)
    def save_csv(self):
        if not self.system.patients:
            messagebox.showwarning("No Data", "No patient records to save.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_path:
            self.system.save_to_csv(file_path)
            messagebox.showinfo("Saved", "Patient records saved successfully.")
    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_path:
            try:
                self.system.load_from_csv(file_path)
                self.update_table()
                self.update_dashboard()
                self.update_history()
                messagebox.showinfo("Loaded", "Patient records loaded successfully.")
            except Exception:
                messagebox.showerror("Error", "Could not load file.")
    def show_report(self):
        report = self.system.generate_report()
        report_window = tk.Toplevel(self.root)
        report_window.title("Triage Report")
        report_window.geometry("700x500")
        report_window.configure(bg="#eef3f8")
        text_box = tk.Text(
            report_window,
            wrap="word",
            bg="white",
            fg="#111827",
            font=("Consolas", 11)
        )
        text_box.pack(fill="both", expand=True, padx=10, pady=10)
        text_box.insert(tk.END, report)
        text_box.config(state="disabled")
    def export_report(self):
        if not self.system.patients:
            messagebox.showwarning("No Data", "No patient records available.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            report = self.system.generate_report()
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(report)
            messagebox.showinfo("Exported", "Report exported successfully.")
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartERGUI(root)
    root.mainloop()