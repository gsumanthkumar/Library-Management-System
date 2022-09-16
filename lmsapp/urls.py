from unicodedata import name
from django.urls import path
from .import views

urlpatterns = [

    #updatepassword
    path('updatepassword/',views.update_password,name='updatepassword'),
    #signin
    path('signin/',views.signin,name='signin'),
    #signout
    path('signout/',views.signout,name='signout'),
    
#SuperAdmin API
    #create library
    path('library/',views.LibraryView.as_view(),name='libraryview'),
    #read,update and delete library
    path('library/<int:lid>/',views.LibraryView.as_view(),name='libraryview'),

    #create librarian
    path('librarian/',views.LibrarianView.as_view(),name='librarianview'),
    #delete librarian
    path('librarian/<int:uid>/',views.LibrarianView.as_view(),name='librarianview'),

#Librarian API
    #create Book
    path('book/',views.BookView.as_view(),name='bookview'),
    #read,update and delete Book
    path('book/<int:bid>/',views.BookView.as_view(),name='bookview'),

    #create borrower
    path('borrower/',views.BorrowerView.as_view(),name='Borrowerview'),
    #delete borrower
    path('borrower/<int:uid>/',views.BorrowerView.as_view(),name='Borrowerview'),

    #Lend a book
    path('lendbook/',views.BookTransactionView.as_view(),name='BookTransactionview'),

#Borrower API

    #return a book
    path('returnbook/<int:tid>/',views.BookTransactionView.as_view(),name='BookTransactionview'),

    #get borrowed books
    path('borrowerbook/',views.BorrowerBookView.as_view(),name='Borrowerbookview'),

    #get borrowed books from specific library
    path('borrowerbooks/<int:lid>/',views.BorrowerBooksView.as_view(),name='Borrowerbooksview')
]