import json

class BlockButton:
    def __init__(self, title: str, block_name: str):
        self.title = title
        self.block_name = block_name
    
    def to_dict(self):
        return {
            "type": "show_block",
            "block_names": [self.block_name],
            "title": self.title,
        }

class UrlButton:
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url

    def to_dict(self):
        return {
            "type": "web_url",
            "url": self.url,
            "title": self.title,
        }
    
class JsonButton:
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url

    def to_dict(self):
        return {
            "type": "json_plugin_url",
            "url": self.url,
            "title": self.title,
        }

class ButtonMessage:
    def __init__(self, text: str, buttons=[]):
        self.text = text
        self.buttons = buttons

    def add_button(self, button):
        self.buttons.append(button)

    def to_dict(self):
        return {
            "attachment": {
                "type": "template",
                "payload": {
                "template_type": "button",
                "text": self.text,
                "buttons": [b.to_dict() for b in self.buttons[:3]]
                }
            }
        }

class TextMessage:
    def __init__(self, message: str):
        self.message = message

    def to_dict(self):
        return {
            "text": self.message,
        }

class GalleryMessage:
    def __init__(self, aspect_ratio: str, cards=[]):
        self.aspect_ratio = aspect_ratio
        self.cards = []
        self.quick_replies = []

    def add_card(self, card):
        self.cards.append(card)

    def add_quick_reply(self, reply):
        self.quick_replies.append(reply)

    def to_dict(self):
        gallery = {
            "attachment":{
                "type":"template",
                "payload":{
                    "template_type":"generic",
                    "image_aspect_ratio": self.aspect_ratio,
                    "elements": [c.to_dict() for c in self.cards[:10]]
                }
            }
        }

        if len(self.quick_replies) > 0:
            gallery['quick_replies'] = [q.to_dict() for q in self.quick_replies]
        
        return gallery

class GalleryCard:
    def __init__(self, title: str, subtitle: str, image_url: str, buttons=[]):
        self.title = title
        self.subtitle = subtitle
        self.image_url = image_url
        self.buttons = buttons

    def add_button(self, button):
        self.buttons.append(button)

    def to_dict(self):
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "image_url": self.image_url,
            "buttons": [b.to_dict() for b in self.buttons[:3]]
        }

class ChatfuelResponse:
    def __init__(self, messages=[]):
        self.messages = messages
        self.attributes = {}
        self.redirect = None

    def add_message(self, message):
        self.messages.append(message)
    
    def add_redirect(self, block_name):
        self.redirect = block_name

    def set_attribute(self, key, val):
        self.attributes[key] = val

    def to_dict(self):
        message = {
            "messages": [m.to_dict() for m in self.messages]
        }
        
        if len(self.attributes) > 0:
            message['set_attributes'] = self.attributes

        if self.redirect:
            message['redirect_to_blocks'] = [self.redirect]

        return message

class QuickReply:
    def __init__(self, title, block_name=None):
        self.title = title
        self.block_name = block_name
        self.attributes = {}

    def set_attribute(self, key, val):
        self.attributes[key] = val

    def to_dict(self):
        reply = {
            "title": self.title,
        }
        if self.block_name:
            reply['block_names'] = [self.block_name]
        
        if len(self.attributes) > 0:
            reply['set_attributes'] = self.attributes

        return reply