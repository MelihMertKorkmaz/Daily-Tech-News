from django.shortcuts import render

def global_home_view(request):
    return render(request, 'global_home.html')

