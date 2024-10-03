from django.urls import path
from authuser import views

urlpatterns = [
    path('register/', views.register_view, name="register"),
    path("login/",views.login_view, name="login"),
    path('logout/',views.logout_view, name='logout'),
    path('forget/',views.forget_pass, name='forget'),
    path('send_pass/<str:reset_id>/',views.PasswordResetSent, name='send_pass'),
    path('reset/<str:reset_id>/',views.reset_pass, name='reset'),

]
