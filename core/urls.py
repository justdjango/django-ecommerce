from django.urls import path
from .views import (
    ItemDetailView,
    CategoryAll,
    CategoryFU,
    CategoryVE,
    CategoryOD,
    CategoryBP,
    CategoryCL,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    SearchResult,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('search/', SearchResult.as_view(), name='search'),
    path('all/', CategoryAll.as_view(), name='all'),
    path('FU/', CategoryFU.as_view(), name='FU'),
    path('VE/', CategoryVE.as_view(), name='VE'),
    path('OD/', CategoryOD.as_view(), name='OD'),
    path('BP/', CategoryBP.as_view(), name='BP'),
    path('CL/', CategoryCL.as_view(), name='CL'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund')
]
