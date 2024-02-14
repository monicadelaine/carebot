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
            print(f"query: {query}")
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
            ai_response = completion.choices[0].message
            chat_history.append(Message.objects.create(from_user=False, text=ai_response))   # log chatbot response

            # return render(request, 'chat/response.html', {'response': completion.choices[0].message})
            # return redirect('chat')
        return render(request, 'chat/chat.html', {'form': form, 'chat_history': chat_history})
    else:
        form = QueryForm()

    # return render(request, 'chat/query.html', {'form': form})
        
    # Fetch the conversation history, ordering by creation time
    messages = Message.objects.all().order_by('created_at')
    return render(request, 'chat/chat.html', {'form': form, 'messages': messages})
