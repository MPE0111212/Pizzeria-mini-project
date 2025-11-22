import logging as nonflask_logging
from random import randint
from markupsafe import Markup
from flask import *
import datetime
import qrcode
import re

menu = {"Маргарита": 1100, "Пепперони не острая": 1000, "Тесто": 100,
        "Пицца с ананасами": 900, "Вода": 100, "Сок": 200, "Кидс": 950, "Мясная пицца": 1010, "Деревенская пицца": 1050,
        "Сырная пицца": 1199, "Гавайская пицца": 1259}
spec_menu = {"Маргарита с весом 100 тонн": 5000, "Газировка": 300, "Пепперони очень острая": 1100, "Лимонад": 259}
ingredients = {"Колбаса": 100, "Грибы": 120, "Огурцы": 80, "Кетчуп": 40, "Майонез": 30, "Сыр": 50, "Оливки": 20,
               "Горчица": 90, "Бекон": 110, "Помидоры": 70, "Лук": 30, "Шпинат": 40}

app = Flask(__name__)
app.run(threaded=True)
app.logger.setLevel(nonflask_logging.DEBUG)

app.secret_key = b'qEfCC[20s=n\d,w/q1;D'

user_info_string = lambda: (f'Номер заказа: {session.get("order_number")}\nИмя: {session.get("name")}\nФамилия:{session.get("surname")}\nОтчество: {session.get("lastname")}\n'
    f'Возраст: {session.get("age")}\nАдрес электронной почты: {session.get("email")}\n'
    f'Телефонный номер: {session.get("phone")}')


def update_purchases_data():
    session['total_cost'] = 0
    session['purchases_list'] = ""
    for k, v in session.get("purchases").items():
        session['purchases_list'] += f"{v[1]} {k}: {float(v[0])}\n"
        session['total_cost'] += v[0] * v[1]


@app.template_filter('nl2br')
def nl2br_filter(s):
    return Markup(s.replace('\n', '<br>\n'))


def test_info(name, surname, lastname, age, phone_number, email):
    if not name or not surname or not lastname or not age or not phone_number or not email:
        return False
    if (not re.fullmatch(r'[А-Яа-яЁё-]+', name) or not re.fullmatch(r'[А-Яа-яЁё-]+', surname) or not re.fullmatch(r'[А-Яа-яЁё-]+', lastname)
            or not re.fullmatch(r'^[\d\s\-\(\)\+]+$', phone_number)
            or not re.fullmatch(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)):
        return False
    if name != name.capitalize():
        name = name.capitalize()
    if surname != surname.capitalize():
        surname = surname.capitalize()
    if lastname != lastname.capitalize():
        lastname = lastname.capitalize()
    try:
        if not 0 < int(age) < 140:
            age = 1
    except:
        age = 1
    return True


def qr_code():
    qr_url = f"{url_for('receipt')}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=3,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_filename = f"qrcode{session.get('order_number')}.png"
    img.save(qr_filename)
    return qr_filename


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['name'] = request.form.get('name', 'N/A')
        session['surname'] = request.form.get('surname', 'N/A')
        session['lastname'] = request.form.get('lastname', 'N/A')
        session['age'] = request.form.get('age', 'N/A')
        session['email'] = request.form.get('email', 'N/A')
        session['phone'] = request.form.get('phone', 'N/A')
        session['login'] = request.form.get('login', 'N/A')
        session['password'] = request.form.get('password', 'N/A')
        session['order_number'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G'][randint(0, 6)] + str(randint(1, 99))
        session['custom_pizzas_amt'] = 0
        session['total_cost'] = 0
        session['purchases_list'] = ""
        session['c_pizza_cost'] = 100
        session['ingreds_in_custom_pizza'] = []
        session['purchases'] = dict()
        if test_info(session.get("name"), session.get("surname"), session.get("lastname"), session.get("age"),
                     session.get("phone"), session.get("email")):
            return redirect(url_for('main_page'))
        else:
            return ("Введены неверные данные. Проверьте, что ФИО содержит только буквы, возраст - только цифры, "
                    "электронная почта верная, а телефонный номер соответствует формату +x-xxx-xxx-xx-xx или "
                    "x-xxx-xxx-xx-xx, где x - цифра от 0 до 9")
    return render_template("registration.html")


@app.route("/order/", methods=['GET', 'POST'])
def main_page():
    update_purchases_data()
    menu_string = f"\n{' ' * 12}МЕНЮ{' ' * 12}\n{'-' * 30}\n"
    for k, v in menu.items():
        menu_string += f"{k}: стоимость {v}\n"
    menu_string += "-" * 30 + '\n'
    if int(session.get("age")) >= 18:
        menu_string += "МЕНЮ ДЛЯ ВЗРОСЛЫХ\n"
        for k, v in spec_menu.items():
            menu_string += f"{k}: стоимость - {v} рублей\n"
        menu_string += "-" * 30
    order = f"Ваш заказ:\n{'-' * 30}\n{session.get('purchases_list')}\nИТОГО: {session.get('total_cost')} РУБЛЕЙ\n{'-' * 30}"
    return render_template("main_page.html", menu=menu_string, order_preview=order, user_info=user_info_string())


@app.route("/order/add_item", methods=["POST", "GET"])
def add_item():
    purchases = session.get('purchases')
    item = request.form.get("item_to_add", "N/A").strip()
    try:
        purchases[item][0] += menu[item]
        purchases[item][1] += 1
        session["purchases"] = purchases
        return redirect(url_for("main_page"))
    except:
        try:
            purchases[item][0] += spec_menu[item]
            purchases[item][1] += 1
            session["purchases"] = purchases
            return redirect(url_for("main_page"))
        except:
            pass
    try:
        purchases[item] = [menu[item], 1]
        session["purchases"] = purchases
        return redirect(url_for("main_page"))
    except:
        if int(session.get("age")) >= 18:
            try:
                purchases[item] = [spec_menu[item], 1]
                session["purchases"] = purchases
                return redirect(url_for("main_page"))
            except:
                return f"""В меню нет предмета {item}<br><a href="{url_for('main_page')}">Вернуться в меню оформелния заказа</a>"""
        else:
            return f"""В детском меню нет предмета {item}<br><a href="{url_for('main_page')}">Вернуться в меню оформелния заказа</a>"""


@app.route("/order/custom/", methods=["POST", "GET"])
def custom_pizza():
    session['custom_pizzas_amt'] += 1
    ingreds = "-" * 30 + '\n'
    for k, v in ingredients.items():
        ingreds += f"{k}: стоимость {v}\n"
    ingreds_in_pizza = " - Тесто (100 рублей)\n"
    for i in session.get("ingreds_in_custom_pizza"):
        ingreds_in_pizza += f" - {i} ({ingredients[i]} рублей)\n"
        session['c_pizza_cost'] += ingredients[i]
    return render_template("custom_pizza.html", ingreds_in_pizza=ingreds_in_pizza, ingredients=ingreds, user_info=user_info_string())


@app.route("/order/custom/add_ingredient", methods=["POST", "GET"])
def custom_pizza_add_ingredient():
    ingred = request.form.get("ingredient")
    try:
        session['c_pizza_cost'] += ingredients[ingred]
        session['ingreds_in_custom_pizza'].append(ingred)
        return redirect(url_for("custom_pizza"))
    except:
        return f"""Ингредиента {ingred} не существует<br><a href="{url_for('custom_pizza')}">Вернуться в меню создания кастомной пиццы</a>"""


@app.route("/order/custom/finish_custom_pizza", methods=["POST", "GET"])
def finish_custom_pizza():
    session["purchases"][f"Кастомная пицца {session.get('custom_pizzas_amt')}"] = [session.get('c_pizza_cost'), 1]
    session['c_pizza_cost'] = 100
    session['ingreds_in_custom_pizza'] = []
    return redirect(url_for("main_page"))


@app.route("/order/custom/decline", methods=["POST", "GET"])
def decline_custom_pizza():
    session['c_pizza_cost'] = 100
    session['ingreds_in_custom_pizza'] = []
    return redirect(url_for("main_page"))


@app.route("/order/pay/", methods=["POST", "GET"])
def pay():
    update_purchases_data()
    order = f"Ваш заказ:\n{'-' * 30}\n{session.get('purchases_list')}\nИТОГО: {session.get('total_cost')} РУБЛЕЙ\n{'-' * 30}"
    return render_template("pay.html", order_number=session.get("order_number"), purchases=order, total_cost=session.get('total_cost'), user_info=user_info_string())


@app.route("/order/pay/card", methods=["POST", "GET"])
def pay_card():
    bonus_info = "Вам не были начислены бонусы, так как вы не зарегистрированы"
    if session.get("login") and session.get("password"):
        bonus_info = f"На ваш аккаунт начислено {session.get('total_cost') // 10} бонусов"
    pay_info = "Оплата: картой"
    return render_template("thanks_for_the_purchase.html", order_number=session.get('order_number'), bonus_info=bonus_info, user_info=user_info_string(), pay_info=pay_info)


@app.route("/order/pay/cash", methods=["POST", "GET"])
def pay_cash():
    cash = 0
    try:
        cash = int(session.get("cash"))
    except:
        pass
    if cash and cash - session.get("total_cost") >= 0:
        bonus_info = "Вам не были начислены бонусы, так как вы не зарегистрированы"
        if session.get("login") and session.get("password"):
            bonus_info = f"На ваш аккаунт начислено {session.get('total_cost') // 10} бонусов"
        pay_info = f"Оплата: наличными\nСдача: {cash - session.get('total_cost')}"
        return render_template("thanks_for_the_purchase.html", order_number=session.get('order_number'),
                               bonus_info=bonus_info, user_info=user_info_string(), pay_info=pay_info)
    else:
        return redirect(url_for("pay"))


@app.route("/order/pay/receipt", methods=["POST", "GET"])
def receipt():
    update_purchases_data()
    return render_template("receipt.html", date=datetime.date.today(), order_number=session.get("order_number"), client=user_info_string(), total_cost=session.get("total_cost"), purchases_list=session.get("purchases_list"), qr_filename=qr_code())
