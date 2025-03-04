from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("watchlist", views.watchlist_view, name="watchlist"),
    path("handle_watchlist<int:id>", views.handle_watchlist, name="handle_watchlist"),
    path("listings/categories", views.categories_page, name="categories"),
    path("listings/<int:id>/comment", views.action_comment, name="comment"),
    path("listings/<int:id>/close", views.close_listing, name="close"),
    path("listings/<int:id>", views.listing_view, name="listing"),
    path("<str:username>", views.user_listings, name="user_listings"), 
    path("listings/categories/<str:category>", views.category_page, name="category_page"),
]
