from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
class ReverseReservationForm(FlaskForm):
    vehicle_registration = StringField('Vehicle Registration Number', 
                                     validators=[DataRequired(), Length(min=3, max=20)])
    drivers_license = StringField("Driver's License Number", 
                                 validators=[DataRequired(), Length(min=6, max=20)])
    reason = SelectField('Reason for Reversing', 
                        choices=[
                            ('', 'Select a reason'),
                            ('early_departure', 'Leaving earlier than expected'),
                            ('change_plans', 'Change of plans'),
                            ('found_better', 'Found a better spot'),
                            ('other', 'Other reason')
                        ], 
                        validators=[DataRequired()])
    notes = TextAreaField('Additional Notes', 
                         validators=[Length(max=500)])
    submit = SubmitField('Confirm Reversal')
class ReleaseSpotForm(FlaskForm):
    vehicle_registration = StringField('Vehicle Registration Number', 
                                     validators=[DataRequired(), Length(min=3, max=20)])
    drivers_license = StringField("Driver's License Number", 
                                 validators=[DataRequired(), Length(min=6, max=20)])
    payment_method = SelectField('Payment Method',
                               choices=[
                                   ('', 'Select payment method'),
                                   ('credit_card', 'Credit Card'),
                                   ('debit_card', 'Debit Card'),
                                   ('upi', 'UPI'),
                                   ('net_banking', 'Net Banking'),
                                   ('wallet', 'Wallet')
                               ],
                               validators=[DataRequired()])
    card_number = StringField('Card Number', 
                            validators=[Optional(), Length(min=12, max=19)])
    card_expiry = StringField('Expiry Date (MM/YY)', 
                             validators=[Optional(), Length(min=5, max=5)])
    card_cvv = StringField('CVV', 
                          validators=[Optional(), Length(min=3, max=4)])
    upi_id = StringField('UPI ID', 
                        validators=[Optional(), Length(max=50)])
    submit = SubmitField('Confirm Payment & Release')
    def validate(self, **kwargs):
        if not super().validate():
            return False
        self.card_number.errors = []
        self.card_expiry.errors = []
        self.card_cvv.errors = []
        self.upi_id.errors = []
        payment_method = self.payment_method.data
        if payment_method in ['credit_card', 'debit_card']:
            if not self.card_number.data:
                self.card_number.errors.append('Card number is required')
            if not self.card_expiry.data:
                self.card_expiry.errors.append('Expiry date is required')
            if not self.card_cvv.data:
                self.card_cvv.errors.append('CVV is required')
            if self.card_number.errors or self.card_expiry.errors or self.card_cvv.errors:
                return False
        elif payment_method == 'upi':
            if not self.upi_id.data:
                self.upi_id.errors.append('UPI ID is required')
                return False
        elif payment_method in ['net_banking', 'wallet']:
            pass
        return True