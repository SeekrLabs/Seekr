from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import MessengerUser

# # Skeleton code
# # request.POST is a dictionary with request data
def create_messenger_user(request):
    messenger_id = request.POST['messenger_id']
    gender = request.POST['gender']
    profile_pic_url = request.POST['profile_pic_url']

    if not MessengerUser.objects.filter(pk=messenger_id).exists():
        MessengerUser.objects.create(
            id=messenger_id,
            gender=gender,
            profile_pic_url=profile_pic_url
        )
        return HttpResponse("Success")
    return HttpResponse("User already exists")

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
    offset = request.GET['offset']
    user = MessengerUser.objects.get(pk=1)
    return HttpResponse(user.get_postings(int(offset)))