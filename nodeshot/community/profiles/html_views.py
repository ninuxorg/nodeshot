from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.http import base36_to_int
from django.utils.translation import ugettext
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
User = get_user_model()

from .forms import ResetPasswordKeyForm
from .settings import settings, EMAIL_CONFIRMATION


def group_and_bridge(kwargs):
    """
    Given kwargs from the view (with view specific keys popped) pull out the
    bridge and fetch group from database.
    """

    bridge = kwargs.pop("bridge", None)

    if bridge:
        try:
            group = bridge.get_group(**kwargs)
        except ObjectDoesNotExist:
            raise Http404
    else:
        group = None

    return group, bridge


def group_context(group, bridge):
    # @@@ use bridge
    return {
        "group": group,
    }


def password_reset_from_key(request, uidb36, key, **kwargs):
    form_class = kwargs.get("form_class", ResetPasswordKeyForm)
    template_name = kwargs.get("template_name", "profiles/password_reset_from_key.html")
    token_generator = kwargs.get("token_generator", default_token_generator)

    group, bridge = group_and_bridge(kwargs)
    ctx = group_context(group, bridge)

    # pull out user
    try:
        uid_int = base36_to_int(uidb36)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)

    if token_generator.check_token(user, key):
        if request.method == "POST":
            password_reset_key_form = form_class(request.POST, user=user, temp_key=key)
            if password_reset_key_form.is_valid():
                password_reset_key_form.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    ugettext(u"Password successfully changed.")
                )
                password_reset_key_form = None
        else:
            password_reset_key_form = form_class()
        ctx.update({
            "form": password_reset_key_form,
        })
    else:
        ctx.update({
            "token_fail": True,
        })

    return render_to_response(template_name, RequestContext(request, ctx))


if EMAIL_CONFIRMATION:
    from .models import EmailConfirmation, EmailAddress
    from django.contrib.auth import login

    def confirm_email(request, confirmation_key):
        """ confirm email view """
        confirmation_key = confirmation_key.lower()
        # get email confirmation or 404
        email_confirmation = get_object_or_404(EmailConfirmation, key=confirmation_key)
        # make primary if no other primary addresses for this user
        make_primary = EmailAddress.objects.filter(
            user_id=email_confirmation.email_address.user_id,
            primary=True
        ).count() <= 0
        # confirm email
        email_address = EmailConfirmation.objects.confirm_email(
            confirmation_key,
            make_primary=make_primary
        )
        # log in the user if not already authenticated
        if email_address and not request.user.is_authenticated():
            user = email_address.user
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
        return redirect(settings.SITE_URL)
