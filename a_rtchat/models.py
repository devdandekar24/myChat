import os

import shortuuid
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from PIL import Image


class ChatGroup(models.Model):
    # group_name = models.CharField(max_length=128, unique= True,default=shortuuid.uuid)
    group_name = models.CharField(max_length=128, unique= True,blank=True)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    admin = models.ForeignKey(User, related_name='groupchats', blank=True, null=True, on_delete=models.SET_NULL)
    # users who are online ( used in consumers.py )
    users_online = models.ManyToManyField(User,related_name='online_in_groups',blank=True)
    members = models.ManyToManyField(User, related_name='chat_groups',blank=True)
    is_private = models.BooleanField(default=False)
    # 
    blocked_members = models.ManyToManyField(User, related_name='blocked_groups', blank=True)
    removed_members = models.ManyToManyField(User, related_name='removed_groups',blank=True)
    
    def __str__(self):
        return self.group_name
    
    def save(self, *args, **kwargs):
        if not self.group_name:
            self.groupp_name=shortuuid.uuid()
        super().save(*args,**kwargs)
    
class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.CharField(max_length=300, blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
    
    # The @property decorator lets you define a method that you can access like an attribute. It's a clean way to add "calculated" or "derived" fields to your class without actually storing them in the database.
    # pls note it is used as field and not as method
    @property
    def filename(self):
        if self.file:
            return os.path.basename(self.file.name)
        else:
            return None
    
    
    class Meta:
        ordering = ['-created']
        
    @property    
    def is_image(self):
        try:
            image = Image.open(self.file) 
            image.verify()
            return True 
        except:
            return False

    def __str__(self):
        if self.body:
            return f'{self.author.username} : {self.body}'
        elif self.file:
            return f'{self.author.username} : {self.filename}'
        return f'{self.author.username} : [Empty message]'
    
    @property
    def body_decrypted(self):
        f= Fernet(settings.ENCRYPT_KEY)
        message_decrypted = f.decrypt(self.body)
        message_decoded = message_decrypted.decode('utf-8')
        return message_decoded