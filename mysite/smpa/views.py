from django.db.models import Count
from django.shortcuts import get_list_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import UserProfile, Poll,Topic,Choice,Comment,UserProfile
from django.contrib.auth import logout
from django.urls import reverse
from urllib.parse import urlencode

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
        topic = Topic.objects.get(pk=topic_id)
        choice1 = request.POST['choice1']
        choice2 = request.POST['choice2']
        choice3 = request.POST['choice3']
        choice4 = request.POST['choice4']
        choice5 = request.POST['choice5']

        poll = Poll(question_text=question, topic=topic,author=request.user)

        poll.save()

        choices = [choice1, choice2, choice3, choice4, choice5]
        for choice in choices:
            if choice != None and len(choice.strip()) > 0:
                choice_ = Choice(choice_text = choice, poll = poll)
                choice_.save()

        return redirect('smpa:polldetail', pollid=poll.id)
    return render(request, 'smpa/createpoll.html', {'topics': Topic.objects.all()})
    

@login_required()
def polldetail(request, pollid):
    poll = Poll.objects.get(id=pollid)

    # request.user
    # if the logged user has voted already
    #     get the chocies and figure out the voted choice.
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
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        
        return render(
            request,
            "smpa/detail.html",
            {
                "q": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        question.voters.add(request.user)
        selected_choice.users.add(request.user)
        selected_choice.num_votes += 1
        selected_choice.save()

    return redirect(reverse('smpa:polldetail', args=(pollid,)))


@login_required()
def upvote(request, poll_id):
    poll = Poll.objects.get(id=poll_id)
    if request.user in poll.upvoters.all():
        poll.upvoters.remove(request.user)
    else:
        poll.upvoters.add(request.user)

    try:
        poll.downvoters.remove(request.user)
    except:
        pass

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

    return redirect(request.META['HTTP_REFERER'])

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
    user = get_list_or_404(UserProfile, user__username=username)
    if user:
        user = user[0]
        polls = Poll.objects.filter(author=user.user)
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

    return render(request, 'smpa/home.html', {'topics': topics, 'selected_topic':topic, 'polls':polls})


@login_required()
def home(request):
    
    
    polls = Poll.objects.annotate(upvote_count=Count('upvoters')).order_by('-upvote_count')[:5]
    # poll_list = []
    # for poll in polls:
    #     numupvoters = len(poll.upvoters.all())
    #     poll_list.append((numupvoters, poll))
    # poll_list.sort(key=lambda x:x[0], reverse=True)
    # mostupvoted = [poll_list[i][1] for i in range(5)]

    return render(request, 'smpa/home.html', {'topics': Topic.objects.all(), 'polls':polls})

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
        
        login(request, user)

        userp = UserProfile(user=user,firstname=firstname,lastname=lastname,email=email)
        userp.save()

        return redirect('smpa:home')

    else: 
        return render(request, 'smpa/signup.html')
    

def my_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('smpa:home')
        else:
            return render(request, 'smpa/login.html', {'error_message': 'Invalid login'})
    
    return render(request, 'smpa/login.html')

def my_logout(request):
    logout(request)
    return redirect('smpa:my_login')


