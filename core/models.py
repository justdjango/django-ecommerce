from django.conf import settings
from django.db import models
from django.shortcuts import reverse

# first entry is what goes to the database and second one goes to the website
CATEGORY_CHOICES = (
    ('C', 'Cardio'),
    ('DA', 'Dance'),
    ('M', 'Martial Arts'),
    ('T', 'How To/Tutorial'),
    ('CY', 'Cycling'),
    ('H', 'Hi-Intensity'),
    ('CO', 'Core'),
    ('M', 'Mind and Body'),
    ('ST', 'Sculpting & toning')

)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')

)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.CharField(max_length=4)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(max_length=20)
    slug = models.SlugField()
    description = models.TextField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })
    """
   def get_remove_item_from_cart_url(self):
        return reverse("core:remove-item-from-cart", kwargs={
            'slug': self.slug
        })
    """

# link between items and shopping cart
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"


# Our Shopping cart - here are displayed all the classes that the user has booked
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
