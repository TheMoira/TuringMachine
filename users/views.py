from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm
# from .forms import ProfileUpdateForm
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# thanks to that user will have to be logged in to see this page
# @login_required
# def profile(request):
#     if request.method == 'POST':
#         user_form = UserUpdateForm(request.POST, instance=request.user)
#         # prof_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
#         # if user_form.is_valid() and prof_form.is_valid():
#         if user_form.is_valid():
#             user_form.save()
#             # prof_form.save()
#             messages.success(request, 'Account updated')
#             return redirect('profile')
#     else:
#         user_form = UserUpdateForm(instance=request.user)
#         # prof_form = ProfileUpdateForm(instance=request.user.profile)
#     context = {
#         'user_form': user_form,
#         # 'prof_form': prof_form,
#     }
#     return render(request, 'users/profile.html', context)