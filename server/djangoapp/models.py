from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self):
        print(f'CarMake: {self.name}, {self.description}')
        return self.name


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
SEDAN = 'Sedan'
SUV = 'SUV'
WAGON = 'Wagon'
ETC = 'Etc'
TYPE_CHOICES = [
    (SEDAN, 'Sedan'),
    (SUV, 'SUV'),
    (WAGON, 'Wagon'),
    (ETC, 'Etc'),
]


class CarModel(models.Model):
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    dealerId = models.TextField()
    type = models.CharField(
        max_length=5,
        choices=TYPE_CHOICES,
        default=SEDAN,
    )
    year = models.DateField()

    def __str__(self):
        print(f'CarModel: {self.make}, {self.name}, {self.type}, {self.year}')


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name


# <HINT> Create a plain Python class `DealerReview` to hold review data

SENTIMENT_DICT = {
    'positive': 'Positive',
    'neutral': 'Neutral',
    'negative': 'Negative'
}


class DealerReview:

    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, sentiment, id):
        self.id = id
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        # one of positive, neutral, or negative
        if sentiment in SENTIMENT_DICT:
            self.sentiment = SENTIMENT_DICT[sentiment]
        else:
            self.sentiment = SENTIMENT_DICT['neutral']

    def __str__(self):
        return "Review: " + self.review
