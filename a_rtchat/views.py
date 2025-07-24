from django.shortcuts import render, get_object_or_404,redirect
from django.http import Http404,HttpResponse
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def chat_view(request,chatroom_name = 'public-chat'):
    print("HTMX?", request.htmx)

    # chat_group = get_object_or_404(ChatGroup, group_name =chatroom_name)
    chat_group, created = ChatGroup.objects.get_or_create(group_name=chatroom_name)

    # if request.user in chat_group.blocked_members.all():
    #     messages.error(request, "You are blocked from this chatroom.")
    #     return redirect('home')
    
    chat_messages=chat_group.chat_messages.all()[:30]
    form=ChatmessageCreateForm()
    
    other_user = None
    # private chat with other user ( 1 on 1 so we used break)
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all():
            if member != request.user:
                other_user = member
                break
    
    # join chat using url ( only for verified users)
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            # 
            # If removed from chat, redirect
            if request.user in chat_group.removed_members.all():
                messages.info(request,f"You are removed from {chat_group.groupchat_name}.")
                chat_group.removed_members.remove(request.user)
                return redirect('home')
            
            # below code works nice
            if request.user in chat_group.blocked_members.all():
                messages.error(request, f"You are blocked from {chat_group.groupchat_name} chatroom.")
                return redirect('home')
            # 
            if request.user.emailaddress_set.filter(verified=True).exists():
                chat_group.members.add(request.user)
            else:
                messages.warning(request, 'You need to verify your email to join the chat!')
                return redirect('profile-settings')
    
    # no different view created for sending messages
    # if request.method =="POST":
    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author= request.user
            message.group = chat_group
            message.save()
            
            context={
                'message':message,
                'user':request.user
            }
            # return redirect('home')
            return render(request,'a_rtchat/partials/chat_message_p.html',context)
    # if method is not post, i.e. to only display the messages
    # we not used else as messages must be displayed even when one is submitting messages
    context = {
        'chat_messages':chat_messages, 
        'form':form,
        'other_user':other_user,
        'chatroom_name':chatroom_name,
        'chat_group':chat_group,
    }
    
    return render(request,'a_rtchat/chat.html',context)


@login_required
def get_or_create_chatroom(request, username):
    # Handle self-chat scenario
    if request.user.username == username:
        # Try to fetch existing self-chatroom with name "Me"
        self_chat = request.user.chat_groups.filter(is_private=True, groupchat_name="Me").first()
        if self_chat:
            return redirect('chatroom', self_chat.group_name)

        # Create a new self-chatroom and add the user
        self_chat = ChatGroup.objects.create(is_private=True, groupchat_name="Me")
        self_chat.members.add(request.user)
        return redirect('chatroom', self_chat.group_name)

    # Fetch the other user (raises 404 if user doesn't exist)
    other_user = get_object_or_404(User, username=username)

    # Prevent users from trying to access someone else's self-chat
    if username == "self":
        # If someone tries to access /chat/self or similar
        raise Http404("You cannot access another user's self-chat.")

    # Get current user's private chatrooms
    my_private_chatrooms = request.user.chat_groups.filter(is_private=True)

    # Check if a chatroom with the other user already exists
    for chatroom in my_private_chatrooms:
        if other_user in chatroom.members.all():
            return redirect('chatroom', chatroom.group_name)

    # No existing chatroom found — create a new one
    chatroom = ChatGroup.objects.create(is_private=True)
    chatroom.members.add(other_user, request.user)
    return redirect('chatroom', chatroom.group_name)

#  creating a new group chat
@login_required        
def create_groupchat(request):
    form = NewGroupForm()
    
    if request.method == "POST":
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom', new_groupchat.group_name)
    
    context ={
        'form': form,
    }
    return render(request,'a_rtchat/create_groupchat.html',context)

# edit chatroom
@login_required
def chatroom_edit_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    form = ChatRoomEditForm(instance=chat_group) 
    
    if request.method == 'POST':
        # This loads the existing group info into the form
        form = ChatRoomEditForm(request.POST, instance=chat_group)
        if form.is_valid():
            form.save()
            # 
            # multiselect checkboxes # Block selected members
            # blocking also means removing member from group
            block_members = request.POST.getlist('block_members')
            for member_id in block_members:
                member = User.objects.get(id=member_id)
                chat_group.blocked_members.add(member)
                if member in chat_group.members.all():
                    chat_group.members.remove(member)

            # Unblock selected members
            unblock_members = request.POST.getlist('unblock_members')
            for member_id in unblock_members:
                member = User.objects.get(id=member_id)
                chat_group.blocked_members.remove(member) 
                
            # form has a multi-select or checkboxes with name remove_members
            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.removed_members.add(member)
                if member in chat_group.members.all():
                    chat_group.members.remove(member) 
                
            return redirect('chatroom', chatroom_name) 
        
            # blocked and unblocked customers code will come here.
            # to stop removed members from sending messages immediatly need to work on consumers.py
            # also update chatroom_edit.html
    context = {
        'form' : form,
        'chat_group' : chat_group,
        # 'members': chat_group.members.all(),
        # 'blocked_members': chat_group.blocked_members.all()
    }   
    return render(request, 'a_rtchat/chatroom_edit.html', context)

# delete current chatroom
@login_required
def chatroom_delete_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name = chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    if request.method=="POST":
        chat_group.delete()
        messages.success(request, 'Chatroom deleted')
        return redirect('home')
        
    return render(request, 'a_rtchat/chatroom_delete.html',{'chat_group':chat_group})

# leaving the chatroom
@login_required
def chatroom_leave_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    # post the form
    if request.method == "POST":
        chat_group.members.remove(request.user)
        messages.success(request, 'You left the Chat')
        return redirect('home')
    # render leave chat form
    return render(request, "a_rtchat/confirm_leave.html", {
        "chat_group": chat_group
    })
    
@login_required
def chat_file_upload(request, chatroom_name):
    # chat group in which user is currently in
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    # Check if the request is an HTMX request AND it contains a file.
    if request.htmx and request.FILES:
        file = request.FILES['file']
        message = GroupMessage.objects.create(
            file = file,
            author = request.user, 
            group = chat_group,
        )
        #  Get the Django Channels layer to communicate via WebSockets
        channel_layer = get_channel_layer()
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        # Send the event to the WebSocket group named `chatroom_name`.
        # This pushes the file message to all users in that chatroom.
        # ends a real-time event/message to a specific WebSocket group using Django Channels.
        # WebSocket consumers are asynchronous, but Django views are synchronous.
        async_to_sync(channel_layer.group_send)(
            chatroom_name, event
        )
    return HttpResponse()





