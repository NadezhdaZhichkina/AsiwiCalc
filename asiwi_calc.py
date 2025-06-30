<REPLACED_FOR_BREVITYif calc_button and client_sum > 0:
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
        st.caption("20% от стоимости, если подрядчик работает с НДС. Учитывается для расчёта убытка по НДС.")

        st.markdown(f"- **Нетто подрядчику:** `{net_sub:,.2f} ₽`")
        st.caption("Сумма, которую реально получает подрядчик за вычетом НДС.")

        st.markdown(f"- **НДС клиента:** `{client_nds:,.2f} ₽`")
        st.caption("20% от выставленной клиенту суммы (если она включает НДС).")

        st.markdown(f"- **Нетто от клиента:** `{client_net:,.2f} ₽`")
        st.caption("Сумма, полученная от клиента без НДС.")

        st.markdown(f"- **Убыток по НДС (75%):** `{nds_loss:,.2f} ₽`")
        st.caption("Часть входящего НДС, которую нельзя зачесть — условный убыток. Берётся 75% от НДС подрядчика.")

        st.markdown(f"- **Прямые расходы:** `{direct_costs:,.2f} ₽`")
        st.caption("Нетто подрядчику + убыток по НДС. Всё, что компания тратит напрямую.")

        st.markdown(f"- **Налоговая база:** `{tax_base:,.2f} ₽`")
        st.caption("Разница между доходом от клиента и прямыми расходами.")

        st.markdown(f"- **Налог на прибыль (5%):** `{tax:,.2f} ₽`")
        st.caption("5% от налоговой базы — упрощённый расчёт налога на прибыль.")

        st.success(f"💰 **Чистая прибыль:** `{profit:,.2f} ₽`")
        st.caption("То, что остаётся после всех налогов и расходов.")
    else:
        tax_base = client_net - total_partner_sum
        tax = tax_base * 0.05
        profit = tax_base - tax

        st.markdown(f"- **Нетто подрядчику (без НДС):** `{total_partner_sum:,.2f} ₽`")
        st.caption("Полная сумма, уплаченная подрядчику (без НДС).")

        st.markdown(f"- **НДС клиента:** `{client_nds:,.2f} ₽`")
        st.markdown(f"- **Нетто от клиента:** `{client_net:,.2f} ₽`")

        st.markdown(f"- **Налоговая база:** `{tax_base:,.2f} ₽`")
        st.markdown(f"- **Налог на прибыль (5%):** `{tax:,.2f} ₽`")

        st.success(f"💰 **Чистая прибыль:** `{profit:,.2f} ₽`")
>
