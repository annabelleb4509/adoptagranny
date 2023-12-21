from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User



class Profile(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postcode = models.IntegerField()
    state = models.CharField(max_length=100)
    description = models.TextField(max_length=300)
    hobbies = models.CharField(max_length=300)
    excitedby = models.TextField(max_length=100)
    abilities = models.CharField(max_length=100)
    lookingfor = models.TextField(max_length=100)


    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # __str__
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'profile_id': self.id})

    # class Meta:
    #     db_table = 'user_profile'


class Conversation(models.Model):
    participants = models.ManyToManyField(Profile, related_name='conversations')

    def __str__(self):
        return f'({self.id})'

    def get_absolute_url(self):
        return reverse('messages_list', kwargs={'profile_id': self.id})


class Message(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='recipient')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('messages_list', kwargs={'message_id': self.id})

    class Meta:
        db_table = 'chat_messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ('-timestamp',)


    def get_all_messages(id_1, id_2):
        messages = []
        message1 = Message.objects.filter(sender_id=id_1, recipient_id=id_2).order_by('-timestamp')
        for x in range(len(message1)):
            messages.append(message1[x])
        message2 = Message.objects.filter(sender_id=id_2, recipient_id=id_1).order_by('-timestamp')
        for x in range(len(message2)):
            messages.append(message2[x])

        for x in range(len(messages)):
            messages[x].is_read = True
        messages.sort(key=lambda x: x.date, reverse=False)
        return messages

    
    def get_message_list(u):
        m = []
        j = []
        k = []
        for message in Message.objects.all():
            for_you = message.recipient == u 
            from_you = message.sender == u
            if for_you or from_you:
                m.append(message)

        for i in m:
            if i.sender.name not in j or i.recipient.name not in j:
                j.append(i.sender.name)
                j.append(i.recipient.name)
                k.append(i)

        return k