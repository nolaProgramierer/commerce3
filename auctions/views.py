from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.forms import ModelForm

import decimal


from .models import User, Category, Listing, Comment, Bid


class NewEntryForm(ModelForm):
    class Meta:
        model = Listing
        fields = ["description", "category"]


def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {"listings": listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def create(request):
    if request.method == "POST":
        # Assign request data to form
        form = NewEntryForm(request.POST)
        # If backend valid, assign model attributes to vars
        if form.is_valid():
            description = form.cleaned_data["description"]
            user = request.user
            category = form.cleaned_data["category"]
            # Create new listing with vars
            new_listing = Listing(description=description, user=user, category=category)
            new_listing.save()
            # Redirect to home page
            return HttpResponseRedirect(reverse("index"))
    else:
        form = NewEntryForm()
    return render(request, "auctions/create.html", {"form": form})


def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    on_watchlist = listing in request.user.watchlist.all()
    comments = listing.comments.order_by("-creation_time").all()
    return render(
        request,
        "auctions/listing.html",
        {
            "listing": listing,
            "on_watchlist": on_watchlist,
            "comments": comments,
        },
    )


def watchlist(request):
    listings = request.user.watchlist.order_by("-creation_time").all()
    return render(request, "auctions/index.html", {"listings": listings})


def watchlist_delete(request):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=int(request.POST["listing_id"]))
        request.user.watchlist.remove(listing)
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


def watchlist_add(request):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=int(request.POST["listing_id"]))
        request.user.watchlist.add(listing)
        return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


def bid(request):
    if request.method == "POST":
        bid = decimal.Decimal(request.POST["bid"])
        listing = Listing.objects.get(pk=request.POST["listing_id"])
        starting_bid = listing.starting_bid

        # Is seller the bidder
        if listing.seller is request.user:
            msg = "You can't bid on your own item."
            return render(
                request, "auctions/error.html", {"msg": msg, "listing": listing}
            )

        # check for no bids and if bid is higher than previous bid
        elif bid < listing.starting_bid and listing.bids.count() == 0:
            msg = "Your bid must be higher than the starting bid."
            return render(
                request, "auctions/error.html", {"msg": msg, "listing": listing}
            )
        # check
        elif listing.bids.count() > 0 and bid < listing.price():
            msg = "Your bid must be higher than the current bid."
            return render(
                request, "auctions/error.html", {"msg": msg, "listing": listing}
            )

        new_bid = Bid(amount=bid, listing=listing, bidder=request.user)
        new_bid.save()
    return HttpResponseRedirect(reverse("listing", args=(listing.id,)))


def close(request, listing_id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        if request.user != listing.seller:
            message = "You can only close a listing you created"
            return render(request, "error.html", {"msg": message})
        # Make listing inactive and save
        listing.active = False
        listing.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def comment(request, listing_id):
    if request.method == "POST":
        text = request.POST["comment"]
        listing = Listing.objects.get(pk=listing_id)
        comment = Comment(text=text, commenter=request.user, listing=listing)
        comment.save()
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
