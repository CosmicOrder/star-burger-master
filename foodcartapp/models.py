from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, ExpressionWrapper, DecimalField
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class OrderQuerySet(models.QuerySet):
    def fetch_with_order_price(self):
        orders = self.annotate(
            total_price=ExpressionWrapper(
                F('items__product__price') * F('items__quantity'),
                output_field=DecimalField(),
            )
        )

        return orders


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
        verbose_name='ресторан',
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
        db_index=True,
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
    COLLECTING = 'Готовится'
    DELIVERING = 'Курьер выехал'
    DONE = 'Выполнен'
    STATUSES = {
        (ACCEPTED, 'Принят'),
        (COLLECTING, 'Готовится'),
        (DELIVERING, 'Курьер выехал'),
        (DONE, 'Выполнен'),
    }
    CASH = 'При получении'
    ON_SITE = 'На сайте'
    UNDEFINED = 'Способ оплаты не выбран'
    PAYMENT_METHODS = {
        (CASH, 'При получении'),
        (ON_SITE, 'На сайте'),
        (UNDEFINED, 'Способ оплаты не выбран')
    }
    status = models.CharField(
        'Статус заказа',
        max_length=100,
        db_index=True,
        choices=STATUSES,
        default=ACCEPTED,
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=100,
        db_index=True,
        choices=PAYMENT_METHODS,
        default=UNDEFINED,
    )
    restaurant_preparing_order = models.ForeignKey(
        Restaurant,
        related_name='order',
        verbose_name='ресторан, который готовит заказ',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
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
        blank=True,
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
        blank=True,
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
        related_name='items',
        verbose_name='заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='товар',
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    quantity = models.PositiveIntegerField(
        'Количество',
        db_index=True,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        unique_together = [
            ['order', 'product']
        ]

    def __str__(self):
        return self.product.name
