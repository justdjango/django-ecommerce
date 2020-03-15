from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Item, Order, OrderItem
from django.utils import timezone


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "product.html", context)


def checkout(request):
    return render(request, "checkout.html")


class HomeView(ListView):
    model = Item
    template_name = "home.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order is in order
        if order.items.filter(item__slug=item.slug).exists():
            #TODO: change this, user can book just one class
            messages.info(request, "You have already booked this class.")
        else:
            messages.info(request, "You booked this class.")
            order.items.add(order_item)
            return redirect("core:product", slug=slug)
    else:
        order_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=order_date)
        order.items.add(order_item)
        messages.info(request, "You booked this class.")
    return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if order is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "You canceled this booking.")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "You did not book this class.")
            return redirect("core:product", slug=slug)
    else:
        # add a message saying user doesn't have an order
        messages.info(request, "You have no classes booked")
        return redirect("core:product", slug=slug)