from flask_wtf import FlaskForm
from wtforms import StringField, TimeField, TextAreaField
from wtforms.validators import DataRequired

class CheckoutForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    pickup_time = StringField('Pickup Time', validators=[DataRequired()])
    upi_id = StringField('UPI ID', validators=[DataRequired()])
    notes = TextAreaField('Notes')
