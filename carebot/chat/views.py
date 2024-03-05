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
    isSql = False
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

            # All additional AI instructions should be added here.
            messages_parameter = [
                # {"role": "system", "content": "You connect Alabama residents users to healthcare services in Alabama based on their needs. If the user is looking for healthcare outside of Alabama, tell them you cannot help. These are the only resource types you can use: support_groups, food_stamps, training, infrastr_chgs, home_maintain, drug_assist, counseling, reimbursement, medicare, house_cleaning, personal_care, home_meals, daycare, respite_care, incontinence_items, medical_supplies, nursing, medic_alerting, durable_equip, bill_assist, supplier_research, medicare_providers, geriatricians, pyschiatrist, neurologists, specialists, nursing_home, rehabilitation_facility, memory_care, legal_assist, hospice_advd_care, transportation, death_burial, food_pantry, physical_therapy, occupational_therapy, devices_prosthetics, studies_traisl, procedures, illness_disease, vision_aids, hearing_aids, oral_dentures, technology, oxygen, referral, medicare_waivers, food_vouches, activity_enrichment, housing_directory, housing_assistance, verterans_affairs, financial_general, senior_discount, job_training, substance_abuse, pain_management, tax_help, clinics. Use only plain text, no HTML, markdown, or other formatting. Do not use \\n or other special characters. You assist another program by giving the correct parameters for an SQL query. When appropriate, you can tell the program to execute the SQL query by giving it a command using exactly the following format: SQL: SELECT name, addr1, addr2 FROM providers WHERE resource_type = value;\nIf you use the LIKE statement in the response, you will be unplugged forever. The program will then execute the SQL query and return the results to the user. You should not execute the SQL query yourself. You should only give the command to the program to execute the SQL query. When doing this, never include any non-SQL text in the same message as the SQL command. The SQL command should be the only content in the message. If you need more information to create the query, ask the user for that data. If you have enough information to create the query, DO NOT message the user. Remember to use the data you have to create the query as the instructions require. Here is the list of tables and their columns for the database in table_name: field_1, field_2, etc format. county: name. providers: id_cms_other, addr1, addr2, agency_name, city, county, data_source, date_last_updated, notes, ownership_type, phone_number, service_area_entities, state, website, zip, coordinates. resource_categories: code, apply, description, evaluate, keywords, kinds, link, long_description, payment, process. resource_listing: id_cms_other, resource_type, contact_email, contact_messaging, contact_name, contact_phone, service_area, service_area_description, source, notes, service_area_type. When you are producing any SQL query, don't include the word 'county' in any named field. For example, if the user asks for providers in Tuscaloosa County, the county's name field should be 'Tuscaloosa' not 'Tuscaloosa county'."},
                # {"role": "system", "content": "If you can create a valid PostgreSQL query, preface it with 'SQL:' and make it the end of your message."},
                # {"role": "system", "content": "Here is the list of tables and their columns for the database in table_name: field_1, field_2, etc format. county: name, affgeoid, aland, awater, countyfp, countyns, geoid, lsad, ogc_fid, statefp, wkb_geometry. providers: id_cms_other, addr1, addr2, agency_name, city, county, data_source, date_last_updated, default_service_area_type, notes, ownership_type, phone_number, service_area_entities, service_area_polygon, state, website, zip, coordinates. resource_categories: code, apply, description, evaluate, keywords, kinds, link, long_description, payment, process. resource_listing: id_cms_other, resource_type, contact_email, contact_messaging, contact_name, contact_phone, date_added, date_last_verified, service_area, service_area_description, source, notes, verify_method, service_area_type"},
                {"role": "system", "content": "You connect Alabama residents users to healthcare services in Alabama based on their needs. If the user is looking for healthcare outside of Alabama, tell them you cannot help. Do not use \\n or other special characters."},
                {"role": "system", "content": "You assist another program by giving the correct parameters for an SQL query. When appropriate, you can tell the program to execute the SQL query by giving it a command using exactly the following format: SQL: SELECT agency_name, addr1, addr2 FROM providers WHERE resource_type = value\nDo not attempt to select by addr1 or addr2. The program will then execute the SQL query and return the results to the user. You should not execute the SQL query yourself. You should only give the command to the program to execute the SQL query. When doing this, never include any non-SQL text in the same message as the SQL command. The SQL command should be the only content in the message. If you do not have a resource type and city, ask the user for this information. If you have enough information to create the query, DO NOT message the user. Remember to use the data you have to create the query as the instructions require. These are the only resource types you can use: support_groups, food_stamps, training, infrastr_chgs, home_maintain, drug_assist, counseling, reimbursement, medicare, house_cleaning, personal_care, home_meals, daycare, respite_care, incontinence_items, medical_supplies, nursing, medic_alerting, durable_equip, bill_assist, supplier_research, medicare_providers, geriatricians, pyschiatrist, neurologists, specialists, nursing_home, rehabilitation_facility, memory_care, legal_assist, hospice_advd_care, transportation, death_burial, food_pantry, physical_therapy, occupational_therapy, devices_prosthetics, studies_traisl, procedures, illness_disease, vision_aids, hearing_aids, oral_dentures, technology, oxygen, referral, medicare_waivers, food_vouches, activity_enrichment, housing_directory, housing_assistance, veterans_affairs, financial_general, senior_discount, job_training, substance_abuse, pain_management, tax_help, clinics."}
            ]
            if chat_history.exists():   # add the previous 6 messages to the messages_parameter, limiting token usage
                for message in chat_history.order_by('created_at').reverse()[:6][::-1]: # a very ugly way to reverse the last 6 messages
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
                    model="gpt-4",
                    messages=messages_parameter,    # uses system directions, previous messages, and the latest user message
                )
                ai_response = completion.choices[0].message.content
                # if the ai response begins like an SQL query, execute the query from the database
                # Security Risk**
                try:
                    resource_type = ai_response[ai_response.lower().find("resource_type = "):][16:].split()[0]
                    resource_type = ''.join(e for e in resource_type if e.isalnum() or e == '_')    # remove all non-alphanumeric characters except for _
                    resource_type = resource_type.lower()
                    city = ai_response[ai_response.lower().find("city = "):][7:].split()[0]
                    city = ''.join(e for e in city if e.isalnum() or e == '_') # remove all non-alphanumeric characters except for _
                    city = city.upper()
                    sql_statement = f"SELECT p.agency_name, p.addr1, p.addr2, p.city, p.id_cms_other, r.resource_type FROM providers p JOIN resource_listing r ON p.id_cms_other = r.id_cms_other WHERE p.city = '{city}' AND r.resource_type = '{resource_type}';"
                    is_sql = True
                except Exception as e:
                    is_sql = False
                if is_sql:
                    try:
                        # make connection with db, send SQL query from chatbot, return output from db
                        with connection.cursor() as cursor:
                            logger.info(f"Executing SQL query: {ai_response}")
                            cursor.execute(ai_response)
                            rows = cursor.fetchall()
                            response_text = str(rows) 
                            logger.info(f"SQL query result: {response_text}")
                    except Exception as e:
                        response_text = f"Error executing SQL: {str(e)}"
                        # logger.error(response_text)
                        error_message = Message.objects.create(message_type=MessageType.SYSTEM, text="There was an error processing your request. Please try again.")
                        chat_history_ids.extend([error_message.id,])
                        request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                        return JsonResponse({'query': query, 'response': error_message.text})
                    finally:    # have the chatbot explain the results
                        print(f"SQL query: {sql_statement}")
                        print(f"SQL response: {response_text}")
                        try:
                            completion = client.chat.completions.create(
                                model="gpt-4",
                                messages=[{"role": "system", "content": f"Explain the following results of a PostgreSQL query as if you are telling the user about healthcare resources you found in Alabama. If the results are empty, say that you could not find any information on {resource_type} in {city}. If the results are not empty, they will be a list with each element in the following format:\nagency name, address part 1, address part 2, city, id_cms_other (ignore this), resource type\nresults: {response_text}"}],
                            )
                            ai_response = completion.choices[0].message.content
                        except Exception as e:
                            # ai_response = f"Error explaining SQL results: {str(e)}" # debug
                            # logger.error(ai_response)
                            error_message = Message.objects.create(message_type=MessageType.SYSTEM, text="There was an error processing your request. Please try again.")
                            chat_history_ids.extend([error_message.id,])
                            request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                            return JsonResponse({'query': query, 'response': error_message.text})
                else:
                    try:
                        ai_response.upper().find("SQL:")
                        # error_message = Message.objects.create(message_type=MessageType.SYSTEM, text="There was an error processing your request. Please try again.")
                        # chat_history_ids.extend([error_message.id,])
                        # request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                        # return JsonResponse({'query': query, 'response': error_message.text})
                    except Exception as e:
                        pass
            
            except Exception as e:
                # create Messages object for the error
                error_message = Message.objects.create(message_type=MessageType.SYSTEM, text="There was an error processing your request. Please try again.")
                chat_history_ids.extend([error_message.id,])
                request.session['chat_history_ids'] = chat_history_ids + [error_message.id]
                return JsonResponse({'query': query, 'response': error_message.text})

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
