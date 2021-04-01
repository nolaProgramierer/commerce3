from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:listing_id>/listing", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path(
        "watchlist/delete",
        views.watchlist_delete,
        name="watchlist_delete",
    ),
    path("watchlist/add", views.watchlist_add, name="watchlist_add"),
    path("bid", views.bid, name="bid"),
    path("listing/<int:listing_id>/close", views.close, name="close"),
    path("listing/<int:listing_id>/comment", views.comment, name="comment"),
]
