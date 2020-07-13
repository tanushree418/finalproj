from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),
    path('orders/', views.OrderList.as_view(), name='orderlist'),
    path('orders/<str:ref_code>/detail', views.OrderDetail.as_view(), name='orderdetail'),
    path("signup/", views.handleSignup, name="handleSignup"),
    path("sellerlogin/", views.SellerLogin.as_view(), name="handleLogin"),
    path("logout/", views.handleLogout, name="handleLogout"),
]