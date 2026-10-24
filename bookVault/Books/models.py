from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, null=True)
    about_author = models.TextField(max_length=1000, null=True)
    category = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    editor = models.CharField(max_length=100, null=True)
    published_date = models.DateField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    total_quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1)
    isbn_number = models.CharField(max_length=13, unique=True)
    pages = models.IntegerField()
    cover_image = models.ImageField(upload_to='cover/', null=True, blank=True)
    language = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # content_file = models.FileField(upload_to='books/content/', null=True, blank=True)
    # is_issued = models.BooleanField(default=False)

    @property
    def is_available(self):
        return self.available_quantity > 0

    @property
    def status(self):
        return "Available" if self.available_quantity > 0 else "Unavailable"

    def __str__(self):
        return self.title

class Profile(models.Model):
    ROLE_CHOICES = (
        ('reader', 'Reader'),
        ('librarian', 'Librarian'),
        ('admin', 'Admin')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class BookIssue(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="book_issues"
    )

    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="issues"
    )

    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issued_books_as_librarian"
    )

    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(null=True , blank=True)

    fine = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00
    )

    # class Meta:
    #     ordering = ["-issued_at"]
    #     constraints = [
    #         models.CheckConstraint(
    #             check=models.Q(due_date__gte=models.F("issued_at")),
    #             name="due_date_after_issue"
    #         )
    #     ]

    @property
    def is_active(self):
        return self.returned_at is None

    @property
    def is_overdue(self):
        if not self.is_active:
            return False
            
        today = timezone.localdate()
        due = self.due_date
        
        # Defensive: convert datetime to date if needed
        if hasattr(due, 'date'):
            due = due.date()
        
        return today > due

    def calculate_fine(self):
        if not self.is_overdue:
            return 0

        end_date = (
            self.returned_at
            if self.returned_at
            else timezone.localdate()
        )

        overdue_days = (end_date - self.due_date).days
        return overdue_days * settings.FINE_PER_DAY

    def mark_returned(self):
        if self.returned_at:
            return  # already returned

        self.returned_at = timezone.localdate()
        self.fine = self.calculate_fine()
        self.save(update_fields=["returned_at", "fine"])

        # update book availability
        self.book.available_quantity += 1
        self.book.save(update_fields=["available_quantity"])

    def __str__(self):
        return f"{self.book.title} → {self.user.username}"

    
    # def __str__(self):
    #     return f"{self.book.title} → {self.user.email}"