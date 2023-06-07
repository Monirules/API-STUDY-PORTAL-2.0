from django.conf import settings
from django.core.checks import messages
from django.db.models.fields import CharField
from django.forms.widgets import Input
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from . forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import wikipedia
from django.contrib.auth.decorators import login_required
from django.template import loader
from .models import Complain, Comment
from django.views.generic.base import TemplateView
from django.shortcuts import render
from .fetch_data import fetch_data, read_keywords, store_data
from .models import WikiData
import requests
import json
from .models import Book, BookReview
from datetime import datetime
from dateutil import parser
from rest_framework import viewsets
from rest_framework import serializers
from .serializers import BookSerializer, BookReviewSerializer
from rest_framework.decorators import api_view




# Create your views here.

def fetch_and_store_data(request):
    keywords = read_keywords('dashboard/keywords.txt')
    for keyword in keywords:
        title, content = fetch_data(keyword)
        store_data(title, content)
    return render(request, 'dashboard/home.html')

def fetch_data(keyword):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{keyword}"
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8'))
    title = data['title']
    content = data['extract']
    return title, content


def read_keywords(file_path):
    with open(file_path, 'r') as f:
        keywords = f.read().splitlines()
    return keywords

def store_data(title, content):
    wiki_data = WikiData.objects.create(title=title, content=content)
    return wiki_data





# Google Book api start here

def fetch_books_from_api(request):
        # Get keywords from text file
        with open('dashboard/book_keyword.txt', 'r') as file:
            keywords = file.read().splitlines()
        

        # Fetch data from Google Books API for each keyword
        for keyword in keywords:
            url = f'https://www.googleapis.com/books/v1/volumes?q={keyword}'
            response = requests.get(url)
            data = response.json()

            # Store fetched data in the database
            for item in data['items']:
                title = item['volumeInfo'].get('title', '')
                author = item['volumeInfo'].get('authors', ['Unknown Author'])[0]
                description = item['volumeInfo'].get('description', '')
                published_date = item['volumeInfo'].get('publishedDate', '') 
                # Parse and convert the published_date to the correct format
                if published_date:
                    published_date = parser.parse(published_date).date().isoformat()

                book = Book(title=title, author=author, description=description, published_date=published_date)
                #book = Book(title=title, author=author, description=description)

                book.save()

        return render(request, 'dashboard/home.html')








class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def fetch_books_from_api(request):
        # Get keywords from text file
        with open('dashboard/book_keyword.txt', 'r') as file:
            keywords = file.read().splitlines()
        

        # Fetch data from Google Books API for each keyword
        for keyword in keywords:
            url = f'https://www.googleapis.com/books/v1/volumes?q={keyword}'
            response = requests.get(url)
            data = response.json()

            # Store fetched data in the database
            for item in data['items']:
                title = item['volumeInfo'].get('title', '')
                author = item['volumeInfo'].get('authors', ['Unknown Author'])[0]
                description = item['volumeInfo'].get('description', '')
                published_date = item['volumeInfo'].get('publishedDate', '') 
                # Parse and convert the published_date to the correct format
                if published_date:
                    published_date = parser.parse(published_date).date().isoformat()

                book = Book(title=title, author=author, description=description, published_date=published_date)
                book.save()

        return render(request, 'dashboard/home.html')





def home(request):
    return render(request,'dashboard/home.html')


@login_required
def notes(request):
    if request.method=="POST":
        form=NotesForm(request.POST)
        if form.is_valid():
            notes=Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully")
        return redirect('notes')
    else:
            
        form=NotesForm()
    notes=Notes.objects.filter(user=request.user)
    context={'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)



class NotesDetailView(generic.DetailView):
    model=Notes

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


@login_required
def homework(request):

    if request.method=="POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished=request.POST['is_finished']
                if finished=="on":
                    finished=True
                else:
                    finished=False
            except:
                finished=False
            homeworks=Homework(
                user=request.user,
                subject=request.POST['subject'],
                title=request.POST['title'],
                description=request.POST['description'],
                due=request.POST['due'],
                is_finished=finished
            )
            homeworks.save()
            messages.success(request,f'Homework Added from {request.user.username}!!')
            return redirect('homework')
    else:
          form=HomeworkForm()
              
    homework=Homework.objects.filter(user=request.user)

    if len(homework)==0:
        homework_done= True
    else:
        homework_done=False
    context={'homeworks':homework,
        'homeworks_done':homework_done,
        'form':form,
    }
    return render(request,'dashboard/homework.html',context)
    
    
@login_required
def update_homework(request, pk=None):
    homework=Homework.objects.get(id=pk)
    if homework.is_finished== True:
        homework.is_finished=False
    else:
        homework.is_finished=True
    homework.save()
    return redirect('homework')


@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


def youtube(request):
    if request.method=="POST":
        form=DashboardForm(request.POST)
        text=request.POST['text']
        video=VideosSearch(text,limit=10)
        result_list=[]
        for i in video.result()['result']:
            result_dict={
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnail':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']

            }
            desc=''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc+=j['text']
            result_dict['description']=desc
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form=DashboardForm()
        form=DashboardForm()
        context={'form':form}
    return render(request,'dashboard/youtube.html',context)    


@login_required
def todo(request):
    return render(request,'dashboard/todo.html')



def books(request):
    if request.method=="POST":
        form=DashboardForm(request.POST)
        text=request.POST['text']
        
        url="https://www.googleapis.com/books/v1/volumes?q="+text
        r=requests.get(url)
        answer=r.json()
        result_list=[]
        
        for i in range(10):
            volume_info = answer['items'][i]['volumeInfo']
            authors = volume_info.get('authors', [])
            
            result_dict={
                 'title':answer['items'][i]['volumeInfo']['title'],
                 'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                 #'authors':answer['items'][1]['volumeInfo']['authors'],
                 'authors': ', '.join(authors),
                 'description':answer['items'][i]['volumeInfo'].get('description'),
                 'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                 'categories':answer['items'][i]['volumeInfo'].get('categories'),
                 'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                 'thumbnail':answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail'),
                 'preview':answer['items'][i]['volumeInfo'].get('previewLink'),
                
            }
            result_list.append(result_dict)
            context={
                'form':form,
                'results':result_list,
                
            }
        reviews = request.POST.get('reviews')
 
        book = Book(reviews=reviews)
        book.save()    
        return render(request,'dashboard/books.html',context)
    else:
        form=DashboardForm()
    form=DashboardForm()
    context={'form':form}
    return render(request,'dashboard/books.html',context)






    
@login_required
def dictionary(request):
    
    return render(request,'dashboard/home.html')
          

@login_required
def wiki(request):
    if request.method=='POST':
        text=request.POST['text']
        form=DashboardForm(request.POST)
        search=wikipedia.page(text)
        context={
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:

        form=DashboardForm()
        context={
            'form':form
        }
    return render(request,'dashboard/wiki.html',context)




def register(request):
    if request.method=='POST':
        form=UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            
            reg = request.POST.get('username')
            messages.success(request,'Account created for - ' + reg)
            return redirect("register")
    else:
        form=UserRegistrationForm()
    context={
            'form':form
        }
           
    return render(request,'dashboard/register.html',context)


@login_required
def profile(request):
    homeworks=Homework.objects.filter(is_finished=False,user=request.user)
    
    if len(homeworks)==0:
        homework_done=True
    else:
        homework_done=False
    
    context={
        'homeworks':homeworks,
        'homework_done':homework_done,
        
    }
    return render(request,"dashboard/profile.html",context)





@login_required
def complain(request):
	mymembers = Complain.objects.filter(email=request.user.email)
	comment = Comment.objects.filter(email=request.user.email)
	
	template = loader.get_template('dashboard/complain.html')
	context = {
			'mymembers': mymembers,
			'comment': comment
			}

	if request.method=='POST':  
			email = request.POST['email']
			complain = request.POST['complain']
			against = request.POST['against']
			position = request.POST['position']
			image = request.FILES.get('image')
			user = User.objects.filter(username = against)
			
			if user.first() is not None:
				if User.objects.filter(username = against).exists():	
					complain = Complain(email = email, complain=complain, against = against, position = position, image=image)
					complain.save()
					messages.success(request, 'Complain Submit Successful')		
					return HttpResponse(template.render(context, request))
					
			else:
					messages.error(request, 'You are complaining against Non-User (-,-)')
					return redirect('complain')
    
	else:
   		return render(request,'dashboard/complain.html', context)




@login_required
def contact(request):

	return render (request, 'dashboard/home.html')			
 
def error_404(request, exception):
    return render(request,"dashboard/404.html") 

def error_500(request):
    return render(request,"dashboard/500.html") 


