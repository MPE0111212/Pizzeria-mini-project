from datetime import date
from PIL import Image
import numpy
import qrcode

LOCAL_IP = "192.168.0.0"  # Обязательно поменять на ip компьютера, чтобы работал qr код
port = "8000"

menu = {"Маргарита": 1100, "Пепперони не острая": 1000, "Тесто": 100,
        "Пицца с ананасами": 900, "Вода": 100, "Сок": 200, "Кидс": 950, "Мясная пицца": 1010, "Деревенская пицца": 1050,
        "Сырная пицца": 1199, "Гавайская пицца": 1259}
spec_menu = {"Маргарита с весом 100 тонн": 5000, "Газировка": 300, "Пепперони очень острая": 1100, "Лимонад": 259}
ingredients = {"Колбаса": 50, "Грибы": 60, "Огурцы": 40, "Кетчуп": 20, "Майонез": 15, "Сыр": 25, "Оливки": 10,
               "Горчица": 45, "Бекон": 55, "Помидоры": 35, "Лук": 15, "Шпинат": 20}
info = []
purchases = {}
custom_pizzas_amt = 0


def show_menu():
    print(f"\n{' ' * 12}МЕНЮ{' ' * 12}")
    print("-" * 30)
    for k, v in menu.items():
        print(f"{k}: стоимость {v}")
    print("-" * 30)
    if info[3] >= 18:
        print("МЕНЮ ДЛЯ ВЗРОСЛЫХ")
        for k, v in spec_menu.items():
            print(f"{k}: стоимость - {v} рублей")
        print("-" * 30)


def test_info(name, surname, lastname, age):
    correct_name = True
    for i in range(1, len(name)):
        if not name[i].islower():
            correct_name = False
            break
    correct_name = correct_name and name[0].isupper()
    correct_surname = True
    for i in range(1, len(surname)):
        if not surname[i].islower():
            correct_surname = False
            break
    correct_surname = correct_surname and surname[0].isupper()
    correct_lastname = True
    for i in range(1, len(lastname)):
        if not lastname[i].islower():
            correct_lastname = False
            break
    correct_lastname = correct_lastname and lastname[0].isupper()
    if age > 140 or age < 1 or not correct_name or not correct_surname or not correct_lastname:
        return False
    return True


def get_info():
    try:
        name = input("Введите ваше имя: ")
        surname = input("Введите вашу фамилию: ")
        lastname = input("Введите ваше отчество: ")
        age = int(input("Введите ваш возраст: "))
        if test_info(name=name, surname=surname, lastname=lastname, age=age):
            print("\nДанные приняты\n")
            return [name, surname, lastname, age]
        else:
            print("\nВведены неверные данные\n")
    except:
        print("\nВведены неверные данные\n")


def custom_pizza():
    global custom_pizzas_amt, purchases
    custom_pizzas_amt += 1
    cost = 100
    ingreds_in_custom_pizza = []
    flag = True
    while True:
        print("\nИнгредиенты")
        print("-" * 30)
        for k, v in ingredients.items():
            print(f"{k}: стоимость {v}")
        print("-" * 30)
        ingred = input("Введите ингредиент или ничего, чтобы завершить создание пиццы: ")
        flag = True
        if not ingred:
            print(f"{'-' * 30}\nКастомная пицца {custom_pizzas_amt}:\n - Тесто (100 рублей)")
            for i in ingreds_in_custom_pizza:
                print(f" - {i} ({ingredients[i]} рублей)")
            print(f"ИТОГО: {cost} РУБЛЕЙ\n{'-' * 30}")
            action = input(
                "Введите 1, чтобы подтвердить, 0, чтобы удалить пиццу, или любой другой символ, чтобы продолжить добавление ингредиентов: ")
            if action == '1':
                print("Кастомная пицца была добавлена в заказ")
                purchases[f"Кастомная пицца {custom_pizzas_amt}"] = [cost, 1]
                break
            elif action == '0':
                print("Кастомная пицца была удалена")
                custom_pizzas_amt -= 1
                break
            else:
                flag = False
        elif flag:
            try:
                cost += ingredients[ingred]
                ingreds_in_custom_pizza.append(ingred)
            except:
                print("Такого ингредиента не существует")


def qr_code(d, client, summary):
    html_filename = "qr.html"
    qr_url = f"http://{LOCAL_IP}:{port}/{html_filename}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=0,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_filename = "qrcode.png"
    img.save(qr_filename)
    qr_character_list = numpy.array(Image.open(qr_filename)).tolist()
    qr_character_image = ""
    for r in qr_character_list:
        for c in r:
            if c == 1:
                qr_character_image += '⬜'
            else:
                qr_character_image += '⬛'
        qr_character_image += '\n'
    page_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <style>
    	    <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </style>
        <head>
        <title>PIZZERIA CASH RECEIPT</title>
        </head>
        <body>

        <pre>
    	            ПИЦЦЕРИЯ
        </pre>
        <p>{d}</p>
        <pre>
    	             Оплата	
        </pre>
        <p>Клиент: {client}</p>
        <p>Сумма (Руб): {summary}</p>
        <p>{'-' * 40}</p>
        <pre>
                  Товарный чек
        </pre>
        <p>ИНФОРМАЦИЯ НА САЙТЕ: pizzeria.fake.ru</p>
        <p>----------------------------------------</p>
        <p>ИТОГ К ОПЛАТЕ.....................{summary}</p>
        <p>----------------------------------------</p>
        <h1>ИТОГ = {summary}</h1>
        <p>{qr_character_image}</p>
        </body>
        </html>
        """
    with open(html_filename, "w") as f:
        f.write(page_content)
    return qr_character_image


def show_purchases(receipt=False):
    global purchases
    if not receipt:
        #  Вывод в виде предпросмотра заказа
        print(f"\nВаш заказ:\n{'-' * 30}")
        for k, v in purchases.items():
            print(f"{v[1]} {k}: {v[0]}")
        summary = 0
        for i in list(purchases.values()):
            summary += i[0]
        print(f"ИТОГО: {summary} РУБЛЕЙ\n{'-' * 30}")
        input("\nВведите что-либо, чтобы продолжить\n")
    else:
        #  Вывод в виде чека
        summary = 0
        d = f"{date.today().day}.{date.today().month}.{date.today().year % 100}"
        client = f"{info[0]} {info[1]} {info[2]}"
        for i in list(purchases.values()):
            summary += i[0]
        print(f"\n\n\n{' ' * 12}ПИЦЦЕРИЯ\n{d}\n"
              f"{' ' * 13}Оплата\nКлиент: {client}\nСумма (Руб): {float(summary)}\n"
              f"{'-' * 40}\n{' ' * 10}Товарный чек")
        for k, v in purchases.items():
            print(f"{v[1]} {k}: {float(v[0])}")
        print(
            f"ИНФОРМАЦИЯ НА САЙТЕ: pizzeria.fake.ru\n{'-' * 40}\nИТОГ К ОПЛАТЕ{'.' * 21}{float(summary)}\n{'-' * 40}\n"
            f"И Т О Г = {float(summary)}")
        print(qr_code(d, client, summary))
        input("\nВведите что-либо, чтобы продолжить\n")


def add_purchase(item):
    global purchases, menu, spec_menu
    try:
        purchases[item][0] += menu[item]
        purchases[item][1] += 1
        print(f"{item} был добавлен в заказ\n")
        return
    except:
        pass
    try:
        purchases[item] = [menu[item], 1]
        print(f"{item} был добавлен в заказ\n")
    except:
        if info[3] >= 18:
            try:
                purchases[item] = [spec_menu[item], 1]
                print(f"{item} был добавлен в заказ\n")
            except:
                print(f"В меню нет предмета {item}\n")
        else:
            print(f"В детском меню нет предмета {item}\n")


def pay():
    global purchases
    show_purchases(receipt=True)
    total_cost = 0
    for i in list(purchases.values()):
        total_cost += i[0]
    payment_type = input(
        "Введите 'н' для оплаты наличными, 'к' для оплаты картой, или любой другой символ для отмены: ")
    if payment_type == 'н':
        try:
            payment = 0
            while payment < total_cost:
                payment = int(input("Введите сумму к оплате наличными: "))
            print(f"Сдача: {payment - total_cost} рублей.\n")
            return True
        except:
            print("\nВведена неверная сумма к оплате наличными\n")
            return False
    elif payment_type == 'к':
        print(f"Сумма оплаты: {total_cost} рублей.\n")
        return True
    return False


#  Основная часть программы
print(
    "\n\n\n\n\n\n\n-----------Добро пожаловать в Пиццерию-----------\n"
    "Пожалуйста, введите ваше имя, фамилию и возраст:\n")
while not info:
    info = get_info()
print(f"\nЗдравстуйте, {info[0]} {info[1]}\n")
while True:
    show_menu()
    action = input(
        "\nВведите 1, чтобы посмотреть ваш заказ, 2, чтобы добавить предмет в заказ, "
        "3, чтобы добавить кастомную пиццу в заказ, 0, чтобы оплатить заказ: ")
    if action == '1':
        show_purchases()
    elif action == '2':
        add_purchase(input("\nВведите, какой предмет из меню вы хотите добавить в заказ: "))
    elif action == '3':
        custom_pizza()
    elif action == '0':
        if pay():
            print(f"\nСпасибо за покупку, {info[0]}!")
            break
