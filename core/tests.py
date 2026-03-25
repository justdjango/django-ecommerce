from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# Set required settings for testing
if not hasattr(settings, 'STRIPE_SECRET_KEY'):
    settings.STRIPE_SECRET_KEY = 'test_key'
if not hasattr(settings, 'STRIPE_PUBLIC_KEY'):
    settings.STRIPE_PUBLIC_KEY = 'test_public_key'

from django_countries import countries
from unittest.mock import patch, MagicMock

from .models import (
    Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile,
    CATEGORY_CHOICES, LABEL_CHOICES, ADDRESS_CHOICES
)
from .forms import (
    CheckoutForm, CouponForm, RefundForm, PaymentForm, PAYMENT_CHOICES
)
from .views import create_ref_code, is_valid_form

User = get_user_model()


class ModelTests(TestCase):
    """Test cases for all models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_userprofile_creation_on_user_creation(self):
        """Test that UserProfile is created when User is created"""
        self.assertTrue(hasattr(self.user, 'userprofile'))
        self.assertIsInstance(self.user.userprofile, UserProfile)
        self.assertEqual(self.user.userprofile.user, self.user)

    def test_userprofile_str(self):
        """Test UserProfile __str__ method"""
        self.assertEqual(str(self.user.userprofile), 'testuser')

    def test_item_creation(self):
        """Test Item model creation and methods"""
        item = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            discount_price=80.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )

        # Test __str__
        self.assertEqual(str(item), 'Test Shirt')

        # Test get_absolute_url
        self.assertEqual(
            item.get_absolute_url(),
            reverse('core:product', kwargs={'slug': 'test-shirt'})
        )

        # Test get_add_to_cart_url
        self.assertEqual(
            item.get_add_to_cart_url(),
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )

        # Test get_remove_from_cart_url
        self.assertEqual(
            item.get_remove_from_cart_url(),
            reverse('core:remove-from-cart', kwargs={'slug': 'test-shirt'})
        )

    def test_item_without_discount(self):
        """Test Item without discount price"""
        item = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )
        self.assertIsNone(item.discount_price)

    def test_order_item_creation(self):
        """Test OrderItem model creation and price calculation methods"""
        item = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            discount_price=80.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )

        order_item = OrderItem.objects.create(
            user=self.user,
            item=item,
            quantity=3
        )

        # Test __str__
        self.assertEqual(str(order_item), '3 of Test Shirt')

        # Test price calculation methods
        self.assertEqual(order_item.get_total_item_price(), 300.00)
        self.assertEqual(order_item.get_total_discount_item_price(), 240.00)
        self.assertEqual(order_item.get_amount_saved(), 60.00)
        self.assertEqual(order_item.get_final_price(), 240.00)

    def test_order_item_final_price_without_discount(self):
        """Test OrderItem final price calculation without discount"""
        item = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )

        order_item = OrderItem.objects.create(
            user=self.user,
            item=item,
            quantity=3
        )

        self.assertEqual(order_item.get_final_price(), 300.00)

    def test_order_creation(self):
        """Test Order model creation and get_total method"""
        order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now()
        )

        # Test __str__
        self.assertEqual(str(order), 'testuser')

        # Test empty order total
        self.assertEqual(order.get_total(), 0)

    def test_order_total_with_items(self):
        """Test Order total calculation with items and coupon"""
        order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now()
        )

        item1 = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )

        item2 = Item.objects.create(
            title='Test Pants',
            price=150.00,
            discount_price=120.00,
            category='OW',
            label='S',
            slug='test-pants',
            description='Test description',
            image='test.jpg'
        )

        order_item1 = OrderItem.objects.create(user=self.user, item=item1, quantity=2)
        order_item2 = OrderItem.objects.create(user=self.user, item=item2, quantity=1)

        order.items.add(order_item1, order_item2)

        # Test total without coupon: (2*100) + (1*120) = 320
        self.assertEqual(order.get_total(), 320.00)

        # Add coupon and test again
        coupon = Coupon.objects.create(code='TEST50', amount=50)
        order.coupon = coupon
        order.save()

        self.assertEqual(order.get_total(), 270.00)

    def test_address_creation(self):
        """Test Address model creation"""
        address = Address.objects.create(
            user=self.user,
            street_address='123 Test St',
            apartment_address='Apt 4B',
            country='US',
            zip='12345',
            address_type='B',
            default=True
        )

        self.assertEqual(str(address), 'testuser')

    def test_payment_creation(self):
        """Test Payment model creation"""
        payment = Payment.objects.create(
            stripe_charge_id='ch_test123',
            user=self.user,
            amount=100.00
        )

        self.assertEqual(str(payment), 'testuser')
        self.assertIsNotNone(payment.timestamp)

    def test_coupon_creation(self):
        """Test Coupon model creation"""
        coupon = Coupon.objects.create(code='TEST20', amount=20)
        self.assertEqual(str(coupon), 'TEST20')

    def test_refund_creation(self):
        """Test Refund model creation"""
        order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
            ref_code='test123'
        )

        refund = Refund.objects.create(
            order=order,
            reason='Defective item',
            email='refund@example.com'
        )

        self.assertEqual(str(refund), str(refund.pk))
        self.assertFalse(refund.accepted)


class ViewTests(TestCase):
    """Test cases for all views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.item = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )
        self.coupon = Coupon.objects.create(code='TEST20', amount=20)

    def test_home_view_basic(self):
        """Test HomeView returns 200 response"""
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_item_detail_view(self):
        """Test ItemDetailView returns 200 for existing item"""
        response = self.client.get(
            reverse('core:product', kwargs={'slug': 'test-shirt'})
        )
        self.assertEqual(response.status_code, 200)

    def test_item_detail_view_not_found(self):
        """Test ItemDetailView with non-existent slug returns 404"""
        response = self.client.get(
            reverse('core:product', kwargs={'slug': 'non-existent'})
        )
        self.assertEqual(response.status_code, 404)

    def test_order_summary_view_redirect_without_login(self):
        """Test OrderSummaryView redirects when not logged in"""
        response = self.client.get(reverse('core:order-summary'))
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_order_summary_view_no_active_order(self):
        """Test OrderSummaryView when user has no active order"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('core:order-summary'))
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_order_summary_view_with_active_order_basic(self):
        """Test OrderSummaryView with an active order - basic functionality"""
        self.client.login(username='testuser', password='testpass123')

        # Create an active order
        order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
            ordered=False
        )
        order_item = OrderItem.objects.create(
            user=self.user,
            item=self.item,
            quantity=1
        )
        order.items.add(order_item)

        # Should not raise server error
        response = self.client.get(reverse('core:order-summary'))
        self.assertNotEqual(response.status_code, 500)


class CartFunctionTests(TestCase):
    """Test cases for shopping cart functions"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.item = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )

    def test_add_to_cart_authenticated(self):
        """Test add_to_cart for authenticated user"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )

        # Should redirect
        self.assertEqual(response.status_code, 302)

        # Check that order and order_item were created
        order = Order.objects.get(user=self.user, ordered=False)
        self.assertEqual(order.items.count(), 1)

        order_item = OrderItem.objects.get(user=self.user, item=self.item, ordered=False)
        self.assertEqual(order_item.quantity, 1)

    def test_add_to_cart_increase_quantity(self):
        """Test adding same item again increases quantity"""
        self.client.login(username='testuser', password='testpass123')

        # Add item twice
        self.client.get(
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )
        self.client.get(
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )

        order_item = OrderItem.objects.get(user=self.user, item=self.item, ordered=False)
        self.assertEqual(order_item.quantity, 2)

    def test_remove_from_cart(self):
        """Test remove_from_cart function"""
        self.client.login(username='testuser', password='testpass123')

        # First add the item
        self.client.get(
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )

        # Now remove it
        response = self.client.get(
            reverse('core:remove-from-cart', kwargs={'slug': 'test-shirt'})
        )

        self.assertEqual(response.status_code, 302)

        # Check that order_item was deleted
        with self.assertRaises(ObjectDoesNotExist):
            OrderItem.objects.get(user=self.user, item=self.item, ordered=False)

    def test_remove_from_cart_item_not_in_cart(self):
        """Test remove_from_cart when item is not in cart"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(
            reverse('core:remove-from-cart', kwargs={'slug': 'test-shirt'})
        )

        self.assertEqual(response.status_code, 302)

    def test_remove_single_item_from_cart(self):
        """Test remove_single_item_from_cart function"""
        self.client.login(username='testuser', password='testpass123')

        # Add item twice
        self.client.get(
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )
        self.client.get(
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )

        order_item = OrderItem.objects.get(user=self.user, item=self.item, ordered=False)
        self.assertEqual(order_item.quantity, 2)

        # Remove single item
        response = self.client.get(
            reverse('core:remove-single-item-from-cart', kwargs={'slug': 'test-shirt'})
        )

        self.assertEqual(response.status_code, 302)

        order_item.refresh_from_db()
        self.assertEqual(order_item.quantity, 1)

    def test_remove_single_item_last_item(self):
        """Test remove_single_item_from_cart removes item from order when quantity is 1"""
        self.client.login(username='testuser', password='testpass123')

        # Add item once
        self.client.get(
            reverse('core:add-to-cart', kwargs={'slug': 'test-shirt'})
        )

        # Verify order has the item
        order = Order.objects.get(user=self.user, ordered=False)
        self.assertEqual(order.items.count(), 1)

        # Remove single item (quantity is 1, so it should be removed from order)
        self.client.get(
            reverse('core:remove-single-item-from-cart', kwargs={'slug': 'test-shirt'})
        )

        # Refresh from DB and verify it's removed from order
        order.refresh_from_db()
        self.assertEqual(order.items.count(), 0)


class FormTests(TestCase):
    """Test cases for all forms"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_checkout_form_valid(self):
        """Test CheckoutForm with valid data"""
        form_data = {
            'shipping_address': '123 Test St',
            'shipping_address2': 'Apt 4B',
            'shipping_country': 'US',
            'shipping_zip': '12345',
            'billing_address': '456 Billing St',
            'billing_address2': 'Apt 1A',
            'billing_country': 'US',
            'billing_zip': '67890',
            'same_billing_address': False,
            'set_default_shipping': True,
            'use_default_shipping': False,
            'set_default_billing': False,
            'use_default_billing': False,
            'payment_option': 'S'
        }
        form = CheckoutForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_checkout_form_empty(self):
        """Test CheckoutForm with empty data - payment_option is required"""
        form = CheckoutForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('payment_option', form.errors)

    def test_coupon_form_valid(self):
        """Test CouponForm with valid data"""
        form_data = {'code': 'TESTCODE'}
        form = CouponForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_coupon_form_empty(self):
        """Test CouponForm with empty data"""
        form = CouponForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

    def test_refund_form_valid(self):
        """Test RefundForm with valid data"""
        form_data = {
            'ref_code': 'TEST123',
            'message': 'Item was defective',
            'email': 'test@example.com'
        }
        form = RefundForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_refund_form_invalid_email(self):
        """Test RefundForm with invalid email"""
        form_data = {
            'ref_code': 'TEST123',
            'message': 'Item was defective',
            'email': 'invalid-email'
        }
        form = RefundForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_payment_form_valid(self):
        """Test PaymentForm with valid data"""
        form_data = {
            'stripeToken': 'tok_test123',
            'save': True,
            'use_default': False
        }
        form = PaymentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_payment_form_empty(self):
        """Test PaymentForm with empty data - stripeToken is optional"""
        form = PaymentForm(data={})
        self.assertTrue(form.is_valid())


class UtilityFunctionTests(TestCase):
    """Test cases for utility functions"""

    def test_create_ref_code(self):
        """Test create_ref_code generates valid ref codes"""
        ref_code1 = create_ref_code()
        ref_code2 = create_ref_code()

        # Test length
        self.assertEqual(len(ref_code1), 20)

        # Test uniqueness
        self.assertNotEqual(ref_code1, ref_code2)

        # Test only lowercase letters and digits
        import re
        pattern = r'^[a-z0-9]+$'
        self.assertTrue(re.match(pattern, ref_code1))

    def test_is_valid_form_with_valid_values(self):
        """Test is_valid_form with all non-empty values"""
        values = ['value1', 'value2', 'value3']
        self.assertTrue(is_valid_form(values))

    def test_is_valid_form_with_empty_values(self):
        """Test is_valid_form with empty values"""
        values = ['value1', '', 'value3']
        self.assertFalse(is_valid_form(values))

    def test_is_valid_form_with_all_empty(self):
        """Test is_valid_form with all empty values"""
        values = ['', '', '']
        self.assertFalse(is_valid_form(values))

    def test_is_valid_form_empty_list(self):
        """Test is_valid_form with empty list"""
        values = []
        self.assertTrue(is_valid_form(values))


class CheckoutViewTests(TestCase):
    """Test cases for CheckoutView"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.item = Item.objects.create(
            title='Test Shirt',
            price=100.00,
            category='S',
            label='P',
            slug='test-shirt',
            description='Test description',
            image='test.jpg'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_checkout_get_without_order(self):
        """Test CheckoutView GET without active order - should handle gracefully"""
        response = self.client.get(reverse('core:checkout'))
        self.assertNotEqual(response.status_code, 500)

    def test_checkout_get_with_order(self):
        """Test CheckoutView GET with active order"""
        order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
            ordered=False
        )
        order_item = OrderItem.objects.create(
            user=self.user,
            item=self.item
        )
        order.items.add(order_item)

        response = self.client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout_post_basic(self):
        """Test CheckoutView POST with basic data"""
        order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
            ordered=False
        )
        order_item = OrderItem.objects.create(
            user=self.user,
            item=self.item
        )
        order.items.add(order_item)

        # Basic form submission with payment option
        form_data = {
            'payment_option': 'S'
        }

        response = self.client.post(reverse('core:checkout'), data=form_data)
        # Should handle gracefully (not 500 error)
        self.assertNotEqual(response.status_code, 500)


class AddCouponViewTests(TestCase):
    """Test cases for AddCouponView"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.coupon = Coupon.objects.create(code='TEST20', amount=20)
        self.client.login(username='testuser', password='testpass123')

    def test_add_coupon_view_basic(self):
        """Test AddCouponView handles POST gracefully"""
        Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
            ordered=False
        )

        form_data = {'code': 'TEST20'}
        response = self.client.post(reverse('core:add-coupon'), data=form_data)

        # Should redirect (any redirect is fine, as long as no 500 error)
        self.assertEqual(response.status_code, 302)

    def test_add_coupon_post_no_order(self):
        """Test AddCouponView without active order"""
        form_data = {'code': 'TEST20'}
        response = self.client.post(reverse('core:add-coupon'), data=form_data)

        self.assertEqual(response.status_code, 302)


class RequestRefundViewTests(TestCase):
    """Test cases for RequestRefundView"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.order = Order.objects.create(
            user=self.user,
            ordered_date=timezone.now(),
            ordered=True,
            ref_code='TESTREF123'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_request_refund_get(self):
        """Test RequestRefundView GET returns 200"""
        response = self.client.get(reverse('core:request-refund'))
        self.assertEqual(response.status_code, 200)

    def test_request_refund_post_basic(self):
        """Test RequestRefundView POST with valid data"""
        form_data = {
            'ref_code': 'TESTREF123',
            'message': 'Item was defective',
            'email': 'test@example.com'
        }
        response = self.client.post(reverse('core:request-refund'), data=form_data)

        # Should redirect
        self.assertEqual(response.status_code, 302)
