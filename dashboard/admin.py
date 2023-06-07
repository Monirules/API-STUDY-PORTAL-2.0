#from studentstudyportal.dashboard.models import Notes
from django.contrib import admin
from . models  import *

# Register your models here.

admin.site.register(Notes)
admin.site.register(Homework)
admin.site.register(WikiData)
admin.site.register(Book)
admin.site.register(BookReview)
admin.site.register(Complain)