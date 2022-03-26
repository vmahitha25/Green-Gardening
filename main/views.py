from django.db.models.aggregates import Count,Avg
from django.http.response import HttpResponseRedirect, JsonResponse,HttpResponse
from django.shortcuts import render,redirect
from django.template.loader import render_to_string
from main.models import *
from .forms import AddressBookForm, AppointmentForm, ProfileForm, ReviewAdd, SignupForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.db.models.functions import ExtractMonth
import calendar



#Home Page
def home(request):
    return render(request, 'index.html')

def review(request):
    return render(request, 'review.html')

def flower_product_list(request):
    data=Product.objects.filter(category = 5)
    return render(request, 'product_list.html',{'data':data})

def home_plants(request):
    data=Product.objects.filter(category = 6)
    return render(request, 'product_list.html',{'data':data})

def seeds(request):
    data=Product.objects.filter(category = 2)
    return render(request, 'product_list.html',{'data':data})

def manure(request):
    data=Product.objects.filter(category = 3)
    return render(request, 'product_list.html',{'data':data})

def fruits(request):
    data=Product.objects.filter(category = 4)
    return render(request, 'product_list.html',{'data':data})

def home_kits(request):
    data=Product.objects.filter(category = 1)
    return render(request,'homekits.html',{'data':data})

def crop_list(request):
    return render(request,'crop_list.html')

def gardening(request):
    return render(request,'gardening.html')

def indoor(request):
    return render(request,'indoor.html')

def outdoor(request):
    return render(request,'outdoor.html')

def balcony(request):
    return render(request,'balcony.html')

def terrace(request):
    return render(request,'terrace.html')

def landscape(request):
    return render(request,'landscape.html')

def product_detail(request,slug,id):
    product=Product.objects.get(id=id)
    reviewForm=ReviewAdd()
    reviews=ProductReview.objects.filter(product=product)
    avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))

    return render(request, 'product_detail.html',{'data':product,'reviewForm':reviewForm, 'reviews':reviews,'avg_reviews': avg_reviews})

# Add to cart
def add_to_cart(request):
    #  del request.session['cartdata']
    cart_p={}
    cart_p[str(request.GET['id'])]={
        'image':request.GET['image'],
        'title':request.GET['title'],
        'qty':request.GET['qty'],
        'price':request.GET['price'],
    }
    if 'cartdata' in request.session:
        if str(request.GET['id']) in request.session['cartdata']:
            cart_data=request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty']=int(cart_p[str(request.GET['id'])]['qty'])
            cart_data.update(cart_data)
            request.session['cartdata']=cart_data
        else:
            cart_data=request.session['cartdata']
            cart_data.update(cart_p)
            request.session['cartdata']=cart_data
    else:
        request.session['cartdata']=cart_p
    return JsonResponse({'data':request.session['cartdata'],'totalitems':len(request.session['cartdata'])})


def cart(request):
    total_amt=0
    address=UserAddressBook.objects.filter(user=request.user,status=True).first()

    if 'cartdata' in request.session:
        for p_id,item in request.session['cartdata'].items():
            total_amt+=int(item['qty'])*float(item['price'])
        return render(request, 'cart.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt,'address':address})
    else:
        return render(request, 'cart.html',{'cart_data':'','totalitems':0,'total_amt':total_amt,'address':address})

def delete_cart_item(request):
    p_id=str(request.GET['id'])
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data=request.session['cartdata']
            del request.session['cartdata'][p_id]
            request.session['cartdata']=cart_data
    total_amt=0
    for p_id,item in request.session['cartdata'].items():
        total_amt+=int(item['qty'])*float(item['price'])
    t=render_to_string('ajax/cart_list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
    return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})

def update_cart_item(request):
    p_id=str(request.GET['id'])
    p_qty=request.GET['qty']
    if 'cartdata' in request.session:
        if p_id in request.session['cartdata']:
            cart_data=request.session['cartdata']
            cart_data[str(request.GET['id'])]['qty']=p_qty
            request.session['cartdata']=cart_data
    total_amt=0
    for p_id,item in request.session['cartdata'].items():
        total_amt+=int(item['qty'])*float(item['price'])
    t=render_to_string('ajax/cart_list.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt})
    return JsonResponse({'data':t,'totalitems':len(request.session['cartdata'])})

def signup(request):
    if request.method=='POST':
        form=SignupForm(request.POST)
        if form.is_valid():
            form.save()
            # username=form.cleaned_data.get('username')
            # pwd=form.cleaned_data.get('password1')
            # user=authenticate(username=username,password=pwd)
            # login(request, user)
            return redirect('login')
    form=SignupForm
    return render(request, 'registration/signup.html',{'form':form})


@login_required
def checkout(request):
    total_amt=0
    totalAmt=0
    if 'cartdata' in request.session:
        for p_id,item in request.session['cartdata'].items():
            totalAmt+=int(item['qty'])*float(item['price'])
        # Order
        order=CartOrder.objects.create(
                user=request.user,
                total_amt=totalAmt
            )
        # End
        for p_id,item in request.session['cartdata'].items():
            total_amt+=int(item['qty'])*float(item['price'])
            # OrderItems
            items=CartOrderItems.objects.create(
                order=order,
                invoice_no='INV-'+str(order.id),
                item=item['title'],
                image=item['image'],
                qty=item['qty'],
                price=item['price'],
                total=float(item['qty'])*float(item['price'])
                )
            # End
        # Process Payment
        host = request.get_host()
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total_amt,
            'item_name': 'OrderNo-'+str(order.id),
            'invoice': 'INV-'+str(order.id),
            'currency_code': 'USD',
            'notify_url': 'http://{}{}'.format(host,reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,reverse('payment_done')),
            'cancel_return': 'http://{}{}'.format(host,reverse('payment_cancelled')),
        }			
        # End
        form = PayPalPaymentsForm(initial=paypal_dict)
        address=UserAddressBook.objects.filter(user=request.user,status=True).first()
        return render(request, 'checkout.html',{'cart_data':request.session['cartdata'],'totalitems':len(request.session['cartdata']),'total_amt':total_amt,'form':form,'address':address})

@csrf_exempt
def payment_done(request):
    returnData=request.POST
    del request.session['cartdata']
    return render(request, 'payment-success.html',{'data':returnData})



@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment-fail.html')

def save_review(request,pid):
    product=Product.objects.get(pk=pid)
    user=request.user
    review =ProductReview.objects.create(
        user=user,
        product=product,
        review_text=request.POST['review_text'],
        review_rating=request.POST['review_rating'],
        )
    data={
        'user':user.username,
        'review_text': request.POST['review_text'],
        'review_rating': request.POST['review_rating'],
    }
    avg_reviews=ProductReview.objects.filter(product=product).aggregate(avg_rating=Avg('review_rating'))
    return JsonResponse({'bool':True, 'data':data,'avg_reviews':avg_reviews,})

def my_orders(request):
	orders=CartOrder.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/orders.html',{'orders':orders})

def my_order_items(request,id):
	order=CartOrder.objects.get(pk=id)
	orderitems=CartOrderItems.objects.filter(order=order).order_by('-id')
	return render(request, 'user/order-items.html',{'orderitems':orderitems})

def add_wishlist(request):
	pid=request.GET['product']
	product=Product.objects.get(pk=pid)
	data={}
	checkw=Wishlist.objects.filter(product=product,user=request.user).count()
	if checkw > 0:
		data={
			'bool':False
		}
	else:
		wishlist=Wishlist.objects.create(
			product=product,
			user=request.user
		)
		data={
			'bool':True
		}
	return JsonResponse(data)

def my_wishlist(request):
	wlist=Wishlist.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/wishlist.html',{'wlist':wlist})

def my_reviews(request):
	reviews=ProductReview.objects.filter(user=request.user).order_by('-id')
	return render(request, 'user/review.html',{'reviews':reviews})


def deletewishlist(request, id):
    customer=request.user
    Wishlist.objects.filter(user_id=customer.id, product=Product.objects.get(id=id)).delete()
    return redirect('my_wishlist')

def delete_address(request, id):
    address=UserAddressBook.objects.get(pk=id)
    address.delete()
    return redirect('my-addressbook')

def my_addressbook(request):
    addbook=UserAddressBook.objects.filter(user=request.user).order_by('-id')
    return render(request, 'user/addressbook.html',{'addbook':addbook})

def save_address(request):
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm
	return render(request, 'user/add-address.html',{'form':form,'msg':msg})

def activate_address(request):
	a_id=str(request.GET['id'])
	UserAddressBook.objects.update(status=False)
	UserAddressBook.objects.filter(id=a_id).update(status=True)
	return JsonResponse({'bool':True})

def edit_profile(request):
	msg=None
	if request.method=='POST':
		form=ProfileForm(request.POST,instance=request.user)
		if form.is_valid():
			form.save()
			msg='Data has been saved'
	form=ProfileForm(instance=request.user)
	return render(request, 'user/edit-profile.html',{'form':form,'msg':msg})

@csrf_exempt
def add_appointment(request):
	msg=None
	if request.method=='POST':
		form=AppointmentForm(request.POST)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				Appointments.objects.update(status=False)
			saveForm.save()
			msg='Your Appointment has been booked!'
	form=AppointmentForm
	return render(request, 'appointment.html',{'form':form,'msg':msg})


def update_address(request,id):
	address=UserAddressBook.objects.get(pk=id)
	msg=None
	if request.method=='POST':
		form=AddressBookForm(request.POST,instance=address)
		if form.is_valid():
			saveForm=form.save(commit=False)
			saveForm.user=request.user
			if 'status' in request.POST:
				UserAddressBook.objects.update(status=False)
			saveForm.save()
			msg='Data has been saved'
	form=AddressBookForm(instance=address)
	return render(request, 'user/update-address.html',{'form':form,'msg':msg})


#Terms and conditions
def terms_condition(request):
    return render(request, 'terms_condition.html')

#Cancellation
def cancellation(request):
    return render(request, 'cancellation.html')

def search(request):
    q=request.GET['q']
    data=Product.objects.filter(title__icontains=q).order_by('-id')
    return render(request, 'search.html',{'data':data})
