## django-basic-jwt-auth

Accounts is a Django app to authenticate user using JWT Token on custom users.

#### 1. Install dependencies

```shell script
$ pip install rest_framework
$ pip install rest_framework_simplejwt
$ pip install django-cors-headers
$ install -i https://test.pypi.org/simple/ django-basic-jwt-auth
```

#### 2. Add "accounts" to your INSTALLED_APPS `setting.py` like this:

``` python
INSTALLED_APPS = [
    ...
    'accounts',
    ...
]
```

#### 3. add the following codes to the `settings.py`:

``` python
AUTH_USER_MODEL = 'accounts.User'
...
... 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

#### 4. Run migrations

```shell script
$ python manage.py migrate
```

#### 5. Access the views

```python

from django.contrib import admin
from django.urls import path
from accounts import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('admin/', admin.site.urls),
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

```