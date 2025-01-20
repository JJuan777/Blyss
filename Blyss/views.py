from django.shortcuts import render

def index(request):
    return render(request, 'Blyss/index.html', {'mensaje': '¡Bienvenido a Blyss!'})
