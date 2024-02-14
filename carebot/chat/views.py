from django.shortcuts import render
from .forms import QueryForm
from openai import OpenAI
from django.conf import settings

def query_view(request):
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
                return render(request, 'chat/error.html', {'error': str(e)})
            return render(request, 'chat/response.html', {'response': completion.choices[0].message})
    else:
        form = QueryForm()
    return render(request, 'chat/query.html', {'form': form})
