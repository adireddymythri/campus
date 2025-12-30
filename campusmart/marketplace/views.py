from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from .models import User, Product, Category, Conversation, Message, GlobalSettings, Favorite
from .forms import UserRegistrationForm, ProductUploadForm, EmailLoginForm
import random, json
from uuid import UUID
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

# ---------------------------
# logout
# ---------------------------
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

    # FIX: Render page instead of returning JSON error
    return render(request, 'auth.html')


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
def user_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})

        username_or_email = data.get('username')
        password = data.get('password')

        # Allow login by email
        if '@' in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                print(f"DEBUG: Found user via email: {user_obj.username}")
                username_or_email = user_obj.username
            except User.DoesNotExist:
                print(f"DEBUG: No user found with email: {username_or_email}")
                pass

        user = authenticate(request, username=username_or_email, password=password)
        print(f"DEBUG: Authenticate result for {username_or_email}: {user}")

        if user is not None:
            if user.is_active:
                # Check if user is verified (admin approval required)
                if not user.is_verified:
                    return JsonResponse({'status': 'error', 'message': 'Your account is pending admin approval. Please wait for approval before logging in.'})
                
                login(request, user)
                # Check if user is admin and redirect accordingly
                if getattr(user, 'is_admin_user', False):
                    return JsonResponse({'status': 'success', 'redirect': '/admin_dashboard/'})
                else:
                    return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Account is not active.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid username or password'})

    # Render page for GET requests
    return render(request, 'auth.html')

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
    context = {
        'user': user,
        'published_count': Product.objects.filter(seller=user).count(),
        'purchased_count': Product.objects.filter(buyer=user, status='sold').count(),
        'user': user,
        'published_count': Product.objects.filter(seller=user).count(),
        'purchased_count': Product.objects.filter(buyer=user, status='sold').count(),
        'favorite_count': Favorite.objects.filter(user=user).count(),
        'favorites': Favorite.objects.filter(user=user).select_related('product'),
    }
    return render(request, 'user_details.html', context)

# ---------------------------
# Dashboard
# ---------------------------
@login_required
def dashboard(request):
    if getattr(request.user, 'is_admin_user', False):
        return redirect('admin_dashboard')

    products = Product.objects.all().order_by('-created_at')[:12]
    categories = Category.objects.all()
    
    # Get user's own products count
    user_products_count = Product.objects.filter(seller=request.user).count()

    context = {
        'products': products,
        'categories': categories,
        'user': request.user,
        'total_products': Product.objects.count(),
        'user_products_count': user_products_count,
        'published_count': user_products_count,  # For consistency with user_details template
        'favorite_ids': list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    }
    return render(request, 'dashboard_v2.html', context)

# ---------------------------
# Upload product
# ---------------------------
@login_required
def upload_product(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            cost = request.POST.get('cost', '')
            category_id = request.POST.get('category', '')
            image = request.FILES.get('image')

            category = Category.objects.get(id=int(category_id))
            product = Product.objects.create(
                title=title,
                description=description,
                cost=float(cost),
                category=category,
                seller=request.user,
                image=image,
                is_approved=True,
                status='available'
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'redirect': '/dashboard/'})
            
            return redirect('dashboard')

        except Exception as e:
            categories = Category.objects.all()
            return render(request, 'upload_product.html', {'categories': categories, 'errors': [str(e)]})
    else:
        categories = Category.objects.all()
        return render(request, 'upload_product.html', {'categories': categories})

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
# Update Profile
# ---------------------------
@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.phone_number = request.POST.get('phone')
        user.college_name = request.POST.get('college_name')
        user.college_id = request.POST.get('college_id')
        user.branch = request.POST.get('branch')
        user.hostel_block = request.POST.get('hostel_block')
        user.room_no = request.POST.get('room_no')
        user.save()
        messages.success(request, "Profile updated successfully!")
    return redirect('user_details')

# ---------------------------
# Chat system
# ---------------------------
@login_required
def chat_system(request):
    user = request.user
    conversation_id = request.GET.get('conversation')
    product_id = request.GET.get('product')
    seller_id = request.GET.get('seller')

    # Get conversations where user is either buyer or seller using Q objects
    from django.db.models import Q
    conversations = Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    ).order_by('-last_message_at')
    
    active_conversation = None
    messages_list = []

    if conversation_id:
        try:
            # Get conversation and verify user is part of it
            active_conversation = Conversation.objects.filter(
                id=conversation_id
            ).filter(
                Q(buyer=user) | Q(seller=user)
            ).first()
            if active_conversation:
                messages_list = Message.objects.filter(conversation=active_conversation).order_by('timestamp')
            else:
                active_conversation = None
        except Exception:
            active_conversation = None
    elif product_id and seller_id:
        product = get_object_or_404(Product, id=product_id)
        seller = get_object_or_404(User, id=seller_id)
        
        # Create or get conversation
        # If user is the seller, they are viewing messages about their product
        # If user is not the seller, they are the buyer
        if seller == user:
            # User is the seller, need to find existing conversation or create one
            # In this case, we need the buyer - but we don't have it from the URL
            # So we'll get the first conversation for this product where user is seller
            active_conversation = Conversation.objects.filter(
                product=product, seller=user
            ).first()
            if not active_conversation:
                # If no conversation exists, we can't create one without a buyer
                # This case shouldn't happen normally, but handle it gracefully
                active_conversation = None
        else:
            # User is buyer, seller is the product owner
            active_conversation, _ = Conversation.objects.get_or_create(
                product=product, buyer=user, seller=seller
            )
        
        if active_conversation:
            messages_list = Message.objects.filter(conversation=active_conversation).order_by('timestamp')

    return render(request, 'chat_system.html', {
        'user': user,
        'conversations': conversations,
        'active_conversation': active_conversation,
        'messages': messages_list,
    })

# ---------------------------
# Send message
# ---------------------------
@login_required
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status':'error','message':'Invalid JSON'}, status=400)
        
        conversation_id = data.get('conversation_id')
        content = data.get('content')
        
        # Validate input
        if not conversation_id:
            return JsonResponse({'status':'error','message':'Conversation ID is required'}, status=400)
        
        if not content or not content.strip():
            return JsonResponse({'status':'error','message':'Message content cannot be empty'}, status=400)
        
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return JsonResponse({'status':'error','message':'Conversation not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status':'error','message':f'Invalid conversation ID: {str(e)}'}, status=400)

        # Check if user is part of this conversation
        if request.user not in [conversation.buyer, conversation.seller]:
            return JsonResponse({'status':'error','message':'Unauthorized'}, status=403)

        # Create message
        try:
            message = Message.objects.create(
                conversation=conversation, 
                sender=request.user, 
                content=content.strip()
            )
            conversation.last_message_at = timezone.now()
            conversation.save()

            return JsonResponse({
                'status':'success',
                'message': {
                    'id': str(message.id), 
                    'content': message.content, 
                    'sender': message.sender.username, 
                    'timestamp': message.timestamp.strftime('%H:%M')
                }
            })
        except Exception as e:
            return JsonResponse({'status':'error','message':f'Failed to send message: {str(e)}'}, status=500)
    
    return JsonResponse({'status':'error','message':'Invalid request method'}, status=405)

# ---------------------------
# Get messages for a conversation (API endpoint for polling)
# ---------------------------
@login_required
def get_messages(request, conversation_id):
    """API endpoint to fetch messages for a conversation"""
    try:
        conversation = get_object_or_404(Conversation, id=conversation_id)
        
        # Check if user is part of this conversation
        if request.user not in [conversation.buyer, conversation.seller]:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
        # Get last message ID from query parameter (for polling new messages)
        last_message_id = request.GET.get('last_message_id')
        
        if last_message_id:
            try:
                # Convert string to UUID for comparison
                from uuid import UUID
                last_uuid = UUID(last_message_id)
                # Return only new messages after the last known message
                messages = Message.objects.filter(
                    conversation=conversation,
                    timestamp__gt=Message.objects.get(id=last_uuid).timestamp
                ).order_by('timestamp')
            except (ValueError, Message.DoesNotExist):
                # If invalid UUID or message not found, return all messages
                messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        else:
            # Return all messages
            messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': str(msg.id),
                'content': msg.content,
                'sender': msg.sender.username,
                'sender_id': msg.sender.id,
                'is_own': msg.sender == request.user,
                'timestamp': msg.timestamp.strftime('%H:%M'),
                'full_timestamp': msg.timestamp.isoformat(),
            })
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data,
            'conversation_id': str(conversation_id)
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

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
# Admin actions
# ---------------------------
@login_required
def verify_user(request, user_id):
    if not getattr(request.user, 'is_admin_user', False) and not request.user.is_staff:
        return JsonResponse({'status':'error','message':'Unauthorized'}, status=403)
    user = get_object_or_404(User, id=user_id)
    user.is_verified = True
    user.is_active = True  # Ensure user can login after verification
    user.save()
    return JsonResponse({'status':'success','message':'User verified successfully'})

@login_required
def block_user(request, user_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status':'error','message':'Unauthorized'})
    user = get_object_or_404(User, id=user_id)
    user.is_blocked = True
    user.save()
    return JsonResponse({'status':'success','message':'User blocked successfully'})

@login_required
def reject_user(request, user_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status':'error','message':'Unauthorized'})
    user = get_object_or_404(User, id=user_id)
    user.delete() 
    return JsonResponse({'status':'success','message':'User rejected'})

@login_required
def remove_product(request, product_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status':'error','message':'Unauthorized'})
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return JsonResponse({'status':'success','message':'Product removed'})

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

# ---------------------------
# API endpoints for admin dashboard
# ---------------------------
@login_required
def get_users_data(request):
    """API endpoint to fetch all users for admin dashboard"""
    if not getattr(request.user, 'is_admin_user', False) and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    users = User.objects.all().order_by('-date_joined')
    users_data = []
    
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'name': user.name or user.username,
            'email': user.email,
            'joinDate': user.date_joined.strftime('%Y-%m-%d') if user.date_joined else 'N/A',
            'verified': user.is_verified,
            'blocked': user.is_blocked,
            'is_active': user.is_active,
            'productsCount': Product.objects.filter(seller=user).count(),
            'phone_number': user.phone_number or 'N/A',
            'college_name': user.college_name or 'N/A',
        })
    
    return JsonResponse({'status': 'success', 'users': users_data})

@login_required
def get_products_data(request):
    """API endpoint to fetch all products for admin dashboard"""
    if not getattr(request.user, 'is_admin_user', False) and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        products = Product.objects.all().order_by('-created_at')
        products_data = []
        
        for product in products:
            image_url = None
            if product.image:
                try:
                    image_url = product.image.url
                except Exception:
                    image_url = None

            products_data.append({
                'id': str(product.id), # Cast UUID to string
                'title': product.title,
                'seller': product.seller.username if product.seller else 'N/A',
                'category': product.category.name if product.category else 'Uncategorized',
                'price': float(product.cost),
                'status': product.status,
                'created': product.created_at.strftime('%Y-%m-%d') if product.created_at else 'N/A',
                'image': image_url,
            })
        
        return JsonResponse({'status': 'success', 'products': products_data})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_dashboard_stats(request):
    """API endpoint to fetch dashboard statistics"""
    if not getattr(request.user, 'is_admin_user', False) and not request.user.is_staff:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    stats = {
        'total_users': User.objects.count(),
        'pending_users': User.objects.filter(is_verified=False).count(),
        'verified_users': User.objects.filter(is_verified=True).count(),
        'blocked_users': User.objects.filter(is_blocked=True).count(),
        'total_products': Product.objects.count(),
        'blocked_products': Product.objects.filter(status='blocked').count() if hasattr(Product, 'status') else 0,
        'available_products': Product.objects.filter(status='available').count() if hasattr(Product, 'status') else Product.objects.count(),
        'sold_products': Product.objects.filter(status='sold').count() if hasattr(Product, 'status') else 0,
    }
    
    return JsonResponse({'status': 'success', 'stats': stats})

# ---------------------------
# admin login
# ---------------------------

def admin_login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({'status': 'error', 'message': 'Username and password are required'})

        # Allow login by email for admins too
        if '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                if user.is_staff: # Only allow users with admin access
                    login(request, user)
                    return JsonResponse({
                        'status': 'success', 
                        'redirect': '/admin_dashboard/' # Redirect to admin dashboard
                    })
                else:
                    return JsonResponse({'status': 'error', 'message': 'You are not an authorized admin.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Account is not active.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid Credentials'})
    
    # Render the auth page for GET requests
    return render(request, 'auth.html')

# ---------------------------
# Admin Category Management
# ---------------------------
@login_required
def add_category(request):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            icon = data.get('icon', '')
            
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Category name is required'})
                
            category = Category.objects.create(name=name, icon=icon)
            return JsonResponse({
                'status': 'success', 
                'category': {'id': category.id, 'name': category.name, 'icon': category.icon}
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

@login_required
def delete_category(request, category_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return JsonResponse({'status': 'success', 'message': 'Category deleted'})
    except Category.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Category not found'})

# ---------------------------
# Admin Global Settings
# ---------------------------
@login_required
def get_global_settings(request):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    settings_obj, created = GlobalSettings.objects.get_or_create(id=1)
    
    return JsonResponse({
        'status': 'success',
        'settings': {
            'auto_approve_products': settings_obj.auto_approve_products,
            'require_user_verification': settings_obj.require_user_verification,
            'email_notifications': settings_obj.email_notifications,
            'maintenance_mode': settings_obj.maintenance_mode
        }
    })

@login_required
def update_global_settings(request):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            settings_obj, created = GlobalSettings.objects.get_or_create(id=1)
            
            settings_obj.auto_approve_products = data.get('auto_approve_products', settings_obj.auto_approve_products)
            settings_obj.require_user_verification = data.get('require_user_verification', settings_obj.require_user_verification)
            settings_obj.email_notifications = data.get('email_notifications', settings_obj.email_notifications)
            settings_obj.maintenance_mode = data.get('maintenance_mode', settings_obj.maintenance_mode)
            
            settings_obj.save()
            return JsonResponse({'status': 'success', 'message': 'Settings updated'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

# ---------------------------
# Admin Product Moderation
# ---------------------------
@login_required
def admin_approve_product(request, product_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    product.is_approved = True
    product.status = 'available'
    product.save()
    return JsonResponse({'status': 'success', 'message': 'Product approved'})

@login_required
def admin_block_product(request, product_id):
    if not getattr(request.user, 'is_admin_user', False):
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    
    product = get_object_or_404(Product, id=product_id)
    product.status = 'blocked'
    product.is_approved = False
    product.save()
    return JsonResponse({'status': 'success', 'message': 'Product blocked'})

# ---------------------------
# Favorites
# ---------------------------
@login_required
def toggle_favorite(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        
        if not created:
            # If it already exists, remove it (toggle off)
            favorite.delete()
            is_favorited = False
            message = 'Removed from favorites'
        else:
            # If created (toggle on)
            is_favorited = True
            message = 'Added to favorites'
            
        return JsonResponse({
            'status': 'success',
            'is_favorited': is_favorited,
            'message': message,
            'count': Favorite.objects.filter(product=product).count()
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)