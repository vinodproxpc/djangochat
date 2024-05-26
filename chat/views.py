from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Message, UserChannel



class Main(View):
    def get(self, request):
        # data = {
        #     "type": "receiver_function",
        #     "data": {
        #         "message": "Hello, World!"
        #     }
        # }
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     "chat", data
        # )
        return render(request=request, template_name="chat/main.html")
    
    
    
class Login(View):
    def get(self,request):
        return render(request=request, template_name="chat/login.html")
    
    def post(self, request):
        data = request.POST.dict()
        context = {'username': data.get("username")}
        username = data.get("username")
        password = data.get("password")

        if username and password:
            authuser = authenticate(request, username=username, password=password)
            if authuser is not None:
                login(request, authuser)
                messages.success(request, "Login successful.")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
                return render(request=request, template_name="chat/login.html", context=context)
        
        messages.error(request, "Both username and password are required.")
        return render(request=request, template_name="chat/login.html", context=context)
    
    
class Register(View):
    def get(self,request):
        return render(request=request, template_name="chat/register.html")
    
    def post(self, request):
        data = request.POST.dict()
        context = {}
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
        }

        if not (first_name and last_name and username and email and password):
            messages.error(request, "All fields are required.")
            return render(request=request, template_name="chat/register.html", context=context)

        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            messages.error(request, "Username or email already exists.")
            return render(request=request, template_name="chat/register.html", context=context)

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        messages.success(request, "Registration successful. You can now log in.")
        return redirect("login")
    
class Logout(View):
    def get(self,request):
        messages.success(request, "you have successfully logout")
        logout(request)
        return redirect("login")

class Home(View):
    def get(self,request):
        if request.user.is_authenticated:
            users = User.objects.exclude(username=request.user.username)

            return render(request=request, template_name="chat/home.html", context={"users":users})
        else:
            return redirect("login")
    
class ChatPerson(View):
    def get(self,request, user_id):
        me = request.user
        person = User.objects.get(id=user_id)
        
        messages = Message.objects.filter(Q(from_who=me,to_who=person) | Q(to_who=me,from_who=person)).order_by("date","time")
        # sending data back to user logged in
        try:
            user_channel = UserChannel.objects.get(user=person)
            data = {
                "type": "receiver_function","message_type":"has_been_seen_by_other_person"
            }
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.send)(user_channel.channel_name, data)
            message_have_not_been_seen = Message.objects.filter(from_who=person,to_who=me,has_been_seen=False)
            message_have_not_been_seen.update(has_been_seen=True)
        except:
            pass
        context = {"person": person, "me":me, "messages":messages}
        return render(request=request, template_name="chat/chat_person.html", context=context)
