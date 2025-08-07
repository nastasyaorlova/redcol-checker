import streamlit as st
import re
from difflib import SequenceMatcher

st.set_page_config(page_title="Сравнение редколлегий", layout="wide")

st.title("🔍 Сравнение членов редколлегий")
st.write("Введите данные о членах редакционных коллегий двух журналов (доля совпадений будет расчитана по первому введеному журналу).Вы можете вручную исключить ошибки в совпадениях, чтобы скорректировать расчёт.")

# --- Функции ---
def extract_names(text):
    pattern = r'[А-ЯЁ][а-яё]+ [А-ЯЁ][а-яё]+(?: [А-ЯЁ][а-яё]+)?'
    matches = re.findall(pattern, text)
    return list(set(matches))

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def compare_names(list1, list2, threshold=0.9):
    matches = []
    for name1 in list1:
        for name2 in list2:
            if similar(name1, name2) >= threshold:
                matches.append((name1, name2))
    return matches

# --- Ввод ---
col1, col2 = st.columns(2)
with col1:
    text1 = st.text_area("Данные о редколлегии журнала № 1", height=400)
with col2:
    text2 = st.text_area("Данные о редколлегии журнала № 2", height=400)

threshold = st.slider("Порог схожести имён (0.9–1.0)", 0.9, 1.0, 0.9, 0.01)

# --- Сессия ---
if "matches" not in st.session_state:
    st.session_state.matches = []
if "checked" not in st.session_state:
    st.session_state.checked = []
if "names1" not in st.session_state:
    st.session_state.names1 = []

# --- Кнопка сравнения ---
if st.button("Сравнить"):
    names1 = extract_names(text1)
    names2 = extract_names(text2)
    matches = compare_names(names1, names2, threshold)

    st.session_state.matches = matches
    st.session_state.checked = [True] * len(matches)
    st.session_state.names1 = names1

# --- Вывод результатов ---
if st.session_state.matches:
    st.subheader("🔁 Выберите совпадения, которые **учитываются**:")

    updated_checked = []
    for i, (name1, name2) in enumerate(st.session_state.matches):
        label = f"{name1} ≈ {name2}"
        checked = st.checkbox(label, value=st.session_state.checked[i], key=f"match_{i}")
        updated_checked.append(checked)

    st.session_state.checked = updated_checked

    selected = [match for match, flag in zip(st.session_state.matches, updated_checked) if flag]
    rejected = [match for match, flag in zip(st.session_state.matches, updated_checked) if not flag]

    count_selected = len(selected)
    count_rejected = len(rejected)
    total_names1 = len(set(st.session_state.names1))

    # 📐 Новый скорректированный расчёт
    adjusted_denominator = total_names1 - count_rejected
    percent_overlap = (count_selected / adjusted_denominator * 100) if adjusted_denominator > 0 else 0

    st.markdown("#### 📐 Итог после ручной фильтрации:")
    st.write(f"- **Корректных совпадений:** {count_selected}")
    st.write(f"- **Ошибочных совпадений (исключено):** {count_rejected}")
    st.write(f"- **Доля совпадений (отн. к журналу 1, скорректировано):** {percent_overlap:.1f}%")

    if count_selected > 0:
        st.markdown("#### ✅ Итоговый список совпадений:")
        for name1, name2 in selected:
            st.write(f"- {name1} ≈ {name2}")

else:
    st.info("Нажмите кнопку **'Сравнить'**, чтобы увидеть результаты.")
