from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,ListModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
from .models import Cart, CartItem, Product,Collection,Review
from .serializers import UpdateCartItemSerializer,AddCartItemSerializer, CartItemSerializer, CartSerializer, ProductSerializer,CollectionSerializer, ReviewSerializer
from .pagination import DefaultPagination




class ProductViewSet(ModelViewSet):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_fields=['collection_id']
    search_fields=['title','description']
    ordering_fields=['unit_price','last_update']
    pagination_class=DefaultPagination
   

    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self,request,pk,*args, **kwargs):
        product=get_object_or_404(Product,pk=pk)
        if product.orderitem.exists() :
            return Response({'error':'this is not allowed to delete because it contains an order item'})
        
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset=Collection.objects.annotate(product_count=Count('products'))
    serializer_class=CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        collection = self.get_object()

        # Check if the collection has any associated products
        if collection.products.exists():
            return Response(
                {'error': 'This collection cannot be deleted because it contains products.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If no products are associated, proceed with the deletion
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class=ReviewSerializer

    def get_queryset(self):
        product_id=self.kwargs['product_pk']
        return Review.objects.filter(product_id=product_id)
    def perform_create(self,serializer):
        product_id=self.kwargs['product_pk']
        product=Product.objects.get(id=product_id)
        serializer.save(product=product)


class CartViewSet(CreateModelMixin, RetrieveModelMixin,GenericViewSet,DestroyModelMixin):
    queryset=Cart.objects.prefetch_related('items__product').all()
    serializer_class=CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names=['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method=='POST':
            return AddCartItemSerializer
        elif self.request.method=='PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        cart_id=self.kwargs['cart_pk']
        return CartItem.objects.filter(cart_id=cart_id).select_related('product')