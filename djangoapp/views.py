from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import os
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Current file path
current_dir = os.path.dirname(__file__)

app_name = 'djangoapp'

template_dir = os.path.join(current_dir, 'templates', app_name)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, f'{template_dir}/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, f'{template_dir}/contact.html', context)


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('psw')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            messages.error(request, 'Invalid username or password.')

        return redirect(f'{app_name}:index')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    context = {}
    print("Log out the user `{}`".format(request.user.username))
    if request.method == "GET":
        logout(request)

    return redirect(f'{app_name}:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, os.path.join(template_dir, 'registration.html'), context)
    # If it is a POST request
    elif request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        password = request.POST.get('psw')

        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=password)
            # <HINT> Login the user and
            # redirect to course list page
            return redirect(f"{app_name}:index")
        else:
            return render(request, os.path.join(template_dir, 'registration.html'), context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}

    if request.method == "GET":
        url = f'{env("CLOUDANT_URL")}/dealerships/_all_docs'
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        # dealer_names = ' '.join([dealer.short_name for dealer in dealerships])

        # Return a list of dealer short name
        context["dealership_list"] = dealerships
        return render(request, f'{template_dir}/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}

    if request.method == "GET":
        context["dealer"] = dealer_id

        url = f'{env("CLOUDANT_URL")}/reviews/_find'
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context["reviews"] = reviews

        for review in reviews:
            print(f"Review: {review.review} {review.sentiment}")

        return render(request, f'{template_dir}/dealer_details.html', context)


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
def add_review(request, dealer_id):
    context = {}

    if request.method == "GET":
        url = f'{env("CLOUDANT_URL")}/dealerships/_find'
        dealer = get_dealer_by_id_from_cf(url, dealer_id)

        cars = CarModel.objects.filter(dealerId=dealer_id)

        context["cars"] = cars
        context["dealer"] = dealer

        return render(request, f'{template_dir}/add_review.html', context)
