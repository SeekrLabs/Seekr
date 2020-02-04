from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import MessengerUser
from profiles.models import Profile
from postings.models import Alert
from global_variables import linkedin_scraper
from .chatfuel import *
import json

# # Skeleton code
# # request.POST is a dictionary with request data
def create_messenger_user(request):
    data = json.loads(request.body)
    print(data)

    messenger_id = data['messenger_id']
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
    
    else:
        # Update existing user if it's already in Database
        user = MessengerUser.objects.get(pk=messenger_id)
        user.gender = gender
        user.profile_pic_url = profile_pic_url
        user.first_name = first_name
        user.last_name = last_name
        user.save()
    
    response = ChatfuelResponse()
    return JsonResponse(response.to_dict())

def confirm_linkedin_profile(request):
    
    data = json.loads(request.body)
    messenger_id = data['messenger_id']
    username = data['linkedin_username']

    print("Received data: messenger_id: %s, linkedin_username: %s" \
            %(messenger_id, username))

    response = ChatfuelResponse(messages=[])
    profile_url = 'https://www.linkedin.com/in/' + username

    if Profile.username_validator(username) \
            and linkedin_scraper.get_profile_by_url(profile_url):
        
        message = TextMessage("Great! We've found you.")    
        response.add_message(message)
        response.add_redirect("Menu")
            
    else:
        response.add_redirect("VerifyLinkedIn")
        
    
    response = response.to_dict()
    return JsonResponse(response)



# def add_preferences(request):
#     pass

# def browse_jobs(request):
#     pass

# def save_job(request):
#     pass

# def browse_saved_jobs(request):
#     pass

def search_jobs(request):

    data = json.loads(request.body)
    print(data)

    messenger_id = data['messenger_id']
    title = data['title']
    location = data['location']
    offset = int(data['page'])

    user = MessengerUser.objects.get(pk=messenger_id)
    postings = user.get_postings(title, location, offset)

    #Alert users based on postings
    #---
    
    gallery_message = GalleryMessage("square")
    
    for posting in postings:
        if posting.image_url == '':
            image_url = 'https://blog.herzing.ca/hubfs/becoming%20a%20programmer%20analyst%20lead-1.jpg'
        else:
            image_url = posting.image_url

        apply_button = UrlButton("Apply Now!", posting.url)
        gallery_card = GalleryCard(posting.title, posting.company, image_url,
                buttons=[apply_button])

        gallery_message.add_card(gallery_card)

    next_page = QuickReply("Next Page", block_name="JobSearch")
    next_page.set_attribute("result_page", str(offset+1))
    gallery_message.add_quick_reply(next_page)

    alert = TextMessage("Would you like to recieve alerts related to this search?")
    
    response = ChatfuelResponse(messages=[])
    response.add_message(gallery_message)
    response.add_message(alert)
    
    response = response.to_dict()
    
    #Handle code for checking if user says yes or no to this
    #---
    wantAlert = false
    
    if wantAlert:
        newAlert = Alert(jobTitle=title,jobLocation=location)
        Alert.objects.bulk_create(newAlert)
    
    return JsonResponse(response)
