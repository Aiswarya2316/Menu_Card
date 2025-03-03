from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .models import *
from .forms import *



# Customer Registration
def customer_register(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer registered successfully!")
            return redirect("login")
    else:
        form = CustomerRegistrationForm()
    return render(request, "customer/register.html", {"form": form, "user_type": "Customer"})



# Seller Registration
def seller_register(request):
    if request.method == "POST":
        form = StafRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Seller registered successfully!")
            return redirect("login")
    else:
        form = StafRegistrationForm()
    return render(request, "staf/register.html", {"form": form, "user_type": "Staf"})



# Admin Registration
def admin_register(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin registered successfully!")
            return redirect("login")
    else:
        form = AdminRegistrationForm()
    return render(request, "admin/register.html", {"form": form, "user_type": "Admin"})



# --- User Login ---
def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = None
            redirect_url = "login"  # Default in case of failure

            if Customer.objects.filter(email=email, password=password).exists():
                user = Customer.objects.get(email=email)
                request.session["user_type"] = "Customer"
                redirect_url = "customerhome"
            elif Staf.objects.filter(email=email, password=password).exists():
                user = Staf.objects.get(email=email)
                request.session["user_type"] = "Staf"
                redirect_url = reverse("stafhome")

            elif AdminReg.objects.filter(email=email, password=password).exists():
                user = AdminReg.objects.get(email=email)
                request.session["user_type"] = "Admin"
                redirect_url = "adminhome"

            if user:
                request.session["user_id"] = user.id
                messages.success(request, f"Welcome {user.name}!")
                return redirect(redirect_url)
            else:
                messages.error(request, "Invalid credentials")

    form = LoginForm()
    return render(request, "login.html", {"form": form})



# Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect("home")

def home(request):
    return render(request,'home.html')



def adminhome(request):
    total_customers = Customer.objects.count()
    total_staff = Staf.objects.count()
    total_orders = Order.objects.count()
    total_items = MenuCard.objects.count()  # Count total menu items

    customers = Customer.objects.all()
    staff = Staf.objects.all()
    orders = Order.objects.all()
    menu_items = MenuCard.objects.all()  # Fetch all menu items

    context = {
        'total_customers': total_customers,
        'total_staff': total_staff,
        'total_orders': total_orders,
        'total_items': total_items,  # Pass total menu items
        'customers': customers,
        'staff': staff,
        'orders': orders,
        'menu_items': menu_items,  # Pass menu items to template
    }
    return render(request, 'admin/adminhome.html', context)



def stafhome(request):
    return render(request, 'staf/stafhome.html')



def add_menu_item(request):
    if "user_id" not in request.session or request.session.get("user_type") != "Staf":
        messages.error(request, "You must be logged in as a staff member to add menu items.")
        return redirect("login")

    staf = Staf.objects.get(id=request.session["user_id"])  # Get logged-in staff member

    if request.method == "POST":
        form = MenuCardForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.staf = staf
            menu_item.save()
            messages.success(request, "Menu item added successfully!")
            return redirect("stafhome")
    else:
        form = MenuCardForm()

    return render(request, "staf/add_menu.html", {"form": form})

def menu_list(request):
    menu_items = MenuCard.objects.all()  # Fetch all menu items
    return render(request, "staf/menu_list.html", {"menu_items": menu_items})


def customerhome(request):
    user_id = request.session.get("user_id")  # Ensure user is logged in

    if not user_id:
        return redirect("login")  # Redirect if not logged in

    customer = get_object_or_404(Customer, id=user_id)
    
    # Get the latest order for the logged-in user
    latest_order = Order.objects.filter(customer=customer, paid=True).order_by('-id').first()

    return render(request, "customer/customerhome.html", {"latest_order": latest_order})




def about(request):
    user_id = request.session.get("user_id")  # Ensure user is logged in

    if not user_id:
        return redirect("login")  # Redirect if not logged in
    customer = get_object_or_404(Customer, id=user_id)
    latest_order = Order.objects.filter(customer=customer, paid=True).order_by('-id').first()
    return render(request, 'customer/about.html',{"latest_order": latest_order})



def menulist(request):
    menu_items = MenuCard.objects.all()  # Fetch all menu items
    return render(request, 'customer/menulist.html', {'menu_items': menu_items})


import razorpay
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.http import JsonResponse
from .models import MenuCard, Order, Customer, Staf, AdminReg
from .forms import CustomerRegistrationForm, StafRegistrationForm, AdminRegistrationForm, LoginForm

# --- Order Placement ---
def order_item(request, item_id):
    user_id = request.session.get("user_id")  # Use "user_id" instead of "customer_id"
    
    if not user_id:
        return redirect("login")  # Redirect if not logged in

    customer = get_object_or_404(Customer, id=user_id)  # Fetch customer based on "user_id"
    item = get_object_or_404(MenuCard, id=item_id)

    # Initialize Razorpay client
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # Create Razorpay Order
    payment_data = {
        "amount": int(item.price * 100),  # Convert price to paise
        "currency": "INR",
        "receipt": f"order_{customer.id}_{item.id}",
        "payment_capture": 1  # Auto capture payment
    }

    razorpay_order = client.order.create(data=payment_data)

    # Save order in database
    order = Order.objects.create(
        customer=customer,
        item=item,
        amount=item.price,
        razorpay_order_id=razorpay_order["id"]
    )

    return render(request, "customer/payment.html", {
        "order": order,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "amount": payment_data["amount"]
    })


# --- Payment Success ---
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        order = get_object_or_404(Order, razorpay_order_id=order_id)
        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.paid = True
        order.save()

        return JsonResponse({"status": "Payment successful", "redirect_url": reverse("order_details", args=[order.id])})
    return JsonResponse({"status": "Payment failed"}, status=400)

def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, "customer/order_details.html", {"order": order})
