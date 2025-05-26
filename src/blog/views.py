from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'blog/index.html')

def article(request, article_id):
    if article_id not in ["01", "02", "03"]:
        return render(request, 'blog/article_not_found.html', status=404)
    return render(request, f"blog/article_{article_id}.html")
