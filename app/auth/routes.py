from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import UserLoginForm, RegistrationForm, ChangePasswordForm, \
	    PasswordResetRequestForm, PasswordResetForm
from app.models import User
from app.sendSMS import send_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = UserLoginForm()
	if form.validate_on_submit():
		print("Form validated")
		user = User.query.filter_by(email=form.email.data).first()
		print(user, user is None)
		if user is None or not user.check_password(form.password.data):
			flash('Invalid email or password')
			return redirect(url_for('auth.login', form=form))
		login_user(user, remember=form.remember_me.data)
		flash("Logged in as {}".format(user.email))
		return redirect(url_for('main.index'))
	return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('auth.login'))



@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email('Confirm Your Account', current_app.config['ADMINS'][0],
        			[user.email], "auth/confirmEmail.txt",
                   'auth/confirmEmail.html', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/confirm/<token>')
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    user = User.query.filter_by(id=User.get_token_id(token)).first()
    if user:
        login_user(user)
        user.confirm(token)
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@bp.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email('Confirm Your Account', current_app.config['ADMINS'][0],
    	        [current_user.email], 'auth/confirmEmail.txt', 
    	        'auth/confirmEmail.html', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template("auth/change_password.html", form=form)


@bp.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email('Reset Your Password', current_app.config['ADMINS'][0],
    	        [user.email], 'auth/reset_password_email.txt',
               'auth/reset_password_email.html', user=current_user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)