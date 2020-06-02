from django.urls import path, include
from rest_framework.routers import DefaultRouter
from user import views

app_name = 'user'

router = DefaultRouter()

urlpatterns = [
    path('signup/', views.CreateUserView.as_view(), name='signup'),
    path('login/', views.CreateTokenView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('userInfo/', views.UserInfoView.as_view(), name='userInfo'),
    path('', include(router.urls)),
]