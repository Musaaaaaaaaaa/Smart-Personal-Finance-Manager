import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt

class FinanceManager:
  def __init__(self, file_name):
    self.file_name = file_name
    self.data = self.load_data()

  def load_data(self):
    if os.path.exists(self.file_name):
      with open(self.file_name, "r") as file:
        try:
          data = json.load(file)
          if isinstance(data, dict) and "users" in data:
            return data
          else:
            return {"users": {}}
        except json.JSONDecodeError:
          return {"users": {}}
    else:
      return {"users": {}}

  def save_data(self):
    with open(self.file_name, "w") as file:
      json.dump(self.data, file, indent=4)

  def create_user(self, username, password):
    if username in self.data["users"]:
      return False

    self.data["users"][username] = {
      "password": password,
      "balance": 0.0,
      "transactions": [],
      "budgets": {}
    }
    self.save_data()
    return True

  def authenticate_user(self, username, password):
    if username in self.data["users"]:
      return self.data["users"][username]["password"] == password
    return False

  def get_user_data(self, username):
    return self.data["users"].get(username)

  def add_transaction(self, username, transaction_type, amount, category, description):
    user = self.data["users"][username]

    transaction = {
      "type": transaction_type,
      "amount": amount,
      "category": category,
      "description": description,
      "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    user["transactions"].append(transaction)

    if transaction_type == "Income":
      user["balance"] += amount
    elif transaction_type == "Expense":
      user["balance"] -= amount

    self.save_data()

  def set_budget(self, username, category, amount):
    self.data["users"][username]["budgets"][category] = amount
    self.save_data()

  def get_total_spending_by_category(self, username):
    user = self.data["users"][username]
    spending = {}

    for transaction in user["transactions"]:
      if transaction["type"] == "Expense":
        category = transaction["category"]
        amount = transaction["amount"]

        if category in spending:
          spending[category] += amount
        else:
          spending[category] = amount

    return spending

  def get_budget_report(self, username):
    user = self.data["users"][username]
    budgets = user["budgets"]
    spending = self.get_total_spending_by_category(username)

    report = []

    for category in budgets:
      budget_amount = budgets[category]
      spent_amount = spending.get(category, 0)
      remaining = budget_amount - spent_amount

      report.append((category, budget_amount, spent_amount, remaining))

    return report


class FinanceApp:
  def __init__(self, root):
    self.root = root
    self.root.title("Smart Personal Finance Manager")
    self.root.geometry("950x650")

    self.manager = FinanceManager("finance_data.json")
    self.current_user = None

    self.build_login_screen()

  def clear_window(self):
    for widget in self.root.winfo_children():
      widget.destroy()

  def build_login_screen(self):
    self.clear_window()

    title = tk.Label(self.root, text="Smart Personal Finance Manager", font=("Arial", 20, "bold"))
    title.pack(pady=20)

    frame = tk.Frame(self.root)
    frame.pack(pady=20)

    username_label = tk.Label(frame, text="Username:")
    username_label.grid(row=0, column=0, padx=10, pady=10)

    self.username_entry = tk.Entry(frame, width=25)
    self.username_entry.grid(row=0, column=1, padx=10, pady=10)

    password_label = tk.Label(frame, text="Password:")
    password_label.grid(row=1, column=0, padx=10, pady=10)

    self.password_entry = tk.Entry(frame, width=25, show="*")
    self.password_entry.grid(row=1, column=1, padx=10, pady=10)

    login_button = tk.Button(self.root, text="Login", width=15, command=self.login)
    login_button.pack(pady=10)

    create_button = tk.Button(self.root, text="Create Account", width=15, command=self.create_account)
    create_button.pack(pady=10)

  def login(self):
    username = self.username_entry.get()
    password = self.password_entry.get()

    if self.manager.authenticate_user(username, password):
      self.current_user = username
      self.build_dashboard()
    else:
      messagebox.showerror("Error", "Invalid username or password.")

  def create_account(self):
    username = self.username_entry.get()
    password = self.password_entry.get()

    if username == "" or password == "":
      messagebox.showerror("Error", "Please enter both username and password.")
      return

    if self.manager.create_user(username, password):
      messagebox.showinfo("Success", "Account created successfully.")
    else:
      messagebox.showerror("Error", "Username already exists.")

  def build_dashboard(self):
    self.clear_window()

    top_frame = tk.Frame(self.root)
    top_frame.pack(fill="x", pady=10)

    welcome_label = tk.Label(top_frame, text="Welcome, " + self.current_user, font=("Arial", 16, "bold"))
    welcome_label.pack(side="left", padx=20)

    logout_button = tk.Button(top_frame, text="Logout", command=self.logout)
    logout_button.pack(side="right", padx=20)

    self.balance_label = tk.Label(self.root, text="", font=("Arial", 14, "bold"))
    self.balance_label.pack(pady=10)

    button_frame = tk.Frame(self.root)
    button_frame.pack(pady=10)

    add_transaction_button = tk.Button(button_frame, text="Add Transaction", width=18, command=self.open_transaction_window)
    add_transaction_button.grid(row=0, column=0, padx=10)

    set_budget_button = tk.Button(button_frame, text="Set Budget", width=18, command=self.open_budget_window)
    set_budget_button.grid(row=0, column=1, padx=10)

    chart_button = tk.Button(button_frame, text="Show Spending Chart", width=18, command=self.show_chart)
    chart_button.grid(row=0, column=2, padx=10)

    refresh_button = tk.Button(button_frame, text="Refresh", width=18, command=self.refresh_dashboard)
    refresh_button.grid(row=0, column=3, padx=10)

    transactions_label = tk.Label(self.root, text="Transaction History", font=("Arial", 13, "bold"))
    transactions_label.pack(pady=(20, 5))

    self.transaction_tree = ttk.Treeview(
      self.root,
      columns=("Type", "Amount", "Category", "Description", "Date"),
      show="headings",
      height=10
    )

    self.transaction_tree.heading("Type", text="Type")
    self.transaction_tree.heading("Amount", text="Amount")
    self.transaction_tree.heading("Category", text="Category")
    self.transaction_tree.heading("Description", text="Description")
    self.transaction_tree.heading("Date", text="Date")

    self.transaction_tree.column("Type", width=100)
    self.transaction_tree.column("Amount", width=100)
    self.transaction_tree.column("Category", width=120)
    self.transaction_tree.column("Description", width=200)
    self.transaction_tree.column("Date", width=180)

    self.transaction_tree.pack(pady=5)

    budget_label = tk.Label(self.root, text="Budget Report", font=("Arial", 13, "bold"))
    budget_label.pack(pady=(20, 5))

    self.budget_tree = ttk.Treeview(
      self.root,
      columns=("Category", "Budget", "Spent", "Remaining"),
      show="headings",
      height=8
    )

    self.budget_tree.heading("Category", text="Category")
    self.budget_tree.heading("Budget", text="Budget")
    self.budget_tree.heading("Spent", text="Spent")
    self.budget_tree.heading("Remaining", text="Remaining")

    self.budget_tree.column("Category", width=150)
    self.budget_tree.column("Budget", width=120)
    self.budget_tree.column("Spent", width=120)
    self.budget_tree.column("Remaining", width=120)

    self.budget_tree.pack(pady=5)

    self.refresh_dashboard()

  def refresh_dashboard(self):
    user = self.manager.get_user_data(self.current_user)

    self.balance_label.config(text="Current Balance: $" + format(user["balance"], ".2f"))

    for item in self.transaction_tree.get_children():
      self.transaction_tree.delete(item)

    for transaction in user["transactions"]:
      self.transaction_tree.insert(
        "",
        "end",
        values=(
          transaction["type"],
          "$" + format(transaction["amount"], ".2f"),
          transaction["category"],
          transaction["description"],
          transaction["date"]
        )
      )

    for item in self.budget_tree.get_children():
      self.budget_tree.delete(item)

    report = self.manager.get_budget_report(self.current_user)

    for row in report:
      category, budget, spent, remaining = row
      self.budget_tree.insert(
        "",
        "end",
        values=(
          category,
          "$" + format(budget, ".2f"),
          "$" + format(spent, ".2f"),
          "$" + format(remaining, ".2f")
        )
      )

  def logout(self):
    self.current_user = None
    self.build_login_screen()

  def open_transaction_window(self):
    transaction_window = tk.Toplevel(self.root)
    transaction_window.title("Add Transaction")
    transaction_window.geometry("350x300")

    type_label = tk.Label(transaction_window, text="Transaction Type:")
    type_label.pack(pady=5)

    type_combo = ttk.Combobox(transaction_window, values=["Income", "Expense"], state="readonly")
    type_combo.pack(pady=5)
    type_combo.set("Expense")

    amount_label = tk.Label(transaction_window, text="Amount:")
    amount_label.pack(pady=5)

    amount_entry = tk.Entry(transaction_window)
    amount_entry.pack(pady=5)

    category_label = tk.Label(transaction_window, text="Category:")
    category_label.pack(pady=5)

    category_entry = tk.Entry(transaction_window)
    category_entry.pack(pady=5)

    description_label = tk.Label(transaction_window, text="Description:")
    description_label.pack(pady=5)

    description_entry = tk.Entry(transaction_window)
    description_entry.pack(pady=5)

    def save_transaction():
      try:
        amount = float(amount_entry.get())
        if amount <= 0:
          messagebox.showerror("Error", "Amount must be greater than 0.")
          return
      except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")
        return

      category = category_entry.get()
      description = description_entry.get()
      transaction_type = type_combo.get()

      if category == "":
        messagebox.showerror("Error", "Please enter a category.")
        return

      self.manager.add_transaction(
        self.current_user,
        transaction_type,
        amount,
        category,
        description
      )

      self.refresh_dashboard()
      transaction_window.destroy()

    save_button = tk.Button(transaction_window, text="Save", command=save_transaction)
    save_button.pack(pady=15)

  def open_budget_window(self):
    budget_window = tk.Toplevel(self.root)
    budget_window.title("Set Budget")
    budget_window.geometry("300x220")

    category_label = tk.Label(budget_window, text="Category:")
    category_label.pack(pady=5)

    category_entry = tk.Entry(budget_window)
    category_entry.pack(pady=5)

    amount_label = tk.Label(budget_window, text="Budget Amount:")
    amount_label.pack(pady=5)

    amount_entry = tk.Entry(budget_window)
    amount_entry.pack(pady=5)

    def save_budget():
      category = category_entry.get()

      try:
        amount = float(amount_entry.get())
        if amount <= 0:
          messagebox.showerror("Error", "Budget must be greater than 0.")
          return
      except ValueError:
        messagebox.showerror("Error", "Please enter a valid number.")
        return

      if category == "":
        messagebox.showerror("Error", "Please enter a category.")
        return

      self.manager.set_budget(self.current_user, category, amount)
      self.refresh_dashboard()
      budget_window.destroy()

    save_button = tk.Button(budget_window, text="Save Budget", command=save_budget)
    save_button.pack(pady=15)

  def show_chart(self):
    spending = self.manager.get_total_spending_by_category(self.current_user)

    if len(spending) == 0:
      messagebox.showinfo("No Data", "No expense data available.")
      return

    categories = list(spending.keys())
    amounts = list(spending.values())

    plt.figure(figsize=(8, 5))
    plt.bar(categories, amounts)
    plt.title("Spending by Category")
    plt.xlabel("Category")
    plt.ylabel("Amount Spent ($)")
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()


root = tk.Tk()
app = FinanceApp(root)
root.mainloop()