"""
Professional Test Suite for Library Management System
Using pytest with industry best practices

INSTALLATION:
    pip install pytest pytest-cov

EXECUTION:
    pytest test_library_professional.py -v
    pytest test_library_professional.py --cov=library
    pytest test_library_professional.py -k "search"
    pytest test_library_professional.py -x
"""

import pytest
from datetime import date, timedelta
from library import Library, Book, Member, Loan


# ============================================
# FIXTURES - Reusable Setup
# ============================================

@pytest.fixture
def library():
    """Fixture: creates clean library for each test"""
    return Library("Test Library")


@pytest.fixture
def book():
    """Fixture: creates a standard book"""
    return Book("Test Book", "Test Author", "123-456")


@pytest.fixture
def another_book():
    """Fixture: creates another book"""
    return Book("Another Book", "Another Author", "789-012")


@pytest.fixture
def member():
    """Fixture: creates standard member"""
    return Member("John Doe", "john@test.com")


@pytest.fixture
def another_member():
    """Fixture: creates another member"""
    return Member("Jane Smith", "jane@test.com")


@pytest.fixture
def library_with_book(library, book):
    """Fixture: library with one book added"""
    library.add_book(book)
    return library


@pytest.fixture
def library_with_member(library, member):
    """Fixture: library with one member added"""
    library.add_member(member)
    return library


@pytest.fixture
def library_ready(library, book, member):
    """Fixture: library ready for borrowing"""
    library.add_book(book)
    library.add_member(member)
    return library


# ============================================
# UNIT TESTS - Book
# ============================================

class TestBook:
    """Unit tests for Book class"""
    
    def test_book_creation(self, book):
        """Should create book with correct attributes"""
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.isbn == "123-456"
        assert book.id is not None
    
    def test_book_id_is_unique(self):
        """Should generate unique IDs for each book"""
        book1 = Book("Same Title", "Same Author", "Same ISBN")
        book2 = Book("Same Title", "Same Author", "Same ISBN")
        assert book1.id != book2.id
    
    def test_book_equality_same_object(self, book):
        """Should consider same object as equal"""
        assert book == book
    
    def test_book_equality_different_objects(self):
        """Should consider different objects as different"""
        book1 = Book("Book", "Author", "123")
        book2 = Book("Book", "Author", "123")
        assert book1 != book2
    
    def test_book_hashable(self, book, another_book):
        """Should allow usage in sets and dicts"""
        book_set = {book, another_book}
        assert len(book_set) == 2
    
    def test_book_str_representation(self, book):
        """Should have readable string representation"""
        str_repr = str(book)
        assert "Test Book" in str_repr
        assert "Test Author" in str_repr


# ============================================
# UNIT TESTS - Member
# ============================================

class TestMember:
    """Unit tests for Member class"""
    
    def test_member_creation(self, member):
        """Should create member with correct attributes"""
        assert member.name == "John Doe"
        assert member.email == "john@test.com"
        assert member.outstanding_fees == 0.0
        assert member.id is not None
    
    def test_member_id_is_unique(self):
        """Should generate unique IDs for each member"""
        member1 = Member("Same Name", "same@email.com")
        member2 = Member("Same Name", "same@email.com")
        assert member1.id != member2.id
    
    def test_member_initial_fees_zero(self, member):
        """Should initialize with zero fees"""
        assert member.outstanding_fees == 0.0


# ============================================
# UNIT TESTS - Loan
# ============================================

class TestLoan:
    """Unit tests for Loan class"""
    
    def test_loan_creation(self, book, member):
        """Should create loan with correct attributes"""
        due_date = date.today() + timedelta(days=14)
        loan = Loan(book, member, due_date)
        
        assert loan.book == book
        assert loan.member == member
        assert loan.date_checkout == date.today()
        assert loan.date_due == due_date
        assert loan.late_fee == 0.0
    
    @pytest.mark.parametrize("days_late,expected_fee", [
        (0, 0.0),
        (1, 0.5),
        (5, 2.5),
        (10, 5.0),
        (30, 15.0),
    ])
    def test_calculate_late_fee(self, book, member, days_late, expected_fee):
        """Should calculate late fee correctly"""
        due_date = date.today() - timedelta(days=days_late)
        loan = Loan(book, member, due_date)
        
        calculated_fee = loan._calculate_late_fee()
        assert calculated_fee == expected_fee
    
    def test_calculate_late_fee_early_return(self, book, member):
        """Should return zero if returned early"""
        due_date = date.today() + timedelta(days=14)
        loan = Loan(book, member, due_date)
        
        return_date = date.today() + timedelta(days=5)
        fee = loan._calculate_late_fee(return_date)
        assert fee == 0.0


# ============================================
# UNIT TESTS - Library Basic Operations
# ============================================

class TestLibraryBasicOperations:
    """Tests for library basic operations"""
    
    def test_library_creation(self, library):
        """Should create empty library"""
        assert library.name == "Test Library"
        assert len(library.books) == 0
        assert len(library.members) == 0
        assert len(library.active_loans) == 0
    
    def test_add_book_success(self, library, book):
        """Should add book successfully"""
        result = library.add_book(book)
        
        assert book.id in library.books
        assert "Test Book" in result
    
    def test_add_duplicate_book_raises_error(self, library, book):
        """Should reject duplicate book"""
        library.add_book(book)
        
        with pytest.raises(ValueError, match="already registered"):
            library.add_book(book)
    
    def test_add_member_success(self, library, member):
        """Should add member successfully"""
        result = library.add_member(member)
        
        assert member.id in library.members
        assert "John Doe" in result
    
    def test_add_duplicate_member_raises_error(self, library, member):
        """Should reject duplicate member"""
        library.add_member(member)
        
        with pytest.raises(ValueError, match="already registered"):
            library.add_member(member)
    
    def test_add_member_duplicate_email_raises_error(self, library, member):
        """Should reject duplicate email"""
        library.add_member(member)
        
        duplicate_member = Member("Different Name", "john@test.com")
        with pytest.raises(ValueError, match="Email.*already used"):
            library.add_member(duplicate_member)


# ============================================
# BORROWING TESTS
# ============================================

class TestBorrowing:
    """Tests for borrowing operations"""
    
    def test_borrow_book_success(self, library_ready, book, member):
        """Should borrow book successfully"""
        loan = library_ready.member_borrow_book(book, member)
        
        assert isinstance(loan, Loan)
        assert loan.book == book
        assert loan.member == member
        assert book in library_ready.active_loans
    
    def test_borrow_sets_correct_due_date(self, library_ready, book, member):
        """Should set correct due date (14 days)"""
        loan = library_ready.member_borrow_book(book, member)
        
        expected_due = date.today() + timedelta(days=14)
        assert loan.date_due == expected_due
    
    def test_borrow_already_borrowed_book_fails(self, library_ready, book, member, another_member):
        """Should reject borrowing already borrowed book"""
        library_ready.add_member(another_member)
        library_ready.member_borrow_book(book, member)
        
        with pytest.raises(ValueError, match="already borrowed"):
            library_ready.member_borrow_book(book, another_member)
    
    def test_borrow_nonexistent_book_fails(self, library_with_member, member):
        """Should reject borrowing non-existent book"""
        fake_book = Book("Nonexistent", "Author", "999")
        
        with pytest.raises(ValueError, match="dont exist"):
            library_with_member.member_borrow_book(fake_book, member)
    
    def test_borrow_with_nonexistent_member_fails(self, library_with_book, book):
        """Should reject borrowing by non-member"""
        fake_member = Member("Fake", "fake@test.com")
        
        with pytest.raises(ValueError, match="dont exist"):
            library_with_book.member_borrow_book(book, fake_member)
    
    def test_borrow_respects_max_books_limit(self, library, member):
        """Should enforce 3 books limit per member"""
        library.add_member(member)
        
        books = [Book(f"Book {i}", f"Author {i}", f"00{i}") for i in range(4)]
        for book in books:
            library.add_book(book)
        
        library.member_borrow_book(books[0], member)
        library.member_borrow_book(books[1], member)
        library.member_borrow_book(books[2], member)
        
        with pytest.raises(ValueError, match="limit"):
            library.member_borrow_book(books[3], member)
    
    def test_multiple_members_can_borrow_different_books(self, library, member, another_member):
        """Should allow different members to borrow different books"""
        library.add_member(member)
        library.add_member(another_member)
        
        book1 = Book("Book 1", "Author 1", "001")
        book2 = Book("Book 2", "Author 2", "002")
        library.add_book(book1)
        library.add_book(book2)
        
        library.member_borrow_book(book1, member)
        library.member_borrow_book(book2, another_member)
        
        assert len(library.active_loans) == 2


# ============================================
# RETURNING TESTS
# ============================================

class TestReturning:
    """Tests for returning operations"""
    
    def test_return_book_success(self, library_ready, book, member):
        """Should return borrowed book successfully"""
        library_ready.member_borrow_book(book, member)
        loan = library_ready.member_return_book(book)
        
        assert isinstance(loan, Loan)
        assert book not in library_ready.active_loans
        assert loan in library_ready.historic_loans
    
    def test_return_on_time_no_fee(self, library_ready, book, member):
        """Should return on time without late fee"""
        library_ready.member_borrow_book(book, member)
        loan = library_ready.member_return_book(book)
        
        assert loan.late_fee == 0.0
        assert member.outstanding_fees == 0.0
    
    @pytest.mark.parametrize("days_late,expected_fee", [
        (1, 0.5),
        (5, 2.5),
        (10, 5.0),
    ])
    def test_return_late_calculates_fee(self, library_ready, book, member, days_late, expected_fee):
        """Should calculate fee for late returns"""
        loan = library_ready.member_borrow_book(book, member)
        loan.date_due = date.today() - timedelta(days=days_late)
        
        returned_loan = library_ready.member_return_book(book)
        
        assert returned_loan.late_fee == expected_fee
        assert member.outstanding_fees == expected_fee
    
    def test_return_not_borrowed_book_fails(self, library_with_book, book):
        """Should reject returning non-borrowed book"""
        with pytest.raises(ValueError, match="already returned"):
            library_with_book.member_return_book(book)
    
    def test_return_nonexistent_book_fails(self, library):
        """Should reject returning non-existent book"""
        fake_book = Book("Fake", "Author", "999")
        
        with pytest.raises(ValueError, match="dont exist"):
            library.member_return_book(fake_book)
    
    def test_member_can_borrow_again_after_return(self, library_ready, book, member):
        """Should allow re-borrowing after return"""
        library_ready.member_borrow_book(book, member)
        library_ready.member_return_book(book)
        
        loan = library_ready.member_borrow_book(book, member)
        assert isinstance(loan, Loan)
        assert book in library_ready.active_loans


# ============================================
# SEARCH TESTS
# ============================================

class TestSearch:
    """Tests for search functionality"""
    
    @pytest.fixture
    def library_with_books(self, library):
        """Fixture: library with multiple books"""
        books_data = [
            ("Python Programming", "John Smith", "001"),
            ("Java Programming", "Jane Doe", "002"),
            ("Python Data Science", "John Smith", "003"),
            ("Web Development", "Alice Johnson", "004"),
        ]
        
        for title, author, isbn in books_data:
            library.add_book(Book(title, author, isbn))
        
        return library
    
    def test_search_by_exact_title(self, library_with_books):
        """Should find book by exact title"""
        results = library_with_books.search_book("Python Programming")
        assert len(results) == 1
        assert results[0].title == "Python Programming"
    
    def test_search_by_partial_title(self, library_with_books):
        """Should find books by partial title"""
        results = library_with_books.search_book("Python")
        assert len(results) == 2
    
    def test_search_by_author(self, library_with_books):
        """Should find books by author"""
        results = library_with_books.search_book("John Smith")
        assert len(results) == 2
    
    @pytest.mark.parametrize("query", ["python", "PYTHON", "PyThOn"])
    def test_search_case_insensitive(self, library_with_books, query):
        """Should search case-insensitively"""
        results = library_with_books.search_book(query)
        assert len(results) == 2
    
    def test_search_no_results(self, library_with_books):
        """Should return empty list for no matches"""
        results = library_with_books.search_book("Nonexistent Book")
        assert len(results) == 0
        assert isinstance(results, list)


# ============================================
# INTEGRATION TESTS
# ============================================

class TestIntegrationScenarios:
    """Integration tests for complete scenarios"""
    
    def test_complete_borrow_return_cycle(self, library, book, member):
        """Should complete full borrow-return cycle"""
        library.add_book(book)
        library.add_member(member)
        
        loan = library.member_borrow_book(book, member)
        assert book in library.active_loans
        
        returned_loan = library.member_return_book(book)
        assert book not in library.active_loans
        assert returned_loan.id == loan.id
    
    def test_accumulated_fees_multiple_loans(self, library, member):
        """Should accumulate fees from multiple loans"""
        library.add_member(member)
        
        book1 = Book("Book 1", "Author 1", "001")
        library.add_book(book1)
        loan1 = library.member_borrow_book(book1, member)
        loan1.date_due = date.today() - timedelta(days=2)
        library.member_return_book(book1)
        
        assert member.outstanding_fees == 1.0
        
        book2 = Book("Book 2", "Author 2", "002")
        library.add_book(book2)
        loan2 = library.member_borrow_book(book2, member)
        loan2.date_due = date.today() - timedelta(days=4)
        library.member_return_book(book2)
        
        assert member.outstanding_fees == 3.0
    
    def test_multiple_members_realistic_scenario(self, library):
        """Should handle realistic multi-member scenario"""
        alice = Member("Alice", "alice@test.com")
        bob = Member("Bob", "bob@test.com")
        library.add_member(alice)
        library.add_member(bob)
        
        books = [Book(f"Book {i}", f"Author {i}", f"00{i}") for i in range(5)]
        for book in books:
            library.add_book(book)
        
        library.member_borrow_book(books[0], alice)
        library.member_borrow_book(books[1], alice)
        library.member_borrow_book(books[2], bob)
        library.member_borrow_book(books[3], bob)
        library.member_borrow_book(books[4], bob)
        
        assert len(library.active_loans) == 5
        
        library.member_return_book(books[0])
        
        assert len(library.active_loans) == 4
        assert len(library.historic_loans) == 1


# ============================================
# CONSTANTS TESTS
# ============================================

class TestLibraryConstants:
    """Tests for library constants"""
    
    def test_max_books_constant(self):
        """Should have MAX_BOOKS constant set to 3"""
        assert Library.MAX_BOOKS == 3
    
    def test_free_days_constant(self):
        """Should have FREE_DAYS constant set to 14"""
        assert Library.FREE_DAYS == 14
    
    def test_fee_per_day_constant(self):
        """Should have FEE_PER_DAY_EXTRA constant set to 0.50"""
        assert Library.FEE_PER_DAY_EXTRA == 0.50