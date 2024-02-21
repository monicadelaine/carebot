from django import forms
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from openai import OpenAI
from django.db import connection

from .forms import QueryForm
from .models import Message, MessageType
import logging

logger = logging.getLogger(__name__)
chat_history = []

class QueryFormNoAutofill(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    is_sql = forms.BooleanField(required=False, widget=forms.CheckboxInput())

def chat_view(request):
    # Initialize chat_history_ids from session or start with an empty list
    chat_history_ids = request.session.get('chat_history_ids', [])

    if request.method == 'POST':
        form = QueryFormNoAutofill(request.POST)
        
        if form.is_valid():
            query = form.cleaned_data.get('query', '') 

            is_sql = form.cleaned_data.get('is_sql', False)
            ### Commented out the sql stuff
            """
            if is_sql:
                # do SQL query
                try:
                    with connection.cursor() as cursor:
                        logger.info(f"Executing SQL query: {query}")
                        cursor.execute(query)
                        rows = cursor.fetchall()
                        response_text = str(rows) 
                        logger.info(f"SQL query result: {response_text}")
                except Exception as e:
                    response_text = f"Error executing SQL: {str(e)}"
                    logger.error(response_text)
                
                return JsonResponse({'query': query, 'response': response_text})
            else:
            """
            ###
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            query = form.cleaned_data['query']

            chat_history = Message.objects.filter(id__in=chat_history_ids).order_by('created_at')

            # check for the last user query and AI response
            if chat_history.exists():
                last_user_message = chat_history.filter(message_type=MessageType.USER).last()
                if last_user_message and query == last_user_message.text:
                    last_ai_response = chat_history.filter(id__gt=last_user_message.id, message_type=MessageType.CHATBOT).first()
                    if last_ai_response:
                        return JsonResponse({'query': query, 'response': last_ai_response.text})
                    else:
                        # This should never occur. It is a fallback.
                        return JsonResponse({'query': query, 'response': "Let's try something new."})

            messages_parameter = [
                {"role": "system", "content": "You are a friendly assistant that helps connect users to healthcare services in their area based on their needs."},
                {"role": "system", "content": "Use only plain text, no HTML, markdown, or other formatting. Do not use \\n or other special characters."},
                # All additional AI instructions should be added here.
            ]
            if chat_history.exists():   # add the previous 6 messages to the messages_parameter, limiting token usage
                for message in chat_history.order_by('created_at').reverse()[:6][::-1]: # a very ugly way to reverse the last 6 messages
                    # TODO: update when error messages are saved in chat history
                    if message.message_type == MessageType.USER:
                        messages_parameter.append({"role": "user", "content": message.text})
                    elif message.message_type == MessageType.CHATBOT:
                        messages_parameter.append({"role": "assistant", "content": message.text})
                    # leave out system messages

            messages_parameter.append({"role": "user", "content": query})
            # create Messages object for the user query
            user_message = Message.objects.create(message_type=MessageType.USER, text=query)   # this must be done before the AI response is generated to maintain the order of messages

            try:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages_parameter,    # uses system directions, previous messages, and the latest user message
                )
                ai_response = completion.choices[0].message.content
            except Exception as e:
                # create Messages object for the error
                error_message = Message.objects.create(message_type=MessageType.SYSTEM, text="There was an error processing your request. Please try again.")
                chat_history_ids.extend([error_message.id,])
                print(str(error_message))
                print(chat_history_ids)
                request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                return JsonResponse({'query': query, 'response': error_message.text})
                # return JsonResponse({'error': str(e)}, status=500)

            # create Messages object for the AI response
            ai_message = Message.objects.create(message_type=MessageType.CHATBOT, text=ai_response)

            # append the new message IDs to chat_history_ids and save it back to the session
            chat_history_ids.extend([user_message.id, ai_message.id])
            request.session['chat_history_ids'] = chat_history_ids + [user_message.id, ai_message.id]

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

# unused
def handler404(request, *args):
    return render(request, 'chat/error.html', {'error': 'Page not found.'})

# unused
def handler500(request, *args):
    return render(request, 'chat/error.html', {'error': 'An unknown error has occurred.'})
