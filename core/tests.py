"""
Django E-commerce Project Tests
Generated for production-ready testing coverage
"""
import os
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from core.models import (
    UserProfile,
    Item,
    OrderItem,
    Order,
    Address,
    Payment,
    Coupon,
    Refund
)

User = get_user_model()


def create_test_image():
    image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x4c\x01\x00\x3b'
    return SimpleUploadedFile(
        name='test_image.jpg',
        content=image_content,
        content_type='image/jpeg'
    )


class TestHelperMixin:
    def create_user(self, username='testuser', password='testpass123'):
        return User.objects.create_user(
            username=username,
            password=password
        )

    def create_item(self, title='Test Item', price=100.00, discount_price=None, slug='test-item'):
        image = create_test_image()
        return Item.objects.create(
            title=title,
            price=price,
            discount_price=discount_price,
            category='S',
            label='P',
            slug=slug,
            description='Test description',
            image=image
        )

    def create_order_item(self, user, item, quantity=1, ordered=False):
        return OrderItem.objects.create(
            user=user,
            item=item,
            quantity=quantity,
            ordered=ordered
        )

    def create_order(self, user, items=None, coupon=None):
        order = Order.objects.create(
            user=user,
            ordered_date=timezone.now(),
            ordered=False
        )
        if items:
            for item in items:
                order.items.add(item)
        if coupon:
            order.coupon = coupon
            order.save()
        return order

    def create_coupon(self, code='TESTCODE', amount=10.00):
        return Coupon.objects.create(
            code=code,
            amount=amount
        )

    def create_address(self, user, address_type='S', default=False):
        return Address.objects.create(
            user=user,
            street_address='123 Test Street',
            apartment_address='Apt 1',
            country='US',
            zip='12345',
            address_type=address_type,
            default=default
        )

    def create_payment(self, user, amount=100.00, stripe_charge_id='ch_test123'):
        return Payment.objects.create(
            stripe_charge_id=stripe_charge_id,
            user=user,
            amount=amount
        )


class UserProfileSignalTestCase(TestCase, TestHelperMixin):
    def test_user_creation_should_automatically_create_userprofile(self):
        user = self.create_user()
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)

    def test_userprofile_should_have_correct_user_reference(self):
        user = self.create_user(username='uniqueuser')
        userprofile = UserProfile.objects.get(user=user)
        self.assertEqual(userprofile.user, user)

    def test_userprofile_should_have_default_values(self):
        user = self.create_user()
        userprofile = UserProfile.objects.get(user=user)
        self.assertEqual(userprofile.stripe_customer_id, None)
        self.assertFalse(userprofile.one_click_purchasing)

    def test_userprofile_str_should_return_username(self):
        user = self.create_user(username='strtestuser')
        userprofile = UserProfile.objects.get(user=user)
        self.assertEqual(str(userprofile), 'strtestuser')


class OrderItemPriceCalculationTestCase(TestCase, TestHelperMixin):
    def test_get_total_item_price_should_return_correct_value(self):
        user = self.create_user()
        item = self.create_item(price=100.00)
        order_item = self.create_order_item(user=user, item=item, quantity=3)
        self.assertEqual(order_item.get_total_item_price(), 300.00)

    def test_get_total_item_price_with_quantity_one_should_return_item_price(self):
        user = self.create_user()
        item = self.create_item(price=50.00)
        order_item = self.create_order_item(user=user, item=item, quantity=1)
        self.assertEqual(order_item.get_total_item_price(), 50.00)

    def test_get_total_discount_item_price_should_return_correct_value(self):
        user = self.create_user()
        item = self.create_item(price=100.00, discount_price=80.00)
        order_item = self.create_order_item(user=user, item=item, quantity=2)
        self.assertEqual(order_item.get_total_discount_item_price(), 160.00)

    def test_get_amount_saved_should_return_correct_savings(self):
        user = self.create_user()
        item = self.create_item(price=100.00, discount_price=75.00)
        order_item = self.create_order_item(user=user, item=item, quantity=2)
        self.assertEqual(order_item.get_amount_saved(), 50.00)

    def test_get_final_price_without_discount_should_return_total_item_price(self):
        user = self.create_user()
        item = self.create_item(price=100.00, discount_price=None)
        order_item = self.create_order_item(user=user, item=item, quantity=3)
        self.assertEqual(order_item.get_final_price(), 300.00)

    def test_get_final_price_with_discount_should_return_discounted_price(self):
        user = self.create_user()
        item = self.create_item(price=100.00, discount_price=70.00)
        order_item = self.create_order_item(user=user, item=item, quantity=2)
        self.assertEqual(order_item.get_final_price(), 140.00)

    def test_get_final_price_with_zero_discount_should_return_original_price_due_to_falsy_check(self):
        user = self.create_user()
        item = self.create_item(price=100.00, discount_price=0.00)
        order_item = self.create_order_item(user=user, item=item, quantity=2)
        self.assertEqual(order_item.get_final_price(), 200.00)

    def test_get_amount_saved_with_no_discount_should_raise_error(self):
        user = self.create_user()
        item = self.create_item(price=100.00, discount_price=None)
        order_item = self.create_order_item(user=user, item=item, quantity=2)
        with self.assertRaises(TypeError):
            order_item.get_amount_saved()


class OrderTotalCalculationTestCase(TestCase, TestHelperMixin):
    def test_get_total_without_coupon_should_return_sum_of_final_prices(self):
        user = self.create_user()
        item1 = self.create_item(title='Item 1', price=100.00, slug='item-1')
        item2 = self.create_item(title='Item 2', price=50.00, slug='item-2')
        order_item1 = self.create_order_item(user=user, item=item1, quantity=2)
        order_item2 = self.create_order_item(user=user, item=item2, quantity=1)
        order = self.create_order(user=user, items=[order_item1, order_item2])
        self.assertEqual(order.get_total(), 250.00)

    def test_get_total_with_coupon_should_apply_discount(self):
        user = self.create_user()
        item = self.create_item(price=100.00, slug='test-item')
        order_item = self.create_order_item(user=user, item=item, quantity=2)
        coupon = self.create_coupon(code='DISCOUNT10', amount=15.00)
        order = self.create_order(user=user, items=[order_item], coupon=coupon)
        self.assertEqual(order.get_total(), 185.00)

    def test_get_total_with_discounted_items_and_coupon_should_apply_both(self):
        user = self.create_user()
        item = self.create_item(price=100.00, discount_price=80.00, slug='discount-item')
        order_item = self.create_order_item(user=user, item=item, quantity=2)
        coupon = self.create_coupon(code='SAVE20', amount=20.00)
        order = self.create_order(user=user, items=[order_item], coupon=coupon)
        self.assertEqual(order.get_total(), 140.00)

    def test_get_total_with_empty_items_should_return_zero(self):
        user = self.create_user()
        order = self.create_order(user=user, items=[])
        self.assertEqual(order.get_total(), 0)

    def test_get_total_with_coupon_exceeding_order_total_should_return_negative(self):
        user = self.create_user()
        item = self.create_item(price=50.00, slug='cheap-item')
        order_item = self.create_order_item(user=user, item=item, quantity=1)
        coupon = self.create_coupon(code='HUGEDISCOUNT', amount=100.00)
        order = self.create_order(user=user, items=[order_item], coupon=coupon)
        result = order.get_total()
        self.assertEqual(result, -50.00)
        self.assertLess(result, 0)

    def test_get_total_with_coupon_equal_to_order_total_should_return_zero(self):
        user = self.create_user()
        item = self.create_item(price=100.00, slug='exact-item')
        order_item = self.create_order_item(user=user, item=item, quantity=1)
        coupon = self.create_coupon(code='FREEITEM', amount=100.00)
        order = self.create_order(user=user, items=[order_item], coupon=coupon)
        self.assertEqual(order.get_total(), 0.00)

    def test_get_total_without_coupon_attribute_should_not_apply_discount(self):
        user = self.create_user()
        item = self.create_item(price=100.00, slug='no-coupon-item')
        order_item = self.create_order_item(user=user, item=item, quantity=1)
        order = self.create_order(user=user, items=[order_item])
        order.coupon = None
        order.save()
        self.assertEqual(order.get_total(), 100.00)


class ItemURLMethodsTestCase(TestCase, TestHelperMixin):
    def test_get_absolute_url_should_return_correct_product_url(self):
        item = self.create_item(slug='test-product')
        expected_url = reverse('core:product', kwargs={'slug': 'test-product'})
        self.assertEqual(item.get_absolute_url(), expected_url)
        self.assertEqual(item.get_absolute_url(), '/product/test-product/')

    def test_get_add_to_cart_url_should_return_correct_url(self):
        item = self.create_item(slug='add-cart-item')
        expected_url = reverse('core:add-to-cart', kwargs={'slug': 'add-cart-item'})
        self.assertEqual(item.get_add_to_cart_url(), expected_url)
        self.assertEqual(item.get_add_to_cart_url(), '/add-to-cart/add-cart-item/')

    def test_get_remove_from_cart_url_should_return_correct_url(self):
        item = self.create_item(slug='remove-cart-item')
        expected_url = reverse('core:remove-from-cart', kwargs={'slug': 'remove-cart-item'})
        self.assertEqual(item.get_remove_from_cart_url(), expected_url)
        self.assertEqual(item.get_remove_from_cart_url(), '/remove-from-cart/remove-cart-item/')

    def test_all_url_methods_should_use_item_slug(self):
        item = self.create_item(slug='unique-slug-123')
        self.assertIn('unique-slug-123', item.get_absolute_url())
        self.assertIn('unique-slug-123', item.get_add_to_cart_url())
        self.assertIn('unique-slug-123', item.get_remove_from_cart_url())


class ItemModelTestCase(TestCase, TestHelperMixin):
    def test_item_str_should_return_title(self):
        item = self.create_item(title='Special Item')
        self.assertEqual(str(item), 'Special Item')

    def test_item_with_discount_price_should_have_both_prices(self):
        item = self.create_item(price=200.00, discount_price=150.00)
        self.assertEqual(item.price, 200.00)
        self.assertEqual(item.discount_price, 150.00)

    def test_item_without_discount_price_should_have_null_discount(self):
        item = self.create_item(price=100.00, discount_price=None)
        self.assertIsNone(item.discount_price)


class OrderModelTestCase(TestCase, TestHelperMixin):
    def test_order_str_should_return_username(self):
        user = self.create_user(username='orderuser')
        order = self.create_order(user=user)
        self.assertEqual(str(order), 'orderuser')

    def test_order_should_have_correct_default_values(self):
        user = self.create_user()
        order = self.create_order(user=user)
        self.assertFalse(order.ordered)
        self.assertFalse(order.being_delivered)
        self.assertFalse(order.received)
        self.assertFalse(order.refund_requested)
        self.assertFalse(order.refund_granted)

    def test_order_should_allow_multiple_items(self):
        user = self.create_user()
        item1 = self.create_item(title='Item 1', slug='item-1')
        item2 = self.create_item(title='Item 2', slug='item-2')
        item3 = self.create_item(title='Item 3', slug='item-3')
        order_item1 = self.create_order_item(user=user, item=item1)
        order_item2 = self.create_order_item(user=user, item=item2)
        order_item3 = self.create_order_item(user=user, item=item3)
        order = self.create_order(user=user, items=[order_item1, order_item2, order_item3])
        self.assertEqual(order.items.count(), 3)


class CouponModelTestCase(TestCase, TestHelperMixin):
    def test_coupon_str_should_return_code(self):
        coupon = self.create_coupon(code='SUMMER2024', amount=25.00)
        self.assertEqual(str(coupon), 'SUMMER2024')

    def test_coupon_amount_should_be_positive(self):
        coupon = self.create_coupon(code='POSITIVE', amount=50.00)
        self.assertGreater(coupon.amount, 0)

    def test_coupon_with_zero_amount_should_be_valid(self):
        coupon = self.create_coupon(code='ZERO', amount=0.00)
        self.assertEqual(coupon.amount, 0.00)


class AddressModelTestCase(TestCase, TestHelperMixin):
    def test_address_str_should_return_username(self):
        user = self.create_user(username='addressuser')
        address = self.create_address(user=user)
        self.assertEqual(str(address), 'addressuser')

    def test_address_should_have_correct_address_type_choices(self):
        user = self.create_user()
        shipping_address = self.create_address(user=user, address_type='S')
        billing_address = self.create_address(user=user, address_type='B')
        self.assertEqual(shipping_address.address_type, 'S')
        self.assertEqual(billing_address.address_type, 'B')

    def test_address_default_should_be_false(self):
        user = self.create_user()
        address = self.create_address(user=user)
        self.assertFalse(address.default)


class PaymentModelTestCase(TestCase, TestHelperMixin):
    def test_payment_str_should_return_username(self):
        user = self.create_user(username='paymentuser')
        payment = self.create_payment(user=user)
        self.assertEqual(str(payment), 'paymentuser')

    def test_payment_should_have_correct_attributes(self):
        user = self.create_user()
        payment = self.create_payment(user=user, amount=99.99, stripe_charge_id='ch_abc123')
        self.assertEqual(payment.stripe_charge_id, 'ch_abc123')
        self.assertEqual(payment.amount, 99.99)
        self.assertEqual(payment.user, user)


class RefundModelTestCase(TestCase, TestHelperMixin):
    def test_refund_str_should_return_pk(self):
        user = self.create_user()
        item = self.create_item()
        order_item = self.create_order_item(user=user, item=item)
        order = self.create_order(user=user, items=[order_item])
        refund = Refund.objects.create(
            order=order,
            reason='Product damaged',
            accepted=False,
            email='test@example.com'
        )
        self.assertEqual(str(refund), str(refund.pk))

    def test_refund_should_have_correct_default_values(self):
        user = self.create_user()
        item = self.create_item()
        order_item = self.create_order_item(user=user, item=item)
        order = self.create_order(user=user, items=[order_item])
        refund = Refund.objects.create(
            order=order,
            reason='Test reason',
            email='test@example.com'
        )
        self.assertFalse(refund.accepted)


class OrderItemModelTestCase(TestCase, TestHelperMixin):
    def test_order_item_str_should_return_quantity_and_title(self):
        user = self.create_user()
        item = self.create_item(title='Test Product')
        order_item = self.create_order_item(user=user, item=item, quantity=5)
        self.assertEqual(str(order_item), '5 of Test Product')

    def test_order_item_should_have_correct_default_quantity(self):
        user = self.create_user()
        item = self.create_item()
        order_item = OrderItem.objects.create(user=user, item=item)
        self.assertEqual(order_item.quantity, 1)

    def test_order_item_should_have_correct_default_ordered_status(self):
        user = self.create_user()
        item = self.create_item()
        order_item = self.create_order_item(user=user, item=item)
        self.assertFalse(order_item.ordered)


class EdgeCasesTestCase(TestCase, TestHelperMixin):
    def test_order_item_with_large_quantity_should_calculate_correctly(self):
        user = self.create_user()
        item = self.create_item(price=10.00)
        order_item = self.create_order_item(user=user, item=item, quantity=1000)
        self.assertEqual(order_item.get_total_item_price(), 10000.00)

    def test_order_item_with_decimal_price_should_handle_precision(self):
        user = self.create_user()
        item = self.create_item(price=99.99, discount_price=79.99)
        order_item = self.create_order_item(user=user, item=item, quantity=3)
        self.assertAlmostEqual(order_item.get_total_item_price(), 299.97, places=2)
        self.assertAlmostEqual(order_item.get_total_discount_item_price(), 239.97, places=2)
        self.assertAlmostEqual(order_item.get_amount_saved(), 60.00, places=2)

    def test_multiple_orders_for_same_user_should_be_independent(self):
        user = self.create_user()
        item1 = self.create_item(title='Item 1', price=100.00, slug='item-1')
        item2 = self.create_item(title='Item 2', price=200.00, slug='item-2')
        order_item1 = self.create_order_item(user=user, item=item1, quantity=1)
        order_item2 = self.create_order_item(user=user, item=item2, quantity=2)
        order1 = self.create_order(user=user, items=[order_item1])
        order2 = self.create_order(user=user, items=[order_item2])
        self.assertEqual(order1.get_total(), 100.00)
        self.assertEqual(order2.get_total(), 400.00)

    def test_user_can_have_multiple_addresses(self):
        user = self.create_user()
        address1 = self.create_address(user=user, address_type='S')
        address2 = self.create_address(user=user, address_type='B')
        self.assertEqual(Address.objects.filter(user=user).count(), 2)

    def test_order_with_payment_should_link_correctly(self):
        user = self.create_user()
        item = self.create_item(price=100.00)
        order_item = self.create_order_item(user=user, item=item)
        order = self.create_order(user=user, items=[order_item])
        payment = self.create_payment(user=user, amount=100.00)
        order.payment = payment
        order.save()
        self.assertEqual(order.payment, payment)
        self.assertEqual(order.payment.amount, 100.00)

    def test_order_with_addresses_should_link_correctly(self):
        user = self.create_user()
        item = self.create_item()
        order_item = self.create_order_item(user=user, item=item)
        shipping = self.create_address(user=user, address_type='S')
        billing = self.create_address(user=user, address_type='B')
        order = self.create_order(user=user, items=[order_item])
        order.shipping_address = shipping
        order.billing_address = billing
        order.save()
        self.assertEqual(order.shipping_address, shipping)
        self.assertEqual(order.billing_address, billing)
