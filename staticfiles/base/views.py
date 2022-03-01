from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from .models import Room, Topic, Message
from django.db.models import Q
from .forms import RoomForm, UserForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
            
        except :
            messages.error(request, 'kullanıcı bulunmamaktadır.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'Kullanıcı adı ya da parola hatalı')

            


    context = {
        'page' : page,
    }
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'kayıt sırasında bir hata oluştu ')

    context = {
        'form' : form
    }

    return render(request, 'base/login_register.html', context)


def home(request):
    # q başlıkları odalara yarır. ve all da hepsi görünür
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    #başlangıca göre sıralar
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
    )

    topics = Topic.objects.all()
    room_count = rooms.count()
    #her odaya kendi son paylaşımlarını gösterir.
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context =  { 
        'rooms':rooms,
        'topics':topics,
        'room_count': room_count,
        'room_messages':room_messages
    }
    return render(request, 'base/home.html', context)



def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room=room,
            body = request.POST.get('body')
        )
        #oda katılımcı değil katılımcı olmasını sağlar.
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    

    context = {
        'room':room,
        'room_messages':room_messages,
        'participants':participants
    } 

    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    # kullanıcının odaları görünür
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = Message.objects.all()

    context = {
        'user':user,
        'rooms':rooms,
        'topics':topics,
        'room_messages':room_messages,

    }

    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    #form kurma
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.all().get_or_create(name=topic_name)
       
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )       
        
        return redirect('home')


    context = {
        'form':form,
        'topics':topics,    
    }
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    #güncelleme  ve en başa koyar
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()


    if request.user != room.host:
        return HttpResponse('senin bunu yapmaya ne hakkın var')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, create = Topic.objects.all().get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic 
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {
        'form':form,
        'topics':topics,
        'room':room,
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')

    if request.user != room.host:
        return HttpResponse('senin bunu yapmaya ne hakkın var')    

    context = {
        'obj':room,
    }

    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.method == 'POST':
        message.delete()
        return redirect('home')

    if request.user != message.user:
        return HttpResponse('senin bunu yapmaya ne hakkın var')    

    context = {
        'obj':message,
    }

    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid:
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {
        'form':form,
    }

    return render(request, 'base/update_user.html', context)