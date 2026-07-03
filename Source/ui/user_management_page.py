"""
===========================================
 User Management Page (Admin only)
===========================================
Lets the Admin create, edit, delete users, reset passwords and
assign roles. This page should only ever be reachable when the
logged-in user's role is "Admin" (enforced by the sidebar + dashboard
router, but we double check here too).
"""

import customtkinter as ctk
from tkinter import ttk, messagebox

from assets.themes import colors
from models.user import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    reset_password,
    delete_user,
    username_exists,
    count_active_admins,
)
from services.audit_service import log_action
from ui.components.watermark import add_watermark

ROLES = ["Admin", "Manager", "Cashier"]


class UserManagementPage(ctk.CTkFrame):

    def __init__(self, parent, current_user):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        self.current_user = current_user
        self.selected_user_id = None

        if (current_user["role"] if current_user else None) != "Admin":
            ctk.CTkLabel(
                self,
                text="🔒 You need Admin access to view this page.",
                font=colors.FONT_H2,
                text_color=colors.DANGER
            ).pack(pady=60)
            return

        title = ctk.CTkLabel(
            self,
            text="👤 User Management",
            font=colors.FONT_H1,
            text_color=colors.PRIMARY
        )
        title.pack(anchor="w", padx=10, pady=(10, 0))

        subtitle = ctk.CTkLabel(
            self,
            text="Create accounts, assign roles and manage access for your team.",
            font=colors.FONT_BODY,
            text_color=colors.TEXT_LIGHT
        )
        subtitle.pack(anchor="w", padx=10, pady=(0, 15))

        self.build_form()
        self.build_table()

        self.load_users()

    # ------------------------------------------------------------
    def build_form(self):

        card = ctk.CTkFrame(self, fg_color=colors.CARD, corner_radius=colors.RADIUS)
        card.pack(fill="x", padx=10, pady=10)
        card.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            card, text="Username", font=colors.FONT_BODY_BOLD
        ).grid(row=0, column=0, padx=20, pady=(18, 8), sticky="w")
        self.username_entry = ctk.CTkEntry(card, width=220)
        self.username_entry.grid(row=0, column=1, padx=10, pady=(18, 8), sticky="w")

        ctk.CTkLabel(
            card, text="Full Name", font=colors.FONT_BODY_BOLD
        ).grid(row=0, column=2, padx=10, pady=(18, 8), sticky="w")
        self.fullname_entry = ctk.CTkEntry(card, width=220)
        self.fullname_entry.grid(row=0, column=3, padx=20, pady=(18, 8), sticky="w")

        ctk.CTkLabel(
            card, text="Password", font=colors.FONT_BODY_BOLD
        ).grid(row=1, column=0, padx=20, pady=8, sticky="w")
        self.password_entry = ctk.CTkEntry(card, width=220, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(
            card, text="Role", font=colors.FONT_BODY_BOLD
        ).grid(row=1, column=2, padx=10, pady=8, sticky="w")
        self.role_option = ctk.CTkOptionMenu(card, values=ROLES, width=220)
        self.role_option.grid(row=1, column=3, padx=20, pady=8, sticky="w")

        ctk.CTkLabel(
            card, text="Status", font=colors.FONT_BODY_BOLD
        ).grid(row=2, column=0, padx=20, pady=8, sticky="w")
        self.status_option = ctk.CTkOptionMenu(card, values=["Active", "Inactive"], width=220)
        self.status_option.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        button_row = ctk.CTkFrame(card, fg_color="transparent")
        button_row.grid(row=3, column=0, columnspan=4, padx=20, pady=(10, 20), sticky="w")

        ctk.CTkButton(
            button_row, text="➕ Create User", font=colors.FONT_BUTTON,
            fg_color=colors.SUCCESS, hover_color=colors.SUCCESS_HOVER,
            height=colors.BUTTON_HEIGHT, corner_radius=colors.RADIUS_SM,
            command=self.create_user_action
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row, text="✎ Update Details", font=colors.FONT_BUTTON,
            fg_color=colors.SECONDARY, hover_color=colors.SECONDARY_HOVER,
            height=colors.BUTTON_HEIGHT, corner_radius=colors.RADIUS_SM,
            command=self.update_user_action
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row, text="🔑 Reset Password", font=colors.FONT_BUTTON,
            fg_color=colors.WARNING, hover_color=colors.WARNING_HOVER,
            height=colors.BUTTON_HEIGHT, corner_radius=colors.RADIUS_SM,
            command=self.reset_password_action
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row, text="🗑 Delete User", font=colors.FONT_BUTTON,
            fg_color=colors.DANGER, hover_color=colors.DANGER_HOVER,
            height=colors.BUTTON_HEIGHT, corner_radius=colors.RADIUS_SM,
            command=self.delete_user_action
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row, text="✖ Clear", font=colors.FONT_BUTTON,
            fg_color=colors.SIDEBAR_BUTTON,
            height=colors.BUTTON_HEIGHT, corner_radius=colors.RADIUS_SM,
            command=self.clear_form
        ).pack(side="left", padx=5)

    # ------------------------------------------------------------
    def build_table(self):

        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Username", "Full Name", "Role", "Status", "Created")

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_row_selected)

    # ------------------------------------------------------------
    def load_users(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for user in get_all_users():
            status = "Active" if user["status"] else "Inactive"
            self.tree.insert(
                "", "end",
                values=(
                    user["id"], user["username"], user["full_name"],
                    user["role"], status, user["created_at"]
                )
            )

    def on_row_selected(self, event):

        selected = self.tree.focus()

        if not selected:
            return

        values = self.tree.item(selected)["values"]

        if not values:
            return

        self.clear_form()

        self.selected_user_id = values[0]

        self.username_entry.insert(0, values[1])
        self.username_entry.configure(state="disabled")  # usernames are immutable
        self.fullname_entry.insert(0, values[2])
        self.role_option.set(values[3])
        self.status_option.set(values[4])

    # ------------------------------------------------------------
    def create_user_action(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        full_name = self.fullname_entry.get().strip()
        role = self.role_option.get()

        if not username or not password or not full_name:
            messagebox.showwarning("Validation", "Username, Password and Full Name are required.")
            return

        if len(password) < 6:
            messagebox.showwarning("Validation", "Password must be at least 6 characters.")
            return

        if username_exists(username):
            messagebox.showwarning("Validation", "That username is already taken.")
            return

        create_user(username, password, full_name, role)
        log_action(self.current_user["username"], f"Created user '{username}' ({role})")

        messagebox.showinfo("Success", "User created successfully.")
        self.clear_form()
        self.load_users()

    def update_user_action(self):

        if not self.selected_user_id:
            messagebox.showwarning("Update", "Please select a user from the table first.")
            return

        full_name = self.fullname_entry.get().strip()
        role = self.role_option.get()
        status = 1 if self.status_option.get() == "Active" else 0

        if not full_name:
            messagebox.showwarning("Validation", "Full Name is required.")
            return

        if role != "Admin" or status == 0:
            # Guard: don't allow demoting/deactivating the last admin
            user = get_user_by_id(self.selected_user_id)
            if user and user["role"] == "Admin" and user["status"] == 1:
                if count_active_admins(exclude_id=self.selected_user_id) == 0:
                    messagebox.showerror(
                        "Not Allowed",
                        "You can't remove Admin rights from the last active "
                        "Administrator account."
                    )
                    return

        update_user(self.selected_user_id, full_name, role, status)
        log_action(self.current_user["username"], f"Updated user id={self.selected_user_id}")

        messagebox.showinfo("Success", "User updated successfully.")
        self.clear_form()
        self.load_users()

    def reset_password_action(self):

        if not self.selected_user_id:
            messagebox.showwarning("Reset Password", "Please select a user from the table first.")
            return

        new_password = self.password_entry.get()

        if not new_password or len(new_password) < 6:
            messagebox.showwarning(
                "Validation",
                "Enter a new password (min 6 characters) in the Password field, "
                "then click Reset Password."
            )
            return

        reset_password(self.selected_user_id, new_password)
        log_action(self.current_user["username"], f"Reset password for user id={self.selected_user_id}")

        messagebox.showinfo("Success", "Password reset successfully.")
        self.clear_form()
        self.load_users()

    def delete_user_action(self):

        if not self.selected_user_id:
            messagebox.showwarning("Delete", "Please select a user from the table first.")
            return

        user = get_user_by_id(self.selected_user_id)

        if user and user["username"] == self.current_user["username"]:
            messagebox.showerror("Not Allowed", "You can't delete the account you're currently logged in with.")
            return

        if user and user["role"] == "Admin" and count_active_admins(exclude_id=self.selected_user_id) == 0:
            messagebox.showerror(
                "Not Allowed",
                "You can't delete the last active Administrator account."
            )
            return

        if messagebox.askyesno("Confirm", f"Delete user '{user['username']}'? This cannot be undone."):
            delete_user(self.selected_user_id)
            log_action(self.current_user["username"], f"Deleted user '{user['username']}'")

            messagebox.showinfo("Deleted", "User deleted successfully.")
            self.clear_form()
            self.load_users()

    def clear_form(self):

        self.selected_user_id = None

        self.username_entry.configure(state="normal")
        self.username_entry.delete(0, "end")
        self.fullname_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.role_option.set(ROLES[0])
        self.status_option.set("Active")
