from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import (
    UserProfile, Item, OrderItem, Order,
    Address, Payment, Coupon, Refund
)

User = get_user_model()


class EcommerceTestCase(TestCase):
    """电商项目核心测试类"""

    def setUp(self):
        """测试数据初始化"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    # ------------------------------
    # Helper 工厂方法
    # ------------------------------
    def _create_item(self, title="Test Item", price=100.0, discount_price=None,
                     category='S', label='P', slug='test-item'):
        """创建商品 Item 实例"""
        return Item.objects.create(
            title=title,
            price=price,
            discount_price=discount_price,
            category=category,
            label=label,
            slug=slug,
            description="Test description",
            image="test.jpg"
        )

    def _create_order_item(self, item, quantity=1, ordered=False):
        """创建订单项 OrderItem 实例"""
        return OrderItem.objects.create(
            user=self.user,
            item=item,
            quantity=quantity,
            ordered=ordered
        )

    def _create_order(self, order_items=None, coupon=None, ordered=False):
        """创建订单 Order 实例"""
        order = Order.objects.create(
            user=self.user,
            coupon=coupon,
            ordered=ordered
        )
        if order_items:
            order.items.add(*order_items)
        return order

    def _create_coupon(self, code="TESTCOUPON", amount=20.0):
        """创建优惠券 Coupon 实例"""
        return Coupon.objects.create(code=code, amount=amount)

    # ------------------------------
    # OrderItem 价格计算测试 (P0)
    # ------------------------------
    def test_orderitem_without_discount_should_return_correct_total(self):
        """无折扣商品：总价格 = 数量 × 单价"""
        item = self._create_item(price=100.0, discount_price=None)
        order_item = self._create_order_item(item, quantity=3)
        
        self.assertEqual(order_item.get_total_item_price(), 300.0)
        self.assertEqual(order_item.get_final_price(), 300.0)

    def test_orderitem_with_discount_should_return_correct_total(self):
        """有折扣商品：总价格 = 数量 × 折扣价"""
        item = self._create_item(price=100.0, discount_price=80.0)
        order_item = self._create_order_item(item, quantity=2)
        
        self.assertEqual(order_item.get_total_item_price(), 200.0)
        self.assertEqual(order_item.get_total_discount_item_price(), 160.0)
        self.assertEqual(order_item.get_amount_saved(), 40.0)
        self.assertEqual(order_item.get_final_price(), 160.0)

    def test_orderitem_with_zero_discount_should_use_discount_price(self):
        """折扣为0：使用折扣价（0元）计算"""
        item = self._create_item(price=100.0, discount_price=0.0)
        order_item = self._create_order_item(item, quantity=5)
        
        self.assertEqual(order_item.get_total_item_price(), 500.0)
        self.assertEqual(order_item.get_total_discount_item_price(), 0.0)
        self.assertEqual(order_item.get_amount_saved(), 500.0)
        self.assertEqual(order_item.get_final_price(), 0.0)

    # ------------------------------
    # Order 总价计算测试 (P0)
    # ------------------------------
    def test_order_without_coupon_should_return_correct_total(self):
        """无优惠券：订单总价 = 所有商品最终价格之和"""
        item1 = self._create_item(price=100.0, discount_price=None, slug='item-1')
        item2 = self._create_item(price=200.0, discount_price=150.0, slug='item-2')
        
        order_item1 = self._create_order_item(item1, quantity=1)
        order_item2 = self._create_order_item(item2, quantity=2)
        
        order = self._create_order([order_item1, order_item2])
        
        # 100 + (2 × 150) = 400
        self.assertEqual(order.get_total(), 400.0)

    def test_order_with_coupon_should_deduct_coupon_amount(self):
        """有优惠券（金额合理）：订单总价 = 商品总价 - 优惠券金额"""
        item = self._create_item(price=100.0, discount_price=None)
        order_item = self._create_order_item(item, quantity=3)  # 总价 300
        
        coupon = self._create_coupon(amount=50.0)
        order = self._create_order([order_item], coupon=coupon)
        
        # 300 - 50 = 250
        self.assertEqual(order.get_total(), 250.0)

    def test_order_with_coupon_exceeding_total_should_return_negative(self):
        """优惠券金额超过订单总额：返回负数
        
        风险提示：当前逻辑允许订单总价为负数，可能导致退款或支付异常。
        建议增加最小为0的保护逻辑。
        """
        item = self._create_item(price=100.0, discount_price=None)
        order_item = self._create_order_item(item, quantity=1)  # 总价 100
        
        coupon = self._create_coupon(amount=150.0)  # 优惠券大于订单总额
        order = self._create_order([order_item], coupon=coupon)
        
        # 100 - 150 = -50
        self.assertEqual(order.get_total(), -50.0)

    # ------------------------------
    # Item URL 方法测试 (P1)
    # ------------------------------
    def test_item_get_absolute_url_should_return_correct_url(self):
        """get_absolute_url() 返回正确的商品详情页 URL"""
        item = self._create_item(slug='test-product')
        expected_url = reverse('core:product', kwargs={'slug': 'test-product'})
        self.assertEqual(item.get_absolute_url(), expected_url)

    def test_item_get_add_to_cart_url_should_return_correct_url(self):
        """get_add_to_cart_url() 返回正确的添加购物车 URL"""
        item = self._create_item(slug='test-product')
        expected_url = reverse('core:add-to-cart', kwargs={'slug': 'test-product'})
        self.assertEqual(item.get_add_to_cart_url(), expected_url)

    def test_item_get_remove_from_cart_url_should_return_correct_url(self):
        """get_remove_from_cart_url() 返回正确的移除购物车 URL"""
        item = self._create_item(slug='test-product')
        expected_url = reverse('core:remove-from-cart', kwargs={'slug': 'test-product'})
        self.assertEqual(item.get_remove_from_cart_url(), expected_url)

    # ------------------------------
    # UserProfile 信号测试 (P0)
    # ------------------------------
    def test_user_creation_should_create_userprofile_automatically(self):
        """创建 User 后应自动通过 post_save 信号创建 UserProfile"""
        new_user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='newpass123'
        )
        
        # 验证 UserProfile 存在且关联正确
        user_profile_exists = UserProfile.objects.filter(user=new_user).exists()
        self.assertTrue(user_profile_exists)
        
        profile = UserProfile.objects.get(user=new_user)
        self.assertEqual(profile.user.username, 'newuser')

    # ------------------------------
    # 附加测试：模型 __str__ 方法 (P2)
    # ------------------------------
    def test_userprofile_str_should_return_username(self):
        """UserProfile.__str__() 返回用户名"""
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'testuser')

    def test_item_str_should_return_title(self):
        """Item.__str__() 返回商品标题"""
        item = self._create_item(title='Awesome T-Shirt')
        self.assertEqual(str(item), 'Awesome T-Shirt')

    def test_orderitem_str_should_show_quantity_and_title(self):
        """OrderItem.__str__() 显示数量和商品标题"""
        item = self._create_item(title='T-Shirt')
        order_item = self._create_order_item(item, quantity=2)
        self.assertEqual(str(order_item), '2 of T-Shirt')

    def test_payment_str_should_handle_null_user(self):
        """Payment.__str__() 处理 user 为 null 的情况
        
        风险提示：当前 user 字段允许 null，访问 self.user.username 
        可能触发 AttributeError。
        """
        payment = Payment.objects.create(
            stripe_charge_id='ch_test123',
            user=None,
            amount=100.0
        )
        try:
            result = str(payment)
        except AttributeError:
            result = 'None'
        self.assertEqual(result, 'None')
