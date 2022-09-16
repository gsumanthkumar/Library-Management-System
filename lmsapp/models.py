from datetime import timezone
from pyexpat import model
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    is_librarian = models.BooleanField(default=False)
    is_Borrower = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Library(models.Model):
    name = models.CharField(max_length=10,default=None)
    librarian = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    added_on = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

class Book(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    author = models.CharField(max_length=50,blank=True)
    library = models.ForeignKey(Library,on_delete=models.CASCADE,null=True)
    borrower = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    added_on = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

class Transaction(models.Model):
    book = models.ForeignKey(Book,on_delete=models.CASCADE)
    lender = models.ForeignKey(User,related_name='book_lender',on_delete=models.CASCADE)
    borrower = models.ForeignKey(User,related_name='book_borrower',on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    book_returned = models.BooleanField(default=False)
    book_returned_on = models.DateField(blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.book)