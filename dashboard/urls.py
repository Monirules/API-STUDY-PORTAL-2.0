from django.urls import path, include
from . import views
from .views import fetch_and_store_data, fetch_books_from_api
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)


urlpatterns=[
    path('',views.home,name="home"),
    path('api/', include(router.urls)),

    path('notes',views.notes,name="notes"),
    path('delete_note/<int:pk>',views.delete_note,name="delete-note"),
    path('notes_detail/<int:pk>',views.NotesDetailView.as_view(),name="notes-detail"),
    path('homework',views.homework,name="homework"),
    path('update_homework/<int:pk>',views.update_homework,name="update-homework"),
    path('delete_homework/<int:pk>',views.delete_homework,name="delete-homework"),
    path('youtube',views.youtube,name="youtube"),
    path('todo',views.todo,name="todo"),
    #path('update_todo/<int:pk>',views.update_todo,name="update-todo"),
    #path('delete_todo/<int:pk>',views.delete_todo,name="delete-todo"),
    path('books',views.books,name="books"),
    path('dictionary',views.dictionary,name="dictionary"),
    path('wiki',views.wiki,name="wiki"),
    path('complain', views.complain, name="complain"),
    path('contact', views.contact, name="contact"),
    path('fetch/', fetch_and_store_data, name='fetch_and_store_data'),
    #path('fetch_books/', fetch_books_from_api, name='fetch_books'),

]

handler404 = 'dashboard.views.error_404'
handler500 = 'dashboard.views.error_500'