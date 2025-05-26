import datetime

from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
def index(request):
    """
    Render the index page.
    """
    return render (request, 'index.html')
