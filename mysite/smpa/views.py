from django.db.models import Count
from django.shortcuts import get_list_or_404, get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import UserProfile, Poll,Topic,Choice,Comment,UserProfile
from django.contrib.auth import logout
from django.urls import reverse
from urllib.parse import urlencode
from django.conf import settings

# Create your views here.

def makeurl(baseurl_name, args, query_args):
    base = reverse(baseurl_name, args=args)
    print(base)
    query_string =  urlencode(query_args) 
    return f'{base}?{query_string}'

@login_required()
def createpoll(request):
    if request.method == 'POST':
        
        question = request.POST['question_text']
        topic_id = request.POST['topic']
        topic = Topic.objects.get(pk=topic_id) # gets topic chosen from list of topics in database using the topic id
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        choice3 = request.POST['choice3']
        choice4 = request.POST['choice4']
        choice5 = request.POST['choice5']

        poll = Poll(question_text=question, topic=topic,author=request.user) # instantiates poll

        poll.save()

        choices = [choice1, choice2, choice3, choice4, choice5]
        for choice in choices:
            if choice != None and len(choice.strip()) > 0:
                choice_ = Choice(choice_text = choice, poll = poll)
                choice_.save()
            # if the choice entered isn't empty it is saved to the database as an object of the choice class
        return redirect('smpa:polldetail', pollid=poll.id)
    return render(request, 'smpa/createpoll.html', {'topics': Topic.objects.all()})
    

@login_required()
def polldetail(request, pollid):
    poll = Poll.objects.get(id=pollid)

    
    # if the logged user has voted already
    #     get the choices and figure out the voted choice.
    #     that becomes the selected_choice
    selected_choice = ''
    choices = Choice.objects.filter(poll=poll)
    for choice in choices:
        if request.user in choice.users.all():
            selected_choice = choice
            break
    
    return render(request,'smpa/detail.html', {'poll':poll, 'selected_choice':selected_choice})

@login_required()
def vote(request, pollid):
    question = Poll.objects.get(id=pollid)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"]) # identifies selected choice
    except (KeyError, Choice.DoesNotExist):
        
        return render(
            request,
            "smpa/detail.html",
            {
                "q": question,
                "error_message": "You didn't select a choice.",
            },
        ) # if user attempts to vote without selecting a choice, an error message is displayed
    else:
        question.voters.add(request.user)
        selected_choice.users.add(request.user)
        selected_choice.num_votes += 1
        selected_choice.save()
        # updates the database by adding user to voters for that question, 
        # pairs the user to the selected choice and increases num votes for that choice by 1 
    return redirect(reverse('smpa:polldetail', args=(pollid,)))
# loads poll results page for that specific poll (identified by pollid)

@login_required()
def upvote(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    if request.user in poll.upvoters.all():
        poll.upvoters.remove(request.user)
    else:
        poll.upvoters.add(request.user)
# use of condition checks if the user is an upvoter when the user selects upvote, 
# and either removes or adds them depending on upvote status
    try:
        poll.downvoters.remove(request.user)
    except:
        pass
# use of try and except clause attempts to remove the user from downvoters as you cannot be upvoter and downvoter of a poll simultaneously, 
# if the user is not a downvoter it passes (handles the potential cause of error)
    return redirect(request.META['HTTP_REFERER'])

@login_required()
def downvote(request,poll_id):
    poll = Poll.objects.get(id=poll_id)
    if request.user in poll.downvoters.all():
        poll.downvoters.remove(request.user)
    else:
        poll.downvoters.add(request.user)

    try:
        poll.upvoters.remove(request.user)
    except:
        pass
        
    return redirect(request.META['HTTP_REFERER'])

@login_required()
def like(request,comment_id):
    comment = Comment.objects.get(id=comment_id)
    if request.user in comment.likers.all():
        comment.likers.remove(request.user)
    else: 
        comment.likers.add(request.user)

    return redirect(request.META['HTTP_REFERER']) # line reloads the same page with the new updated information from the database

@login_required()
def postcomment(request,poll_id):
    poll = Poll.objects.get(id=poll_id)
    text = request.POST['comment_text']
    comment = Comment(author=request.user, poll=poll,comment_text=text)
    comment.save()

    return redirect(request.META['HTTP_REFERER'])

@login_required()
def profilepage(request,username):
    print('argument:', username)
    user = get_list_or_404(UserProfile, user__username=username) # identifies userprofile of that user by calling UserProfile class and addressing the user's username
    if user:
        user = user[0]
        polls = Poll.objects.filter(author=user.user) # filters polls by auther username - only displays polls authored by the logged in user
        print(polls)
        return render(request, 'smpa/profilepage.html', {'user':user, 'polls':polls})
    
    
    
    # TODO: ERROR FINDING USER
    return redirect(request.META['HTTP_REFERER'])











@login_required()
def topic_home(request, topic_id):
    topics = Topic.objects.all()
    topic = Topic.objects.get(id=topic_id)
    print(topic.topic_name)
    polls = topic.poll_set.all()

    return render(request, 'smpa/home.html', {'topics': topics, 'selected_topic':topic, 'polls':polls}) # reloads home page displaying only polls matching the selected topic




@login_required()
def home(request):
    
    
    polls = Poll.objects.annotate(upvote_count=Count('upvoters')).order_by('-upvote_count')[:5] 
    # displays only the top 5 most upvoted polls on the home page main feed, in decreasing order(most upvoted at top)

    # poll_list = []
    # for poll in polls:
    #     numupvoters = len(poll.upvoters.all())
    #     poll_list.append((numupvoters, poll))
    # poll_list.sort(key=lambda x:x[0], reverse=True)
    # mostupvoted = [poll_list[i][1] for i in range(5)]

    return render(request, 'smpa/home.html', {'topics': Topic.objects.all(), 'polls':polls})

@login_required()
def followingfeed(request):
    ifollow =  request.user.follow.all()
    print(ifollow)

    polls = Poll.objects.filter(author__userp__in=ifollow)
    return render(request,'smpa/followingfeed.html',{"polls":polls})


@login_required()
def follow(request,user_id):

    userprofile = UserProfile.objects.get(user=User.objects.get(id=user_id))
    if request.user in userprofile.followers.all():
        userprofile.followers.remove(request.user)
    else:
        userprofile.followers.add(request.user)
    
    return redirect(request.META['HTTP_REFERER'])


def get_polls_with_comment_by(request, user):
    comments = user.comments.all()
    # polls = Poll.objects.none()

    # for comment in comments:
    #     polls |= comment.poll

    polls =  Poll.objects.filter(comment__in=comments)
    # print(user.username, '-', polls)
    return polls

def get_polls_engaged_with_by(request, user):
    if not user:
        return Poll.objects.none()
    
    return user.upvoted.all().union(user.voted.all(), get_polls_with_comment_by(request, user))

#@login_required()
#def recommended(request):

# user affinity
#  - if two users follow the same person, then that's a positive signal for user likeness
#  - if two users like the same polls, then that's also signal
#  - if two users like the same topics, then that's also a signal
#  - if two user's voted the same choice, commented on the same poll or engaged with the same poll that's a positive signal


def get_affinity_score(request, other_user):
    following_affinity = request.user.follow.all().intersection(other_user.follow.all()).count()
    # upvoting_affinity = other_user.upvoted.all().intersection(request.user.upvoted.all()).count()

    polls_engaged1 = get_polls_engaged_with_by(request, other_user)
    polls_engaged2 = get_polls_engaged_with_by(request, request.user)
    engagement_affinity = polls_engaged1.intersection(polls_engaged2).count()

    # print(f'me:{request.user.username}, other:{other_user.username}') 
    # print(f'  - # common followed: {following_affinity}, # common polls engaged: {engagement_affinity}')

    return following_affinity + engagement_affinity

def get_topics_engaged_with_by(request, user):
    my_engaged_polls = get_polls_engaged_with_by(request, user) 
    topics = Topic.objects.none()

    for poll in my_engaged_polls:
        topics |= Topic.objects.filter(poll=poll) 
    
    topics = topics.distinct() # removes duplicates
    return topics, my_engaged_polls


def get_most_similar_users(request, thisuser, top_user_count):
    
    others = User.objects.exclude(id=thisuser.id) # compares logged in user to others to calculate affinity
    affinity_scores = {}
    
    for other_user in others:
        score = get_affinity_score(request, other_user)
        affinity_scores[other_user] = score # scores generate for affinity between each other user and the logged in user


    # print('Logged in user:', request.user.username)
    user_ranks = sorted(affinity_scores, reverse=True, key=lambda x:affinity_scores[x]) # ranks other users in descending order of affinity score to logged in user

    top_user_count = get_setting('RECOMMEND_BASED_ON_HOW_MANY_SIMILAR_USERS', 2)
    # only displays polls from 2 similar users

    best_users = user_ranks[:top_user_count] # ranks other users on affinity

    # remove users that have no affinity with thisuser
    # i.e affinity score == 0
    while best_users and affinity_scores[best_users[-1]] == 0:
        best_users.pop()

    return best_users

def get_setting(setting_name, default_value):
    if settings.SMPA and setting_name in settings.SMPA:
        return settings.SMPA[setting_name]

    return default_value

# Recommendation
#  - recommend based on topics that the user has interacted with before
#  - and based on what other similar users poll on or engage with
def recommendedfeed(request):
    # TODO: optimise this by not calculating all these scores for me!
    #   - for instance, pass the polls i engage with already to the affinity function

    # topics user has engaged with
    topics, my_engaged_polls = get_topics_engaged_with_by(request, request.user)

    # filters polls to display polls from topics that logged in user has engaged with that have not been made by that user or have been downvoted by that user
    topic_polls = Poll.objects.filter(topic__in=topics).exclude(author=request.user).exclude(downvoters=request.user).difference(my_engaged_polls)    
    
    best_users = get_most_similar_users(request, request.user, 2)

    user_polls = Poll.objects.none()

    for user in best_users:
        user_polls.union(get_polls_engaged_with_by(request, user)) # displays polls that similar users have engaged with

    user_polls = user_polls.exclude(author=request.user).exclude(downvoters=request.user).difference(my_engaged_polls)    
    # these polls must not have been made by the logged in user or have been downvoted by them

    common_polls = topic_polls.intersection(user_polls)
    only_topic_polls = topic_polls.difference(common_polls)
    only_user_polls = user_polls.difference(common_polls)

    common_polls = list(common_polls)
    common_polls.sort(reverse=True, key=Poll.get_engagement_score)

    max_polls = get_setting('MAX_RECS', 5)
    if len(common_polls) >= max_polls:
        return render(request, 'smpa/recommendedfeed.html', {'polls':common_polls[:max_polls]})


    min_topic_polls = get_setting('MIN_RECS_FROM_INTERESTING_TOPICS', 3) - len(common_polls)
    min_user_polls = get_setting('MIN_RECS_FROM_SIMILAR_USERS', 3) - len(common_polls)

    polls = common_polls[:]

    if min_user_polls > 0:
        list_only_user_polls = list(only_user_polls)
        list_only_user_polls.sort(reverse=True, key=Poll.get_engagement_score)
        polls += list_only_user_polls[:min_user_polls]
    
    if min_topic_polls > 0:
        list_only_topic_polls = list(only_topic_polls)
        list_only_topic_polls.sort(reverse=True, key=Poll.get_engagement_score)
        polls += list_only_topic_polls[:min_topic_polls]

    if max_polls > len(polls):
        joined_polls = list_only_topic_polls[min_topic_polls:] + list_only_user_polls[min_user_polls:]
        joined_polls.sort(reverse=True, key=Poll.get_engagement_score)

        polls += joined_polls[:max_polls - len(polls)]

    # loads recommended feed template, displaying polls that match the users topic and user affinity
    return render(request, 'smpa/recommendedfeed.html', {'polls':polls})


def signup(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        try:
            user = User.objects.create_user(username=username, password=password)
        except:
            return render(request, 'smpa/signup.html', {'error_message': 'Invalid username'})
        # try and except used to attempt to create a new user and except catches the error caused by the username being taken
        # in this case, an error message is displayed to the user

        login(request, user)

        userp = UserProfile(user=user,firstname=firstname,lastname=lastname,email=email) # updates UserProfile table with user details
        userp.save()

        return redirect('smpa:home')

    else: 
        return render(request, 'smpa/signup.html')
    

def my_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password) # validates user details against database
        if user is not None: # if the user exists in the database, they are logged in
            login(request, user)
            return redirect('smpa:home')
        else:
            return render(request, 'smpa/login.html', {'error_message': 'Invalid login'})
        # if the user doesn't exist in the database, they have entered invalid login details
    return render(request, 'smpa/login.html')

def my_logout(request):
    logout(request)
    return redirect('smpa:my_login')
# logout button quickly logs user out of database and transfers user from home page to login page

