from flask import Flask
import telebot
import requests
import json
import threading
import os

app = Flask(__name__)

bot_token = '7227344044:AAEtkqtKng7GGgIJIUK7C2unVDqlwOHQlqs'
spoon = '4ea75d07744643a6a17eea36eb47140e'

bot = telebot.TeleBot(bot_token)

Details = {"cusine": "", "dish": "", "type": "", "diet": ""}

def recepie_getter(query1, cuisine1, type1, diet1):
    url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={spoon}&query={query1}&cuisine={cuisine1}&type={type1}&diet={diet1}"
    response = requests.get(url)
    return response.text

def convert_to_readable_format(response_text):
    data = json.loads(response_text)
    total_results = data['totalResults']
    list1 = []
    if total_results == 0:
        list1.append("Sorry, we could not find anything. Please type /start to search for something new.")
        return list1

    results = data['results']
    ans = []
    images = []
    for recipe in results:
        ans.append(f"Recipe: {recipe['title']}\nRecipe ID: {recipe['id']}\n" + "-" * 50 + "\n")
        images.append(recipe['image'])

    list1 = [ans, images]
    return list1

def detailedinstructions(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/analyzedInstructions?apiKey={spoon}"
    response = requests.get(url)
    return json.loads(response.text)

def extract_steps_and_images(recipes):
    steps_list = []
    images_list = []
    for recipe in recipes:
        if recipe.get('steps'):
            for step in recipe['steps']:
                step_description = f"Step {step['number']}: {step['step']}\n"
                if step.get('ingredients'):
                    step_description += "Ingredients:\n"
                    for ingredient in step['ingredients']:
                        step_description += f"- {ingredient['localizedName']} ({ingredient['name']})\n"
                if step.get('equipment'):
                    step_description += "Equipment:\n"
                    for equip in step['equipment']:
                        step_description += f"- {equip['localizedName']} ({equip['name']})\n"
                if step.get('length'):
                    step_description += f"Estimated time: {step['length']['number']} {step['length']['unit']}\n"
                steps_list.append(step_description)
                step_images = []
                if step.get('ingredients'):
                    for ingredient in step['ingredients']:
                        if ingredient.get('image'):
                            step_images.append(ingredient['image'])
                if step.get('equipment'):
                    for equip in step['equipment']:
                        if equip.get('image'):
                            step_images.append(equip['image'])
                images_list.append(step_images)
    return steps_list, images_list

@bot.message_handler(commands=['hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello and welcome to Recipe Bot. I will take certain instructions from you about the type of food you want to cook and return a detailed recipe for it. To start, type /start.")

@bot.message_handler(commands=['start'])
def dish_name(message):
    text = "Enter the name of the dish you want to make: \nType None if you don't have specifics in mind."
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, cuisine_name)

def cuisine_name(message):
    Details["dish"] = message.text.lower()
    text = ("What specific cuisine are you looking for? Currently, my catalog has these cuisines available:\n"
            "African \n"
            "Asian\n"
            "American\n"
            "British\n"
            "Cajun\n"
            "Caribbean\n"
            "Chinese\n"
            "Eastern European \n"
            "European\n"
            "French\n"
            "German\n"
            "Greek\n"
            "Indian\n"
            "Irish\n"
            "Italian\n"
            "Japanese\n"
            "Jewish\n"
            "Korean\n"
            "Latin American\n"
            "Mediterranean\n"
            "Mexican\n"
            "Middle Eastern\n"
            "Nordic\n"
            "Southern\n"
            "Spanish\n"
            "Thai\n"
            "Vietnamese\n"
            "Type None for no specific choice.")
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, type_name)

def type_name(message):
    Details["cusine"] = message.text.lower()
    meal_types = [
        "main course",
        "side dish",
        "dessert",
        "appetizer",
        "salad",
        "bread",
        "breakfast",
        "soup",
        "beverage",
        "sauce",
        "marinade",
        "fingerfood",
        "snack",
        "drink",
        "Type None for no specific meal type"
    ]
    text = ("What type of meal would you like to request?\n"
            "Currently, we support the following meal types:\n" +
            "\n".join(meal_types))
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, diet_name)

def diet_name(message):
    Details["type"] = message.text.lower()
    text = ("What type of diet would you like to request?\n"
            "Currently, we support the following diets:\n"
            "Gluten Free\n"
            "Ketogenic\n"
            "Vegetarian\n"
            "Lacto-Vegetarian\n"
            "Ovo-Vegetarian\n"
            "Vegan\n"
            "Pescetarian\n"
            "Paleo\n"
            "Primal\n"
            "Type None for no specific type.")
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, dish_list)

def dish_list(message):
    Details["diet"] = message.text.lower()
    text = "Here are the results for your search:\n"
    q1 = Details["dish"] if Details["dish"] != "none" else ""
    c1 = Details["cusine"] if Details["cusine"] != "none" else ""
    d1 = Details["diet"] if Details["diet"] != "none" else ""
    t1 = Details["type"] if Details["type"] != "none" else ""
    Items = convert_to_readable_format(recepie_getter(q1, c1, t1, d1))
    text2 = "Please enter the ID of the recipe you want details of:"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    if len(Items) == 1:
        bot.send_message(message.chat.id, Items[0], parse_mode="Markdown")
        sent_msg = bot.send_message(message.chat.id, "Type /start to search for something new", parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, dish_name)
    else:
        for i in range(len(Items[0])):
            if Items[0][i]:
                bot.send_message(message.chat.id, Items[0][i], parse_mode="Markdown")
            if requests.head(Items[1][i]).status_code == 200:
                bot.send_photo(message.chat.id, photo=Items[1][i], parse_mode="Markdown")
        sent_msg = bot.send_message(message.chat.id, text2, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, recepie)

def recepie(message):
    id = message.text
    text = "Here is your recipe:"
    lawda, lasoon = extract_steps_and_images(detailedinstructions(id))
    text1 = "Hope you enjoyed the dish. Remember to follow me on Instagram: https://www.instagram.com/aabsurdy/"
    text2 = "To start again, type /start."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    for i in range(len(lawda)):
        bot.send_message(message.chat.id, lawda[i], parse_mode="Markdown")
    sent_msg = bot.send_message(message.chat.id, text1 + text2, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, dish_name)

@app.route('/')
def index():
    return "The bot is running!"

def start_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))