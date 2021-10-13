import json
import os
import sqlite3


class DBOperations:
    # Define DBOperation class to manage all data into the database.

    def __init__(self):

        # Import sql queries from json utils file
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
        self.conn = sqlite3.connect("TheHive.db")
        self.cur = self.conn.cursor()

    def create_table(self) -> None:
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

    def insert_data(self):
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

    def select_all(self):
        try:
            self.get_connection()
            self.cur.execute(self.sql_queries_dict["sql_select_all"])
            results = self.cur.fetchall()

            Menu.display_results_table(results)

        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def search_data(self):
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
                for index, detail in enumerate(result):
                    Menu.display_results_table(result)
            else:
                print(f"No record(s) found.")

        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    '''
    def update_data(self):
        try:
            self.get_connection()

            # Update statement
            valid_id = False
            id_update = 0
            while not valid_id:
                try:
                    id_update = input("\nSelect the ID of the employee record to update. To exit press q: ")
                    if id_update.lower() == "q":
                        return
                    else:
                        id_update = int(id_update)
                    valid_id = True
                except ValueError:
                    print("Please try again - enter a valid integer ID.")

            result = self.cur.execute(self.sql_queries_dict["sql_select_id"], tuple(str(id_update))).fetchall()

            if len(result) != 0:
                valid_field = False
                field = ""
                while not valid_field:
                    input("Please input a field to update: ")
                print(str(len(result)) + "Row(s) affected.")
            else:
                print("Cannot find this record in the database")

        except Exception as e:
            print(e)
        finally:
            self.conn.close()
    '''

    def delete_data(self):
        # Define Delete_data method to delete data from the table. The user will need to input the employee id to
        # delete the corresponding record.
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
                result = self.cur.execute(self.sql_queries_dict["sql_delete_data"], (id_delete,)).fetchall()
                self.conn.commit()
            else:
                print("\nCannot find this record in the database.\n")

        except Exception as e:
            print(e)
        finally:
            self.conn.close()


class Employee:
    def __init__(self):
        self.id = 0
        self.title = ""
        self.forename = ""
        self.surname = ""
        self.email = ""
        self.salary = 0.

    def set_employee_id(self, id):
        self.id = id

    def set_employee_title(self, title):
        self.title = title

    def set_employee_forename(self, forename):
        self.forename = forename

    def set_employee_surname(self, surname):
        self.surname = surname

    def set_employee_email(self, email):
        self.email = email

    def set_employee_salary(self, salary):
        self.salary = salary

    def get_employee_id(self):
        return self.id

    def get_employee_title(self):
        return self.title

    def get_forename(self):
        return self.forename

    def get_surname(self):
        return self.surname

    def get_email(self):
        return self.email

    def get_salary(self):
        return self.salary

    def employee_str_no_id(self):
        return self.title + "\n" + self.forename + "\n" + self.surname + "\n" + self.email + "\n" + str(
            self.salary)

    def __str__(self):
        return str(
            self.id) + "\n" + self.title + "\n" + self.forename + "\n" + self.surname + "\n" + self.email + "\n" + str(
            self.salary)


class AdminLogin:

    def __init__(self, id, email, username, password, date_of_birth):
        self.email = email
        self.username = username
        self.password = password
        self.date_of_birth = date_of_birth

    def check_password(self, input_password):
        pass

    def reset_password(self):
        date_of_birth = ""  # query the admin table
        print(f"A password has been sent to your email address: {self.email}\n")

    @staticmethod
    def check_username_exists(username):
        pass


class Menu:

    @staticmethod
    def display_logo() -> None:
        """Prints the application logo, used in the main menu.

        Returns:
            None
        """
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
        """Prints the main menu.

        Returns:
            None
        """
        main_menu = (
            "Main Menu: \n\n"
            " 1. Create table Employee table\n"
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
            "Key fields stored in The Hive are:\n"
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
    def login_menu():
        pass


class Validation:

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
                id_delete = input("\nSelect an employee ID. To exit press q: ")
                if id_delete.lower() == "q":
                    return "q"
                else:
                    return int(id_delete)
            except ValueError:
                print("Please try again - enter a valid integer ID.")


def run():
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
