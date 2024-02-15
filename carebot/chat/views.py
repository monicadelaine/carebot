from django.shortcuts import render, redirect
from .forms import QueryForm
from openai import OpenAI
from django.conf import settings
from .models import Message

chat_history = []

def chat_view(request):
    if request.method == 'POST':
        form = QueryForm(request.POST)
        if form.is_valid():
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            query = form.cleaned_data['query']

            # If the user sends the same message twice in a row, don't send it to the chatbot.
            if len(chat_history) >= 2 and query == chat_history[-2].text:
                # Add the user's message to the chat history and then add the chatbot's last response again.
                chat_history.append(Message.objects.create(from_user=True, text=query))
                chat_history.append(Message.objects.create(from_user=False, text=chat_history[-2].text))
                return render(request, 'chat/chat.html', {'form': form, 'chat_history': chat_history})

            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a friendly assistant that helps connect users to healthcare services in their area based on their needs."},
                        {"role": "user", "content": query}
                    ]
                )
            except Exception as e:
                return render(request, 'chat/error.html', {'error': str(e)})    # TODO: make a proper error page
            
            chat_history.append(Message.objects.create(from_user=True, text=query))   # log user query
            ai_response = completion.choices[0].message.content
            chat_history.append(Message.objects.create(from_user=False, text=ai_response))   # log chatbot response

        return render(request, 'chat/chat.html', {'form': form, 'chat_history': chat_history})
    else:
        form = QueryForm()
        
    # Fetch the conversation history, ordering by creation time
    chat_history.sort(key=lambda x: x.created_at)
    return render(request, 'chat/chat.html', {'form': form, 'chat_history': chat_history})

def home_view(request):
    return render(request, 'chat/home.html')

def dashboard_view(request):
    return render(request, 'chat/dashboard.html')
