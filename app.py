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
@st.cache_data(ttl=600)
def load_latest_data():
    csv_files = glob.glob("*.csv")
    if not csv_files:
        return None, None
    latest_file = max(csv_files, key=os.path.getmtime)
    df = pd.read_csv(latest_file, sep=';')
    return df, latest_file

df, filename = load_latest_data()

if df is not None:
    st.caption(f"📁 Останнє оновлення з файлу: `{filename}`")
    
    # Бокова панель з фільтрами
    st.sidebar.header("🔍 Фільтри")
    
    # Фільтр по громадах
    all_channels = sorted(df['Канал'].dropna().astype(str).unique())
    selected_channels = st.sidebar.multiselect("Оберіть громаду:", options=all_channels, default=all_channels)
    
    # Фільтр по тематиках
    all_themes = sorted(df['Тематика'].dropna().astype(str).unique())
    selected_themes = st.sidebar.multiselect("Оберіть напрямок:", options=all_themes, default=all_themes)
    
    # Пошуковий рядок
    search_query = st.sidebar.text_input("Пошук за словом у тексті:")

    # Застосування фільтрів
    filtered_df = df[
        (df['Канал'].isin(selected_channels)) & 
        (df['Тематика'].isin(selected_themes))
    ]
    
    if search_query:
        filtered_df = filtered_df[filtered_df['Текст'].str.contains(search_query, case=False, na=False)]

    # Загальні метрики
    col1, col2 = st.columns(2)
    col1.metric("Знайдено публікацій", len(filtered_df))
    col2.metric("Охоплено громад", filtered_df['Канал'].nunique())

    st.divider()

    # Інтерактивна таблиця
    st.dataframe(
        filtered_df,
        column_config={
            "Посилання": st.column_config.LinkColumn("Джерело", display_text="Перейти 🔗")
        },
        use_container_width=True,
        hide_index=True,
        height=500
    )
    
    # Кнопка завантаження результатів у Excel
    csv_export = filtered_df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button(
        label="📥 Завантажити відфільтровані дані в Excel (CSV)",
        data=csv_export,
        file_name="filtered_barrier_free_news.csv",
        mime="text/csv"
    )
else:
    st.error("У цій папці не знайдено жодного CSV-файлу з даними. Спочатку запустіть ваш скрапер!")
