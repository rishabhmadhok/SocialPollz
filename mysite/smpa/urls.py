from django.urls import path

from . import views

app_name = 'smpa'

urlpatterns = [
    path('', views.home, name='home'),
    path('topics/<int:topic_id>', views.topic_home,name = 'topics' ),
    path('signup',views.signup,name = 'signup'),
    path('login',views.my_login,name = 'my_login'),
    path('logout',views.my_logout,name = 'my_logout'),
    path('createpoll',views.createpoll, name = 'createpoll'),
    path('<int:pollid>/polldetail', views.polldetail, name = 'polldetail'),
    path('<int:pollid>/vote', views.vote, name = 'vote'),
    path('<int:poll_id>/upvote',views.upvote,name = 'upvote'),
    path('<int:poll_id>/downvote',views.downvote,name = 'downvote'),
    path('<int:comment_id>/like',views.like,name = 'like'),
    path('<int:poll_id>/postcomment',views.postcomment,name = 'postcomment'),
    path('profile/<str:username>',views.profilepage,name = 'profilepage'),
    path('<int:user_id>/follow',views.follow,name = 'follow'),
    path('following',views.followingfeed, name = 'followingfeed'),
    path('recommended',views.recommendedfeed,name = 'recommendedfeed')

]