import logging
import re
import json

from django import forms
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from openai import OpenAI

from .forms import QueryForm
from .models import Message, MessageType

logger = logging.getLogger(__name__)
chat_history = []
user_coords = []


class QueryFormNoAutofill(forms.Form):
    query = forms.CharField(widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    is_sql = forms.BooleanField(required=False, widget=forms.CheckboxInput())


def storeUserLocation(request):
    #grab user's location from ajax function from chat.js
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_latitude = data[0]['user_latitude']
        user_longitude = data[1]['user_longitude']
        user_loc = (user_latitude, user_longitude)
        user_coords.append(user_loc)
        for coord in user_coords:
            print(coord)
        return JsonResponse({'status': 'success'})
    
    #catch the exception of "cannot access request body more than once", make sure it does not affect chatbot
    except Exception as e:
        # print(e)
        pass

def chat_view(request):
    # Initialize chat_history_ids from session or start with an empty list
    chat_history_ids = request.session.get('chat_history_ids', [])

    storeUserLocation(request)
    
    if request.method == 'POST':
        form = QueryFormNoAutofill(request.POST)

        if form.is_valid():

            query = form.cleaned_data.get('query', '') 

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

            # All additional AI instructions should be added here.
            messages_parameter = [
                {"role": "system", "content": "You connect Alabama residents users to healthcare services in Alabama based on their needs. If the user is looking for healthcare outside of Alabama, tell them you cannot help. Do not use any special characters in your responses except for \\n. You assist another program by giving the correct parameters for an SQL query. When appropriate, you can tell the program to execute the SQL query by giving it a command using exactly the following format: SQL: SELECT * FROM providers WHERE resource_type = value AND city = city_name OR county = county_name\nIf the user leaves out 1 or 2 of those 3 criteria, leave it out of your SQL statement. The program will then execute the SQL query and return the results to the user. You should not execute the SQL query yourself. You should only give the command to the program to execute the SQL query. When doing this, never include any non-SQL text in the same message as the SQL command. The SQL command should be the only content in the message. If you do not have any of these (resource type, city, or county), ask the user for this information. If you have at least one of those, DO NOT message the user. Remember to use the data you have to create the query as the instructions require. These are the only resource types you can use: support_groups, food_stamps, training, infrastr_chgs, home_maintain, drug_assist, counseling, reimbursement, medicare, house_cleaning, personal_care, home_meals, daycare, respite_care, incontinence_items, medical_supplies, nursing, medic_alerting, durable_equip, bill_assist, supplier_research, medicare_providers, geriatricians, pyschiatrist, neurologists, specialists, nursing_home, rehabilitation_facility, memory_care, legal_assist, hospice_advd_care, transportation, death_burial, food_pantry, physical_therapy, occupational_therapy, devices_prosthetics, studies_traisl, procedures, illness_disease, vision_aids, hearing_aids, oral_dentures, technology, oxygen, referral, medicare_waivers, food_vouches, activity_enrichment, housing_directory, housing_assistance, veterans_affairs, financial_general, senior_discount, job_training, substance_abuse, pain_management, tax_help, clinics.\nIf the user asks for all healthcare resources in a particular area, make the query."}
            ]
            if chat_history.exists():   # add the previous 6 messages to the messages_parameter, limiting token usage
                for message in chat_history.order_by('created_at').reverse()[:6][::-1]: # reverse the last 6 messages
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
                request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                return JsonResponse({'query': query, 'response': error_message.text})
            # extract the parameters for the SQL query from the AI response
            resource_type = None
            city = None
            county = None
            try:
                resource_type = ai_response[ai_response.lower().find("resource_type = "):][16:].split()[0]
                resource_type = ''.join(e for e in resource_type if e.isalnum() or e == '_')    # remove all non-alphanumeric characters except for _
                resource_type = resource_type.lower()
                is_sql = True
            except Exception as e:
                pass
            try:
                city = ai_response[ai_response.lower().find("city = "):][7:].split()[0]
                city = ''.join(e for e in city if e.isalnum() or e == '_') # remove all non-alphanumeric characters except for _
                city = city.upper()
            except Exception as e:
                pass
            try:
                county = ai_response[ai_response.lower().find("county = "):][9:].split()[0]
                county = ''.join(e for e in county if e.isalnum() or e == '_') # remove all non-alphanumeric characters except for _
                county = county.upper()
            except Exception as e:
                pass

            columns_to_select = "*"
            """
            Determine which SQL query to use based on the AI response, if any.
            0. If the AI response does not contain a resource type, city, or county, do not execute a SQL query.
            1. If the AI response contains both a resource type and a city, use the following SQL query:
                f"SELECT p.agency_name, p.addr1, p.addr2, p.city, p.id_cms_other, r.resource_type FROM providers p JOIN resource_listing r ON p.id_cms_other = r.id_cms_other WHERE UPPER(p.city) = '{city}' AND UPPER(r.resource_type) = '{resource_type}';"
            2. If the AI response contains both a resource type and a county, use the following SQL query:
                f"SELECT p.agency_name, p.addr1, p.addr2, p.city, p.id_cms_other, r.resource_type FROM providers p JOIN resource_listing r ON p.id_cms_other = r.id_cms_other WHERE UPPER(p.county) = '{county}' AND r.resource_type = '{resource_type}';"
            3. If the AI response contains only a resource type, use the following SQL query:
                f"SELECT p.agency_name, p.addr1, p.addr2, p.city, p.id_cms_other, r.resource_type FROM providers p JOIN resource_listing r ON p.id_cms_other = r.id_cms_other WHERE LOWER(r.resource_type) = '{resource_type}';"
            4. If the AI response contains only a city or county, use the following SQL query:
                f"SELECT p.agency_name, p.addr1, p.addr2, p.city, p.id_cms_other, r.resource_type FROM providers p WHERE UPPER(p.city) = '{city}';"
            5. If the AI response contains only a county, use the following SQL query:
                f"SELECT p.agency_name, p.addr1, p.addr2, p.city, p.id_cms_other, r.resource_type FROM providers p WHERE UPPER(p.county) = '{county}';"
            """
            # 0. If the AI response does not contain a resource type, city, or county, do not execute a SQL query.
            if resource_type is None and city is None and county is None:
                is_sql = False
            # 1. If the AI response contains both a resource type and a city
            elif resource_type is not None and city is not None:
                columns_to_select = "p.agency_name, p.addr1, p.addr2, p.city, p.county, p.id_cms_other, r.resource_type"
                sql_statement = f"SELECT {columns_to_select} FROM providers p JOIN resource_listing r ON p.id_cms_other = r.id_cms_other WHERE UPPER(p.city) = '{city}' AND r.resource_type = '{resource_type}';"
                is_sql = True
            # 2. If the AI response contains both a resource type and a county
            elif resource_type is not None and county is not None:
                columns_to_select = "p.agency_name, p.addr1, p.addr2, p.city, p.county, p.id_cms_other, r.resource_type"
                sql_statement = f"SELECT {columns_to_select} FROM providers p JOIN resource_listing r ON p.id_cms_other = r.id_cms_other WHERE UPPER(p.county) = '{county}' AND r.resource_type = '{resource_type}';"
                is_sql = True
            # 3. If the AI response contains only a resource type
            elif resource_type is not None and city is None and county is None:
                columns_to_select = "p.agency_name, p.addr1, p.addr2, p.city, p.county, p.id_cms_other, r.resource_type"
                sql_statement = f"SELECT {columns_to_select} FROM providers p JOIN resource_listing r ON p.id_cms_other = r.id_cms_other WHERE LOWER(r.resource_type) = '{resource_type}';"
                is_sql = True
            # 4. If the AI response does not contain a resource type and contains a city
            elif resource_type is None and city is not None:
                columns_to_select = "p.agency_name, p.addr1, p.addr2, p.city, p.county"
                sql_statement = f"SELECT {columns_to_select} FROM providers p WHERE UPPER(p.city) = '{city}';"
                is_sql = True
            # 5. If the AI response does not contain a resource type and contains a county
            elif resource_type is None and county is not None:
                columns_to_select = "p.agency_name, p.addr1, p.addr2, p.city, p.county"
                sql_statement = f"SELECT {columns_to_select} FROM providers p WHERE UPPER(p.county) = '{county}';"
                is_sql = True
            else:
                is_sql = False

            if is_sql:
                try:
                    # make connection with db, send SQL query from chatbot, return output from db
                    with connection.cursor() as cursor:
                        logger.info(f"Executing SQL query: {sql_statement}")
                        cursor.execute(sql_statement)
                        rows = cursor.fetchall()
                        response_text = str(rows) 
                        logger.info(f"SQL query result: {response_text}")
                except Exception as e:
                    response_text = f"Error executing SQL: {str(e)}"
                    logger.error(response_text)
                    error_message = Message.objects.create(message_type=MessageType.SYSTEM, text="There was an error processing your request. Please try again.")
                    chat_history_ids.extend([error_message.id,])
                    request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                    return JsonResponse({'query': query, 'response': error_message.text})
                finally:    # have the chatbot explain the results
                    if len(rows) <= 0:
                        completion = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "system", "content": f"Explain to the user that you could not find {resource_type if resource_type is not None else "the healthcare resource"} like they were looking for. Tell them that if they provide a resource type, you should be able to find the resources. If they include a city or a county, you should be able to find the resources in that area. If they just include a city or county, you can find all healthcare resources in that area."}],
                        )
                        ai_response = completion.choices[0].message.content
                    try:
                        completion = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "system", "content": f"Explain the following results of a PostgreSQL query as if you are telling the user about healthcare providers you found in Alabama. Do not mention anything related to SQL by name, including row ID values. Mention that you found {len(rows)} results matching the request. Output the first 20 results, at most. Preface each result with a number and period, starting with 1. Each {resource_type} found in {city} is in the following format:\n{columns_to_select}\nresults: {response_text}"}],
                        )
                        ai_response = completion.choices[0].message.content
                        # regex to find all instances of a number followed by a period and a space, and add a newline before each one
                        regex_pattern = r'(\d+\.\s)'
                        ai_response = re.sub(regex_pattern, r'<br>\1', ai_response)
                    except Exception as e:
                        error_message = Message.objects.create(message_type=MessageType.SYSTEM, text="There was an error processing your request. Please try again.")
                        chat_history_ids.extend([error_message.id,])
                        request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                        return JsonResponse({'query': query, 'response': error_message.text})
            elif ai_response.upper().find("SQL:") != -1:
                completion = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": f"Explain to the user that you could not find the healthcare resource {resource_type if resource_type is not None else ''} they were looking for. Tell them that if they provide a resource type, you should be able to find the resources. If they include a city or a county, you should be able to find the resources in that area. If they just include a city or county, you can find all healthcare resources in that area."}],
                )
                ai_response = completion.choices[0].message.content
            
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

def clear_session(request):
    if request.method == 'POST':
        request.session.flush()
        return JsonResponse({'status': 'session_cleared'})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def error_view(request, *args):
    return render(request, 'chat/error.html', {'error': 'Page not found.'})

def home_view(request):
    return render(request, 'chat/home.html')

def dashboard_view(request):
    return render(request, 'chat/dashboard.html')

def about_carebot_view(request):
    return render(request, 'chat/about-carebot.html')

def about_us_view(request):
    return render(request, 'chat/about-us.html')

def deliverables_view(request):
    return render(request, 'chat/deliverables.html')

# unused
def handler404(request, *args):
    return render(request, 'chat/error.html', {'error': 'Page not found.'})

# unused
def handler500(request, *args):
    return render(request, 'chat/error.html', {'error': 'An unknown error has occurred.'})
