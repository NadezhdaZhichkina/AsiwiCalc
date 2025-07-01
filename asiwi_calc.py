import streamlit as st
import pandas as pd

st.set_page_config(page_title="Калькулятор партнёрской прибыли", layout="wide")
st.title("🤝 Калькулятор партнёрской прибыли")

st.markdown("""
Этот инструмент поможет пересчитать спецификацию под заданную маржу или итоговую сумму для клиента.
Загрузите Excel-файл или введите спецификацию вручную.
""")

uploaded_file = st.file_uploader("Загрузите спецификацию (xlsx или csv)", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith("xlsx"):
        df_spec = pd.read_excel(uploaded_file)
    else:
        df_spec = pd.read_csv(uploaded_file)
else:
    df_spec = pd.DataFrame(columns=["Наименование", "Сумма, руб."])

st.markdown("### ✏️ Спецификация")
edited_df = st.data_editor(df_spec, num_rows="dynamic", use_container_width=True)

st.markdown("---")

st.markdown("### ⚙️ Параметры расчёта")

partner_vat = st.selectbox("Партнёр работает с НДС?", ["Да", "Нет"]) == "Да"
include_vat = st.selectbox("Сумма включает НДС?", ["Да", "Нет"]) == "Да"
method = st.radio("Выберите способ расчёта", ["По итоговой сумме для клиента", "По желаемой прибыли"])

col1, col2 = st.columns(2)

client_sum = None
desired_profit = None

with col1:
    if method == "По итоговой сумме для клиента":
        client_sum = st.number_input("Итоговая сумма для клиента, руб.", min_value=0.0, step=100.0)
    else:
        desired_profit = st.number_input("Желаемая прибыль, руб.", min_value=0.0, step=100.0)

st.markdown("### 📊 Результат")

price_col = df_spec.columns[-1]

# Исключаем строки, в которых в наименовании встречается "итого" (в любом регистре)
filtered_spec_df = edited_df[~edited_df[edited_df.columns[0]].astype(str).str.lower().str.contains("итого")]

try:
    total_original = filtered_spec_df[price_col].sum()

    if method == "По итоговой сумме для клиента" and client_sum:
        k = client_sum / total_original if total_original else 1
    elif desired_profit is not None:
        target_sum = total_original + desired_profit
        k = target_sum / total_original if total_original else 1
    else:
        k = 1

    # Расчёт партнёрской стоимости с учётом НДС
    def compute_partner_price(x):
        base = x * k
        if partner_vat:
            if include_vat:
                return base / 1.2
            else:
                return base
        else:
            return base

    filtered_spec_df["Стоимость для нас, руб."] = filtered_spec_df[price_col].apply(compute_partner_price).round(2)

    total_partner_sum = filtered_spec_df["Стоимость для нас, руб."].sum()

    st.dataframe(filtered_spec_df, use_container_width=True)

    st.markdown(f"**Сумма от подрядчика:** {total_partner_sum:,.2f} ₽".replace(",", " ").replace(".", ","))

except Exception as e:
    st.error(f"Ошибка при расчёте: {e}")
