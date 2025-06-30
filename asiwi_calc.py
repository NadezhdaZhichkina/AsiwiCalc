import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document

st.set_page_config(page_title="Калькулятор партнёрской прибыли", layout="centered")
st.title("🔢 Калькулятор партнёрской прибыли")

# Только два варианта
partners = {
    "Партнёр с НДС": {"nds": True},
    "Партнёр без НДС": {"nds": False},
}

partner_name = st.selectbox("Выберите подрядчика:", list(partners.keys()))
partner_nds = partners[partner_name]["nds"]

uploaded_file = st.file_uploader("Загрузите спецификацию (Excel или DOCX):", type=["xlsx", "xls", "docx"])

def parse_file(file):
    if file.name.endswith(".xlsx") or file.name.endswith(".xls"):
        df = pd.read_excel(file)
    elif file.name.endswith(".docx"):
        doc = Document(file)
        rows = []
        for table in doc.tables:
            for row in table.rows:
                cols = [cell.text.strip() for cell in row.cells]
                if len(cols) >= 2:
                    try:
                        cost = float(cols[1].replace(",", ".").replace(" ", ""))
                        rows.append([cols[0], cost])
                    except:
                        continue
        df = pd.DataFrame(rows, columns=["Наименование", "Стоимость"])
    else:
        df = pd.DataFrame()
    return df

def find_price_column(df):
    possible_names = [
        "стоимость", "цена", "стоимость с ндс", "цена с ндс", "стоимость без ндс"
    ]
    for col in df.columns:
        if isinstance(col, str):
            col_lower = col.lower().strip()
            for name in possible_names:
                if name in col_lower:
                    return col
    return None

def generate_docx(table_df, total):
    doc = Document()
    doc.add_heading('Спецификация для клиента', 0)
    table = doc.add_table(rows=1, cols=2)
    table.autofit = True
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Услуга'
    hdr_cells[1].text = 'Цена с НДС (₽)'

    for i, row in table_df.iterrows():
        cells = table.add_row().cells
        cells[0].text = str(row['Услуга'])
        cells[1].text = f"{row['Цена с НДС']:,.2f}".replace(",", " ")

    doc.add_paragraph()
    doc.add_paragraph(f"Итого с НДС: {total:,.2f} ₽".replace(",", " "))
    byte_io = BytesIO()
    doc.save(byte_io)
    byte_io.seek(0)
    return byte_io

if uploaded_file:
    df_spec = parse_file(uploaded_file)
    if df_spec.empty:
        st.error("❌ Не удалось распознать таблицу. Убедитесь, что файл содержит услуги и цены.")
    else:
        st.subheader("📄 Считанная спецификация:")
        st.dataframe(df_spec)

        price_col = find_price_column(df_spec)
        if not price_col:
            st.error("❌ Таблица должна содержать колонку с ценами (например, 'Стоимость', 'Цена с НДС' и т.п.).")
        else:
            first_col = df_spec.columns[0]
            total_partner_sum = df_spec[price_col].sum()

            st.markdown(f"**Сумма от подрядчика:** `{total_partner_sum:,.2f} ₽`")

            st.markdown("### ➕ Расчёт чистой прибыли")
            client_sum = st.number_input("Сумма, которую планируем выставить клиенту (включает НДС):", value=0.0, step=1000.0)
            desired_profit = st.number_input("Желаемая чистая прибыль (обратный расчёт):", value=0.0, step=1000.0)

            nds_included = False
            if partner_nds:
                nds_included = st.checkbox("Сумма в спецификации включает НДС", value=True)

            col1, col2 = st.columns(2)
            with col1:
                calc_button = st.button("🔁 Пересчитать прибыль")
            with col2:
                spec_button = st.button("📋 Показать спецификацию и выгрузить в DOCX/Excel")

            if calc_button and client_sum > 0:
                st.markdown("### 📊 Расчёт прибыли")
                client_nds = client_sum * 20 / 120
                client_net = client_sum - client_nds

                if partner_nds:
                    if nds_included:
                        nds_sub = total_partner_sum * 20 / 120
                        net_sub = total_partner_sum - nds_sub
                    else:
                        net_sub = total_partner_sum
                        nds_sub = net_sub * 0.20
                        total_partner_sum = net_sub + nds_sub

                    nds_loss = nds_sub * 0.75
                    direct_costs = net_sub + nds_loss
                    tax_base = client_net - direct_costs
                    tax = tax_base * 0.05
                    profit = tax_base - tax

                    st.markdown(f"- **НДС подрядчика:** `{nds_sub:,.2f} ₽`")
                    st.markdown(f"- **Нетто подрядчику:** `{net_sub:,.2f} ₽`")
                    st.markdown(f"- **НДС клиента:** `{client_nds:,.2f} ₽`")
                    st.markdown(f"- **Нетто от клиента:** `{client_net:,.2f} ₽`")
                    st.markdown(f"- **Убыток по НДС (75%):** `{nds_loss:,.2f} ₽`")
                    st.markdown(f"- **Прямые расходы:** `{direct_costs:,.2f} ₽`")
                    st.markdown(f"- **Налоговая база:** `{tax_base:,.2f} ₽`")
                    st.markdown(f"- **Налог на прибыль (5%):** `{tax:,.2f} ₽`")
                    st.success(f"💰 **Чистая прибыль:** `{profit:,.2f} ₽`")
                else:
                    tax_base = client_net - total_partner_sum
                    tax = tax_base * 0.05
                    profit = tax_base - tax

                    st.markdown(f"- **Нетто подрядчику (без НДС):** `{total_partner_sum:,.2f} ₽`")
                    st.markdown(f"- **НДС клиента:** `{client_nds:,.2f} ₽`")
                    st.markdown(f"- **Нетто от клиента:** `{client_net:,.2f} ₽`")
                    st.markdown(f"- **Налоговая база:** `{tax_base:,.2f} ₽`")
                    st.markdown(f"- **Налог на прибыль (5%):** `{tax:,.2f} ₽`")
                    st.success(f"💰 **Чистая прибыль:** `{profit:,.2f} ₽`")

            if desired_profit > 0:
                d = desired_profit
                if partner_nds:
                    if nds_included:
                        nds_sub = total_partner_sum * 20 / 120
                        net_sub = total_partner_sum - nds_sub
                    else:
                        net_sub = total_partner_sum
                    nds_loss = net_sub * 0.2 * 0.75
                    tax_base = d / 0.95
                    net_client = net_sub + nds_loss + tax_base
                    x = net_client * 1.2
                else:
                    net_sum = d / 0.95 + total_partner_sum
                    x = net_sum * 1.2
                st.info(f"🧾 Чтобы получить **{desired_profit:,.2f} ₽** прибыли, нужно выставить клиенту: **{x:,.2f} ₽**")
                client_sum = x

            if spec_button:
                st.markdown("### 📑 Спецификация для клиента")
                spec_df = df_spec.copy()
                total_original = spec_df[price_col].sum()

                if client_sum <= 0 or total_original == 0:
                    st.warning("Введите сумму для клиента и убедитесь, что спецификация не пустая.")
                else:
                    k = client_sum / total_original
                    spec_df["Цена с НДС"] = spec_df[price_col] * k
                    spec_df["Цена с НДС"] = spec_df["Цена с НДС"].round(2)

                    total_for_client = spec_df["Цена с НДС"].sum()
                    spec_display = spec_df[[first_col, "Цена с НДС"]].rename(columns={first_col: "Услуга"})

                    st.dataframe(spec_display)
                    st.markdown(f"💼 **Итоговая сумма для клиента (с НДС): `{total_for_client:,.2f} ₽`**")

                    docx_file = generate_docx(spec_display, total_for_client)
                    st.download_button(
                        label="💾 Скачать спецификацию (DOCX)",
                        data=docx_file,
                        file_name="Спецификация_для_клиента.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

                    excel_io = BytesIO()
                    with pd.ExcelWriter(excel_io, engine="openpyxl") as writer:
                        spec_display.to_excel(writer, index=False, sheet_name="Спецификация")
                        worksheet = writer.sheets["Спецификация"]
                        worksheet.cell(row=len(spec_display) + 2, column=1, value="Итого:")
                        worksheet.cell(row=len(spec_display) + 2, column=2, value=total_for_client)
                    excel_io.seek(0)

                    st.download_button(
                        label="📥 Скачать спецификацию (Excel)",
                        data=excel_io,
                        file_name="Спецификация_для_клиента.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
