from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Profile, BookIssue, Book
from datetime import datetime
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def redirect_user_by_role(user):
    role = user.profile.role

    if role == "reader":
        return redirect("/studentDashboard")
    elif role == "librarian":
        return redirect("/librarianDashboard/")
    else:
        return redirect("/homepage/")

def renderHomePage(request):
    return render(request, 'homePage.html')

def renderContactPage(request):
    return render(request, 'contactPage.html')


#Student Dashboard and its related logics
@login_required
def renderStudentDashboard(request):
    if request.user.is_superuser:
        return HttpResponseForbidden("Admins cannot access student dashboard")
    
    # Get the count of books issued to the current user
    issued_books_count = BookIssue.objects.filter(user=request.user).count()
    issued_book_ids = set(
        BookIssue.objects.filter(
            user=request.user,
            returned_at__isnull=True
        ).values_list("book_id", flat=True)
    )
    available_books = Book.objects.all()

    # Books with fines (returned or not returned)
    pending_fines_count = BookIssue.objects.filter(user=request.user, fine__gt=0).count()


    # Get the count of books to be returned
    to_be_returned_count = BookIssue.objects.filter(user=request.user, returned_at__isnull=True).count()



    # Get the count of issued Books with fines
    issued_books_with_fines = BookIssue.objects.filter(user=request.user, fine__gt=0).count()

    # Get recent avtivities of readers
    recent_activities = []

    # Get recently issued books (last 5)
    recent_issued_books = BookIssue.objects.filter(user=request.user).select_related('book', 'user').order_by('-issued_at')[:5]

    for issue in recent_issued_books:
        recent_activities.append({
            'type': 'issue',
            'message': f"{issue.book.title} issued by {issue.issued_by.first_name} {issue.issued_by.last_name} ",
            'date': issue.issued_at,
            'icon': '📚'
        })

    # Get recently returned books (last 5)
    returned_books = BookIssue.objects.filter(user=request.user, returned_at__isnull=False).select_related('book', 'user').order_by('-returned_at')[:5]

    for issue in returned_books:
        recent_activities.append({
            'type': 'return',
            'message': f"{issue.book.title} returned by {issue.user.first_name} {issue.user.last_name} ",
            'date': issue.returned_at,
            'icon': '↩️'
        })

    context = {
        'issued_books_count': issued_books_count,
        'issued_books_with_fines': issued_books_with_fines,
        'pending_fines_count': pending_fines_count,
        'to_be_returned_count': to_be_returned_count,
        'available_books': available_books,
        'issued_book_ids': issued_book_ids,
        'recent_activities': recent_activities,
    }

    return render(request, 'studentDashboard.html', context)

def renderProfilePage(request):
    return render(request, 'profilePage.html')

# book_id came from totalBooksList
def renderBookDetailsPage(request, book_id):
    """
    Fetch a specific book from database and display its details
    """
    try:
        # Get book from database using ID
        book = Book.objects.get(id=book_id)
        
        context = {
            'book': book,
            'id': book.id,
            'title': book.title,
            'editor': book.editor,
            'description': book.description,
            'author': book.author,
            'about_author': book.about_author,
            'category': book.category,
            'publisher': book.publisher,
            'published_date': book.published_date,
            'price': book.price,
            'total_quantity': book.total_quantity,
            'available_quantity': book.available_quantity,
            'isbn_number': book.isbn_number,
            'pages': book.pages,
            'cover_image': book.cover_image,
            'language': book.language,
            'created_at': book.created_at,
            'created_by': book.created_by
        }
        
        return render(request, 'bookDetailsPage.html', context)
    
    except Book.DoesNotExist:
        return render(request, 'bookDetailsPage.html', {
            'error': 'Book not found'
        })

def renderBookLists(request):
    # Get book statistics
    total_books = Book.objects.all().count()
    available_books = Book.objects.filter(available_quantity__gt=0).count()
    issued_books = BookIssue.objects.filter(returned_at__isnull=True).count()
    
    # Get all books with their details
    all_books = Book.objects.all().select_related('created_by')
    
    context = {
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'all_books': list(all_books),
    }
    
    return render(request, 'totalBooksList.html', context)

@login_required
def renderLibrarianDashboard(request):
    # Get book statistics
    total_books = Book.objects.all().count()
    available_books = Book.objects.filter(available_quantity__gt=0).count()
    issued_books = BookIssue.objects.filter(returned_at__isnull=True).count()
    
    # Get recently issued books (last 5)
    recent_issued_books = BookIssue.objects.filter(
        returned_at__isnull=True
    ).select_related('book', 'user').order_by('-issued_at')[:5]
    
    # Calculate pending fines
    all_unreturned_issues = BookIssue.objects.filter(returned_at__isnull=True)
    total_pending_fines = sum(issue.calculate_fine() for issue in all_unreturned_issues)
    
    # Get recent activities
    recent_activities = []
    
    # Get recently returned books (last 5)
    returned_books = BookIssue.objects.filter(
        returned_at__isnull=False
    ).select_related('book', 'user').order_by('-returned_at')[:5]
    
    for issue in returned_books:
        recent_activities.append({
            'type': 'return',
            'message': f"{issue.book.title} returned by {issue.user.first_name} {issue.user.last_name} ",
            'date': issue.returned_at,
            'icon': '↩️'
        })
    
    # Get recently issued books (last 3)
    issued = BookIssue.objects.filter(
        returned_at__isnull=True
    ).select_related('book', 'user').order_by('-issued_at')[:3]
    
    for issue in issued:
        recent_activities.append({
            'type': 'issue',
            'message': f"{issue.book.title} issued to {issue.user.first_name} {issue.user.last_name}",
            'date': issue.issued_at,
            'icon': '📘'
        })
    
    # Get recently added books (last 3)
    added_books = Book.objects.order_by('-created_at')[:3]
    
    for book in added_books:
        recent_activities.append({
            'type': 'add',
            'message': f"{book.title} added by {book.created_by.first_name or book.created_by.username}",
            'date': book.created_at,
            'icon': '📚'
        })
    
    # Sort by date (most recent first) and take last 5
    recent_activities.sort(key=lambda x: x['date'], reverse=True)
    recent_activities = recent_activities[:5] 
    
    context = {
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'total_pending_fines': total_pending_fines,
        'recent_issued_books': recent_issued_books,
        'recent_activities': recent_activities,
        'today': timezone.localdate()
    }
    
    return render(request, 'librarianDashboard.html', context)

#Authentication
def renderLogin(request):
    # if request.user.is_authenticated:
    #     return redirect("/homePage/")
    return render(request, 'login.html')

def authLogin(request):
    if request.method == "POST":
        logout(request)

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect_user_by_role(user)

        return render(request, "login.html", {
            "error": "invalid credentials"
        })
    return render(request, "login.html")

def authSignup(request):
    if request.method == "POST":
        username = request.POST.get('email')
        fullName = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")
        phone = request.POST.get('phone')
        address = request.POST.get('address')
    
        if User.objects.filter(email=email).exists():
            return render(request, "login.html", {
                "error": "email already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fullName
        )

        Profile.objects.create(
            user=user,
            phone=phone,
            role=role,
            address=address
        )

        login(request, user)

        return redirect_user_by_role(user)
    
@login_required
def renderPendingFines(request):
    """
    View to display pending fines for all students
    """
    # Get all users with pending fines
    all_issues = BookIssue.objects.filter(returned_at__isnull=True)
    
    student_fines = []
    
    for issue in all_issues:
        # Calculate fine for this issue
        fine_amount = issue.calculate_fine()

        # 🚨 Skip users with no fine
        if fine_amount <= 0:
            continue
        
        # Get due_date as a proper date object
        due = issue.due_date
        if hasattr(due, 'date'):
            due = due.date()
        
        today = timezone.localdate()
        
        # Determine status
        if today > due:
            status = 'overdue'
        else:
            # Check if due date is approaching
            days_until_due = (due - today).days
            if days_until_due < 3 and days_until_due >= 0:
                status = 'warning'
            else:
                status = '  '
        
        # Get student initials
        user = issue.user
        initials = (user.first_name[0] if user.first_name else user.username[0]).upper()
        if user.last_name:
            initials += user.last_name[0].upper()
        
        student_fines.append({
            'id': issue.id,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'student_id': user.id,
            'amount': float(fine_amount),
            'due_date': due.isoformat(),
            'status': status,
            'initials': initials
        })
    
    # Calculate stats
    total_fines = sum(fine['amount'] for fine in student_fines)
    overdue_fines = sum(fine['amount'] for fine in student_fines if fine['status'] == 'overdue')
    
    context = {
        'student_fines': student_fines,
        'total_students': len(student_fines),
        'total_fines': total_fines,
        'overdue_fines': overdue_fines,
    }
    
    return render(request, 'pendingFines.html', context)

@login_required
def renderAddBook(request):
    """
    View to display form for adding new books
    """
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        category = request.POST.get('category', '').strip()
        publisher = request.POST.get('publisher', '').strip()
        published_date = request.POST.get('published_date')
        price = request.POST.get('price')
        quantity = request.POST.get('total_quantity')
        isbn_number = request.POST.get('isbn_number', '').strip()
        pages = request.POST.get('pages')
        language = request.POST.get('language', '').strip()
        description = request.POST.get('description', '').strip()
        about_author = request.POST.get('about_author', '').strip()
        editor = request.POST.get('editor', '').strip()
        cover_image = request.FILES.get('cover_image')
        created_by = request.user
        
        # Validate required fields
        errors = []
        if not title:
            errors.append('Title is required')
        if not author:
            errors.append('Author is required')
        if not category:
            errors.append('Category is required')
        if not publisher:
            errors.append('Publisher is required')
        if not published_date:
            errors.append('Published date is required')
        if not isbn_number:
            errors.append('ISBN number is required')
        if not language:
            errors.append('Language is required')
        
        # Validate numeric fields
        try:
            if not price:
                raise ValueError('Price is required')
            price = float(price)
        except (ValueError, TypeError):
            errors.append('Price must be a valid number')
        
        try:
            if not quantity:
                raise ValueError('Quantity is required')
            quantity = int(quantity)
        except (ValueError, TypeError):
            errors.append('Quantity must be a valid number')
        
        try:
            if not pages:
                raise ValueError('Pages is required')
            pages = int(pages)
        except (ValueError, TypeError):
            errors.append('Pages must be a valid number')
        
        # Check for ISBN uniqueness
        if isbn_number and Book.objects.filter(isbn_number=isbn_number).exists():
            errors.append('ISBN number already exists')
        
        if errors:
            context = {
                'error': ', '.join(errors)
            }
            return render(request, 'addBook.html', context)
        
        try:
            # Create new book
            book = Book.objects.create(
                title=title,
                author=author,
                description=description,
                about_author=about_author,
                category=category,
                publisher=publisher,
                editor=editor,
                published_date=published_date,
                price=price,
                isbn_number=isbn_number,
                pages=pages,
                language=language,
                total_quantity=quantity,
                available_quantity=quantity,
                cover_image=cover_image,
                created_by=created_by
            )
            
            return redirect('renderBookLists')  # Redirect to books list
            
        except Exception as e:
            context = {
                'error': f'Error adding book: {str(e)}'
            }
            return render(request, 'addBook.html', context)
    
    return render(request, 'addBook.html')

@login_required
def renderIssuedBooks(request):
    if request.method == 'GET':
        issued_books = BookIssue.objects.filter(returned_at__isnull=True).select_related('book', 'user')

        context = {
            'issued_books': issued_books,
            'today': timezone.localdate()
        }

        return render(request, 'issuedBooks.html', context)
    
@login_required
def renderStudentIssuedbooks(request):
    if request.method == 'GET':
        issued_books = BookIssue.objects.filter(user=request.user, returned_at__isnull=True).select_related('book', 'user')

        user_id = request.user.id

        context = {
            'user_id': user_id,
            'issued_books': issued_books,
            'today': timezone.localdate()
        }

        return render(request, 'studentBookIssued.html', context)
    # return render(request, 'studentBookIssued.html')

@login_required
def renderBookIssueReq(request):
    return render(request, 'bookIssueReq.html')

@login_required
def renderStudentPendingFines(request):
    return render(request, 'studentFines.html')

@login_required
def renderReturnBookList(request):
    # Get all issued books for the user (both returned and not returned)
    issued_books = BookIssue.objects.filter(
        user=request.user
    ).select_related('book').order_by('-issued_at')
    
    # Count pending returns
    pending_count = issued_books.filter(returned_at__isnull=True).count()
    
    # Calculate total fines
    total_fines = sum(book.fine for book in issued_books)
    
    context = {
        'issued_books': issued_books,
        'issued_books_count': issued_books.count(),
        'pending_count': pending_count,
        'total_fines': total_fines,
    }
    
    return render(request, 'returnBookList.html', context)


@login_required
def confirmIssueBook(request, book_id):
    """
    Display confirmation page before issuing book
    """
    try:
        book = Book.objects.get(id=book_id)
        
        # Check if book is available
        if book.available_quantity <= 0:
            return render(request, 'confirmIssueBook.html', {
                'error': 'This book is currently unavailable'
            })
        
        # Check if user already has this book issued
        already_issued = BookIssue.objects.filter(
            book=book,
            user=request.user,
            returned_at__isnull=True
        ).exists()
        
        if already_issued:
            return render(request, 'confirmIssueBook.html', {
                'error': 'You have already issued this book'
            })
        
        # Calculate dates
        today = timezone.localdate()
        due_date = today + timedelta(days=14)
        
        context = {
            'book': book,
            'today': today,
            'book_id': book_id,
            'due_date': due_date
        }
        
        return render(request, 'confirmIssueBook.html', context)
        
    except Book.DoesNotExist:
        return redirect('studentDashboard')


def processIssueBook(request, book_id):
    """
    Process the book issue after confirmation
    """
    if request.method == 'POST':
        try:
            book = Book.objects.get(id=book_id)
            
            # Double check availability
            if book.available_quantity <= 0:
                messages.error(request, 'Book is no longer available')
                return redirect('studentDashboard')
            
            # Check if already issued
            already_issued = BookIssue.objects.filter(
                book=book,
                user=request.user,
                returned_at__isnull=True
            ).exists()
            
            if already_issued:
                messages.error(request, 'You have already issued this book')
                return redirect('studentDashboard')
            
            # Calculate due date
            due_date = timezone.localdate() + timedelta(days=14)
            
            # Create book issue
            BookIssue.objects.create(
                book=book,
                user=request.user,
                issued_by=request.user,  # Self-issue or get librarian
                issued_at=timezone.localdate(),
                due_date=due_date,
                returned_at=None,
                fine=0
            )
            
            # Update book quantity
            book.available_quantity -= 1
            book.is_issued = True
            book.save()
            
            messages.success(request, f'Successfully issued "{book.title}". Due date: {due_date}')
            return redirect('studentDashboard')
            
        except Book.DoesNotExist:
            messages.error(request, 'Book not found')
            return redirect('studentDashboard')
    
    return redirect('studentDashboard')

@login_required
def returnBook(request, issue_id):
    if request.method == 'POST':
        try:
            issue = BookIssue.objects.get(id=issue_id, user=request.user)
            
            if issue.returned_at:
                messages.warning(request, 'This book has already been returned')
            else:
                issue.mark_returned()
                messages.success(request, f'Successfully returned "{issue.book.title}"!')
            
        except BookIssue.DoesNotExist:
            messages.error(request, 'Book issue not found')
        
        return redirect('renderReturnBookList')
    
    return redirect('renderReturnBookList')