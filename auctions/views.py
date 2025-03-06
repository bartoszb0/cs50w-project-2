from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Bid, Comment, CATEGORY_CHOICES
from .forms import AuctionForm, BidForm, CommentForm


def index(request):
    all_auctions = Auction.objects.filter(is_open=True).order_by("-created_on")
    return render(request, "auctions/index.html", {
        "auctions": all_auctions,
        "heading": "Active Listings"
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if request.method == "POST":
        creator = User.objects.get(username=request.user.username)
        form = AuctionForm(request.POST)
        if form.is_valid():
            new_auction = Auction(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                highest_bid=form.cleaned_data["highest_bid"],
                image=form.cleaned_data["image"],
                category=form.cleaned_data["category"],
                listed_by=creator,
                starting_price=form.cleaned_data["highest_bid"],
            )
            new_auction.save()
            messages.success(request, "Listing created")
            return HttpResponseRedirect(reverse("listing", args=[new_auction.id]))
        else:
            return render(request, "auctions/create.html", {
                "form": form
            })
    return render(request, "auctions/create.html", {
        "form": AuctionForm()
    })


def listing_view(request, id):
    auction = Auction.objects.get(id=id)

    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["bid"] <= auction.highest_bid:
                messages.error(request, "Bid must be bigger than the current price")
                return HttpResponseRedirect(reverse("listing", args=[id]))
            else:
                new_bid = Bid(
                    bid = form.cleaned_data["bid"],
                    bid_author = User.objects.get(username=request.user.username),
                    bid_on = auction
                )
                new_bid.save()

                messages.success(request, "Succesfully placed a bid")
                return HttpResponseRedirect(reverse("listing", args=[id]))
        else:
            messages.error(request, "Invalid bid input")
            return HttpResponseRedirect(reverse("listing", args=[id]))
    else:
        return render(request, "auctions/listing.html", {
            "auction": auction,
            "form": BidForm(),
            "highest_bid": Bid.objects.filter(bid_on=auction).order_by("-bid").first(),
            "comments": Comment.objects.filter(comment_on=auction).order_by("-id"),
            "comment_form": CommentForm(),
            "on_watchlist": Auction.objects.filter(id=auction.id, watchlist=User.objects.filter(username=request.user.username).first()),
            "is_creator": Auction.objects.filter(id=auction.id, listed_by=User.objects.filter(username=request.user.username).first()),
        })

def user_listings(request, username):
    user = User.objects.get(username=username)
    auctions = Auction.objects.filter(listed_by=user).order_by("-created_on")
    return render(request, "auctions/user.html", {
        "auctions": auctions,
        "username": username
    })

def categories_page(request):
    categories = []
    for category in CATEGORY_CHOICES:
        categories.append(category[0])
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_page(request, category):
    auctions = Auction.objects.filter(category=category, is_open=True).order_by("-created_on")
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "heading": "Active Listings"
    })

def action_comment(request, id):
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            auction = Auction.objects.get(id=id)
            user = User.objects.get(username=request.user.username)
            comment = form.cleaned_data["comment"]
            Comment(comment=comment, author=user, comment_on=auction).save()
            messages.success(request, "Succesfully commented")
        else:
            messages.error(request, "Invalid comment")
    return HttpResponseRedirect(reverse("listing", args=[id]))
        
@login_required
def watchlist_view(request):
    auctions = Auction.objects.filter(watchlist=User.objects.get(username=request.user.username))
    return render(request, "auctions/index.html", {
        "auctions": auctions,
        "heading": "Watchlist",
    })


@login_required
def handle_watchlist(request, id):
    if request.method == "POST":
        auction = Auction.objects.get(id=id)
        user = User.objects.get(username=request.user.username)
        if Auction.objects.filter(id=id, watchlist=user).exists():
            auction.watchlist.remove(user)
            auction.save()
            messages.info(request, "Auction removed from Watchlist")
        else:
            auction.watchlist.add(user)
            auction.save()
            messages.success(request, "Auction added to Watchlist")
    return HttpResponseRedirect(reverse("listing", args=[id]))


@login_required
def close_listing(request, id):
    if request.method == "POST":
        close_auction = Auction.objects.get(id=id)
        close_auction.is_open = False
        close_auction.save()
        messages.info(request, "Auction closed")
    return HttpResponseRedirect(reverse("listing", args=[id]))