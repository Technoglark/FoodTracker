import streamlit as st
import json
from agent.agent import FoodTrackerAgent

# ==========================================
# 1. ИНИЦИАЛИЗАЦИЯ (СТРОГО ОДИН РАЗ)
# ==========================================
if "meal_types" not in st.session_state:
    st.session_state.meal_types = ["Завтрак", "Обед", "Ужин", "Перекус"]

if "diary" not in st.session_state:
    st.session_state.diary = {m: [] for m in st.session_state.meal_types}

if "agent" not in st.session_state:
    st.session_state.agent = FoodTrackerAgent()

# ==========================================
# 2. НАСТРОЙКИ СТРАНИЦЫ
# ==========================================
st.set_page_config(page_title="AI Food Tracker", layout="wide")

# ==========================================
# 3. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================
def save_log_meal(meal_name, calories, protein, carbs, fats, meal_type):
    # Если агент придумал новый тип, добавляем его в структуру

    meal_type = meal_type.capitalize()
    if meal_type not in st.session_state.diary:
        st.session_state.diary[meal_type] = []
        if meal_type not in st.session_state.meal_types:
            st.session_state.meal_types.append(meal_type)

    # Добавляем запись
    st.session_state.diary[meal_type].append({
        "name": meal_name,
        "cal": calories,
        "p": protein,
        "c": carbs,
        "f": fats
    })

# ==========================================
# 4. ИНТЕРФЕЙС (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("⚙️ Настройки")
    new_type = st.text_input("Новая категория")
    if st.button("Добавить категорию"):
        if new_type and new_type not in st.session_state.meal_types:
            st.session_state.meal_types.append(new_type)
            st.session_state.diary[new_type] = []
            st.rerun()
    
    if st.button("🗑️ Очистить всё"):
        st.session_state.diary = {m: [] for m in st.session_state.meal_types}
        st.rerun()

# ==========================================
# 5. ОСНОВНОЙ КОНТЕНТ (ОДИН ВЫЗОВ COLUMNS)
# ==========================================
st.title("🥗 Умный трекер питания")

# Создаем ОДНУ сетку из двух колонок
left_col, right_col = st.columns([1, 1])

# --- ЛЕВАЯ КОЛОНКА: ЧАТ ---
with left_col:
    st.subheader("💬 Чат с агентом")
    # chat_input ВСЕГДА прижат к низу колонки
    user_query = st.chat_input("Напиши, что ты съел...")
    
    if user_query:
        # Получаем ответ от ML-агента
        msg = st.session_state.agent.save_meal(user_query)
        
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                save_log_meal(
                    meal_name=args.get('food_item', 'Еда'),
                    calories=args.get('calories', 0),
                    protein=args.get('protein', 0),
                    carbs=args.get('carbs', 0),
                    fats=args.get('fats', 0),
                    meal_type=args.get('meal_type', 'Перекус')
                )
            st.success("Данные обновлены!")
        elif msg.content:
            st.info(msg.content)

# --- ПРАВАЯ КОЛОНКА: ДНЕВНИК ---
with right_col:
    st.subheader("📊 Дневник питания")
    day_total = 0

    # Цикл отрисовки категорий (ТОЛЬКО ЗДЕСЬ)
    for m_type in st.session_state.meal_types:
        items = st.session_state.diary.get(m_type, [])
        
        with st.expander(f"{m_type} ({len(items)})", expanded=True):
            if not items:
                st.caption("Пока нет записей")
            else:
                current_meal_total = 0
                for item in items:
                    st.write(f"🍴 **{item['name']}**")
                    st.caption(f"🔥 {item['cal']} ккал | Б:{item['p']} Ж:{item['f']} У:{item['c']}")
                    current_meal_total += item['cal']
                    day_total += item['cal']
                
                st.divider()
                st.write(f"Всего за {m_type.lower()}: **{current_meal_total} ккал**")

    # Итоговая статистика дня
    st.divider()
    st.metric("ИТОГО ЗА ДЕНЬ", f"{day_total} ккал")
    
    norm = 2000
    st.progress(min(day_total / norm, 1.0), text=f"Цель: {norm} ккал")