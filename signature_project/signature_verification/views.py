from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import numpy as np
from PIL import Image
from keras.models import load_model
from .forms import RegistrationForm, LoginForm, VerificationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail

from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator


# Define model paths based on your structure
MODEL_PATHS = {
    "bi_rnn": os.path.join(settings.BASE_DIR, "signature_verification/models/bi_rnn_signature_verification_model.h5"),
    "rnn": os.path.join(settings.BASE_DIR, "signature_verification/models/rnn_signature_verification_model.h5"),
    "crnn": os.path.join(settings.BASE_DIR, "signature_verification/models/crnn_signature_verification_model.keras"),
}

# Load models
bi_rnn_model = load_model(MODEL_PATHS["bi_rnn"])
rnn_model = load_model(MODEL_PATHS["rnn"])
crnn_model = load_model(MODEL_PATHS["crnn"])

def preprocess_image(image_file, model_type, img_size=(128, 128)):
    """
    Preprocess the uploaded image based on the model type.
    - Resizes to `img_size`.
    - Normalizes pixel values to [0, 1].
    - Reshapes based on model type requirements.
    """
    try:
        image = Image.open(image_file).convert("L")  # Convert to grayscale
        image = image.resize(img_size)  # Resize to match model input size
        image_array = np.array(image) / 255.0  # Normalize to range [0, 1]

        if model_type == "bi_rnn":  # For bi_rnn, flatten and add sequence dimension
            image_array = image_array.flatten()  # Shape: (16384,)
            image_array = image_array.reshape(1, 1, -1)  # Shape: (1, 1, 16384)

        elif model_type == "rnn" or model_type == "crnn":  # For rnn and crnn, add channel dimension
            image_array = image_array.reshape(1, *img_size, 1)  # Shape: (1, 128, 128, 1)

        return image_array
    except Exception as e:
        raise ValueError(f"Error processing image for {model_type}: {e}")

def get_model_predictions(image_file):
    """
    Get predictions from all three models and compute the average.
    """
    # Preprocess for each model
    bi_rnn_input = preprocess_image(image_file, model_type="bi_rnn")
    

    # Get predictions
    bi_rnn_pred = bi_rnn_model.predict(bi_rnn_input)
    
    # Debugging predictions
    print(f"bi_rnn_pred: {bi_rnn_pred}")
    
    avg_pred = (bi_rnn_pred  )
    print(f"Averaged prediction: {avg_pred}")

    # Determine result
    result = "Real" if avg_pred[0][0] > 0.5 else "Forged"
    confidence = avg_pred[0][0] * 100 if result == "Real" else (1 - avg_pred[0][0]) * 100
    return result, confidence

def verification(request):
    """
    Handle signature verification using multiple models.
    """
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid():
            purpose = form.cleaned_data['purpose']
            image_file = request.FILES.get('image')  # Uploaded image file
            # Save image to the MEDIA directory
            fs = FileSystemStorage()  # Specify the subdirectory if needed
            filename = fs.save(image_file.name, image_file)  # Save the image
            image_url = fs.url(filename)
            try:
                # Preprocess the image for each model
                result, confidence = get_model_predictions(image_file)

                # Render the result page
                return render(request, 'result.html', {
                    'purpose': purpose,
                    'result': result,
                    'accuracy': confidence,
                    'image': image_url,  # Pass the image file for display
                })
            except Exception as e:
                print(f"Error during verification: {e}")
                messages.error(request, f"Verification failed: {e}")
                return redirect('verification')
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = VerificationForm()

    return render(request, 'verification.html', {'form': form})

def index(request):
    return render(request, 'index.html')  # Ensure index.html exists in templates
# Forgot password view

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())
            reset_link = f"http://{get_current_site(request).domain}/reset_password/{uid}/{token}"

            # Send password reset email
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link below to reset your password: {reset_link}',
                from_email='no-reply@yourdomain.com',  # Replace with a valid sender email
                recipient_list=[email],
            )

            messages.success(request, 'Password reset email has been sent.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
            return render(request, 'forgot_password.html')

    return render(request, 'forgot_password.html')

# Registration view

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']

            # Check if the username or email already exists
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, 'This username is already registered. Try logging in.')
            elif User.objects.filter(email__iexact=email).exists():
                messages.error(request, 'This email is already registered. Try logging in.')
            else:
                # Save new user and redirect to login with success message
                form.save()
                messages.success(request, 'Registration successful. You can now log in.')
                return redirect('login')

        # If form is invalid or duplicate data exists, re-render the form with messages
        return render(request, 'register.html', {'form': form})
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:  # Check if the user was authenticated successfully
                login(request, user)  # Log the user in
                return redirect('verification')  # Redirect to the verification page
            else:
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'Invalid username or password'
                })
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
def logout_view(request):
    """
    Handle user logout.
    """
    logout(request)
    return redirect("index")

def result_view(request):
    return render(request, "result.html")