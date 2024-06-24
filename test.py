import os
import telebot
import requests
import json

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

lasoon = convert_to_readable_format(recepie_getter("","indian","side dish","vegetarian"))

for i in lasoon[1]:
    print(requests.head(i).status_code)
