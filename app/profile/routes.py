"""
Profile and settings routes for ALTO.
Handles user preferences, currency customization, and secure password updates.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.profile import profile_bp
from app.extensions import db
from app.forms import UpdateProfileForm, ChangePasswordForm


@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def index():
    """Display user profile settings with forms to update details and password."""
    profile_form = UpdateProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    # Distinguish which form was submitted
    if 'submit_profile' in request.form and profile_form.validate_on_submit():
        current_user.name = profile_form.name.data.strip()
        current_user.currency = profile_form.currency.data
        db.session.commit()
        flash('Your profile settings have been updated successfully!', 'success')
        return redirect(url_for('profile.index'))

    if 'submit_password' in request.form and password_form.validate_on_submit():
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Your password has been changed securely!', 'success')
        return redirect(url_for('profile.index'))

    return render_template(
        'profile/profile.html',
        title='Account Settings',
        profile_form=profile_form,
        password_form=password_form
    )
