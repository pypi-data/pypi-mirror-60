from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from . import models
from .utils import code_generator
from .utils.shortcuts import json_response, dictify
from .utils.decorators import ensure_signed_in
from .api import get_verification_code, get_verification_link
import logging
from threading import Thread
from django.conf import settings
from django.core import signing
import re
from django.db import IntegrityError
from django.core.mail import send_mail
from . import signals 

logger = logging.getLogger("AccountRecoveryApp.views")
User = get_user_model()

def create_verification(request):
    """
        creates a verification object and attaches it to the user
    """
    username = request.POST.get("username")
    if username:
        try:
            user = User.objects.get(**{
                User.USERNAME_FIELD: username
            })
        except User.DoesNotExist:
            return json_response(False, error="Account not found")
    else:
        user = request.user
    verification, created = models.Verification.objects.get_or_create(user=user)
    if created or not verification.username_signature:
        verification.username_signature = signing.Signer().signature(user.get_username())
    if request.POST.get("mode", "") == "send":
        verification.code = code_generator.generate_number_code(settings.ACCOUNTS_APP["code_length"])
    verification.code_signature = signing.Signer().signature(verification.code)
    verification.save()
    return verification

def send_verification_mail(verification, subject, message, error):
    """
        sends verification mail utility. Used in lambda functions for extra readability
    """
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [verification.user.__dict__[User.get_email_field_name()]])
    except Exception as e:
        logger.error(error %e)

def send_verification_code(request):
    """
        Sends a verification code to the user via email. 
        This view is used for both sending and resending the code depending on the value of the GET variable "mode".
    """
    verification = create_verification(request)
    if type(verification) is not models.Verification:
        return verification
    message = "Your verification code is %s" %(verification.code)
    verification.recovery = True
    verification.save()
    error = "Failed to send verification code to %s <%s> by email\n %s" %(verification.user.__dict__[User.USERNAME_FIELD], verification.user.__dict__[User.get_email_field_name()], "%s")
    Thread(target=lambda: send_verification_mail(verification, "Account Verification", message, error)).start()
    signals.verification_code_sent.send(sender=send_verification_code, request=request, verification=verification)
    return json_response(True)

def send_verification_link(request):
    """
        sends the user a link for verification
    """
    verification = create_verification(request)
    if type(verification) is not models.Verification:
        return verification
    message = "Please follow the link below to verify your account\n %s/%s/verify-link/?u=%s&c=%s" %(request.META["HTTP_HOST"], settings.ACCOUNTS_APP["base_url"], verification.username_signature, verification.code_signature)
    verification.recovery = True
    verification.save()
    error = "Failed to send verification code to %s <%s> by email\n %s" %(verification.user.__dict__[User.USERNAME_FIELD], verification.user.__dict__[User.get_email_field_name()], "%s")
    Thread(target=lambda: send_verification_mail(verification, "Account Verification", message, error)).start()
    signals.verification_link_sent.send(sender=send_verification_link, request=request, verification=verification)
    return json_response(True)

def verify_code(request):
    """ 
        Verifies the user via code.
    """
    try:
        verification = models.Verification.objects.get(**{
            "user__%s" %User.USERNAME_FIELD: request.POST["username"],
            "code": request.POST["code"]
        })
        if not verification.recovery:
            return json_response(False, error="Incorrect verification code.")
        verification.verified = True
        verification.save()
        signals.code_verified.send(sender=verify_code, request=request, verification=verification)
        return json_response(True)
    except models.Verification.DoesNotExist:
        return json_response(False, error="Incorrect verification code.")

def verify_link(request):
    """ 
        Verifies the user via link.
    """
    try:
        verification = models.Verification.objects.get(username_signature=request.GET["u"], code_signature=request.GET["c"])
        if not verification.recovery:
            return json_response(False, error="Incorrect verification code.")
        verification.verified = True
        verification.save()
        if settings.ACCOUNTS_APP["sign_in_after_verification"]:
            login(request, verification.user)
        signals.link_verified.send(sender=verify_link, request=request, verification=verification)
        return HttpResponseRedirect("{0}?u={1}&c={2}".format(settings.ACCOUNTS_APP["redirect_link"], request.GET["u"], request.GET["c"]))
    except models.Verification.DoesNotExist:
        return HttpResponseNotFound()

def reset_password(request):
    """
        Resets the password of the user.
    """
    try:
        verification = models.Verification.objects.get(**{
            "user__%s" %User.USERNAME_FIELD: request.POST["username"],
            "code": request.POST["code"]
        })
        if not verification.recovery:
            return HttpResponseNotFound()
        verification.recovery = False
        verification.user.set_password(request.POST["new_password"])
        verification.user.save()
        signals.password_reset.send(sender=reset_password, request=request, verification=verification)
    except models.Verification.DoesNotExist:
        return json_response(False, error="Incorrect verification code.")
    return json_response(True)

@ensure_signed_in
def change_password(request):
    """
        changes the password of the user
    """
    if authenticate(username=request.user._wrapped.__dict__[request.user.USERNAME_FIELD], password=request.POST["old_password"]):
        request.user.set_password(request.POST["new_password"])
        signals.password_changed.send(sender=change_password, request=request, user=request.user)
        return json_response(True)
    return json_response(False, error="Incorrect password")

def sign_in(request):
    """
        logs the user in
    """
    user = authenticate(request, **dictify(request.POST))
    if user:
        if request.GET.get("r", "false") == "false":
            request.session.set_expiry(0)
        login(request, user)
        signals.signed_in.send(sender=sign_in, request=request, user=user)
        return json_response(True)
    return json_response(False, error="Incorrect credentials")

def sign_up(request):
    """
        creates a new user
    """
    try:
        user = User(**dictify(request.POST))
        user.set_password(request.POST["password"])
        user.save()
        if request.GET.get("r", "false") == "false":
            request.session.set_expiry(0)
        login(request, user)
        signals.signed_up.send(sender=sign_up, request=request, user=user)
        return json_response(True)
    except IntegrityError as e:
        print(e)
        return json_response(False, error=e.args)

@ensure_signed_in
def authenticate_user(request):
    """
        authenticates the user
    """
    if request.user.check_password(request.POST["password"]):
        return json_response(True)
    else:
        return json_response(False)

def sign_out(request):
    """
        signs out the user
    """
    try:
        logout(request)
    except:
        pass
    signals.signed_out.send(sender=sign_out)
    return json_response(True)
