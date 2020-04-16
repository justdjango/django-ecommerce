from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.template import Context

from .CW2.recommend_new_user import new_user_recommendation_new
from .models import Item, Order, OrderItem
from .forms import FeedbackForm, NewUserForm
from django.utils import timezone

from churn import churn


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "product.html", context)


def checkout(request):
    return render(request, "checkout.html")


def recommended_classes(request):
    return render(request, "recommended_classes.html")


def staff(request):
    return render(request, "staff.html")



class FeedbackView(View):
    def get(self, *args, **kwargs):
        # form
        form = FeedbackForm()
        context = {
            'form': form
        }
        return render(self.request, "feedback.html", context)

    def post(self, *args, **kwargs):
        form = FeedbackForm(self.request.POST or None)
        if form.is_valid():
            print("The form is valid")
            class_per_week = form.cleaned_data['Classes_per_week']
            instructor = form.cleaned_data['Happy_with_instructors']
            time = form.cleaned_data['Happy_with_class_duration']
            timetable = form.cleaned_data['Happy_with_class_timings']
            class_size = form.cleaned_data['Happy_with_class_size']
            facilities = form.cleaned_data['Happy_with_facilities']
            price = form.cleaned_data['Happy_with_price']
            dictionary = {'Classes_per_week': class_per_week, 'Happy_with_instructors': instructor, 'Happy_with_class_duration': time, 'Happy_with_class_timings': timetable,
                          'Happy_with_class_size': class_size, 'Happy_with_facilities': facilities, 'Happy_with_price': price}
            # This method is called after the user submit their answers.
            # This method should be the one that does the churn prediction for the current user
            # TODO: fill the method with the churn model. The method is in churn.py
            prediction = churn(dictionary)
            if prediction == 'Yes':
                return redirect("core:discount-page")

        return redirect("/")

class DiscountView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {'object': order}
            return render(self.request, "discounts.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any class booked")
            return redirect("core:discount-page")

class NewUserView(View):
    def get(self, *args, **kwargs):
        # form
        form = NewUserForm()
        context = {
            'form': form
        }
        return render(self.request, "newuser.html", context)

    def post(self, *args, **kwargs):
        form = NewUserForm(self.request.POST)
        if form.is_valid():
            print("The form is valid")
            Lose_weight = form.cleaned_data['Lose_weight']
            Stay_fit = form.cleaned_data['Stay_fit']
            Build_muscle = form.cleaned_data['Build_muscle']
            Stretching = form.cleaned_data['Stretching']
            list = [Lose_weight, Stay_fit, Build_muscle, Stretching]
            # dictionary = {'Lose_weight': Lose_weight, 'Stay_fit': Stay_fit,
            #               'Build_muscle': Build_muscle, 'Stretching': Stretching}
            # This method is called after the user submit their answers.
            # This method should be the one that does the churn prediction for the current user
            # TODO: fill the method with the churn model. The method is in churn.py
            print("We recommend the following classes based on experiences of people with similar tastes to you:")
            recommended_classes = new_user_recommendation_new([0, 0, 0, 0, 0, 0, 0, 0, int(list[0]), int(list[1]), int(list[2]), int(list[3])])
            variables = {
                'recommended': recommended_classes
            }
        return render(self.request, 'recommended_classes.html', variables)
        # return redirect('core:recommended-classes')


class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "home.html"
    ordering = ['title']
    context_object_name = 'classes_list'


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {'object': order}
            return render(self.request, "order_summary.html", context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have any class booked")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    paginate_by = 80
    template_name = "product.html"

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['classes_list'] = Item.objects.all() #filter(category=Item.category).order_by('title')
        return context


@login_required
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
            messages.info(request, "You have already booked this class")
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


@login_required
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


''' 
This method should use RecommendedItem and RecommendedList (created in models.py).
Should return a List of items to recommend to the user.
'''