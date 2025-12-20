import openai
import os
from openai import OpenAI
import json
import pandas as pd
from dotenv import load_dotenv

class FoodTrackerAgent:
    def __init__(self):

        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )


    def save_meal(self, meal_description: str):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "save_food_log",
                    "description": "Записать продукт в дневник питания",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "food_item": {"type": "string", "description": "Название продукта"},
                            "calories": {"type": "integer", "description": "Калории"},
                            "protein": {"type": "integer"},
                            'count': {'type':['string', 'integer'], 'description':'Количество порций или вес продукта'},
                            'meal_type': {'type':'string', 'description':'Тип приема пищи (завтрак, обед, ужин, перекус или иное)'}
                        },
                        "required": ["food_item", "calories", 'protein', 'count', 'meal_type'],
                    }
                }
            }
        ]

        messages = [
            {"role": "system", "content": "Ты эксперт-нутрициолог. Для записи еды ВСЕГДА используй функцию save_food_log."},
            {"role": "user", "content": meal_description}
        ]

        return self.ask_agent(tools, messages)



    def ask_agent(self, tools, messages):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        return response.choices[0].message
    
    def save_food_log(self, answer, df):

        if answer.tool_calls:
            for tool_call in answer.tool_calls:
                if tool_call.function.name == "save_food_log":

                    arguments_raw = tool_call.function.arguments
                    arguments = json.loads(arguments_raw)


                    df = pd.concat([df, pd.DataFrame([{
                                'food_item': arguments['food_item'],
                                'calories': arguments['calories'], 
                                'protein': arguments['protein'], 
                                'count': arguments['count']}])], ignore_index=True)
        return df




