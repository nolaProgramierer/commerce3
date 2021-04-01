from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing", related_name="watchers")


class Category(models.Model):
    CATEGORY_TYPES = (
        ("FURN", "Furniture"),
        ("COLLLECT", "Collectibles"),
        ("GEN", "General"),
    )
    type = models.CharField(max_length=8, choices=CATEGORY_TYPES, default="GEN.")

    def __str__(self):
        return f"{self.type}"


class Listing(models.Model):
    active = models.BooleanField(default=True)
    description = models.TextField()
    creation_time = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    starting_bid = models.DecimalField(max_digits=12, decimal_places=2)
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="seller_listings"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="category_listings",
    )

    def __str_(self):
        return f"{self.description}"

    def top_bid(self):
        try:
            return max(self.bids.all(), key=lambda b: b.amount)
        except:
            ValueError

    def price(self):
        bid = self.top_bid()
        return bid.amount if bid is not None else self.starting_bid

    def winner(self):
        bid = self.top_bid()
        return bid.bidder


class Bid(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    datetime = models.DateTimeField(auto_now=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.amount} {self.datetime}"


class Comment(models.Model):
    text = models.TextField(blank=True)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="comments"
    )
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text}"
