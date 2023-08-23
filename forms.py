from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DateField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Sign Me Up!")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Let Me In!")


class CommentForm(FlaskForm):
    comment_text = CKEditorField("Comment", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class MasterSalesForm(FlaskForm):
    """
sr.no.	Date	Particulars	Address	GSTIN/UIN	Quantity	CONTACT NO.	NAME	EMAIL ID

    """
    date = StringField(label="Date", name="date", validators=[DataRequired()])
    company_name = StringField(label="Company Name", name="company_name", validators=[DataRequired()])
    gst_no = StringField(label="GST NO", name="gst_no")
    address = StringField(label="Company Address", name="address")
    quantity = StringField(label="Number of Machine", name="quantity", validators=[DataRequired()])
    machine_srno = StringField(label="Machine Serial No", name="machine_srno", validators=[DataRequired()])
    contact_name = StringField(label="Contact Person Name", name="contact_name")
    contact_number = StringField(label="Contact No", name="contact_number")
    email_id = StringField(label="Email ID", name="email_id")
    submit = SubmitField("Submit")


class AMCDataForm(FlaskForm):
    date = DateField(label="Date", name="date", validators=[DataRequired()])
    amc_taken = StringField(label="AMC Taken By", name="amc_taken", validators=[DataRequired()])
    payment_status = BooleanField(label="Payment Status", name="payment_status", validators=[DataRequired()])
    payment_way = StringField()
    submit = SubmitField("Submit")


class AMCServiceDetailForm(FlaskForm):
    date = DateField(label="Date", name="date", validators=[DataRequired()])
    which_service = StringField(label="Service Type: ex: Service1, other", name="which_service", validators=[DataRequired()])
    service_done_by = StringField(label="Person Done Service", name="service_done_by", validators=[DataRequired()])
    service_detail = CKEditorField(label="Service Detail", name="service_detail", validators=[DataRequired()])
    submit = SubmitField("Submit")
