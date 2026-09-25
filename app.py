import streamlit as st
import pandas as pd
import glob
import os

# 1. Налаштування зовнішнього вигляду сторінки
st.set_page_config(
    page_title="Безбар'єрність Київщини", 
    page_icon="♿", 
    layout="wide"
)

st.title("♿ Моніторинг Безбар'єрності в Громадах Київщини")
st.write("Інтерактивний дашборд новин та ініціатив з офіційних джерел громад.")

# 2. Пошук та завантаження найновішого CSV-файлу з даними
@st.cache_data(ttl=300)
def load_data():
    csv_files = glob.glob("*.csv")
    if not csv_files:
        return None, None
    latest_file = max(csv_files, key=os.path.getmtime)
    df = pd.read_csv(latest_file, sep=';')
    return df, latest_file

df, filename = load_data()

if df is not None:
    st.caption(f"📁 Останнє оновлення з файлу: `{filename}`")

    if 'Тип джерела'not in df.columns:
        df['Тип джерела'] = '💬 Telegram'
    
   st.sidebar.header("🔍 Гнучкі фільтри")
    
    # Фільтр по громадах
    all_channels = sorted(df['Канал'].dropna().astype(str).unique())
    selected_channels = st.sidebar.multiselect("Оберіть громаду/джерело:", options=all_channels, default=all_channels)
    
    # Фільтр по тематиках
    all_themes = sorted(df['Тематика'].dropna().astype(str).unique())
    selected_themes = st.sidebar.multiselect("Оберіть напрямок:", options=all_themes, default=all_themes)
    
    # Пошуковий рядок
    search_query = st.sidebar.text_input("Пошук за словом у тексті:")

    # Застосування загальних фільтрів
    filtered_df = df[
        (df['Канал'].isin(selected_channels)) & 
        (df['Тематика'].isin(selected_themes))
    ]
    
   if search_query:
        filtered_df = filtered_df[filtered_df['Текст'].str.contains(search_query, case=False, na=False)]

    # --- СТВОРЕННЯ ВКЛАДОК (СТОРОНОК) НА САЙТІ ---
    tab_all, tab_tg, tab_web = st.tabs(["📊 Усі новини", "💬 Telegram-канали", "🌐 Офіційні сайти"])

    # Функція для відображення таблиці та метрик
    def display_dashboard(data_to_show, title_suffix=""):
        col1, col2 = st.columns(2)
        col1.metric(f"Знайдено публікацій {title_suffix}", len(data_to_show))
        col2.metric("Активних джерел", data_to_show['Канал'].nunique())
        
        st.dataframe(
            data_to_show,
            column_config={
                "Посилання": st.column_config.LinkColumn("Джерело", display_text="Перейти 🔗")
            },
            use_container_width=True,
            hide_index=True,
            height=450
        )
        
        csv_export = data_to_show.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="📥 Завантажити цей список в Excel",
            data=csv_export,
            file_name=f"barrier_free_{title_suffix}.csv",
            mime="text/csv"
        )

    # Вкладка 1: Усі новини
    with tab_all:
        display_dashboard(filtered_df, "(Усі джерела)")

    # Вкладка 2: Тільки Telegram
    with tab_tg:
        tg_data = filtered_df[filtered_df['Тип джерела'].str.contains("Telegram", na=False)]
        display_dashboard(tg_data, "(Telegram)")

    # Вкладка 3: Тільки Сайти
    with tab_web:
        web_data = filtered_df[filtered_df['Тип джерела'].str.contains("Сайт", na=False)]
        display_dashboard(web_data, "(Офіційні сайти)")

else:
    st.error("CSV-файлів з даними не знайдено у папці проєкту!")
