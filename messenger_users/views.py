from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import MessengerUser
import json

# # Skeleton code
# # request.POST is a dictionary with request data
def create_messenger_user(request):
    response = {
        "messages": []
    }
    data = json.loads(request.body)
    print(data)

    messenger_id = int(data['messenger_id'])
    gender = data['gender']
    profile_pic_url = data['profile_pic_url']
    first_name = data['first_name']
    last_name = data['last_name']

    if not MessengerUser.objects.filter(pk=messenger_id).exists():  
        MessengerUser.objects.create(
            id=messenger_id,
            gender=gender,
            profile_pic_url=profile_pic_url,
            first_name=first_name,
            last_name=last_name,
        )
        response['messages'].append({
            'text': "Success!"
        })
        return JsonResponse(response)
    response['messages'].append({
        'text': "User exists."
    })
    
    return JsonResponse(response)

def add_linkedin_profile(request):
    pass

# def confirm_linkedin_profile(request):
#     pass

# def add_preferences(request):
#     pass

# def browse_jobs(request):
#     pass

# def save_job(request):
#     pass

# def browse_saved_jobs(request):
#     pass

def search_jobs(request):
    response = {
        "messages": []
    }
    data = json.loads(request.body)
    print(data)
    messenger_id = int(data['messenger_id'])
    title = data['title']
    location = data['location']
    offset = 0

    user = MessengerUser.objects.get(pk=messenger_id)
    postings = user.get_postings(title, location, offset)

    for posting in postings:
        response['messages'].append({
            "text": str(posting)
        })

    return JsonResponse(response)