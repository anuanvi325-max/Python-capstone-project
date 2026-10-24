from django.urls import path
from . import views

urlpatterns = [
    # langing url for home page
    path('', views.renderHomePage),
    path('loginPage/', views.renderLogin),
    path('homePage/', views.renderHomePage),
    path('contactPage/', views.renderContactPage),

    # student urls
    path('studentDashboard/', views.renderStudentDashboard, name='studentDashboard'),
    path('studentDashboard/studentBooksIssued/', views.renderStudentIssuedbooks),
    path('studentDashboard/bookDetailsPage/<int:book_id>/', views.renderBookDetailsPage),
    path('studentDashboard/pendingFines/', views.renderStudentPendingFines),
    path('studentDashboard/returnBookList/', views.renderReturnBookList, name='renderReturnBookList'),
    # path('studentDashboard/returnBookList/returnBook/<int:issue_id>/', views.returnBook, name='returnBook'),
    path('returnBook/<int:issue_id>/', views.returnBook, name='returnBook'),
    path('profilePage/', views.renderProfilePage),
    # path('bookDetailsPage/<int:book_id>/', views.renderBookDetailsPage),

    # book issue
    path('confirmIssueBook/<int:book_id>/', views.confirmIssueBook, name='confirmIssueBook'),
    path('processIssueBook/<int:book_id>/', views.processIssueBook, name='processIssueBook'),

    # librarian urls
    path('librarianDashboard/', views.renderLibrarianDashboard),
    path('librarianDashboard/booksIssued/', views.renderIssuedBooks),
    path('librarianDashboard/pendingFines/', views.renderPendingFines),
    path('librarianDashboard/booksLists/', views.renderBookLists, name='renderBookLists'),
    path('librarianDashboard/booksLists/addBook/', views.renderAddBook),
    path('librarianDashboard/booksLists/bookDetailsPage/<int:book_id>/', views.renderBookDetailsPage),
    path('librarianDashboard/addBook/', views.renderAddBook),
    path('librarianDashboard/bookIssueRequests/', views.renderBookIssueReq),

    # auth urls
    path('authLogin/', views.authLogin, name='authLogin'),
    path('authSignup/', views.authSignup, name='authSignup'),
]