import datetime
from datetime import date
from functools import wraps

from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from forms import LoginForm, RegisterForm, CreatePostForm, CommentForm, MasterSalesForm, AMCDataForm, \
    AMCServiceDetailForm
# from test import master_sales
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kdlimpexDatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


MASTER_SALES_AMC = []
NON_AMC = []
AMC = []
MASTER_SALES_NON_AMC = []
FORMATE_DATE = '%d-%m-%Y'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


class MasterSales(db.Model):
    __tablename__ = "master_sales"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    company_name = db.Column(db.String(50))
    gst_no = db.Column(db.String(30))
    address = db.Column(db.String(150))
    quantity = db.Column(db.String(10))
    machine_serial_no = db.Column(db.String(20))
    contact_name = db.Column(db.String(20))
    contact_number = db.Column(db.String(15))
    email_id = db.Column(db.String(30))
    # relationship with AmcDate
    amc_detail = relationship("AMCData", back_populates="master_sales_detail")


class AMCData(db.Model):
    __tablename__ = "amc_data"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    amc_taken = db.Column(db.String(30))
    payment_status = db.Column(db.Boolean)
    payment_way = db.Column(db.String)
    # servicr1_date = db.Column(db.String(10))
    # servicr2_date = db.Column(db.String(10))
    # servicr3_date = db.Column(db.String(10))
    # service1 = db.Column(db.Text())
    # service2 = db.Column(db.Text())
    # service3 = db.Column(db.Text())
    # other = db.Column(db.Text())
    # master sales detail relation ship
    mastersales_id = db.Column(db.Integer, db.ForeignKey("master_sales.id"))
    master_sales_detail = relationship("MasterSales", back_populates="amc_detail")

    # relationship with amc service detail
    amc_service_detail = relationship("AMCServiceDetail", back_populates="amc_date_detail")


class AMCServiceDetail(db.Model):
    __tablename__ = "amc_service_detail"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    servicr_done_by = db.Column(db.String(10), nullable=False)
    which_service = db.Column(db.String(10), nullable=False)
    service_detail = db.Column(db.Text, nullable=False)
    # AMC date detail relation ship
    amc_date_id = db.Column(db.Integer, db.ForeignKey("amc_data.id"))
    amc_date_detail = relationship("AMCData", back_populates="amc_service_detail")


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_all_posts"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    form = CommentForm()
    requested_post = BlogPost.query.get(post_id)

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()

    return render_template("post.html", post=requested_post, form=form, current_user=current_user)


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/master-sales")
@login_required
def show_all_mastersales():
    all_sales = db.session.execute(db.Select(MasterSales)).fetchall()

    return render_template("master-sales/master-sales.html", all_sales=all_sales)


@app.route("/create-master-sales", methods=["POST", "GET"])
@login_required
def create_mastersales():
    form = MasterSalesForm()
    if form.validate_on_submit():
        add_master_sales = MasterSales(
            date=form.date.data or None,
            company_name=form.company_name.data or None,
            gst_no=form.gst_no.data or None,
            address=form.address.data or None,
            quantity=form.quantity.data or None,
            machine_serial_no=form.machine_srno.data or None,
            contact_name=form.contact_name.data or None,
            contact_number=form.contact_number.data or None,
            email_id=form.email_id.data or None,
        )
        # print(form.data)
        db.session.add(add_master_sales)
        db.session.commit()
    return render_template("master-sales/master-sales-form.html", form=form)


@app.route("/edit-master-sales/<int:post_id>", methods=["GET", "POST"])
def edit_sales(post_id):
    mastersale = db.session.get(MasterSales, post_id)
    edit_form = MasterSalesForm(
        date=mastersale.date,
        company_name=mastersale.company_name,
        gst_no=mastersale.gst_no,
        address=mastersale.address,
        quantity=mastersale.quantity,
        machine_srno=mastersale.machine_serial_no,
        contact_name=mastersale.contact_name,
        contact_number=mastersale.contact_number,
        email_id=mastersale.email_id,
    )
    if edit_form.validate_on_submit():
        mastersale.date = edit_form.date.data
        mastersale.company_name = edit_form.company_name.data
        mastersale.gst_no = edit_form.gst_no.data
        mastersale.address = edit_form.address.data
        mastersale.quantity = edit_form.quantity.data
        mastersale.machine_serial_no = edit_form.machine_srno.data
        mastersale.contact_name = edit_form.contact_name.data
        mastersale.contact_number = edit_form.contact_number.data
        mastersale.email_id = edit_form.email_id.data
        db.session.commit()
        return redirect(url_for("show_mastersales"))

    return render_template("master-sales/master-sales-form.html", form=edit_form, is_edit=True)


@app.route("/master-sales/<int:mastersales_id>", methods=["GET", "POST"])
def show_mastersales_single(mastersales_id):
    requested_mastersales_detail = db.session.get(MasterSales, mastersales_id)
    return render_template("master-sales/mastersales-detail.html", master_sale_detail=requested_mastersales_detail)


@app.route("/show-amc")
def show_amc():
    master_sales = []
    amc2 = db.session.execute(db.Select(AMCData)).fetchall()
    all_sales = db.session.execute(db.Select(MasterSales)).fetchall()
    for mastersale_amc in all_sales:
        if (datetime.datetime.strptime(mastersale_amc[0].date, FORMATE_DATE).date() + datetime.timedelta(days=365)) > datetime.datetime.today().date():
            master_sales.append(mastersale_amc)
        else:
            MASTER_SALES_NON_AMC.append(mastersale_amc)

    print(master_sales)

    return render_template("amc/show-amc.html", amcs= amc2, under_warrantymachine = master_sales)


@app.route("/amc-date/<int:companyid>", methods=["GET", "POST"])
def create_amc_date(companyid):
    form = AMCDataForm()
    if form.validate_on_submit():
        print(type(form.date.data))
        print(type(form.payment_status.data))

        add_amc = AMCData(
            date=form.date.data,
            amc_taken=form.amc_taken.data,
            payment_status=form.payment_status.data,
            payment_way=form.payment_way.data,
            mastersales_id=companyid
        )
        db.session.add(add_amc)
        db.session.commit()
        return redirect(url_for("show_mastersales_single", mastersales_id=companyid))
    return render_template("amc/amc-date-form.html", form=form)


@app.route("/add-amc-detail/<int:companyid>/<int:amc_id>", methods=["GET", "POST"])
def create_amc_service_detail(companyid, amc_id):
    print(request.args)
    form = AMCServiceDetailForm()
    if form.validate_on_submit():
        add_amc_service = AMCServiceDetail(
            date=form.date.data,
            servicr_done_by=form.service_done_by.data,
            which_service=form.which_service.data,
            service_detail=form.service_detail.data,
            amc_date_id=amc_id
        )
        db.session.add(add_amc_service)
        db.session.commit()
        return redirect(url_for("show_mastersales_single", mastersales_id=companyid))
    return render_template("amc/amc-detail-form.html", form=form)


# show-amc
@app.route("/amc-servics/<int:amc_id>")
def show_amc_detail(amc_id):
    amc_servies = db.session.execute(db.Select(AMCServiceDetail).where(AMCServiceDetail.amc_date_id == amc_id)).fetchall()
    for am in amc_servies:
        print(am)
    return render_template("amc/show-amc-detail.html", amcs = amc_servies)
@app.route("/show-non-amc")
def show_non_amc():
    non_amc = []
    amc = db.session.execute(db.Select(AMCData)).fetchall()
    all_sales = db.session.execute(db.Select(MasterSales)).fetchall()
    for mastersale_amc in all_sales:
        if (datetime.datetime.strptime(mastersale_amc[0].date, FORMATE_DATE).date() + datetime.timedelta(
                days=365)) < datetime.datetime.today().date():
            non_amc.append(mastersale_amc)
        else:
            MASTER_SALES_NON_AMC.append(mastersale_amc)

    for i in range(len(non_amc)):
        # print(non_amc[i][0].id)
        for single_amc in amc:
            # print(single_amc[0].mastersales_id)
            # print(non_amc[i][0].id)
            if single_amc[0].mastersales_id == non_amc[i][0].id:
                non_amc.pop(i)
                break

    return render_template("/non-amc/show-non-amc.html", non_amc=non_amc)

@app.route("/adding-extra-data-crm")
def add_data():
    data = []
    for sales in data:
        add_master_sales = MasterSales(
            date=sales["Date"],
            company_name=sales["Particulars"],
            gst_no=sales["GSTIN\\/UIN"],
            address=sales["Address"],
            quantity=sales["QUantity"],
            machine_serial_no=None,
            contact_name=sales["NAME"],
            contact_number=sales["CONTACT NO."],
            email_id=sales["EMAIL ID"],
        )
        # print(form.data)
        db.session.add(add_master_sales)
        db.session.commit()
    return "SuccessFully added to database"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
