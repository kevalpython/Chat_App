from django.shortcuts import render
from .models import Chat,Group

def index(request):
    return render(request, "chat/index.html")

def room(request, room_name):
    group = Group.objects.filter(name=room_name).first()
    chats = []
    if group:
        chats=Chat.objects.filter(group=group)
    else:
        group = Group(name=room_name)
        group.save()
    return render(request, "chat/room.html", {"room_name": group.name, "chats":chats})