from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from openai import OpenAI

from .forms import QueryForm
from .models import Message

chat_history = []

class QueryFormNoAutofill(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))

def chat_view(request):
    # Initialize chat_history_ids from session or start with an empty list
    chat_history_ids = request.session.get('chat_history_ids', [])

    if request.method == 'POST':
        form = QueryFormNoAutofill(request.POST)
        
        if form.is_valid():
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            query = form.cleaned_data['query']

            chat_history = Message.objects.filter(id__in=chat_history_ids).order_by('created_at')

            # check for the last user query and AI response
            if chat_history.exists():
                last_user_message = chat_history.filter(from_user=True).last()
                if last_user_message and query == last_user_message.text:
                    last_ai_response = chat_history.filter(id__gt=last_user_message.id, from_user=False).first()
                    if last_ai_response:
                        return JsonResponse({'query': query, 'response': last_ai_response.text})
                    else:
                        # This should never occur. It is a fallback.
                        return JsonResponse({'query': query, 'response': "Let's try something new."})


            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    # TODO: have the chatbot remember previous messages
                    messages=[
                        {"role": "system", "content": "You are a friendly assistant that helps connect users to healthcare services in their area based on their needs."},
                        {"role": "system", "content": "Use only plain text, no HTML, markdown, or other formatting. Do not use \\n or other special characters."},
                        {"role": "user", "content": query}
                    ]
                )
                ai_response = completion.choices[0].message.content
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)

            # create Messages objects for the user query and AI response
            user_message = Message.objects.create(from_user=True, text=query)
            ai_message = Message.objects.create(from_user=False, text=ai_response)

            # append the new message IDs to chat_history_ids and save it back to the session
            chat_history_ids.extend([user_message.id, ai_message.id])
            request.session['chat_history_ids'] = chat_history_ids

            return JsonResponse({'query': query, 'response': ai_response})

        else:
            return JsonResponse({'error': 'Form validation failed'}, status=400)
    else:
        form = QueryForm()

    # fetch the conversation history as Message objects from the database
    chat_history = Message.objects.filter(id__in=chat_history_ids).order_by('created_at')

    return render(request, 'chat/chat.html', {'form': form, 'chat_history': chat_history})



@require_POST
@csrf_exempt
def clear_session(request):
    # clear the session
    request.session.flush()
    return JsonResponse({'status': 'session_cleared'})

def error_view(request, *args):
    return render(request, 'chat/error.html', {'error': 'Page not found.'})

def home_view(request):
    return render(request, 'chat/home.html')

def dashboard_view(request):
    return render(request, 'chat/dashboard.html')

def handler404(request, exception, template_name="error.html"):
    return render('chat/error.html', {'error': 'Page not found.'}, context_instance=RequestContext(request))

def handler500(request, *args, **argv):
    response = render('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response
