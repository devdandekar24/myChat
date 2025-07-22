from django.forms import ModelForm
from django import forms
from .models import *
from emoji_picker.widgets import EmojiPickerTextInputAdmin


# widgets dictonary in Meta class customizes how form fields are rendered in html
# the Meta class links the form to a model and specifies which fields to include and how they should be displayed.
class ChatmessageCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        widgets = {
            'body' : forms.TextInput(attrs={'placeholder': 'Add message ...', 'class': 'p-4 text-black', 'maxlength' : '300', 'autofocus': True }),
        }
        
class NewGroupForm(ModelForm):
    class Meta:
        model = ChatGroup
        fields = [ 'groupchat_name']
        widgets = {
            'groupchat_name': forms.TextInput(attrs={
                'placeholder':'Add name ...',
                'class':'p-4 text-black',
                'maxlength':'300',
                'autofocus':True,
            }),
        }
        
class ChatRoomEditForm(ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {
            'groupchat_name': forms.TextInput(attrs={
                'class':'p-4 text-xl font-bold mb-4',
                'maxlength':'300',
            }),
        }