from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from . import views

router=routers.DefaultRouter()
router.register('products',views.ProductViewSet)
router.register('collections',views.CollectionViewSet)
router.register('carts',views.CartViewSet,)

products_router=routers.NestedDefaultRouter(router,'products',lookup='product')
products_router.register('reviews',views.ReviewViewSet,basename='product_review')

cart_item_router=routers.NestedDefaultRouter(router,'carts',lookup='cart')
cart_item_router.register('items',views.CartItemViewSet,basename='cart-items')


urlpatterns = [
    path('',include(router.urls)),
    path('',include(products_router.urls)),
    path('',include(cart_item_router.urls))
    
]
