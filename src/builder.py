import tkinter as tk
from tkinter import ttk, messagebox


class ServiceBuilder(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Service Builder")
        self.geometry("800x600")

        # Divine Service Selection
        tk.Label(self, text="Select Divine Service:").pack(pady=5)
        self.service_selector = ttk.Combobox(self, values=["Divine Service I", "Divine Service II", "Vespers", "Matins"])
        self.service_selector.set("Select a Service")
        self.service_selector.pack(pady=5)

        # Hymn Slots (TreeView)
        tk.Label(self, text="Hymn Slots:").pack(pady=5)
        self.hymn_tree = ttk.Treeview(self, columns=("Details"), show="tree")
        self.hymn_tree.heading("#0", text="Hymn Slots")
        self.hymn_tree.heading("Details", text="Details")
        self.hymn_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Adding predefined slots
        slots = ["Opening Hymn", "Hymn of the Day", "Communion Hymn", "Closing Hymn"]
        for slot in slots:
            self.hymn_tree.insert("", "end", slot, text=slot, values=("Prefill Placeholder",))

        # Buttons for Actions
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        add_button = tk.Button(button_frame, text="Add Hymn", command=self.add_hymn)
        add_button.grid(row=0, column=0, padx=5)

        remove_button = tk.Button(button_frame, text="Remove Hymn", command=self.remove_hymn)
        remove_button.grid(row=0, column=1, padx=5)

        save_button = tk.Button(button_frame, text="Save Service", command=self.save_service)
        save_button.grid(row=0, column=2, padx=5)

        # Enable drag and drop later, if desired.

    def add_hymn(self):
        """Add a hymn to the selected slot."""
        selected_item = self.hymn_tree.focus()
        if selected_item:
            hymn_name = tk.simpledialog.askstring("Add Hymn", "Enter hymn name:")
            if hymn_name:
                self.hymn_tree.item(selected_item, values=(hymn_name,))
        else:
            messagebox.showwarning("No Selection", "Please select a hymn slot first.")

    def remove_hymn(self):
        """Remove the hymn from the selected slot."""
        selected_item = self.hymn_tree.focus()
        if selected_item:
            self.hymn_tree.item(selected_item, values=("Prefill Placeholder",))
        else:
            messagebox.showwarning("No Selection", "Please select a hymn slot first.")

    def save_service(self):
        """Save the service structure."""
        service_name = self.service_selector.get()
        if service_name == "Select a Service":
            messagebox.showwarning("No Service Selected", "Please select a divine service.")
            return

        hymns = []
        for child in self.hymn_tree.get_children():
            slot = self.hymn_tree.item(child, "text")
            hymn = self.hymn_tree.item(child, "values")[0]
            hymns.append((slot, hymn))

        # Example of processing saved data
        print(f"Service: {service_name}")
        for slot, hymn in hymns:
            print(f"  {slot}: {hymn}")

        messagebox.showinfo("Service Saved", "The service has been saved successfully!")


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Main App")
        self.geometry("400x200")

        open_service_builder = tk.Button(self, text="Open Service Builder", command=self.open_service_builder)
        open_service_builder.pack(pady=50)

    def open_service_builder(self):
        ServiceBuilder(self)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
