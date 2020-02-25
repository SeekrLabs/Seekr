from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import MessengerUser
from profiles.models import Profile
from global_variables import linkedin_scraper
from .chatfuel import *
from postings.models import Posting
import json
from constants import *
import logging
from django.db import IntegrityError


logger = logging.getLogger("app")

def create_messenger_user(request):
    """Creates a user
    """
    data = json.loads(request.body)
    logger.info(json.dumps(data, indent=4, sort_keys=True))

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
    response_dict = response.to_dict()
    logger.info('Response: ' + json.dumps(response_dict, indent=4, sort_keys=True))
    return JsonResponse(response_dict)


def confirm_linkedin_profile(request):
    """Attempts to scrape a linkedin user URL and save it to database

    Returns:
        JsonResponse: Found message if user found, else redirects to querying input
    """
    
    data = json.loads(request.body)
    logger.info(json.dumps(data, indent=4, sort_keys=True))

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
        
    
    response_dict = response.to_dict()
    logger.info('Response: ' + json.dumps(response_dict, indent=4, sort_keys=True))
    return JsonResponse(response_dict)


def save_posting(request):
    """Saves the id of the posting in user's saved postings

    Returns:
        JsonResponse: A message asking if they would like to browse their saved jobs
    """
    try:
        data = json.loads(request.body)
        logger.info(json.dumps(data, indent=4, sort_keys=True))

        messenger_id = data['messenger_id']
        posting_id = data['posting_id']

        response = ChatfuelResponse(messages=[])

        try:
            MessengerUser.saved_postings.through.objects.create(
                messengeruser_id=messenger_id, posting_id=posting_id)

        except IntegrityError as e:
            if 'unique constraint' in e.args[0].lower():
                logger.error("hi")
                response.add_message(TextMessage("You've already saved this job."))
            else:
                logging.error("Saving posting error: {}".format(e))
                return send_error_message()

        list_postings_button = BlockButton("Browse Saved Jobs", "BrowseSavedPostings")
        message = ButtonMessage("Posting saved!", buttons=[list_postings_button])
        response.add_message(message)

        response_dict = response.to_dict()
        response_dict['status'] = 'success'

        logger.info('Response: ' + json.dumps(response_dict, indent=4, sort_keys=True))
        return JsonResponse(response_dict)

    except:
        logger.error("", exc_info=True)
        return JsonResponse({'status': 'failure'}, status=500)

def view_posting(request):
    """ Saves a click event by user and redirects to posting URL

    Returns:
        HttpResponseRedirect: Redirects to posting URL
    """
    messenger_id = request.GET['messenger_id']
    posting_id = request.GET['posting_id']

    if not MessengerUser.objects.filter(pk=messenger_id).exists():
        logger.error("User doesn't exist")
        return send_error_message()

    posting = Posting.objects.filter(pk=posting_id)
    if not posting.exists():
        logger.error("Posting doesn't exist")
        return send_error_message()

    # Don't need to handle the case where already exists
    try:
        MessengerUser.clicked_postings.through.objects.create(
            messengeruser_id=messenger_id, posting_id=posting_id)
    except:
        pass

    logger.info("Sending redirect to {}".format(posting.first().url))
    return HttpResponseRedirect(posting.first().url)


def remove_saved_posting(request):
    """Removes the saved posting in user's saved postings

    Returns:
        JsonResponse: Redirects to browse saved postings and displays it
    """
    try:
        data = json.loads(request.body)
        logger.info(json.dumps(data, indent=4, sort_keys=True))

        messenger_id = data['messenger_id']
        posting_id = data['posting_id']

        MessengerUser.saved_postings.through.objects.filter(
                messengeruser_id=messenger_id, posting_id=posting_id).delete()

        response = ChatfuelResponse(
            messages=[TextMessage("Here's your updated saved postings.")])
        response.add_redirect("BrowseSavedPostings")

        response_dict = response.to_dict()
        response_dict['status'] = 'success'

        logger.info('Response: ' + json.dumps(response_dict, indent=4, sort_keys=True))
        return JsonResponse(response_dict)
    except:

        logger.error("", exc_info=True)
        return JsonResponse({'status': 'failure'}, status=500)
    

def browse_saved_postings(request):
    """Browse saved postings of a messenger user

    Returns:
        JsonResponse: A gallery of saved jobs
    """
    try:
        data = json.loads(request.body)
        logger.info(json.dumps(data, indent=4, sort_keys=True))

        messenger_id = data['messenger_id']
        offset = max(int(data['saved_posting_page']), 0)

        postings = Posting.objects.filter(
            messengeruser__id=messenger_id)[offset*10:(offset+1)*10]
        gallery_message = GalleryMessage("horizontal")

        response = ChatfuelResponse(messages=[])
        
        if len(postings) == 0:
            message = ButtonMessage(
                "You don't have any jobs saved! Do you want to browse more jobs?", 
                buttons=[])
            message.add_button(BlockButton("Browse More Jobs", "JobSearchQuery"))
            response.add_message(message)
            
        else:
            for posting in postings:
                if posting.image_url == '':
                    image_url = STOCK_IMAGE_URL
                else:
                    image_url = posting.image_url
                    
                posting_url = get_posting_url(messenger_id, posting.pk)
                apply_button = UrlButton("Apply Now!", posting_url)
                remove_saved_posting = BlockButton("Remove Saved Posting", 
                                                "RemoveSavedPosting")
                remove_saved_posting.set_attribute("var_posting_id", posting.id)

                gallery_card = GalleryCard(posting.title, posting.company, image_url,
                        buttons=[apply_button, remove_saved_posting])

                gallery_message.add_card(gallery_card)

            next_page = QuickReply("Next Page", block_name="BrowseSavedPostings")
            next_page.set_attribute("saved_posting_page", str(offset+1))
            gallery_message.add_quick_reply(next_page)

            prev_page = QuickReply("Prev Page", block_name="BrowseSavedPostings")
            prev_page.set_attribute("saved_posting_page", max(str(offset-1), 0))
            gallery_message.add_quick_reply(prev_page)

            
            response.add_message(gallery_message)
        response_dict = response.to_dict()
        logger.info('Response: ' + json.dumps(response_dict, indent=4, sort_keys=True))
        return JsonResponse(response_dict)

    except:
        logger.error("", exc_info=True)
        return JsonResponse({'status': 'failure'}, status=500)


def search_jobs(request):
    """Searches postings given user's preferred location and title

    Returns:
        JsonResponse: A gallery of posting results
    """
    data = json.loads(request.body)
    logger.info(json.dumps(data, indent=4, sort_keys=True))

    messenger_id = data['messenger_id']
    title = data['title']
    location = data['location']
    offset = int(data['page'])

    user = MessengerUser.objects.get(pk=messenger_id)
    postings = user.get_postings(title, location, offset)


    response = ChatfuelResponse(messages=[])
    if len(postings) == 0:
        response.add_message(TextMessage(
            "Unfortunately I couldn't find any job for you at theis time."))
    else:
        gallery_message = GalleryMessage("horizontal")
        for posting in postings:
            if posting.image_url == '':
                image_url = STOCK_IMAGE_URL
            else:
                image_url = posting.image_url

            posting_url = get_posting_url(messenger_id, posting.pk)
            apply_button = UrlButton("Apply Now!", posting_url)
            save_button = BlockButton('Save Posting', 'SavePosting')
            save_button.set_attribute("var_posting_id", posting.id)

            gallery_card = GalleryCard(posting.title, posting.company, image_url,
                    buttons=[apply_button, save_button])

            gallery_message.add_card(gallery_card)

        next_page = QuickReply("Next Page", block_name="JobSearch")
        next_page.set_attribute("result_page", str(offset+1))
        gallery_message.add_quick_reply(next_page)

        response.add_message(gallery_message)
    response_dict = response.to_dict()

    logger.info('Response: ' + json.dumps(response_dict, indent=4, sort_keys=True))
    return JsonResponse(response_dict)

def get_posting_url(messenger_user_id, posting_id):
    return HOST_URL[:-1] + reverse('view_posting') \
        + '?messenger_id=' \
        + messenger_user_id \
        + '&posting_id=' \
        + posting_id

def send_error_message():
    response = ChatfuelResponse(
        messages=[TextMessage("An error has occured! Please be paitient "
                                "and we'll fix it as soon as possible")])
    response_dict = response.to_dict()
    return JsonResponse(response_dict)