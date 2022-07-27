

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class OrderQuerySet(models.QuerySet):
    def fetch_with_order_price(self):
        total_prices = []
        for order in self.all().prefetch_related('item') \
                               .prefetch_related('item__product'):
            total_prices.append((order.id,
                                 sum(int(order_item.product.price
                                         * order_item.quantity) for
                                     order_item in order.item.all())))

        order_and_prices = dict(total_prices)

        for order in self:
            order.total_price = order_and_prices[order.id]

        return list(self)


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
                .filter(availability=True)
                .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    ACCEPTED = 'Принят'
    COLLECTING = 'Собирается'
    DELIVERING = 'Курьер выехал'
    DONE = 'Выполнен'
    STATUSES = {
        (ACCEPTED, 'Принят'),
        (COLLECTING, 'Собирается'),
        (DELIVERING, 'Курьер выехал'),
        (DONE, 'Выполнен'),
    }
    status = models.CharField(
        'Статус заказа',
        max_length=100,
        db_index=True,
        choices=STATUSES,
        default=ACCEPTED,
    )
    firstname = models.CharField(
        'Имя',
        max_length=100,
        db_index=True,
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=100,
        db_index=True,
    )
    phonenumber = PhoneNumberField(
        'Телефон',
        db_index=True,
    )
    address = models.CharField(
        'Адрес доставки',
        max_length=300,
        db_index=True,
    )
    comment = models.TextField(
        'Комментарии',
        null=True,
    )
    created_at = models.DateTimeField(
        'Дата и время создания',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        'Дата и время звонка',
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        'Дата и время доставки',
        null=True,
        db_index=True,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.address


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='item',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_item',
        verbose_name='товар',
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
    )
    quantity = models.PositiveIntegerField(
        'Количество',
        db_index=True,
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return self.product.name
