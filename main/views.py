from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import registerForm, contentForm
from .models import Content, Comment
from django.contrib import messages
from django.http import JsonResponse

def home(request):
    contents = Content.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'contents': contents})

def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = registerForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def add_content(request):
    if request.method == "POST":
        form = contentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.created_by = request.user
            content.save()
            messages.success(request, "Content added successfully!")
            return redirect('home')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = contentForm()
    return render(request, 'add_content.html', {'form': form})

@login_required
def like_content(request, course_id):
    course = get_object_or_404(Content, id=course_id)
    if request.user in course.likes.all():
        course.likes.remove(request.user)
        liked = False
    else:
        course.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': course.total_likes()})

@login_required
def add_comment(request, course_id):
    if request.method == 'POST':
        body = request.POST.get('body')
        course = get_object_or_404(Content, id=course_id)
        Comment.objects.create(content=course, user=request.user, body=body)
    return redirect('home')

@login_required
def delete_content(request, course_id):
    course = get_object_or_404(Content, id=course_id)
    if course.created_by == request.user:
        course.delete()
        messages.success(request, "Content deleted successfully!")
    else:
        messages.error(request, "You are not allowed to delete this content.")
    return redirect('home')
