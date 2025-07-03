##Studet Name: Mathew Sunil Abraham
##Student ID: s4030103
##Highest Level attempted: HD Level



import sys
import os
from datetime import datetime

class Book: # Class representing book and its parameters
    def __init__(self, book_id, name, book_type, ncopy, maxday, lcharge):
        if not book_id.startswith('B') or not book_id[1:].isdigit():
            raise ValueError(f"Invalid book ID: {book_id}")
        self.book_id = book_id
        self.name = name
        self.book_type = book_type
        self.ncopy = ncopy
        self.maxday = maxday
        self.lcharge = lcharge
        self.borrowed_days = {}

    def add_borrow_record(self, member_id, days): # Add a borrow record for a member
        self.borrowed_days[member_id] = days

    def get_borrow_days(self, member_id): # Retrieve the number of days a book has been borrowed by a member
        return self.borrowed_days.get(member_id, 'xx')

    def compute_statistics(self): # Compute and return statistics for borrowing of the book
        nborrow = sum(1 for days in self.borrowed_days.values() if isinstance(days, int))
        nreserve = sum(1 for days in self.borrowed_days.values() if days == '--')
        borrow_days = [days for days in self.borrowed_days.values() if isinstance(days, int)]
        min_days = min(borrow_days) if borrow_days else 0
        max_days = max(borrow_days) if borrow_days else 0
        return nborrow, nreserve, min_days, max_days

class Member: # Class representing a member and their borrowing details
    def __init__(self, member_id, fname="", lname="", dob="", member_type="Standard"):
        if not member_id.startswith('M') or not member_id[1:].isdigit():
            raise ValueError(f"Invalid member ID: {member_id}")
        self.member_id = member_id
        self.fname = fname
        self.lname = lname
        self.dob = dob
        self.member_type = member_type
        self.borrowed_books = {'T': 0, 'F': 0}
        self.total_days = 0
        self.fee = 0.0

    def add_borrow_record(self, book_type, days): # Add a borrow record for the member
        if book_type not in self.borrowed_books:
            raise ValueError(f"Unknown book type: {book_type}")
        if days != '--':
            self.borrowed_books[book_type] += 1
            self.total_days += days
            limits = {'Standard': {'T': 14, 'F': 14}, 'Premium': {'T': 14, 'F': 14}}
            if days > limits[self.member_type][book_type]:
                self.fee += (days - limits[self.member_type][book_type]) * self.get_lcharge(book_type)

    def get_lcharge(self, book_type):
        return {'T': 1.2, 'F': 1.8}[book_type]

    def compute_statistics(self):
        average_days = self.total_days / sum(self.borrowed_books.values()) if sum(self.borrowed_books.values()) > 0 else 0
        return self.borrowed_books['T'], self.borrowed_books['F'], average_days

    def check_limits(self):
        limits = {'Standard': {'T': 1, 'F': 2}, 'Premium': {'T': 2, 'F': 3}}
        limit_exceeded = False
        if self.borrowed_books['T'] > limits[self.member_type]['T']:
            limit_exceeded = True
        if self.borrowed_books['F'] > limits[self.member_type]['F']:
            limit_exceeded = True
        return limit_exceeded

class Records: # Class for managing all book and member records
    def __init__(self):
        self.books = {}
        self.members = {}
        self.total_days = 0
        self.total_records = 0

    def read_books(self, book_file_name): # Read book records from a file
        try:
            with open(book_file_name, 'r') as file:
                if os.stat(book_file_name).st_size == 0:
                    raise ValueError(f"File {book_file_name} is empty.")
                for line in file:
                    parts = line.strip().split(', ')
                    if len(parts) != 6:
                        print(f"Skipping invalid book line: {line.strip()}")
                        continue
                    book_id, name, book_type, ncopy, maxday, lcharge = parts
                    ncopy = int(ncopy)
                    maxday = int(maxday)
                    lcharge = float(lcharge)
                    self.books[book_id] = Book(book_id, name, book_type, ncopy, maxday, lcharge)
        except FileNotFoundError:
            print(f"File {book_file_name} not found.")
            sys.exit(1)
        except ValueError as e:
            print(e)
            sys.exit(1)

    def read_records(self, record_file_name): # Read borrow records from a file
        try:
            with open(record_file_name, 'r') as file:
                if os.stat(record_file_name).st_size == 0:
                    raise ValueError(f"File {record_file_name} is empty.")
                for line in file:
                    parts = line.strip().split(', ')
                    book_id = parts[0]
                    if book_id not in self.books:
                        print(f"Book ID {book_id} not found in books data.")
                        continue  # skip this record if the book is not found in books data
                    if not book_id.startswith('B') or not book_id[1:].isdigit():
                        raise ValueError(f"Invalid book ID in record file: {book_id}")
                    for record in parts[1:]:
                        member_id, days = record.split(': ')
                        if not member_id.startswith('M') or not member_id[1:].isdigit():
                            raise ValueError(f"Invalid member ID in record file: {member_id}")
                        if member_id not in self.members:
                            self.members[member_id] = Member(member_id)
                        if days == 'R':
                            self.books[book_id].add_borrow_record(member_id, '--')
                        else:
                            try:
                                days = int(days)
                            except ValueError:
                                raise ValueError(f"Invalid borrow days in record file: {days}")
                            self.books[book_id].add_borrow_record(member_id, days)
                            self.members[member_id].add_borrow_record(self.books[book_id].book_type, days)
                            self.total_days += days
                            self.total_records += 1
        except FileNotFoundError:
            print(f"File {record_file_name} not found.")
            sys.exit(1)
        except ValueError as e:
            print(e)
            sys.exit(1)

    def read_members(self, member_file_name): # Read member records from a file
        try:
            with open(member_file_name, 'r') as file:
                if os.stat(member_file_name).st_size == 0:
                    raise ValueError(f"File {member_file_name} is empty.")
                for line in file:
                    parts = line.strip().split(', ')
                    if len(parts) != 5:
                        print(f"Skipping invalid member line: {line.strip()}")
                        continue
                    member_id, fname, lname, dob, member_type = parts
                    if not member_id.startswith('M') or not member_id[1:].isdigit():
                        raise ValueError(f"Invalid member ID in member file: {member_id}")
                    dob = datetime.strptime(dob, '%d/%m/%Y').strftime('%d-%b-%Y')
                    if member_id in self.members:
                        self.members[member_id].fname = fname
                        self.members[member_id].lname = lname
                        self.members[member_id].dob = dob
                        self.members[member_id].member_type = member_type
                    else:
                        self.members[member_id] = Member(member_id, fname, lname, dob, member_type)
        except FileNotFoundError:
            print(f"File {member_file_name} not found.")
            sys.exit(1)
        except ValueError as e:
            print(e)
            sys.exit(1)

    def display_records(self): # Display all borrow records
        output = []
        member_list = sorted(list(self.members.keys()))
        book_list = sorted(self.books.keys())
        header = "{:<12} {:>6} {:>6} {:>6} {:>6} {:>6}".format("Member IDs", *book_list)
        output.append(header)
        output.append("-" * len(header))

        for member in member_list:
            row = [f"{member:<12}"] + [f"{str(self.books[book_id].get_borrow_days(member)):>6}" for book_id in book_list]
            output.append(" ".join(row))

        output.append("\nRECORDS SUMMARY")
        output.append(f"There are {len(self.members)} members and {len(self.books)} books.")
        average_days = self.total_days / self.total_records if self.total_records > 0 else 0
        output.append(f"The average number of borrow days is {average_days:.2f} (days).")

        for line in output:
            print(line)
        return output

    def display_books(self): # Display the statistics of all books
        textbooks = []
        fictions = []
        for book in self.books.values():
            nborrow, nreserve, min_days, max_days = book.compute_statistics()
            row = [
                f"{book.book_id:^7}",
                f"{book.name:<20}",
                f"{book.book_type:^5}",
                f"{book.ncopy:^5}",
                f"{book.maxday:^7}",
                f"{book.lcharge:^7.2f}",
                f"{nborrow:^7}",
                f"{nreserve:^7}",
                f"{min_days}-{max_days}"
            ]
            if book.book_type == 'T':
                textbooks.append(row)
            elif book.book_type == 'F':
                fictions.append(row)

        textbooks.sort(key=lambda x: x[1])  # Sort textbooks
        fictions.sort(key=lambda x: x[1])  # Sort fiction books

        output = []

        # Display textbooks
        header = "{:<8} {:<20} {:<5} {:<5} {:<7} {:<7} {:<7} {:<7} {:<10}".format(
            "Book IDs", "Name", "Type", "Ncopy", "Maxday", "Lcharge", "Nborrow", "Nreserve", "Range"
        )
        output.append("TEXTBOOKS")
        output.append(header)
        output.append("-" * len(header))
        for row in textbooks:
            output.append(" ".join(row))

        # Display fictions
        output.append("\nFICTIONS")
        output.append(header)
        output.append("-" * len(header))
        for row in fictions:
            output.append(" ".join(row))

        output.append("\nBOOKS SUMMARY")
        most_popular_books = [book.name for book in self.books.values() if book.compute_statistics()[1] == max(self.books[book_id].compute_statistics()[1] for book_id in self.books)]
        longest_borrowed_books = [book.name for book in self.books.values() if book.compute_statistics()[3] == max(self.books[book_id].compute_statistics()[3] for book_id in self.books)]
        output.append(f"The most popular book(s): {', '.join(most_popular_books)}")
        output.append(f"The book(s) with the longest days borrowed: {', '.join(longest_borrowed_books)}")

        for line in output:
            print(line)
        return output

    def display_members(self): # Display statistics and summaries of all members
        standard_members = []
        premium_members = []
        for member in self.members.values():
            ntextbook, nfiction, average_days = member.compute_statistics()
            row = [
                f"{member.member_id:<7}",
                f"{member.fname:<10}",
                f"{member.lname:<10}",
                f"{member.member_type:<8}",
                f"{member.dob:<11}",
                f"{ntextbook:<9}",
                f"{nfiction:<8}",
                f"{average_days:<8.2f}",
                f"{member.fee:<6.2f}"
            ]
            if member.member_type == 'Standard':
                standard_members.append(row)
            elif member.member_type == 'Premium':
                premium_members.append(row)

        # Sort by fee - descending
        standard_members.sort(key=lambda x: float(x[8]), reverse=True)
        premium_members.sort(key=lambda x: float(x[8]), reverse=True)

        output = []

        # Display standard members
        header = "{:<7} {:<10} {:<10} {:<8} {:<11} {:<9} {:<8} {:<8} {:<6}".format(
            "Member IDs", "FName", "LName", "Type", "DOB", "Ntextbook", "Nfiction", "Average", "Fee"
        )
        output.append("STANDARD MEMBERS")
        output.append(header)
        output.append("-" * len(header))
        for row in standard_members:
            output.append(" ".join(row))

        # Display premium members
        output.append("\nPREMIUM MEMBERS")
        output.append(header)
        output.append("-" * len(header))
        for row in premium_members:
            output.append(" ".join(row))

        output.append("\nMEMBERS SUMMARY")
        most_active_members = [self.members[member_id].fname for member_id in self.members if sum(self.members[member_id].borrowed_books.values()) == max(sum(self.members[m_id].borrowed_books.values()) for m_id in self.members)]
        least_average_days_members = [self.members[member_id].fname for member_id in self.members if self.members[member_id].compute_statistics()[2] == min(self.members[m_id].compute_statistics()[2] for m_id in self.members)]
        output.append(f"Most active member(s) are: {', '.join(most_active_members)} with {max(sum(self.members[member_id].borrowed_books.values()) for member_id in self.members)} books borrowed/reserved.")
        output.append(f"Member(s) with the least average number of borrowing days is {', '.join(least_average_days_members)} with {min(self.members[member_id].compute_statistics()[2] for member_id in self.members):.2f} days.")

        for line in output:
            print(line)
        return output

def main(): # Main function to execute the script
    if len(sys.argv) < 2:
        print("[Usage:] python my_record.py <record file> [<book file>] [<member file>]")
        return

    record_file_name = sys.argv[1]
    records = Records()

    if len(sys.argv) > 2:
        book_file_name = sys.argv[2]
        records.read_books(book_file_name)

    records.read_records(record_file_name)

    report_lines = []

    if len(sys.argv) > 3:
        member_file_name = sys.argv[3]
        records.read_members(member_file_name)
        report_lines.extend(records.display_members())

    report_lines.extend(records.display_books())
    report_lines.extend(records.display_records())

    # Append report to reports.txt with timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    report_lines.insert(0, f"Report generated on: {timestamp}")

    with open('reports.txt', 'a') as file: #Create reports.txt file which updates regularly
        for line in report_lines:
            file.write(line + "\n")

if __name__ == "__main__":
    main()


"""
Analysis/reflection:
The goal of this project was to develop a library management system that could handle various book and member records, manage borrowing activities, and generate comprehensive reports. The design and implementation of the code were guided by several key considerations to ensure efficiency, scalability, and ease of use. The system was designed using an object-oriented approach to encapsulate the properties and behaviors of books and members. Two main classes, `Book` and `Member`, were created to manage the respective data. A `Records` class was designed to 
manage collections of books and members and handle interactions between them. Methods for adding and retrieving borrow records were designed to facilitate the tracking of which member borrowed which book and for how long. This was crucial for generating accurate reports. Functions were added to compute various statistics such as the number of borrowings, reservations, and the borrowing duration for books and members. This allows the system to generate insightful reports. After the individual components were tested, they were integrated to form a cohesive system. The main function was then developed to tie everything together and handle command-line arguments for file input.
Ensuring that all input data followed the expected formats was a significant challenge. This required extensive validation checks and error handling to prevent the system from crashing due to invalid inputs.
Reading data from files and ensuring that the data was correctly parsed and stored in the system was another challenge. 
This involved handling different file formats and ensuring compatibility with the system’s expected input.

"""