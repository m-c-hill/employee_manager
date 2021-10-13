import json
import os
import sqlite3
TESTING_MODE = True


class DBOperations:
    """
    Class to manage interactions with SQLite database.

    sql_queries_dict : dict
    conn : sqlite3.Connection
    cur: sqlite3.Cursor
    """

    def __init__(self):

        # Import SQL queries from json utils file
        with open('sql_queries.json') as sql_queries_file:
            self.sql_queries_dict = json.load(sql_queries_file)

        try:
            self.conn = sqlite3.connect("TheHive.db")
            self.cur = self.conn.cursor()
            self.cur.execute(self.sql_queries_dict["sql_create_table"])
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def get_connection(self) -> None:
        """Initialise connection with The Hive database"""
        self.conn = sqlite3.connect("TheHive.db")
        self.cur = self.conn.cursor()

    def create_table(self) -> None:
        """Create the employee table"""
        try:
            self.get_connection()
            if not self.conn.execute(self.sql_queries_dict["check_table_exists"]).fetchone():
                self.cur.execute(self.sql_queries_dict["sql_create_table"])
                self.conn.commit()
                print("\nTable 'employee' created successfully\n")
            else:
                print("\nThis table is already created\n")
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def insert_data(self) -> None:
        """Insert employee record"""
        try:
            self.get_connection()

            emp = Employee()

            emp.set_employee_title(Validation.valid_title_input())
            emp.set_employee_forename(str(input("\nEnter Employee forename: ")).capitalize())
            emp.set_employee_surname(str(input("\nEnter Employee surname: ")).capitalize())
            emp.set_employee_email(str(input("\nEnter Employee email address: ")))
            emp.set_employee_salary(Validation.valid_salary_input())

            self.cur.execute(self.sql_queries_dict["sql_insert"], tuple(emp.employee_str_no_id().split("\n")))
            print(f"\nInserted record for {emp.forename} {emp.surname} successfully\n")
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def select_all(self) -> None:
        """Select all records in the employee table and display them in a table"""
        try:
            self.get_connection()
            self.cur.execute(self.sql_queries_dict["sql_select_all"])
            results = self.cur.fetchall()
            Menu.display_results_table(results)

        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def search_data(self) -> None:
        """Search for record by employee ID or surname. Display results in table."""
        try:
            self.get_connection()
            search_type = input("\nSearch by id or by surname. Please enter 'i' or 's': ").strip().lower()
            if search_type == "i":
                id_search = Validation.valid_id_input()
                self.cur.execute(self.sql_queries_dict["sql_select_id"], (id_search,))
            elif search_type == "s":
                surname_search = input("\nPlease enter a surname: ").strip().lower().capitalize()
                self.cur.execute(self.sql_queries_dict["sql_select_surname"], (surname_search,))
            else:
                print("\nInvalid search type, returning to main menu.\n")
                return
            result = self.cur.fetchall()
            if isinstance(result, list):
                print(f"\nFound {len(result)} record matching your query:\n")
                Menu.display_results_table(result)
            else:
                print(f"No record(s) found.")

        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def update_data(self) -> None:
        """Update record by selecting an employee by ID"""
        try:
            self.get_connection()

            id_update = Validation.valid_id_input()
            result = self.cur.execute(self.sql_queries_dict["sql_select_id"], tuple(str(id_update))).fetchall()

            if len(result) != 0:
                Menu.display_results_table(result)
                self.cur.execute(self.sql_queries_dict["sql_select_all"])
                columns = [description[0] for description in self.cur.description]
                column = Validation.valid_column_input(columns)
                if column == "q":
                    return

                new_value = Validation.valid_update_value_input(column)

                if column == "id" and self.check_id_exists(new_value):
                    print("\nEmployee ID already exists. Returning to main menu.\n")
                    return
                print(new_value)
                self.cur.execute(f"UPDATE employee SET { column } = ? WHERE id = ?", (new_value, id_update))
                self.conn.commit()
                print(str(len(result)) + "row(s) affected.")
            else:
                print("Cannot find this record in the database")

        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def delete_data(self) -> None:
        """Method to delete record from the table by selecting employee by ID"""
        try:
            self.get_connection()
            self.cur.execute(self.sql_queries_dict["sql_select_all"])
            results = self.cur.execute(self.sql_queries_dict["sql_select_all"]).fetchall()
            if len(results) == 0:
                print("\nNo records available to delete in Employee table.\n")
                return

            id_delete = Validation.valid_id_input()
            if id_delete == "q":
                return
            else:
                result = self.cur.execute(self.sql_queries_dict["sql_select_id"], (id_delete,)).fetchall()

            if len(result) != 0:
                print(str(len(result)) + " row(s) affected.")
                self.cur.execute(self.sql_queries_dict["sql_delete_data"], (id_delete,)).fetchall()
                self.conn.commit()
            else:
                print("\nCannot find this record in the database.\n")

        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def check_id_exists(self, _id) -> bool:
        """Method to check if an employee ID has already been taken"""
        try:
            self.get_connection()
            self.cur.execute(self.sql_queries_dict["sql_select_id"], (_id,))
            result = self.cur.fetchall()
            return len(result) > 0
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def check_admin_username_exists(self, username) -> bool:
        """Method to check if a given username exists in the admin table"""
        try:
            self.get_connection()
            self.cur.execute(self.sql_queries_dict["check_admin_exists"], (username,))
            result = self.cur.fetchall()
            return len(result) > 0
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def create_admin_table(self) -> None:
        """Method to create the admin table. This is for testing purposes and would be implemented correctly in
        production"""
        try:
            self.get_connection()
            self.cur.execute("DROP TABLE IF EXISTS admin")
            self.cur.execute(self.sql_queries_dict["create_admin_table"])
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def populate_admin_table(self) -> None:
        """Method to populate the admin table. This is for testing purposes and would be implemented correctly in
        production"""
        try:
            self.get_connection()
            self.cur.execute(self.sql_queries_dict["populate_admin_table"])
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def check_password(self, username, password) -> bool:
        """Method to check if user's password matches their input password when logging in."""
        try:
            self.get_connection()
            self.cur.execute(self.sql_queries_dict["get_admin_password"], (username,))
            true_password = self.cur.fetchone()[0]
            return true_password == password

        except Exception as e:
            print(e)
        finally:
            self.conn.close()


class Employee:
    """
    Class to represent Employee with fields that reflect the columns in employee table in database
    """

    def __init__(self):
        self.id = 0
        self.title = ""
        self.forename = ""
        self.surname = ""
        self.email = ""
        self.salary = 0.

    def set_employee_id(self, id) -> None:
        self.id = id

    def set_employee_title(self, title) -> None:
        self.title = title

    def set_employee_forename(self, forename) -> None:
        self.forename = forename

    def set_employee_surname(self, surname) -> None:
        self.surname = surname

    def set_employee_email(self, email) -> None:
        self.email = email

    def set_employee_salary(self, salary) -> None:
        self.salary = salary

    def get_employee_id(self) -> int:
        return self.id

    def get_employee_title(self) -> str:
        return self.title

    def get_forename(self) -> str:
        return self.forename

    def get_surname(self) -> str:
        return self.surname

    def get_email(self) -> str:
        return self.email

    def get_salary(self) -> float:
        return self.salary

    def employee_str_no_id(self) -> str:
        """String representation of employee, omitting user ID"""
        return self.title + "\n" + self.forename + "\n" + self.surname + "\n" + self.email + "\n" + str(
            self.salary)

    def __str__(self) -> str:
        return str(
            self.id) + "\n" + self.title + "\n" + self.forename + "\n" + self.surname + "\n" + self.email + "\n" + str(
            self.salary)


class AdminLogin:
    """
    Admin class to assist with login functionality.
    """
    @staticmethod
    def check_password(username, input_password) -> bool:
        db_ops = DBOperations()
        return db_ops.check_password(username, input_password)

    @staticmethod
    def check_username_exists(username) -> bool:
        db_ops = DBOperations()
        return db_ops.check_admin_username_exists(username)


class Menu:
    """
    Menu class to provide display functions for user interface.
    """
    @staticmethod
    def display_logo() -> None:
        hive_logo = (
            "*=========================================*\n"
            "|  _____ _            _   _ _             |\n"
            "| |_   _| |          | | | (_)            |\n"
            "|   | | | |__   ___  | |_| |___   _____   |\n"
            "|   | | | '_ \ / _ \ |  _  | \ \ / / _ \  |\n"
            "|   | | | | | |  __/ | | | | |\ V /  __/  |\n"
            "|   \_/ |_| |_|\___| \_| |_/_| \_/ \___|  |\n"
            "*=========================================*\n"
            "|       Employee Management System        |\n"
            "*=========================================*\n"
        )
        os.system('cls' if os.name == 'nt' else 'clear')
        print(hive_logo)

    @staticmethod
    def display_main_menu() -> None:
        main_menu = (
            "Main Menu: \n\n"
            " 1. Create Employee table\n"
            " 2. Insert data into Employee table\n"
            " 3. Show all records in Employee table\n"
            " 4. Search for employee\n"
            " 5. Update records\n"
            " 6. Delete record\n"
            " 7. Help\n"
            " 8. Exit\n"
        )
        print(main_menu)

    @staticmethod
    def display_help_message() -> None:
        help_message = (
            "Welcome to The Hive - your one-stop solution for employee data management.\n\n"
            "This application allows you to store, update, delete and filter employee \n"
            "records. \n\n"
            "Key columns stored in The Hive are:\n"
            "    - Employee ID\n"
            "    - Title\n"
            "    - Forename\n"
            "    - Surname\n"
            "    - Email Address\n"
            "    - Salary\n\n"
            "To get started, simply select an option in the main menu and follow the \n"
            "instructions on the screen.\n\n"
            "Stay tuned as new features are being released weekly. To see the latest \n"
            "release notes, please visit https://www.the-hive-application.io/release-log\n"
        )
        print(help_message)

    @staticmethod
    def display_results_table(results) -> None:
        if len(results) > 0:
            print("+--------------------------------------------------------------------------------------------------"
                  "-----------------------+\n"
                  "+ Employee ID |  Title  |         Forename        |         Surname         |         Email Address"
                  "        |    Salary    |\n"
                  "+-------------|---------|-------------------------|-------------------------|----------------------"
                  "--------|--------------+"
                  )
            for id, title, forename, surname, email, salary in results:
                print("| {:<12}| {:<8}| {:<24}| {:<24}| {:<29}| £{:<12.2f}|".format(
                    id, title, forename, surname, email, float(salary)))
            print("+--------------------------------------------------------------------------------------------------"
                  "-----------------------+\n")
        else:
            print("No results to display.")

    @staticmethod
    def login_menu() -> None:
        """Method to take user's credentials and check them against the database"""
        initialise_admin()
        while True:
            Menu.display_logo()
            print("\nWelcome to The Hive. Please enter your login details below: \n")
            if TESTING_MODE:
                print("\nTESTING MODE ACTIVE FOR MARKER: To login, please enter the username 'admin' and the password "
                      "'password123'\n")
            print("\n===== Admin Login =====\n")

            username_exists = False
            username = ""
            while not username_exists:
                username = input("Admin username: ")
                username_exists = AdminLogin.check_username_exists(username)
                if not username_exists:
                    print("Invalid username entered. Please try again. ")

            input_password = input("Password: ")
            if AdminLogin.check_password(username, input_password):
                return
            input("Incorrect username or password, please try again. Press enter to continue: ")


class Validation:
    """
    Class to provide validation techniques for user input.
    """

    @staticmethod
    def valid_title_input():
        titles = ['Mr', 'Mrs', 'Miss', 'Ms', 'Dr', 'Sir', 'Prof', 'Captain']

        while True:
            title = input("\nEnter Employee title: ").strip().lower().capitalize()
            if title in titles:
                return title
            print(f"\n{title} is not a valid title. Please choose from the following: \n"
                  f"Mr, Mrs, Miss, Ms, Dr, Sir, Prof or Captain.")

    @staticmethod
    def valid_salary_input():
        while True:
            salary = input("\nEnter Employee salary: £")
            try:
                return float(salary)
            except ValueError:
                print("\nInvalid input - please enter a number.")

    @staticmethod
    def valid_id_input():
        while True:
            try:
                _id = input("\nSelect an employee ID. To exit press q: ")
                if _id.lower() == "q":
                    return "q"
                else:
                    return int(_id)
            except ValueError:
                print("Please try again - enter a valid integer ID.")

    @staticmethod
    def valid_column_input(columns):
        while True:
            for column_i in columns:
                print(f"- {column_i}")
            column_choice = input("\nPlease select a column from the above list. To quit, press 'q': ").strip().lower()
            if column_choice in columns:
                return column_choice
            print("\nInvalid choice.\n")

    @staticmethod
    def valid_update_value_input(column):
        if column == "id":
            while True:
                try:
                    id = input("\nEnter a new employee ID: ")
                    return int(id)
                except ValueError:
                    print("Please try again - enter a valid integer ID.")

        elif column == "title":
            return Validation.valid_title_input()

        elif column == "forename":
            return input("\nEnter a new forename: ").lower().strip().capitalize()

        elif column == "surname":
            return input("\nEnter a new surname: ").lower().strip().capitalize()

        elif column == "email":
            return input("\nEnter a new email address: ").lower().strip()

        elif column == "salary":
            return Validation.valid_salary_input()

        elif column == "q":
            return "q"


def initialise_admin() -> None:
    """Method to initialise and populate the admin table, used for testing and demonstration purposes."""
    db_ops = DBOperations()
    db_ops.create_admin_table()
    db_ops.populate_admin_table()


def run() -> None:

    # Login
    Menu.login_menu()

    # Once user credentials have been authenticated, continue to main menu
    while True:
        db_ops = DBOperations()
        Menu.display_logo()
        Menu.display_main_menu()

        try:
            choose_menu = int(input("Enter your choice: "))

            if choose_menu == 1:
                db_ops.create_table()
            elif choose_menu == 2:
                db_ops.insert_data()
            elif choose_menu == 3:
                Menu.display_logo()
                db_ops.select_all()
            elif choose_menu == 4:
                db_ops.search_data()
            elif choose_menu == 5:
                db_ops.update_data()
            elif choose_menu == 6:
                Menu.display_logo()
                db_ops.delete_data()
            elif choose_menu == 7:
                Menu.display_logo()
                Menu.display_help_message()
            elif choose_menu == 8:
                exit(0)
            else:
                print("\nInvalid choice - please try again\n")
        except ValueError:
            print("\nInvalid choice - please enter a number\n")

        input("Press Enter to return to the main menu...")


if __name__ == "__main__":
    run()
