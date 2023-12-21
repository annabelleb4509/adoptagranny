from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Profile, Conversation, Message
from .forms import MessageForm
from django.contrib.auth.mixins import LoginRequiredMixin


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')


def profiles_index(request):
  profiles = Profile.objects.all()
  return render(request, 'profiles/index.html', {
    'profiles': profiles,
  })

def profiles_detail(request, profile_id):
  profile = Profile.objects.get(id=profile_id)
  form = MessageForm()
  print('request.user')
  print(request.user.id)
  print('request.user end')
  return render(request, 'profiles/detail.html', {
    'profile': profile, 'form': form
  })

#def own_profiles_detail(request, profile_id):
 # profile = Profile.objects.filter(user=request.user)

#  return render(request, 'profiles/detail.html', {
#    'profile': profile, 'form': form
#  })



class ProfileCreate(CreateView):
    model = Profile
    fields = ['name', 'city', 'postcode', 'state', 'hobbies', 'description', 'excitedby', 'abilities', 'lookingfor' ]

    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)

class ProfileUpdate(UpdateView):
  model = Profile
  fields = [ 'name', 'city', 'postcode', 'state', 'hobbies', 'description', 'excitedby', 'abilities', 'lookingfor' ]

class ProfileDelete(DeleteView):
  model = Profile
  success_url = '/about'


 
class SearchResults(ListView):
    model = Profile
    template_name = 'search_results.html'

    def get_queryset(self): 
        query = self.request.GET.get("q")
        object_list = Profile.objects.filter(
            Q(name__icontains=query) | 
            Q(city__icontains=query) | 
            Q(postcode__icontains=query) | 
            Q(state__icontains=query) | 
            Q(hobbies__icontains=query) |
            Q(description__icontains=query) | 
            Q(excitedby__icontains=query) |
            Q(abilities__icontains=query) |
            Q(lookingfor__icontains=query)
        )
        return object_list


def signup(request):
  error_message = ''
  if request.method == 'POST':

    form = UserCreationForm(request.POST)
    if form.is_valid():

      user = form.save()

      login(request, user)
      return redirect('profiles_create')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)



class MessageCreate(CreateView):
    model = Message
    fields = ['text']

# def send_message(request, profile_id, message_id):
#   profile = Profile.objects.get(id=profile_id).messages.add(message_id)
#   return redirect('messages_list', profile_id=profile_id)

def messages_list(request, profile_id):
  profile = Profile.objects.get(id=profile_id)
  message_ids = Conversation.messages.all().values_list('id')
  return render(request, 'messages_list.html',  {
    'messages': messages, 'profile':profile
  })

def add_message(request, profile_id):
    form = MessageForm(request.POST)
    if form.is_valid():
        new_message = form.save(commit=False)
        new_message.profile_id = profile_id
        new_message.save()
    return redirect('detail', profile_id=profile_id)

  # conversation model stores profile ID of person that is logged in + person's profile they are on
  #

def send_message(request, receiver_id):
  recipient_profile = get_object_or_404(Profile, id=receiver_id)
  print('hell')
  print(request.user.id)
  print('hell end')
  sender_profile = Profile.objects.get(user_id=request.user.id)
  # does conversation already exist?
  conversation = Conversation.objects.filter(participants=sender_profile).filter(participants=recipient_profile).first()

  # If it doesn't create new:
  if not conversation: 
    conversation = Conversation.objects.create()
    conversation.participants.add(sender_profile, recipient_profile)

  if request.method == 'POST':
    content = request.POST.get('text', '')
    message = Message.objects.create(conversation=conversation, sender=sender_profile, recipient=recipient_profile, text=content)
    return redirect('conversation_detail', conversation_id=conversation.id)

  return render(request, 'send_message.html', {'recipient_profile': recipient_profile})


def conversation_detail(request, conversation_id):
  conversation = get_object_or_404(Conversation, id=conversation_id)
  messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
  return render(request, 'conversation_detail.html', {'conversation': conversation, 'messages': messages})



##

class MessagesListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'main_app/messages_list.html'
    login_url = '/login/'

    # context data for latest message to display
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
          user = Profile.objects.get(user_id=self.request.user.pk)  # get your primary key

          messages = Message.get_message_list(user) # get all messages between you and the other user

          other_users = [] # list of other users

          # getting the other person's name from the message list and adding them to a list
          for i in range(len(messages)):
              if messages[i].sender != user:
                  other_users.append(messages[i].sender)
              else:
                  other_users.append(messages[i].recipient)
        except Profile.DoesNotExist:
          user = None 
          messages = None
          other_users = [] # list of other users


        context['messages_list'] = messages
        context['other_users'] = other_users
        context['you'] = user
        return context






# --------------------------------- Chat view -------------------------------- #
class InboxView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'chat/inbox.html'
    login_url = '/login/'
    queryset = Profile.objects.all()


    # to send a message (pass the username instead of the primary key to the post function)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    # override detailView default request pk or slug to get username instead
    def get_object(self):
        UserName= self.kwargs.get("username")
        return get_object_or_404(UserProfile, username=UserName)



    # context data for the chat view
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = Profile.objects.get(pk=self.request.user.pk)  # get your primary key
        other_user = Profile.objects.get(username=self.kwargs.get("username"))  # get the other user's primary key
        messages = Message.get_message_list(user) # get all messages between you and the other user

        other_users = [] # list of other users


       # getting the other person's name from the message list and adding them to a list
        for i in range(len(messages)):
            if messages[i].sender != user:
                other_users.append(messages[i].sender)
            else:
                other_users.append(messages[i].recipient)

        sender = other_user  # the sender of the message will be the recipient of the most recent message after it's sent
        recipient = user # the recipient of the message will be the sender of the most recent message after it's sent

        context['messages'] = Message.get_all_messages(sender, recipient)  # get all the messages between the sender(you) and the recipient (the other user)
        context['messages_list'] = messages # for MessagesListView template
        context['other_person'] = other_user  # get the other person you are chatting with from the username provided
        context['you'] = user  # send your primary key to the post
        context['other_users'] = other_users

        return context

    # send a message
    def post(self, request, *args, **kwargs):
        # print("sender: ", request.POST.get("you"))
        # print("recipient: ", request.POST.get('recipient'))
        sender = UserProfile.objects.get(pk=request.POST.get('you'))  # get the sender of the message(the person sending it)
        recipient = UserProfile.objects.get(pk=request.POST.get('recipient'))  # get the recipient of the message(You)
        message = request.POST.get('message')  # get the message from the form

        if not request.user.is_authenticated:
            return render(request, 'auth/login.html')
        if message and request.method == 'POST':
            Message.objects.create(sender=sender, recipient=recipient, message=message)
        return redirect('chat:inbox', username=recipient.username)  # redirect to the inbox of the recipient

# -------------------------------- Users list -------------------------------- #
class UserListsView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'chat/users_list.html'
    context_object_name = 'users'
    login_url = '/login/'

    # context data for the users list
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = UserProfile.objects.get(pk=self.request.user.pk)  # get your primary key
        context['users'] = UserProfile.objects.exclude(pk=user.pk)  # get all the users except you
        return context