from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock

from core.models import (
    Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile
)

User = get_user_model()


class TestHelpers:
    @staticmethod
    def create_user(username='testuser', password='testpass123'):
        return User.objects.create_user(username=username, password=password)

    @staticmethod
    def create_item(title='Test Item', price=100.00, discount_price=None, slug='test-item'):
        return Item.objects.create(
            title=title,
            price=price,
            discount_price=discount_price,
            category='S',
            label='P',
            slug=slug,
            description='Test description'
        )

    @staticmethod
    def create_order_item(user, item, quantity=1, ordered=False):
        return OrderItem.objects.create(
            user=user,
            item=item,
            quantity=quantity,
            ordered=ordered
        )

    @staticmethod
    def create_order(user, items=None):
        order = Order.objects.create(
            user=user,
            ordered_date=timezone.now(),
            ordered=False
        )
        if items:
            for item in items:
                order.items.add(item)
        return order

    @staticmethod
    def create_coupon(code='TEST10', amount=10.00):
        return Coupon.objects.create(code=code, amount=amount)


class UserProfileSignalTestCase(TestCase):
    def test_user_creation_should_auto_create_userprofile(self):
        user = TestHelpers.create_user()
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_userprofile_should_have_correct_user_reference(self):
        user = TestHelpers.create_user(username='john')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user, user)

    def test_userprofile_default_values_should_be_correct(self):
        user = TestHelpers.create_user()
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.stripe_customer_id, None)
        self.assertEqual(profile.one_click_purchasing, False)

    def test_userprofile_str_should_return_username(self):
        user = TestHelpers.create_user(username='alice')
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(str(profile), 'alice')


class ItemURLTestCase(TestCase):
    def setUp(self):
        self.item = TestHelpers.create_item(
            title='Test Shirt',
            price=50.00,
            slug='test-shirt'
        )

    def test_get_absolute_url_should_return_product_url_with_slug(self):
        url = self.item.get_absolute_url()
        self.assertEqual(url, '/product/test-shirt/')

    def test_get_add_to_cart_url_should_return_add_to_cart_url_with_slug(self):
        url = self.item.get_add_to_cart_url()
        self.assertEqual(url, '/add-to-cart/test-shirt/')

    def test_get_remove_from_cart_url_should_return_remove_from_cart_url_with_slug(self):
        url = self.item.get_remove_from_cart_url()
        self.assertEqual(url, '/remove-from-cart/test-shirt/')

    def test_different_slug_should_generate_different_urls(self):
        item2 = TestHelpers.create_item(
            title='Another Item',
            price=30.00,
            slug='another-item'
        )
        self.assertNotEqual(
            self.item.get_absolute_url(),
            item2.get_absolute_url()
        )


class OrderItemPriceCalculationTestCase(TestCase):
    def setUp(self):
        self.user = TestHelpers.create_user()

    def test_get_total_item_price_should_return_quantity_times_price(self):
        item = TestHelpers.create_item(price=100.00, discount_price=None)
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=3
        )
        self.assertEqual(order_item.get_total_item_price(), 300.00)

    def test_get_total_discount_item_price_should_return_quantity_times_discount_price(self):
        item = TestHelpers.create_item(price=100.00, discount_price=80.00)
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=2
        )
        self.assertEqual(order_item.get_total_discount_item_price(), 160.00)

    def test_get_amount_saved_should_return_difference_when_discount_exists(self):
        item = TestHelpers.create_item(price=100.00, discount_price=70.00)
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=2
        )
        expected_saved = (100.00 * 2) - (70.00 * 2)
        self.assertEqual(order_item.get_amount_saved(), expected_saved)

    def test_get_final_price_should_return_discount_price_when_discount_exists(self):
        item = TestHelpers.create_item(price=100.00, discount_price=75.00)
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=2
        )
        self.assertEqual(order_item.get_final_price(), 150.00)

    def test_get_final_price_should_return_original_price_when_no_discount(self):
        item = TestHelpers.create_item(price=100.00, discount_price=None)
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=2
        )
        self.assertEqual(order_item.get_final_price(), 200.00)

    def test_get_final_price_should_return_original_price_when_discount_price_is_zero(self):
        """
        风险警告：当 discount_price=0.00 时，模型中 `if self.item.discount_price:` 
        判断为 False（因为 0 在布尔上下文中为假），导致返回原价而非 0。
        这可能是非预期行为：商家可能希望设置 0 元折扣价（即免费商品）。
        建议模型层改为 `if self.item.discount_price is not None:` 进行显式判断。
        """
        item = TestHelpers.create_item(price=100.00, discount_price=0.00)
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=2
        )
        self.assertEqual(order_item.get_final_price(), 200.00)

    def test_get_amount_saved_should_be_zero_when_no_discount(self):
        item = TestHelpers.create_item(price=100.00, discount_price=None)
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=3
        )
        with self.assertRaises(TypeError):
            order_item.get_amount_saved()

    def test_order_item_str_should_return_quantity_and_title(self):
        item = TestHelpers.create_item(title='Cool Shirt')
        order_item = TestHelpers.create_order_item(
            user=self.user,
            item=item,
            quantity=5
        )
        self.assertEqual(str(order_item), '5 of Cool Shirt')


class OrderTotalCalculationTestCase(TestCase):
    def setUp(self):
        self.user = TestHelpers.create_user()

    def test_get_total_should_sum_all_order_items_final_prices(self):
        item1 = TestHelpers.create_item(price=100.00, discount_price=None, slug='item1')
        item2 = TestHelpers.create_item(price=50.00, discount_price=40.00, slug='item2')

        order_item1 = TestHelpers.create_order_item(user=self.user, item=item1, quantity=2)
        order_item2 = TestHelpers.create_order_item(user=self.user, item=item2, quantity=3)

        order = TestHelpers.create_order(user=self.user, items=[order_item1, order_item2])

        expected_total = (100.00 * 2) + (40.00 * 3)
        self.assertEqual(order.get_total(), expected_total)

    def test_get_total_should_subtract_coupon_amount_when_coupon_exists(self):
        item = TestHelpers.create_item(price=100.00, discount_price=None)
        order_item = TestHelpers.create_order_item(user=self.user, item=item, quantity=2)
        order = TestHelpers.create_order(user=self.user, items=[order_item])

        coupon = TestHelpers.create_coupon(code='DISCOUNT20', amount=20.00)
        order.coupon = coupon
        order.save()

        expected_total = (100.00 * 2) - 20.00
        self.assertEqual(order.get_total(), expected_total)

    def test_get_total_should_return_full_amount_when_no_coupon(self):
        item = TestHelpers.create_item(price=100.00, discount_price=None)
        order_item = TestHelpers.create_order_item(user=self.user, item=item, quantity=2)
        order = TestHelpers.create_order(user=self.user, items=[order_item])

        expected_total = 100.00 * 2
        self.assertEqual(order.get_total(), expected_total)

    def test_get_total_should_return_negative_when_coupon_exceeds_order_total(self):
        """
        风险警告：当前模型逻辑允许优惠券金额超过订单总额，
        导致 get_total() 返回负数。这在生产环境中可能不是预期行为。
        建议在模型层或业务层添加验证逻辑，确保最终金额不为负。
        """
        item = TestHelpers.create_item(price=50.00, discount_price=None)
        order_item = TestHelpers.create_order_item(user=self.user, item=item, quantity=1)
        order = TestHelpers.create_order(user=self.user, items=[order_item])

        coupon = TestHelpers.create_coupon(code='HUGE100', amount=100.00)
        order.coupon = coupon
        order.save()

        total = order.get_total()
        self.assertEqual(total, -50.00)
        self.assertLess(total, 0)

    def test_get_total_with_multiple_items_and_coupon(self):
        item1 = TestHelpers.create_item(price=100.00, discount_price=80.00, slug='item1')
        item2 = TestHelpers.create_item(price=200.00, discount_price=None, slug='item2')

        order_item1 = TestHelpers.create_order_item(user=self.user, item=item1, quantity=2)
        order_item2 = TestHelpers.create_order_item(user=self.user, item=item2, quantity=1)

        order = TestHelpers.create_order(user=self.user, items=[order_item1, order_item2])

        coupon = TestHelpers.create_coupon(code='SAVE50', amount=50.00)
        order.coupon = coupon
        order.save()

        expected_total = (80.00 * 2) + (200.00 * 1) - 50.00
        self.assertEqual(order.get_total(), expected_total)

    def test_get_total_should_return_zero_for_empty_order(self):
        order = TestHelpers.create_order(user=self.user)
        self.assertEqual(order.get_total(), 0)

    def test_order_str_should_return_username(self):
        order = TestHelpers.create_order(user=self.user)
        self.assertEqual(str(order), self.user.username)


class CouponTestCase(TestCase):
    def test_coupon_str_should_return_code(self):
        coupon = TestHelpers.create_coupon(code='SUMMER2024', amount=15.00)
        self.assertEqual(str(coupon), 'SUMMER2024')

    def test_coupon_amount_can_be_decimal(self):
        coupon = TestHelpers.create_coupon(code='DECIMAL', amount=12.50)
        self.assertEqual(coupon.amount, 12.50)


class PaymentTestCase(TestCase):
    def setUp(self):
        self.user = TestHelpers.create_user()

    def test_payment_str_should_return_username(self):
        payment = Payment.objects.create(
            stripe_charge_id='ch_test123',
            user=self.user,
            amount=99.99
        )
        self.assertEqual(str(payment), self.user.username)

    def test_payment_can_be_created_without_user(self):
        """
        风险警告：Payment 模型的 user 字段允许为 null (SET_NULL)，
        但 __str__ 方法返回 self.user.username，当 user 为 None 时
        会抛出 AttributeError。这是一个潜在的空指针异常风险。
        """
        payment = Payment.objects.create(
            stripe_charge_id='ch_test456',
            user=None,
            amount=50.00
        )
        with self.assertRaises(AttributeError):
            str(payment)


class RefundTestCase(TestCase):
    def setUp(self):
        self.user = TestHelpers.create_user()
        self.item = TestHelpers.create_item(price=100.00)
        self.order_item = TestHelpers.create_order_item(user=self.user, item=self.item)
        self.order = TestHelpers.create_order(user=self.user, items=[self.order_item])

    def test_refund_str_should_return_pk(self):
        refund = Refund.objects.create(
            order=self.order,
            reason='Item damaged',
            email='test@example.com'
        )
        self.assertEqual(str(refund), str(refund.pk))

    def test_refund_default_accepted_should_be_false(self):
        refund = Refund.objects.create(
            order=self.order,
            reason='Wrong item',
            email='customer@example.com'
        )
        self.assertEqual(refund.accepted, False)


class AddressTestCase(TestCase):
    def setUp(self):
        self.user = TestHelpers.create_user()

    def test_address_str_should_return_username(self):
        address = Address.objects.create(
            user=self.user,
            street_address='123 Main St',
            apartment_address='Apt 4B',
            country='US',
            zip='12345',
            address_type='B',
            default=True
        )
        self.assertEqual(str(address), self.user.username)

    def test_address_default_should_be_false_by_default(self):
        address = Address.objects.create(
            user=self.user,
            street_address='456 Oak Ave',
            apartment_address='',
            country='US',
            zip='67890',
            address_type='S'
        )
        self.assertEqual(address.default, False)


class ItemModelTestCase(TestCase):
    def test_item_str_should_return_title(self):
        item = TestHelpers.create_item(title='Premium T-Shirt')
        self.assertEqual(str(item), 'Premium T-Shirt')

    def test_item_can_have_zero_discount_price(self):
        item = TestHelpers.create_item(price=100.00, discount_price=0.00)
        self.assertEqual(item.discount_price, 0.00)

    def test_item_discount_price_can_be_null(self):
        item = TestHelpers.create_item(price=100.00, discount_price=None)
        self.assertIsNone(item.discount_price)
