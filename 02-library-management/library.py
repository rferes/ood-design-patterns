"""
Library Management System

Design a library system where:
- Members can borrow and return books
- Track which books are available
- Calculate late fees ($0.50 per day after 14 days)
- Members can borrow max 3 books at a time
- Search books by title or author

Follow-up questions the interviewer might ask:
- How would you add different book types (ebook, audiobook)?
- How to handle multiple copies of the same book?
- How to add a reservation system?


Objects:
    Library, Book, Members, Loan

Time: 30-40 minutes
"""

from datetime import timedelta, date
import uuid


class Book:
    """Represents a book in the library catalog"""

    def __init__(self, title: str, author: str, isbn: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.isbn = isbn

    def __eq__(self, other) -> bool:
        return isinstance(other, Book) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (id={self.id})"

    def __repr__(self) -> str:
        return f"Book {self.id} ({self.title}, {self.author}, {self.isbn})"


class Member:
    """Represents a Member of the library, who can borrow books"""

    def __init__(self, name: str, email: str) -> None:
        self.id: str = str(uuid.uuid4())
        self.name = name
        self.email = email
        self.outstanding_fees: float = 0.0

    def __eq__(self, other) -> bool:
        return isinstance(other, Member) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __str__(self) -> str:
        return f"{self.name}, email:{self.email} ({self.id})"

    def __repr__(self) -> str:
        return f"Member (id: {self.id}, name: {self.name}, email: {self.email}, outstanding fees: {self.outstanding_fees})"


class Loan:
    """
    Tracks a book loan transaction between a member and the library.

    Records the borrowing date and calculates late fees based on
    a 14-day loan period at $0.50 per day after due date.
    """

    def __init__(self, book: Book, member: Member, date_due: date):
        self.id: str = str(uuid.uuid4())
        self.book = book
        self.member = member
        self.date_checkout: date = date.today()
        self.date_due = date_due
        self.late_fee = 0.0

    def __eq__(self, other) -> bool:
        return isinstance(other, Loan) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def _calculate_late_fee(self, return_date: date | None = None) -> float:
        check_date = return_date or date.today()
        if check_date > self.date_due:
            return (check_date - self.date_due).days * Library.FEE_PER_DAY_EXTRA
        return 0

    def __str__(self) -> str:
        return f"Member {self.member.name} loan the book {self.book.title}"

    def __repr__(self) -> str:
        return f"Loan (id:{self.id}, book:{self.book}, member:{self.member}, checkout date:{self.date_checkout}, due date:{self.date_due}, late_fee {self.late_fee})"


class Library:
    """Library where members can borrow books"""
    MAX_BOOKS = 3
    FREE_DAYS = 14
    FEE_PER_DAY_EXTRA = 0.50  # Dollars per day

    def __init__(self, name: str) -> None:
        self.name = name
        self.members: dict[str, Member] = {}
        self.books: dict[str, Book] = {}
        self.active_loans: dict[Book, Loan] = {}
        self.historic_loans: list[Loan] = []

    def add_member(self, member: Member) -> str:
        """Add new Member to the library"""
        if member.id in self.members:
            raise ValueError(f"Member {member.id} already registered")
        elif any(m.email == member.email for m in self.members.values()):
            raise ValueError(f"Email {member.email} already used")
        self.members[member.id] = member
        return f"Member {member.name} added to the library members"

    def add_book(self, book: Book) -> str:
        """Add new book to the library's collection!"""
        if book.id in self.books:
            raise ValueError(f"Book {book.id} is already registered in the collection")
        self.books[book.id] = book
        return f"Book {book.title} by {book.author}, isbn ({book.isbn}))"

    def show_members(self) -> None:
        """Display all registered members in alphabetical order."""
        sorted_members = sorted(self.members.values(), key=lambda m: m.name)
        print("\nLibrary's Members")
        if sorted_members:
            for index, member in enumerate(sorted_members, start=1):
                print(f"{index} - {member}")
        else:
            print("Don't have any members registered yet")

    def show_books(self) -> None:
        """Display all registered books in alphabetical order."""
        sorted_books = sorted(self.books.values(), key=lambda b: b.title)
        print("\nLibrary's Books")
        if sorted_books:
            for index, book in enumerate(sorted_books, start=1):
                status = 'Avaliable' if book not in self.active_loans else "Borrowed"
                print(f"{index} - {book} is {status}")
        else:
            print("Don't have any book registered yet")

    def show_active_loans(self) -> None:
        sorted_loan = sorted(self.active_loans.values(), key=lambda loan: loan.date_checkout)
        print("\nLibrary's Actives loans")
        if sorted_loan:
            for index, loan in enumerate(sorted_loan, start=1):
                print(f"{index} - {loan.date_checkout.isoformat()}: {loan}")
        else:
            print("Don't have any active loan")

    def show_loan_history(self) -> None:
        sorted_loan = sorted(self.historic_loans, key=lambda loan: loan.date_checkout)
        print("\nLibrary's Historic of loans")
        if sorted_loan:
            for index, loan in enumerate(sorted_loan, start=1):
                print(f"{index} - {loan.date_checkout.isoformat()}: {loan}")
        else:
            print("Library Don't have any historic loan yet")

    def member_borrow_book(self, book: Book, member: Member) -> Loan:
        """Member borrow a book making a loan"""

        if book and book.id not in self.books:
            raise ValueError(f"Book {book.id} dont exist in Library's Collection")

        if member and member.id not in self.members:
            raise ValueError(f"Member {member.id} dont exist in Library's Members")

        if book in self.active_loans:
            raise ValueError(f"Book {book.id} already borrowed")

        qnt_loan_member = sum(1 for loan in self.active_loans.values() if loan.member.id == member.id)
        if qnt_loan_member >= self.MAX_BOOKS:
            raise ValueError(f"Member already have borrowed {qnt_loan_member} is the limit per member")

        date_due = date.today() + timedelta(days=self.FREE_DAYS)
        loan = Loan(book, member, date_due)
        self.active_loans[book] = loan
        return loan

    def member_return_book(self, book: Book) -> Loan:
        """Member return a book and finish the loan of book"""
        if book.id not in self.books:
            raise ValueError(f"Book {book.id} dont exist in Library's Collection")

        if book not in self.active_loans:
            raise ValueError(f"Book {book.id} already returned")

        loan = self.active_loans.pop(book)
        loan.late_fee = loan._calculate_late_fee()
        loan.member.outstanding_fees += loan.late_fee
        self.historic_loans.append(loan)

        return loan

    def search_book(self, query: str) -> list[Book]:
        """Search Books for title or author"""
        query_lower = query.lower()
        matches = [
            book for book in self.books.values()
            if query_lower in book.title.lower() or query_lower in book.author.lower()
        ]
        return matches

    def __str__(self) -> str:
        return f"Library {self.name} with {len(self.books)} books!"

    def __repr__(self) -> str:
        return f"Library {self.name} (Number of Books:{len(self.books)}, Number of borrow books: {len(self.active_loans)}, Number of total finish loans{len(self.historic_loans)})"


def demon():
    print("=== Library Management System ===")

    library = Library("Shakespare Librarys")
    book1 = Book("Title1", "Author1", "0001")
    library.add_book(book1)
    book2 = Book("Title2", "Author2", "0002")
    library.add_book(book2)
    book3 = Book("Title3", "Author3", "0003")
    library.add_book(book3)
    book4 = Book("Title1", "Author1", "0001")
    library.add_book(book4)

    member1 = Member("Name1", "1email@gmail.com")

    library.add_member(member1)
    member2 = Member("Name2", "2email@gmail.com")
    library.add_member(member2)

    library.show_books()
    library.show_members()

    library.member_borrow_book(book1, member1)
    library.member_borrow_book(book2, member1)
    library.member_borrow_book(book3, member1)
    library.member_borrow_book(book4, member2)

    library.member_return_book(book1)
    library.member_return_book(book4)

    library.show_active_loans()
    library.show_loan_history()

    print(library.search_book("title"))
    print(library.search_book("2"))


if __name__ == '__main__':
    demon()
