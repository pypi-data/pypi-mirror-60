
from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.CreateAccountView.as_view(),
         name='user-register'),
    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('users/', views.UserListView.as_view(),
         name='user-list'),
    path('users/<uuid:id>/', views.UserDetailView.as_view(),
         name='user-detail'),
    path('me/', views.CurrentUserView.as_view(),
         name='me'),
]
