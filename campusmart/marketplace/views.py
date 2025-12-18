from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from .models import User, Product, Category, Conversation, Message
from .forms import UserRegistrationForm, ProductUploadForm, EmailLoginForm
import random, json
from .forms import ProductUploadForm  # not ProductForm
from uuid import UUID
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def user_logout(request):
    logout(request)
    return redirect('login')




# ---------------------------
# Home
# ---------------------------
def home(request):
    return render(request, 'auth.html')


# ---------------------------
# User registration with OTP
# ---------------------------
# ---------------------- REGISTER ----------------------
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})

        form = UserRegistrationForm(data)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_verified = False   # wait for admin approval
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return JsonResponse({'status': 'success', 'message': 'Registration successful!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# ---------------------------
# OTP verification
# ---------------------------
def verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status':'error','message':'Invalid JSON'})

        otp = data.get('otp')
        user_id = request.session.get('user_id')

        if not user_id:
            return JsonResponse({'status':'error','message':'Session expired'})

        user = get_object_or_404(User, id=user_id)
        if user.otp_code == otp:
            user.is_active = True
            user.otp_code = None
            user.save()
            login(request, user)
            return JsonResponse({'status':'success','message':'Account verified successfully'})
        else:
            return JsonResponse({'status':'error','message':'Invalid OTP'})

    return JsonResponse({'status':'error','message':'Invalid request method'})


# ---------------------------
# User login
# ---------------------------
# ---------------------------
# USER LOGIN
# ---------------------------
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})

        username_or_email = data.get('username')
        password = data.get('password')

        # Authenticate user
        user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            # ✅ Only allow superuser login for now
            if user.is_superuser:
                login(request, user)
                return JsonResponse({'status': 'success', 'redirect': '/admin_dashboard/'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Access denied! Only admin can log in now.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid username or password'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
# ---------------------------
# Dashboard for users
# ---------------------------

def admin_dashboard(request):
    unverified_users = User.objects.filter(is_verified=False)
    return render(request, 'admin_dashboard.html', {'unverified_users': unverified_users})


# ---------------------------
# Admin dashboard
# ---------------------------
@login_required
def admin_dashboard(request):
    if not getattr(request.user, 'is_admin_user', False):
        return redirect('dashboard')

    products_count = Product.objects.count()
    users_count = User.objects.count()
    categories_count = Category.objects.count()
    unverified_users = User.objects.filter(is_verified=False)
    context = {
        'products_count': products_count,
        'users_count': users_count,
        'categories_count': categories_count,
        'unverified_users': unverified_users,
        'categories': Category.objects.all(),
    }
    return render(request, 'admin_dashboard.html', context)

# ---------------------------
# User details
# ---------------------------
@login_required

def user_details(request):
    user = request.user

    # Count products sold (by this user as seller)
    products_sold = Product.objects.filter(seller=user).count()

    # Count products bought (by this user as buyer)
    products_bought = Product.objects.filter(buyer=user).count()

    return render(request, 'user_details.html', {
        'user': user,
        'products_sold': products_sold,
        'products_bought': products_bought,
    })


# ---------------------------
# Upload product
# ---------------------------
@login_required
def dashboard(request):
    if getattr(request.user, 'is_admin_user', False):
        return redirect('admin_dashboard')

    products = Product.objects.all().order_by('-created_at')[:12]
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'user': request.user,
        'total_products': Product.objects.count(),
    }
    return render(request, 'dashboard.html', context)


# Also update the upload_product view to ensure products are created properly
@login_required
def upload_product(request):
    """Product upload page with proper form handling"""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            cost = request.POST.get('cost', '')
            category_id = request.POST.get('category', '')
            image = request.FILES.get('image')

            print(f"Form data received: title={title}, cost={cost}, category_id={category_id}")  # Debug

            # Validation
            errors = []
            if not title:
                errors.append('Product title is required.')
            if not description:
                errors.append('Product description is required.')
            if not cost:
                errors.append('Price is required.')
            else:
                try:
                    cost_float = float(cost)
                    if cost_float <= 0:
                        errors.append('Price must be greater than 0.')
                except ValueError:
                    errors.append('Price must be a valid number.')
            if not category_id:
                errors.append('Please select a category.')
            if not image:
                errors.append('Product image is required.')

            if errors:
                categories = Category.objects.all()
                for error in errors:
                    print(f"Validation error: {error}")  # Debug
                return render(request, 'upload_product.html', {
                    'categories': categories,
                    'errors': errors
                })

            # Get category
            try:
                category = Category.objects.get(id=int(category_id))
                print(f"Selected category: {category.name}")  # Debug
            except (Category.DoesNotExist, ValueError):
                print(f"Invalid category ID: {category_id}")  # Debug
                categories = Category.objects.all()
                return render(request, 'upload_product.html', {
                    'categories': categories,
                    'errors': ['Invalid category selected.']
                })

            # Create product
            product = Product.objects.create(
                title=title,
                description=description,
                cost=float(cost),
                category=category,
                seller=request.user,
                image=image,
                is_approved=True,  # Make sure it's approved by default
                status='available'  # Set status explicitly
            )
            
            print(f"Product created: {product.title} (ID: {product.id})")  # Debug
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Product uploaded successfully!',
                    'product_id': str(product.id),
                    'redirect': '/dashboard/'
                })
            
            return redirect('dashboard')

        except Exception as e:
            print(f"Upload error: {e}")  # Debug
            error_message = f'An error occurred: {str(e)}'
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': error_message
                })
            
            categories = Category.objects.all()
            return render(request, 'upload_product.html', {
                'categories': categories,
                'errors': [error_message]
            })

    else:
        categories = Category.objects.all()
        print(f"Available categories: {[(cat.id, cat.name) for cat in categories]}")  # Debug
        return render(request, 'upload_product.html', {'categories': categories})


# Also make sure your models.py has the correct Category model
# models.py - Category model update

# ---------------------------
# Product details
# ---------------------------
@login_required
def product_details(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'product_details.html', {
        'product': product,
        'user': request.user
    })



# ---------------------------
# Chat system
# ---------------------------

@login_required
def chat_system(request):
    user = request.user
    conversation_id = request.GET.get('conversation')  # optional
    product_id = request.GET.get('product')
    seller_id = request.GET.get('seller')

    # Fetch existing conversations
    conversations = Conversation.objects.filter(buyer=user) | Conversation.objects.filter(seller=user)
    active_conversation = None
    messages = []

    # If conversation UUID is provided
    if conversation_id:
        try:
            active_conversation = Conversation.objects.get(id=conversation_id)
            messages = Message.objects.filter(conversation=active_conversation)
        except Conversation.DoesNotExist:
            active_conversation = None

    # If product + seller are provided, create/get conversation
    elif product_id and seller_id:
        product = get_object_or_404(Product, id=product_id)
        seller = get_object_or_404(User, id=seller_id)
        # Check if conversation exists
        active_conversation, created = Conversation.objects.get_or_create(
            product=product,
            buyer=user,
            seller=seller
        )
        messages = Message.objects.filter(conversation=active_conversation)

    context = {
        'user': user,
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': messages,
    }
    return render(request, 'chat_system.html', context)

# ---------------------------
# Send message
# ---------------------------
@login_required
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if request.user not in [conversation.buyer, conversation.seller]:
            return JsonResponse({'status':'error','message':'Unauthorized'})

        message = Message.objects.create(conversation=conversation, sender=request.user, content=content)
        conversation.last_message_at = timezone.now()
        conversation.save()

        return JsonResponse({'status':'success','message': {'id': str(message.id), 'content': message.content, 'sender': message.sender.username, 'timestamp': message.timestamp.strftime('%H:%M')}})
    return JsonResponse({'status':'error','message':'Invalid request method'})


# ---------------------------
# Update product status
# ---------------------------
@login_required
def update_product_status(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        status = data.get('status')
        product = get_object_or_404(Product, id=product_id)

        if request.user == product.seller:
            product.status = status
            if status == 'sold':
                conversation = Conversation.objects.filter(product=product).first()
                if conversation:
                    product.buyer = conversation.buyer
            product.save()
            return JsonResponse({'status':'success','message':'Status updated'})
        else:
            return JsonResponse({'status':'error','message':'Unauthorized'})
    return JsonResponse({'status':'error','message':'Invalid request method'})


# ---------------------------
# Admin actions on users/products
# ---------------------------
@login_required
def verify_user(request, user_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status':'error','message':'Unauthorized'})
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save()
    return JsonResponse({'status':'success','message':'User verified successfully'})



@login_required
def block_user(request, user_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status':'error','message':'Unauthorized'})
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save()
    return JsonResponse({'status':'success','message':'User verified successfully'})


@login_required
def reject_user(request, user_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status':'error','message':'Unauthorized'})
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save()
    return JsonResponse({'status':'success','message':'User verified successfully'})


@login_required
def remove_product(request, product_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status':'error','message':'Unauthorized'})
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.save()
    return JsonResponse({'status':'success','message':'User verified successfully'})


# ---------------------------
# Update user status (admin)
# ---------------------------
@login_required
def update_user_status(request, user_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    user = get_object_or_404(User, id=user_id)
    action = request.POST.get('action')

    if action == "verify":
        user.is_verified = True
    elif action == "block":
        user.is_blocked = True
    elif action == "unblock":
        user.is_blocked = False
    elif action == "make_admin":
        user.is_admin_user = True
    elif action == "remove_admin":
        user.is_admin_user = False
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

    user.save()
    return JsonResponse({'status': 'success', 'message': f'{user.username} updated successfully'})

