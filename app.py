import streamlit as st
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from agent.agent import FoodTrackerAgent

agent = FoodTrackerAgent()


def save_log_meal(meal_name, calories, protein, carbs, fats):
    """Сохраняет данные о приеме пищи в сессию Streamlit (вместо БД)"""
    if "history" not in st.session_state:
        st.session_state.history = []
    
    new_entry = {
        "Блюдо": meal_name,
        "Калории": calories,
        "Белки": protein,
        "Углеводы": carbs,
        "Жиры": fats
    }
    st.session_state.history.append(new_entry)
    return f"Успешно записал {meal_name}!"



st.set_page_config(page_title="AI Food Tracker", layout="wide")
st.title("🥗 AI Трекер Питания")


col_chat, col_stats = st.columns([1, 1])

with col_chat:
    st.subheader("О чем ты хочешь рассказать агенту?")
    user_input = st.text_input("Например: Я съел большой бургер и выпил колу", key="input")
    
    if st.button("Отправить"):
        if user_input:
            # Запрос к модели

            msg = agent.save_meal(user_input)
            
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    status = save_log_meal(
                        meal_name=args['food_item'],
                        calories=args['calories'],
                        protein=args['protein'],
                        carbs=0,
                        fats=0
                    )
                    st.success(status)
            else:
                st.info(msg.content)

# --- 4. КРАСИВЫЙ ВЫВОД (Dashboard) ---
with col_stats:
    st.subheader("Твой дневник питания")
    if "history" in st.session_state and st.session_state.history:
        # Показываем общую сумму калорий за сегодня
        total_cal = sum(item['Калории'] for item in st.session_state.history)
        st.metric("Всего калорий за день", f"{total_cal} ккал")
        
        # Выводим таблицу
        st.table(st.session_state.history)
        
        # Добавим визуализацию (мини-график)
        chart_data = {
            "Белки": sum(i['Белки'] for i in st.session_state.history),
            "Жиры": sum(i['Жиры'] for i in st.session_state.history),
            "Углеводы": sum(i['Углеводы'] for i in st.session_state.history)
        }
        st.bar_chart(chart_data)
    else:
        st.write("Тут пока пусто. Расскажи агенту, что ты поел!")