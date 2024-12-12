from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserUpdateForm, ProfileUpdateForm

# Register View
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'  # Automatically assign the student role
            user.save()
            login(request, user)
            return redirect('home')  # Redirect to the home page or any other
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Login View
def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Using email as the username
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page or dashboard
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def custom_logout(request):
    logout(request)  # Log out the user
    return redirect('logout')  # Redirect to the logged_out page

# Profile Update View
@login_required
def profile(request):
    # Check if the user has a profile
    if not hasattr(request.user, 'profile') or request.user.profile is None:
        # If not, redirect them to the profile creation page
        return redirect('profile_create')  # Make sure to create a 'profile_create' view
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')  # Redirect to the profile page after successful update
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_create(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES)

        if u_form.is_valid() and p_form.is_valid():
            user = u_form.save()
            profile = p_form.save(commit=False)
            profile.user = user  # Assign the profile to the user
            profile.save()
            return redirect('profile')  # Redirect to the profile page after profile creation
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm()

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile_create.html', context)