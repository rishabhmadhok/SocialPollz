from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    firstname = models.CharField(max_length = 200,blank=True)
    lastname = models.CharField(max_length = 200,blank=True)
    photo = models.ImageField(blank=True, null=True)
    email = models.CharField(max_length = 200)

    def __str__(self) -> str:
        return self.user.username


class Topic(models.Model):
    topic_name = models.CharField(max_length = 200, unique=True) 

    def __str__(self) -> str:
        return self.topic_name

class Poll(models.Model):
    question_text = models.CharField(max_length = 200)
    author = models.ForeignKey(User,on_delete = models.DO_NOTHING)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    upvoters = models.ManyToManyField(User,related_name='upvoters')
    downvoters = models.ManyToManyField(User,related_name='downvoters')
    topic = models.ForeignKey(Topic,on_delete = models.DO_NOTHING)
    voters = models.ManyToManyField(User, related_name='voters')
    
    def __str__(self) -> str:
        return self.question_text

class Choice(models.Model):
    choice_text = models.CharField(max_length = 200)
    poll = models.ForeignKey(Poll, on_delete = models.CASCADE)
    num_votes = models.PositiveIntegerField(default=0)
    users = models.ManyToManyField(User)

    def percent_votes(self):
        print(self.choice_text)
        print(self.num_votes)
        print(self.poll.voters.all().count())
        if self.num_votes == 0:
            return 0
        
        value = round(self.num_votes / self.poll.voters.all().count() * 100)
        return value

    def __str__(self) -> str:
        return self.choice_text


class Comment(models.Model):
    comment_text = models.TextField() 
    author = models.ForeignKey(User,on_delete = models.DO_NOTHING, related_name='author')
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    poll = models.ForeignKey(Poll,on_delete = models.CASCADE)
    likers = models.ManyToManyField(User, related_name='likers')

    def __str__(self) -> str:
        return self.comment_text



