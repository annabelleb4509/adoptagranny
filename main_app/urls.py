from django.urls import path
from . import views
	
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('profiles/', views.profiles_index, name='index'),
    path('profiles/<int:profile_id>/', views.profiles_detail, name='detail'),
    #path('profiles/<int:profile_id>/', views.own_profiles_detail, name='own_detail'),
    path('profiles/create/', views.ProfileCreate.as_view(), name='profiles_create'),
    path('profile/<int:pk>/update/', views.ProfileUpdate.as_view(), name='profile_update'),
    path('profile/<int:pk>/delete/', views.ProfileDelete.as_view(), name='profile_delete'),
    path('search/', views.SearchResults.as_view(), name='search_results'),
    path('accounts/signup/', views.signup, name='signup'),
   # path('messages/create/', views.MessageCreate.as_view(), name='messages_create'),
    #path('profiles/<int:profile_id>/send_message/<int:message_id>/', views.send_message, name='send_message'),
    #path('messages/', views.messages_list, name='messages_list'),
    path('profiles/<int:profile_id>/add_message/', views.add_message, name='add_message'),
    path('send_message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('conversation_detail/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('messages_list/', views.MessagesListView.as_view(), name='messages_list'),
    path('meet/', views.UserListsView.as_view(), name='users_list'),
    path('inbox/<str:username>/', views.InboxView.as_view(), name='inbox'),
    path('conversation_index', views.conversation_index, name='conversation_index'),
]
