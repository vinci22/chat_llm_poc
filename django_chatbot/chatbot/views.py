from django.shortcuts import render, redirect
from django.http import JsonResponse
import requests
import uuid

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat
from django.utils import timezone
import os
API_ENDPOINT = os.environ.get("API_ENDPOINT")

def generate_session_id():
    return str(uuid.uuid4())

def model_qa(message, session_id):
    api_url = str(API_ENDPOINT)
    print(f"sessionId: {session_id}")
    payload = {
        "user_input": message,
        "session_id": session_id
    }

    response = requests.post(api_url, json=payload)
    print(response)
    if response.status_code == 200:
        response_data = response.json()
        answer = response_data.get("responses")
        return answer
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def chatbot(request):
    # Obtener la cookie de sesión
    session_id = request.COOKIES.get('session_id')

    # Si no hay sesión activa, redirigir al login
    if not session_id:
        return redirect('login')

    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        
        response = model_qa(message, session_id)

        chat = Chat(user=request.user, message=message, created_at=timezone.now())
        chat.save()

        response_data = JsonResponse({'message': message, 'response': response})
        response_data.set_cookie('session_id', session_id, max_age=3600)  # La cookie expira en 1 hora
        return response_data
    
    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            response = redirect('chatbot')
            session_id = generate_session_id()
            response.set_cookie('session_id', session_id, max_age=3600)
            return response
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                response = redirect('chatbot')
                session_id = generate_session_id()
                response.set_cookie('session_id', session_id, max_age=3600)
                return response
            except:
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    # Limpiar la conversación del usuario antes de cerrar sesión
    Chat.objects.filter(user=request.user).delete()
    
    auth.logout(request)
    
    # Eliminar la cookie al cerrar sesión
    response = redirect('login')
    response.delete_cookie('session_id')
    
    return response
