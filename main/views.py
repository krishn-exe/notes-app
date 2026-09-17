from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseForbidden, FileResponse
from django.conf import settings
from . forms import RegisterForm, LoginForm, NoteForm
from . models import Note, Images
import boto3

@csrf_protect
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {'form': form})

@csrf_protect
def login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("index")
    else:
        form = LoginForm()
    return render(request, "login.html", {'form': form})

def logout(request):
    auth_logout(request)
    return render(request, "logout.html")

@login_required
def index(request):
    notes = Note.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, "index.html", {'notes': notes})

@login_required
@csrf_protect
def create_note(request):
    if request.method == "POST":
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            if request.FILES.get('image'):
                Images.objects.create(note=note, image=request.FILES['image'])
            return redirect("index")
    else:
        form = NoteForm()
    return render(request, "create_note.html", {'form': form})

@login_required
@csrf_protect
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            if request.FILES.get('image'):
                Images.objects.create(note=note, image=request.FILES['image'])
            return redirect("index")
    else:
        form = NoteForm(instance=note)
    return render(request, "edit_note.html", {'form': form, 'note': note})

@login_required
@csrf_protect
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == "POST":
        note.delete()
        return redirect("index")
    return render(request, "delete_note.html", {'note': note})

@login_required
@csrf_protect
def delete_image(request, image_id):
    image = get_object_or_404(Images, id=image_id, note__user=request.user)
    note_id = image.note.id
    if request.method == "POST":
        image.image.delete()
        image.delete()
    return redirect("edit_note", note_id=note_id)

@login_required
def serve_image(request, image_id):
    image = get_object_or_404(Images, id=image_id, note__user=request.user)
    return FileResponse(image.image.open('rb'))
