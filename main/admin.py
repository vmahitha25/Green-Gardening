from django.contrib import admin
from .models import *


admin.site.register(Category)

class ProductAdmin(admin.ModelAdmin):
    list_display=('id','title','category','price','status')
    list_editable=('status',)
admin.site.register(Product,ProductAdmin)

class CartOrderAdmin(admin.ModelAdmin):
	list_editable=('paid_status','order_status')
	list_display=('user','total_amt','paid_status','order_dt','order_status',)
admin.site.register(CartOrder,CartOrderAdmin)

class CartOrderItemsAdmin(admin.ModelAdmin):
	list_display=('invoice_no','item','qty','price','total',)
admin.site.register(CartOrderItems,CartOrderItemsAdmin)

class PoductReviewAdmin(admin.ModelAdmin):
	list_display=('user','product','review_text','get_review_rating',)
admin.site.register(ProductReview,PoductReviewAdmin)

admin.site.register(Wishlist)

class UserAddressBookAdmin(admin.ModelAdmin):
	list_display=('user','address','status')
admin.site.register(UserAddressBook,UserAddressBookAdmin)

class AppointmentsAdmin(admin.ModelAdmin):
	list_display=('first_name','last_name','email','mobile')
admin.site.register(Appointments,AppointmentsAdmin)
