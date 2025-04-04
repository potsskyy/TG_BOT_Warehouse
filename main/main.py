from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup, KeyboardButton

import random

import os

from aiogram import Bot, Dispatcher
from aiogram import Router
from PIL import Image, ImageDraw, ImageFont

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

parts = ["Компрессоры","Ремонт ЭБУ","ПЗР","Термостаты","Импульсные клапаны","Испарители",
         "Вентиляторы","Дефростеры","Заслонки","ТЭНы","Датчики температуры"
        #  "ПРОЧЕЕ"
        ]

user_data = {}

async def start(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton(part, callback_data=part)] for part in parts]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Добавляем клавиатуру с кнопкой /start
    reply_keyboard = ReplyKeyboardMarkup([[KeyboardButton("/start")]], resize_keyboard=True)

    await update.message.reply_text("Выберите запчасть:", reply_markup=reply_markup)
    # await update.message.reply_text("Нажмите кнопку, чтобы начать заново", reply_markup=reply_keyboard)




async def handle_part_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    part = query.data
    chat_id = query.message.chat_id

    user_data[chat_id] = {
        "part": part,
        "prices": [],
        "messages": [],
        "brand": None,
        "awaiting_brand": True,
        "awaiting_prices": False,
        "awaiting_final_request": False
    }

    msg = await query.message.reply_text(f"Введите марку холодильника для {part}:")
    user_data[chat_id]["messages"].append(msg.message_id)

async def handle_text_input(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    
    if chat_id not in user_data:
        msg = await update.message.reply_text("Сначала выберите запчасть, нажав /start.")
        data["messages"].append(update.message.message_id)
        data["messages"].append(msg.message_id)
        return

    text = update.message.text
    data = user_data[chat_id]

    if data["awaiting_brand"]:
        data["brand"] = text
        data["awaiting_brand"] = False
        data["awaiting_prices"] = True
        msg = await update.message.reply_text(
            f"Марка холодильника '{text}' сохранена. Теперь введите стоимость для запчасти {data['part']}. Ввeдите стоимость на запчасть, которую считаете приемлемой. Вводите 'круглые числа'  Например: 4000 6000 8000"
        )
        data["messages"].append(update.message.message_id)
        data["messages"].append(msg.message_id)
    
    elif data["awaiting_prices"]:
        
        if len(data["prices"]) == 3:
            data["messages"].append(update.message.message_id)
           
        else:
            try:
                price = int(text)
                data["prices"].append(price)
                
                if len(data["prices"]) <3:
                    msg = await update.message.reply_text(f"{len(data['prices'])}. Добавлена цена: {price}. Введите еще")
                    data["messages"].append(update.message.message_id)
                    data["messages"].append(msg.message_id)
                    
                else: 
                    msg = await update.message.reply_text(f"{len(data['prices'])}. Добавлена цена: {price}.")
                    data["messages"].append(update.message.message_id)
                    data["messages"].append(msg.message_id)
                    # await ebanytu(update, context)  # Вызов функции
                    msg = await update.message.reply_text("Введите ваш итоговый запрос (если будете прикреплять фото запчасти, то сначала отправьте фото отдельным сообщением, а уже после пишите ваш запрос)")
                    data["messages"].append(msg.message_id)
                    data["awaiting_prices"] = False
                    data["awaiting_final_request"] = True
                    
                
                
            except ValueError:
                msg = await update.message.reply_text("Введите число.")
                data["messages"].append(update.message.message_id)
                data["messages"].append(msg.message_id)
    
    elif data["awaiting_final_request"]:
        for msg_id in data["messages"]:
            try:
                await context.bot.delete_message(chat_id, msg_id)
            except Exception:
                pass
        
        part = data["part"]
        brand = data["brand"]
        min_price, max_price = min(data["prices"]), max(data["prices"])
        
        if part == "Компрессоры":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость нового Компрессора составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Все будет зависеть от страны производства, энергопотребления и металла из которого сделаны обмотки компрессора. \n"
                 f"Компрессор — это сердце системы охлаждения. Выбирайте надежные модели, чтобы избежать проблем в будущем!" )
            await handle_numbers(update, context)  # Вызов функции
            
        elif  part == "Ремонт ЭБУ":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость ремонта вашей ЭБУ составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Все будет зависеть от повреждений процессора. Новая ЭБУ на данный холодильник будет стоить {int((max(data['prices']))*1.5)}. \n"
                 f"ЭБУ — это мозги системы охлаждения. Выбирайте надежные и оригинальные модели, чтобы избежать проблем в будущем!" )
            
        elif part == "ПЗР":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость Пускозащитного реле составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Все зависит от модели холодильника, типа компрессора и качества материалов, из которых изготовлено реле. \n"
                 f"Пускозащитное реле отвечает за запуск и защиту компрессора. Выбирайте качественные компоненты, чтобы продлить срок службы холодильника!" )
            await handle_numbers(update, context)  # Вызов функции
            
        elif part == "Термостаты":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость Термостата составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Стоимость зависит от типа термостата, его точности, диапазона температур и производителя. \n"
                 f"Термостат отвечает за поддержание нужной температуры в холодильнике. Выбирайте надежные модели, чтобы избежать проблем с охлаждением!" )
            await handle_numbers(update, context)  # Вызов функции
            
        elif part == "Импульсные клапаны":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость Импульсного клапана составит от {min(data['prices'])} до {max(data['prices'])} рублей\n"
                 f"Стоимость зависит от типа клапана, его производителя и материала изготовления. \n"
                 f"Импульсный клапан регулирует подачу хладагента в систему охлаждения, обеспечивая эффективную работу холодильника. Выбирайте качественные комплектующие для надежной работы устройства!")
            await handle_numbers(update, context)  # Вызов функции
             
        elif part == "Испарители":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость Испарителя составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Стоимость зависит от типа испарителя, материала изготовления и производителя. \n"
                 f"Испаритель отвечает за процесс охлаждения, превращая хладагент из жидкости в газ. От его качества зависит эффективность работы холодильника, поэтому выбирайте надежные и проверенные модели!" )
            await handle_numbers(update, context)  # Вызов функции
        
        elif part == "Вентиляторы":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость Вентилятора составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Стоимость зависит от мощности, материала изготовления и производителя. \n"
                 f"Вентилятор обеспечивает циркуляцию холодного воздуха внутри холодильника, равномерно распределяя температуру. Надёжный вентилятор — залог стабильной и эффективной работы устройства!" )
            await handle_numbers(update, context)  # Вызов функции
            
        elif part == "Дефростеры":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость Дефростера составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Цена зависит от типа дефростера, его мощности и совместимости с конкретными моделями холодильников. \n"
                 f"Дефростер предотвращает образование льда на испарителе, обеспечивая стабильную работу системы охлаждения. Выбирайте качественные комплектующие для надежной эксплуатации!" )
            await handle_numbers(update, context)  # Вызов функции
            
        elif part == "Заслонки":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость Заслонки составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Цена зависит от типа заслонки, её механизма работы (механическая или электронная) и совместимости с моделью холодильника. \n"
                 f"Заслонка регулирует подачу холодного воздуха между камерами, поддерживая оптимальную температуру. Выбирайте надежные детали, чтобы избежать проблем с охлаждением!" )
            await handle_numbers(update, context)  # Вызов функции
            
        elif part == "ТЭНы":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость ТЭНа составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Цена зависит от мощности нагревательного элемента, материала изготовления и совместимости с конкретной моделью холодильника. \n"
                 f"ТЭНы используются для разморозки испарителя и предотвращения образования наледи. Выбирайте качественные компоненты, чтобы продлить срок службы холодильника!" )
            await handle_numbers(update, context)  # Вызов функции
            
        elif part == "Датчики температуры":
            await update.message.reply_text(
                 f"Добрый день. Для холодильника фирмы {brand}, примерная стоимость датчика температуры составит от {min(data['prices'])} до {max(data['prices'])} рублей.\n"
                 f"Цена зависит от типа датчика, точности измерений и совместимости с конкретной моделью холодильника. \n"
                 f"Датчики температуры играют ключевую роль в поддержании оптимального режима охлаждения. Выбирайте надежные модели, чтобы обеспечить стабильную работу холодильника!" )
            await handle_numbers(update, context)  # Вызов функции
        
        del user_data[chat_id]
        



# async def ebanytu(update: Update, context: CallbackContext):
#     chat_id = update.message.chat_id
#     prices = sorted(user_data[chat_id]["prices"])
#     if prices[2]>100000: 
#         msg = await update.message.reply_text(f"Куда какие {max(prices)}")
#         user_data[chat_id]["messages"].append(update.message.message_id)
#         user_data[chat_id]["messages"].append(msg.message_id)
        
        
    

       






async def handle_numbers(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    # Получаем данные о ценах из user_data
    if chat_id not in user_data or "prices" not in user_data[chat_id]:
        await update.message.reply_text("Цены не были введены.")
        return

    prices = sorted(user_data[chat_id]["prices"]) #сортируем прайс чтоб фотки красиво шли во возрастанию
    part = user_data[chat_id]["part"]
    output_paths = ["images/output/output1.jpg", "images/output/output2.jpg", "images/output/output3.jpg"]

    


    if part == "Компрессоры":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/compressor/compressor1.jpg", "images/compressor/compressor2.jpg", "images/compressor/compressor3.jpg"]
        positions = [(310, 230), (310, 235), (310, 210)]  # Координаты текста
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/ARLRDBD.TTF", 40)

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], str(new_price), fill=(83, 137, 180), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
    
    elif part == "ПЗР":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/pzr/pzr1.jpg", "images/pzr/pzr2.jpg", "images/pzr/pzr3.jpg"]
        positions = [(145, 1183), (145, 1167), (135, 990)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 40)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)


    elif part == "Термостаты":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/thermostat/thermostat1.jpg", "images/thermostat/thermostat2.jpg", "images/thermostat/thermostat3.jpg"]
        positions = [(315, 245), (315, 242), (310, 245)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 25)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(83, 137, 180), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)

    elif part == "Импульсные клапаны":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/pulseValve/pulseValve1.jpg", "images/pulseValve/pulseValve2.jpg", "images/pulseValve/pulseValve3.jpg"]
        positions = [(515, 363), (845, 253), (145, 1196)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 30)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)

    elif part == "Испарители":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/evaporator/evaporator1.jpg", "images/evaporator/evaporator2.jpg", "images/evaporator/evaporator3.jpg"]
        positions = [(600, 160), (570, 155), (555, 162)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 30)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
    
    elif part == "Вентиляторы":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/fan/fan1.jpg", "images/fan/fan2.jpg", "images/fan/fan3.jpg"]
        positions = [(190, 1149), (185, 1182), (185, 1174)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 36)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
    
    elif part == "Дефростеры":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/defroster/defroster1.jpg", "images/defroster/defroster2.jpg", "images/defroster/defroster3.jpg"]
        positions = [(550, 137), (560, 142), (550, 136)]  # Координаты текста
        word = "руб/шт"  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 15)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)


    elif part == "Заслонки":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/flaps/flaps1.jpg", "images/flaps/flaps2.jpg", "images/flaps/flaps3.jpg"]
        positions = [(690, 187), (400, 198), (400, 206)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 24)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
        
    elif part == "ТЭНы":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/TEN/ten1.jpg", "images/TEN/ten2.jpg", "images/TEN/ten3.jpg"]
        positions = [(390, 170), (595, 168), (386, 205)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 24)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
    
    elif part == "Датчики температуры":
        # Пути к оригинальным и обработанным изображениям
        image_paths = ["images/temperatureSensor/temperatureSensor1.jpg", "images/temperatureSensor/temperatureSensor2.jpg", "images/temperatureSensor/temperatureSensor3.jpg"]
        positions = [(398, 207), (393, 208), (393, 209)]  # Координаты текста
        word = "руб."  # Заданное слово
        for i in range(len(prices)):  # Используем длину prices
            random_value = random.randrange(100, 300, 5)  # Генерируем случайное число от 120 до 350 с шагом 5
            new_price = prices[i] + random_value  # Добавляем к цене

            image = Image.open(image_paths[i])
            draw = ImageDraw.Draw(image)

             # Загружаем жирный шрифт
            font = ImageFont.truetype("fonts/fonts/arialbd.ttf", 20)

            text = f"{new_price} {word}"

            #Добавляем текст (цвет RGB: 83, 137, 180)
            draw.text(positions[i], text, fill=(0, 0, 0), font=font)

            # Сохраняем измененное изображение
            image.save(output_paths[i])
            with open(output_paths[i], 'rb') as photo_file:
                await context.bot.send_photo(chat_id=chat_id, photo=photo_file)
        

  
    

    

    
   



    

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_part_selection))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_input))

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
