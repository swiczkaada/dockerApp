from django.shortcuts import render

# Create your views here.
def index(request):
    """
    Render the index page.
    """
    return render(request, 'cyjeApp/index.html')