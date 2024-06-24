import os
import telebot
import requests
import json

bot_token = '7227344044:AAEtkqtKng7GGgIJIUK7C2unVDqlwOHQlqs'
spoon = '4ea75d07744643a6a17eea36eb47140e'


def recepie_getter(query1, cuisine1, type1, diet1):
    url = "https://api.spoonacular.com/recipes/complexSearch?apiKey=" + spoon + "&query=" + query1 + "&cuisine=" + cuisine1 + "&type=" + type1 + "&diet=" + diet1
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.text

def convert_to_readable_format(response_text):
    # Parse the JSON response
    data = json.loads(response_text)
    total_results = data['totalResults']
    list1 = []
    if (total_results == 0):
        list1.append("Sorry We Could Not Find Anything for ,please type /start to look for something New")
        return list1

    # Extract the relevant information
    results = data['results']
    ans = []
    images = []
    # Print the results in a readable format
    for recipe in results:
        ans.append(f"Recipe: {recipe['title']}\nRecipe ID: {recipe['id']}\n" + "-" * 50 + "\n")
        images.append(recipe['image'])

    list1 = [ans, images]
    return list1


def detailedinstructions(recipe_id):
    url = "https://api.spoonacular.com/recipes/" + recipe_id + "/analyzedInstructions?apiKey=" + spoon
    response = requests.request("GET", url)
    printer_data = json.loads(response.text)
    return printer_data


def detailedinstructions(recipe_id):
    url = "https://api.spoonacular.com/recipes/" + recipe_id + "/analyzedInstructions?apiKey=" + spoon
    response = requests.request("GET", url)
    printer_data = json.loads(response.text)
    return printer_data


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

# printer_response = detailedinstructions("715538")
#
# # Ensure we handle the parsed JSON properly
# if printer_response and isinstance(printer_response, list) and len(printer_response) > 0:
#     print_recipe(printer_response[0])
# else:
#     print("No detailed instructions found for the given recipe ID.")

Details = {"cusine":"",
           "dish":"",
           "type":"",
           "diet":""}

bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello and welcome to Recepie Bot ,I will take certain instructions from you about the type of food you wanna cook and will return a detailed recepie for it \n to start type /start")

@bot.message_handler(commands=['start'])
def dish_name(message):
    text = "Enter the name of Dish you wanna make: \n Type None if you don't have specifics in Mind"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg,cuisine_name)

def cuisine_name(message):
    Details["dish"] = message.text.lower()
    text = ("what specific cuisine are you looking for ? currently my cataloge has these cuisines available:\n"+
            "African \n"+
            "Asian\n"+
            "American\n"+
            "British\n"+
            "Cajun\n"+
            "Caribbean\n"+
            "Chinese\n"+
            "Eastern European \n"+
            "European\n"+
            "French\n"+
            "German\n"+
            "Greek\n"+
            "Indian\n"+
            "Irish\n"+
            "Italian\n"+
            "Japanese\n"+
            "Jewish\n"+
            "Korean\n"+
            "Latin American\n"+
            "Mediterranean\n"+
            "Mexican\n"+
            "Middle Eastern\n"+
            "Nordic\n"+
            "Southern\n"+
            "Spanish\n"+
            "Thai\n"+
            "Vietnamese\n"+
            "Type None for no specific choice")
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg,type_name)

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
        "type none for no specific meal type"
    ]
    text = ("What type of meal would you like to request?\n"
            "Currently, we support the following meal types:\n" +
            "\n".join(meal_types))
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, diet_name)

def diet_name(message):
    Details["type"] = message.text.lower()
    text = ("What type of Diet would you like to request?\n"
            "Currently, we support the following Diets:\n" +
            "Gluten Free\n"+
            "Ketogenic\n"+
            "Vegetarian\n"+
            "Lacto-Vegetarian\n"+
            "Ovo-Vegetarian\n"+
            "Vegan\n"+
            "Pescetarian\n"+
            "Paleo\n"+
            "Primal\n"+
            "Type None for no specific type"
            )
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, dish_list)

def dish_list(message):
    Details["diet"] = message.text.lower()
    text = ("Here are the results for you search :\n")
    if(Details["dish"]!="none"):
        q1 = Details["dish"]
    else:
        q1 = ""
    if (Details["cusine"] != "none"):
        c1 = Details["cusine"]
    else:
        c1 = ""
    if (Details["diet"] != "none"):
        d1 = Details["diet"]
    else:
        d1 = ""
    if (Details["type"] != "none"):
        t1 = Details["type"]
    else:
        t1 = ""
    Items = (convert_to_readable_format(recepie_getter(q1,c1,t1,d1)))
    text2 = "\n Please Enter the Id of recepie you want details off:"
    # sent_msg = bot.send_message(message.chat.id, text+text2, parse_mode="Markdown")
    # bot.register_next_step_handler(sent_msg, recepie)
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    if(len(Items) == 1):
        bot.send_message(message.chat.id,Items[0], parse_mode="Markdown")
        sent_msg = bot.send_message(message.chat.id, "Type /start for searching something new", parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, dish_name)
    else:
        for i in range(len(Items[0])):
            if(Items[0][i]):
                bot.send_message(message.chat.id, Items[0][i], parse_mode="Markdown")
            if (requests.head(Items[1][i]).status_code == 200):
                bot.send_photo(message.chat.id, photo=Items[1][i],parse_mode="Markdown")
        sent_msg = bot.send_message(message.chat.id, text2, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, recepie)

def recepie(message):
    id = message.text
    text = ("Here is your Recepie :")
    lawda,lasoon = extract_steps_and_images(detailedinstructions(id))
    text1 = ("Hope You enjoyed the dish \n remember to follow me on \n Instagram:https://www.instagram.com/aabsurdy/ \n")
    text2 = ("To start again type /start")
    bot.send_message(message.chat.id, text, parse_mode="Markdown")
    for i in range(len(lawda)):
        bot.send_message(message.chat.id, lawda[i], parse_mode="Markdown")
    sent_msg = bot.send_message(message.chat.id, text1+text2, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, dish_name)

bot.infinity_polling()