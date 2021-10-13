import json
import os
import sqlite3


class DBOperations:
    # TODO: write docstring for class
    # Define DBOperation class to manage all data into the database.

    def __init__(self):

        # Import sql queries from json utils file
        with open('sql_queries.json') as sql_queries_file:
            self.sql_queries_dict = json.load(sql_queries_file)

        try:
            self.conn = sqlite3.connect("DBName.db")
            self.cur = self.conn.cursor()
            self.cur.execute(self.sql_queries_dict["sql_create_table"])
            self.conn.commit()
        except Exception as e:
            print(e)
        finally:
            self.conn.close()

    def get_connection(self) -> None:
        self.conn = sqlite3.connect("DBName.db")
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

            # TODO: validation class
            title_valid = False
            while not title_valid:
                title = input("\nEnter Employee title: ")
                if not Employee.validate_title(title):
                    print(f"\n{title} is not a valid title. Please choose from the following: \n"
                          f"Mr, Mrs, Miss, Ms, Dr, Sir, Prof or Captain.\n")
                else:
                    emp.set_employee_title(title.capitalize())
                    title_valid = True

            emp.set_employee_forename(str(input("\nEnter Employee forename: ")).capitalize())
            emp.set_employee_surname(str(input("\nEnter Employee surname: ")).capitalize())
            emp.set_employee_email(str(input("\nEnter Employee email address: ")))

            salary_valid = False
            while not salary_valid:
                salary = input("\nEnter Employee salary: £")
                try:
                    salary = float(salary)
                    emp.set_employee_salary(salary)
                    salary_valid = True
                except ValueError:
                    print("Invalid input - please enter a number.\n")

            self.cur.execute(self.sql_queries_dict["sql_insert"], tuple(emp.employee_str_no_id().split("\n")))

            self.conn.commit()
            print(f"\nInserted record for {emp.forename} {emp.surname} successfully\n")
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

    '''
    def search_data(self):
        try:
            self.get_connection()
            id = int(input("Enter Employee ID: "))
            self.cur.execute(self.sql_search, tuple(str(id)))
            result = self.cur.fetchone()
            if type(result) == type(tuple()):
                for index, detail in enumerate(result):
                    if index == 0:
                        print("Employee ID: " + str(detail))
                    elif index == 1:
                        print("Employee Title: " + detail)
                    elif index == 2:
                        print("Employee Name: " + detail)
                    elif index == 3:
                        print("Employee Surname: " + detail)
                    elif index == 4:
                        print("Employee Email: " + detail)
                    else:
                        print("Salary: " + str(detail))
            else:
                print("No Record")

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

            result = self.cur.execute(self.sql_queries_dict["sql_select_id"], (id_update,)).fetchall()

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


    def delete_data(self):
        # Define Delete_data method to delete data from the table. The user will need to input the employee id to
        # delete the corresponding record.
        try:
            self.get_connection()
            self.select_all()  # Display the records for the user to choose from
            self.cur.execute(self.sql_queries_dict["sql_select_all"])
            results = self.cur.fetchall()

            # TODO: move to validation
            valid_id = False
            id_delete = 0
            while not valid_id:
                try:
                    id_delete = input("\nSelect the ID of the employee record to delete. To exit press q: ")
                    if id_delete.lower() == "q":
                        return
                    else:
                        id_delete = int(id_delete)
                    valid_id = True
                except ValueError:
                    print("Please try again - enter a valid integer ID.")

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

    @staticmethod
    def validate_title(title):
        titles = ['Mr', 'Mrs', 'Miss', 'Ms', 'Dr', 'Sir', 'Prof', 'Captain']
        return title.strip().capitalize() in titles

    def employee_str_no_id(self):
        return self.title + "\n" + self.forename + "\n" + self.surname + "\n" + self.email + "\n" + str(
            self.salary)

    def __str__(self):
        return str(
            self.id) + "\n" + self.title + "\n" + self.forename + "\n" + self.surname + "\n" + self.email + "\n" + str(
            self.salary)


class Validation:
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
            " 1. Create table EmployeeUoB\n"
            " 2. Insert data into EmployeeUoB\n"
            " 3. Select all data into EmployeeUoB\n"
            " 4. Search an employee\n"
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


def run():
    db_ops = DBOperations()
    while True:
        Menu.display_logo()
        Menu.display_main_menu()

        try:
            choose_menu = int(input("Enter your choice: "))

            if choose_menu == 1:
                db_ops.create_table()
                input("Press Enter to return to the main menu...")
            elif choose_menu == 2:
                db_ops.insert_data()
                input("Press Enter to return to the main menu...")
            elif choose_menu == 3:
                Menu.display_logo()
                db_ops.select_all()
                input("Press Enter to return to the main menu...")
            elif choose_menu == 4:
                db_ops.search_data()
            elif choose_menu == 5:
                db_ops.update_data()
            elif choose_menu == 6:
                Menu.display_logo()
                db_ops.delete_data()
                input("Press Enter to return to the main menu...")
            elif choose_menu == 7:
                Menu.display_logo()
                Menu.display_help_message()
                input("Press Enter to return to the main menu...")
            elif choose_menu == 8:
                exit(0)
            else:
                print("\nInvalid choice - please try again\n")
                input("Press Enter to continue...")
        except ValueError:
            print("\nInvalid choice - please enter a number\n")
            input("Press Enter to continue...")


if __name__ == "__main__":
    run()
