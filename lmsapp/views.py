import imp
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from lmsapp.tasks import send_mail_func
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.http import JsonResponse
from lmsapp.tasks import send_mail_func

# Create your views here.

#to update password
@csrf_exempt
def update_password(request):
    if not request.method == "POST":
        return JsonResponse({"status" : 400, "error": "Send a POST request with valid parameters only."})
    
    username = request.POST["username"]
    old_password = request.POST["old_password"]
    new_password = request.POST["new_password"]

    if len(new_password)>4:
            userdata = User.objects.filter(username=username).first()
            if userdata.check_password(old_password):
                userdata.set_password(new_password)
                userdata.save()
                return JsonResponse({"status" : 200, "data": "Password Updated Succesfully!"})
            else:
                return JsonResponse({"status" : 400, "error": "Invalid Credentials!"})    
    else:
        return JsonResponse({"status" : 400, "error": "Password length must be more than 4 characters"})

#to generate a token (because we used token authentication here)
def get_user_token(user):
    token_instance,  created = Token.objects.get_or_create(user=user)
    return token_instance.key

#to sign in so that we get token
@csrf_exempt
def signin(request):
    if not request.method == "POST":
        return JsonResponse({"status" : 400, "error": "Send a post request with valid parameters only."})
        
    username = request.POST["username"]
    password = request.POST["password"]
    try:
        user = User.objects.get(username=username)
        if user is None:
            return JsonResponse({ "status" : 400, "error": "There is no account with this username!"})
        if( user.check_password(password)):
            if user != request.user:
                login(request, user)
                token = get_user_token(user)
                return JsonResponse({"status" : 200,"token": token,"status":"Logged in"})
            else:
                return JsonResponse({"status":200,"message":"User already logged in!"})
        else:
            return JsonResponse({"status":400,"message":"Invalid Login!"})
    except Exception as e:
        return JsonResponse({"status":500,"message":"Something went wrong!"})

#to signout
@csrf_exempt   
def signout(request):
    try:
        request.user.auth_token.delete()
        logout(request)
        return JsonResponse({ "status" : 200, "success" : "logout successful"})
    except Exception as e:
        return JsonResponse({ "status" : 400, "error": "Something Went wrong! Please try again later."})


#only accessed by Superadmin
#crud operations on Library
class LibraryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        
        if request.user.is_superuser:
            name = request.POST["name"]
            if name:
                try:
                    library = Library(name=name)
                    library.save()
                    return Response({"status":200,"Message":"Library Created!","lid":library.id})
                except Exception as e:
                    return Response({"status":500,"Message":"Something went wrong Please try Again!"})
            else:
                return Response({"status":401,"Message":"Invalid Data!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

    def get(self,request,lid):
        if request.user.is_superuser:
            try:
                library_data = Library.objects.filter(id=lid).annotate(librarian_name=F('librarian__username')).values('id','name','librarian_name')
                return Response({"status":200,"Message":library_data})
            except Exception as e:
                return Response({"status":500,"Message":"Something went wrong Please try Again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})
    
    def put(self,request,lid):
        if request.user.is_superuser:
            name = request.POST["name"]
            username = request.POST["librarian"]
            if name or username:
                try:
                    library = Library.objects.get(id=lid)
                    if username and name:
                        librarian = User.objects.get(username=username)
                        library = Library.objects.filter(id=lid).update(name=name,librarian=librarian)
                        return Response({"status":200,"Message":"Library Edited!"})
                    elif name:
                        library = Library.objects.filter(id=lid).update(name=name)
                        library.save()
                        return Response({"status":200,"Message":"Library Edited!"})
                    elif username:
                        library = Library.objects.filter(id=lid).update(librarian=librarian)
                        library.save()
                        return Response({"status":200,"Message":"Library Edited!"})
                except Exception as e:
                    return Response({"status":500,"Message":"Something Went wrong Please try again!"})
            else:
                return Response({"status":401,"Message":"Invalid Data!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

    def delete(self,request,lid):
        if request.user.is_superuser:
            try:
                Library.objects.filter(id=lid).delete()
                return Response({"status":200,"Message":"Library Deleted!"})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})
    
#only accessed by Superadmin
#create and delete librarian
class LibrarianView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        
        if request.user.is_superuser:
            username = request.POST["username"]
            password = request.POST["password"]
            if username and password:
                try:
                    userdata = User(username=username,is_librarian=True)
                    userdata.set_password(password)
                    userdata.save()
                    return Response({"status":200,"Message":"User Created!","uid":userdata.id})
                except Exception as e:
                    return Response({"status":500,"Message":e})
            else:
                return Response({"status":401,"Message":"Invalid Data!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

    def delete(self,request,uid):
        if request.user.is_superuser:
            try:
                User.objects.filter(id=uid).delete()
                return Response({"status":200,"Message":"User Deleted!"})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})


#only accessed by Librarian
#crud operations on Book
class BookView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        
        if request.user.is_librarian:
            name = request.POST["name"]
            description = request.POST["description"]
            author = request.POST["author"]
            lid = request.POST["lid"]
            try:
                library = Library.objects.get(id=lid)
                book = Book(name=name,description=description,author=author,library=library)
                book.save()
                return Response({"status":200,"Message":"Book Created!","bid":book.id})
            except Exception as e:
                return Response({"status":500,"Message":e})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

    def get(self,request,bid):
        if request.user.is_librarian:
            try:
                book_data = Book.objects.filter(id=bid).annotate(library_name=F('library__name')).values('id','name','description','author','library_name')
                return Response({"status":200,"Message":book_data})
            except Exception as e:
                return Response({"status":500,"Message":"Something went wrong Please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})
    
    def put(self,request,bid):
        if request.user.is_librarian:
            name = request.POST["name"]
            description = request.POST["description"]
            author = request.POST["author"]
            library_id = request.POST["lid"]
            try:
                library = Library.objects.get(id=library_id)
                Book.objects.filter(id=bid).update(name=name,description=description,author=author,library=library)
                return Response({"status":200,"Message":"Book Edited!"})
            except Exception as e:
                return Response({"status":500,"Message":e})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

    def delete(self,request,bid):
        if request.user.is_librarian:
            try:
                Book.objects.filter(id=bid).delete()
                return Response({"status":200,"Message":"Book Deleted!"})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

#only accessed by Librarian
#Create and delete borrower
class BorrowerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        
        if request.user.is_librarian:
            username = request.POST["username"]
            password = request.POST["password"]
            email = request.POST["email"]
            if username and password and email:
                try:
                    userdata = User(username=username,is_Borrower=True,email=email)
                    userdata.set_password(password)
                    userdata.save()
                    return Response({"status":200,"Message":"User Created!","uid":userdata.id})
                except Exception as e:
                    return Response({"status":500,"Message":e})
            else:
                return Response({"status":401,"Message":"Invalid Data!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

    def delete(self,request,uid):
        if request.user.is_librarian:
            try:
                User.objects.filter(id=uid).delete()
                return Response({"status":200,"Message":"User Deleted!"})
            except Exception as e:
                return Response({"status":500,"Message":"Something Went wrong Please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

#only accessed by Librarian and Borrower
#lending book to borrower
class BookTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user
        if request.user.is_librarian:
            book_id = request.POST["book_id"]
            borrower_id = request.POST["borrower_id"]
            days = int(request.POST["days"])
            if Book.objects.filter(id=book_id,library__librarian=user):
                u = User.objects.get(id=borrower_id)
                if u.is_Borrower:
                    try:
                        book = Book.objects.get(id=book_id)
                        d = datetime.today() + timedelta(days=days)
                        transaction = Transaction(book=book,lender=user,borrower=u,book_returned=False,due_date=d)
                        transaction.save()
                        return Response({"status":200,"Message":"Book lended successfully!","Transaction_id":transaction.id})
                    except Exception as e:
                        return Response({"status":500,"Message":"Something went wrong Please try again!"})
                else:
                    return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})
            else:
                return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

    def put(self,request,tid):

        if request.user.is_Borrower:
            try:
                d = datetime.today()
                Transaction.objects.filter(id=tid).update(book_returned=True,book_returned_on = d,is_active=0)
                return Response({"status":200,"Message":"Book Returned successfully!"})
            except Exception as e:
                    return Response({"status":500,"Message":"Something went wrong please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})


#only accessed by borrower
#to get list of borrowed books
class BorrowerBookView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        if request.user.is_Borrower:
            try:
                book_data = Book.objects.filter(transaction__borrower=request.user,transaction__is_active=1).annotate(library_name=F('library__name'),borrowed_date=F('transaction__transaction_date'),due_on=F('transaction__due_date')).values('id','name','description','author','library_name','borrowed_date','due_on')
                return Response({"status":200,"Message":book_data})
            except Exception as e:
                return Response({"status":500,"Message":"Something went wrong Please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

#to get list of borrowed books from library
class BorrowerBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,lid):
        if request.user.is_Borrower:
            try:
                book_data = Book.objects.filter(transaction__borrower=request.user,transaction__is_active=1,library__id=lid).annotate(library_name=F('library__name'),borrowed_date=F('transaction__transaction_date'),due_on=F('transaction__due_date')).values('id','name','description','author','library_name','borrowed_date','due_on')
                return Response({"status":200,"Message":book_data})
            except Exception as e:
                return Response({"status":500,"Message":"Something went wrong Please try again!"})
        else:
            return Response({"status":403,"Message":"You are not Authorized to Perform this Action!"})

def send_mail(request):
    send_mail_func.delay()
    return HttpResponse("sent")