from rest_framework import serializers
from .models import Cart, CartItem, Product, Collection, Review
from decimal import Decimal

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Collection
        fields=['id','title','products_count']

    products_count=serializers.SerializerMethodField(method_name='count_product')
    def count_product(self,collection):
        return collection.products.count()
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['id','title','unit_price','price_with_tax','collection','inventory','description','slug']
    
    price_with_tax=serializers.SerializerMethodField(method_name='calculate_tax')

    def calculate_tax(self,product):
        return product.unit_price*Decimal(1.1)
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields=['id','name','description','date','product']
        read_only_fields=['product']

class SimpleCartItemSerializer(serializers.ModelSerializer):
     class Meta:
          model=Product
          fields=['id','title','unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product=SimpleCartItemSerializer()
    class Meta:
        model=CartItem
        fields=['id','product','quantity','total_price']
        
    total_price=serializers.SerializerMethodField()
    def get_total_price(self,obj):
            return obj.product.unit_price*Decimal(obj.quantity)
    
class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(many=True, read_only=True)
       
    class Meta:
        model=Cart
        fields=['id','items','total_price']
        read_only_fields=['id']

    total_price=serializers.SerializerMethodField()
    def get_total_price(self,obj):
        return sum([item.quantity*item.product.unit_price for item in obj.items.all()])


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField()

    def validate_product_id(self,value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError('no product with the given ID was found.')
        return value


    def save(self,**kwargs):
        cart_id=self.context['cart_id']
        product_id=self.validated_data['product_id']
        quantity=self.validated_data['quantity']

        try:
            cart_item=CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance=cart_item
        except CartItem.DoesNotExist:
            self.instance=CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance
    

    class Meta:
        model=CartItem
        fields=['id','product_id','quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
        class Meta:
            model=CartItem
            fields=['quantity']