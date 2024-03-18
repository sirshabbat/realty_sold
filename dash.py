import pandas as pd
import numpy as np
import streamlit as st
import base64
import toml



st.set_page_config(page_title='Nikoliers · Анализ спроса',
                  page_icon='https://nikoliers.ru/favicon.ico',
                  layout='wide')

st.markdown(
    """
    <style>
    body {
        zoom: 85%;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

# REALTY_SOLD
df = pd.read_pickle('realty_sold_06032024_SPB_LO.gz')


df = df[(df['Купил лотов в ЖК'].isin(np.arange(1,6))) & (df['Покупатель ЮЛ'].isna())] # лотов [1;5] + ЮЛ - NaN
df = df.rename(columns={"ЖК рус": "ЖК_рус"}) # переименуем, чтобы streamlit не ругался
df = df.replace('Шипилевский', 'Шепилевский') # переименуем на "Шепилевский"
df = df[df['Уступка'] == 0] # уберём уступки
df['Цена_м2'] = df['Оценка цены'] / df['Площадь']


# NEW HISTORY
df1 = pd.read_pickle('new_history_04032024_SPB_LO.gz')
df1 = df1.rename(columns={"ЖК рус": "ЖК_рус"}) # переименуем, чтобы streamlit не ругался





projects = sorted(df['ЖК_рус'].unique())



months = ['январь', 'февраль', 'март',
          'апрель', 'май', 'июнь',
          'июль', 'август', 'сентябрь',
          'октябрь', 'ноябрь', 'декабрь']
month_map = {1: 'янв', 2: 'фев', 3: 'мар',
             4: 'апр', 5: 'май', 6: 'июн',
             7: 'июл', 8: 'авг', 9: 'сен',
             10: 'окт', 11: 'ноя', 12: 'дек'}


dummy_df = pd.DataFrame()
dummy_df['Общий итог'] = ['']
dummy_df.loc['Итог по месяцам'] = ['']






# --- ОСНОВНАЯ ЧАСТЬ --- #



st.title("Nikoliers · Анализ спроса")

st.markdown("&nbsp;")



col1, col2 = st.columns(2)
with col1:
    time_min = pd.to_datetime(st.date_input("\U0001f5d3\ufe0f **Выберите начальную дату:**",
                                            value=pd.to_datetime('2023-01-01 00:00:00')))
with col2:
    time_max = pd.to_datetime(st.date_input("\U0001f5d3\ufe0f **Выберите конечную дату:**",
                                            value=pd.to_datetime('2023-12-31 00:00:00')))

st.markdown("&nbsp;")


# ПОЛЗУНКИ
st.sidebar.image('https://nikoliers.ru/assets/img/nikoliers_logo.png', width=230)

st.sidebar.markdown("&nbsp;")

proj = st.sidebar.multiselect('**Выберите проект**:',
                              options=projects)
#st.sidebar.markdown("&nbsp;")

apart_type = st.sidebar.multiselect('**Выберите тип помещения**:',
                                    options=df[df['ЖК_рус'].isin(proj)]['Тип помещения'].unique())

st.sidebar.markdown("&nbsp;")

option = st.sidebar.radio('**Выберите опцию**:', ('Конкурентный обзор', 'Экспозиция'), index=None)









# --- ФУНКЦИИ --- #


# ВЫДЕЛЕНИЕ ПОСЛЕДНЕЙ СТРОКИ
def highlight_last_row(s):
    return ['background-color: #B1E2C0' if i == (len(s) - 1) else '' for i in range(len(s))]


# ВЫДЕЛЕНИЕ ПОСЛЕДНЕЙ СТРОКИ + СТОЛБЦА
def highlight_last_row_and_column(s):
    return ['background-color: #B1E2C0' if (i == (len(s) - 1) or s.name == 'Общий итог') else '' for i in range(len(s))]


# ДДУ ГОТОВО
def get_ddu(name, ap_types):
    project_ddu = df[(df['ЖК_рус'] == name) &
                     (df['Дата регистрации'] >= time_min) &
                     (df['Дата регистрации'] <= time_max) &
                     (df['Тип помещения'].isin(ap_types))].pivot_table(
        index='Тип Комнатности',
        values='ЖК_рус',
        columns=df['Дата регистрации'].dt.month,
        aggfunc='count')

    if project_ddu.shape[0] == 0:
        return dummy_df
        #return st.write('<h6>Невозможно составить таблицу с заданными фильтрами</h6>', unsafe_allow_html=True)
    else:
        project_ddu.fillna(0, inplace=True)
        project_ddu = project_ddu.assign(total=project_ddu.sum(axis=1))
        project_ddu.rename(columns={'total': 'Общий итог'}, inplace=True)
        project_ddu.loc['Итог по месяцам'] = project_ddu.sum()
        project_ddu.rename(columns=month_map, inplace=True)
        project_ddu = project_ddu.applymap(int)
        project_ddu.replace(0, '', inplace=True)
        return project_ddu#.style.format(precision=0).apply(highlight_last_row_and_column)


# Средняя стоимость м2, тыс руб. ГОТОВО
def get_mean_m2(name, ap_types):
    project_mean_m2_price = df[(df['ЖК_рус'] == name) &
                               (df['Дата регистрации'] >= time_min) &
                               (df['Дата регистрации'] <= time_max) &
                               (df['Тип помещения'].isin(ap_types))].pivot_table(
        index='Тип Комнатности',
        values='Оценка цены',
        columns=df['Дата регистрации'].dt.month,
        aggfunc='sum')

    project_mean_m2_price['Общий итог'] = project_mean_m2_price.sum(axis=1)

    project_mean_m2_square = df[(df['ЖК_рус'] == name) &
                                (df['Дата регистрации'] >= time_min) &
                                (df['Дата регистрации'] <= time_max)].pivot_table(
        index='Тип Комнатности',
        values='Площадь',
        columns=df['Дата регистрации'].dt.month,
        aggfunc='sum')

    project_mean_m2_square['Общий итог'] = project_mean_m2_square.sum(axis=1)

    if project_mean_m2_price.shape[0] == 0:
        return dummy_df
        #return st.write('<h6>Невозможно составить таблицу с заданными фильтрами</h6>', unsafe_allow_html=True)
    else:
        new_mean_m2 = project_mean_m2_price / project_mean_m2_square / 1000
        # new_mean_m2['Общий итог'] = project_mean_m2_price.sum(axis=1) / project_mean_m2_square.sum(axis=1) / 1000
        new_mean_m2.loc['Итог по месяцам'] = project_mean_m2_price.sum(axis=0) / project_mean_m2_square.sum(axis=0) / 1000
        # new_mean_m2.loc['Итог по месяцам'] = new_mean_m2.sum(axis=0)
        new_mean_m2.fillna(0, inplace=True)
        new_mean_m2.rename(columns=month_map, inplace=True)
        new_mean_m2 = new_mean_m2.applymap(round)
        new_mean_m2.replace(0, '', inplace=True)
        return new_mean_m2#.style.format(precision=0).apply(highlight_last_row_and_column)


# Средняя площадь, м2 ГОТОВО
def get_mean_square(name, ap_types):
    project_mean_square = df[(df['ЖК_рус'] == name) &
                             (df['Дата регистрации'] >= time_min) &
                             (df['Дата регистрации'] <= time_max) &
                             (df['Тип помещения'].isin(ap_types))].pivot_table(
        index='Тип Комнатности',
        values='Площадь',
        columns=df['Дата регистрации'].dt.month,
        aggfunc='mean')

    df_filtered = df[(df['ЖК_рус'] == name) &
                     (df['Тип помещения'].isin(ap_types)) &
                     (df['Дата регистрации'] >= time_min) &
                     (df['Дата регистрации'] <= time_max)]

    if project_mean_square.shape[0] == 0:
        return dummy_df
        #return st.write('<h6>Невозможно составить таблицу с заданными фильтрами</h6>', unsafe_allow_html=True)
    else:
        project_mean_square.loc['Итог по месяцам'] = [df_filtered[df_filtered['Дата регистрации'].dt.month == month]['Площадь'].mean() for month in sorted(df_filtered['Дата регистрации'].dt.month.unique())]
        project_mean_square['Общий итог'] = [df_filtered[df_filtered['Тип Комнатности'] == apart]['Площадь'].mean() for apart in sorted(df_filtered['Тип Комнатности'].dropna().unique())] + [df_filtered['Площадь'].mean()]

        project_mean_square.fillna(0, inplace=True)
        project_mean_square.rename(columns=month_map, inplace=True)
        project_mean_square.replace(0, '', inplace=True)
        return round(project_mean_square, 1)


# Средняя стоимость лота, млн руб. ГОТОВО
def get_mean_lot(name, ap_types):
    project_mean_lot = df[(df['ЖК_рус'] == name) &
                          (df['Дата регистрации'] >= time_min) &
                          (df['Дата регистрации'] <= time_max) &
                          (df['Тип помещения'].isin(ap_types))].pivot_table(
        index='Тип Комнатности',
        values='Оценка цены',
        columns=df['Дата регистрации'].dt.month,
        aggfunc='mean')

    df_filtered = df[(df['ЖК_рус'] == name) &
                     (df['Тип помещения'].isin(ap_types)) &
                     (df['Дата регистрации'] >= time_min) &
                     (df['Дата регистрации'] <= time_max)]

    if project_mean_lot.shape[0] == 0:
        return dummy_df
        #return st.write('<h6>Невозможно составить таблицу с заданными фильтрами</h6>', unsafe_allow_html=True)
    else:

        project_mean_lot.loc['Итог по месяцам'] = [df_filtered[df_filtered['Дата регистрации'].dt.month == month]['Оценка цены'].mean() for month in sorted(df_filtered['Дата регистрации'].dt.month.unique())]
        project_mean_lot['Общий итог'] = [df_filtered[df_filtered['Тип Комнатности'] == apart]['Оценка цены'].mean() for apart in sorted(df_filtered['Тип Комнатности'].dropna().unique())] + [df_filtered['Оценка цены'].mean()]

        project_mean_lot.fillna(0, inplace=True)
        project_mean_lot = project_mean_lot / 10 ** 6
        project_mean_lot.rename(columns=month_map, inplace=True)
        project_mean_lot = round(project_mean_lot, 1)
        project_mean_lot.replace(0, '', inplace=True)
        return project_mean_lot


# Итоговая таблица ГОТОВО
def get_main(ap_types):
    main_df = pd.DataFrame(columns=['Название проекта',
                                    'Количество зарегистрированных ДДУ, шт.',
                                    'Средняя площадь, м²',
                                    'Средняя стоимость м², тыс. руб.',
                                    'Средняя стоимость одного лота, млн руб.'])

    main_df['Название проекта'] = proj
    main_df['Количество зарегистрированных ДДУ, шт.'] = [get_ddu(name, apart_type)['Общий итог'].loc['Итог по месяцам'] for name in proj]
    main_df['Средняя площадь, м²'] = [get_mean_square(name, apart_type)['Общий итог'].loc['Итог по месяцам'] for name in proj]
    main_df['Средняя стоимость м², тыс. руб.'] = [get_mean_m2(name, apart_type)['Общий итог'].loc['Итог по месяцам'] for name in proj]
    main_df['Средняя стоимость одного лота, млн руб.'] = [get_mean_lot(name, apart_type)['Общий итог'].loc['Итог по месяцам'] for name in proj]
    main_df = main_df.set_index('Название проекта').replace('', '0').astype(float).round(1)

    df_filtered = df[(df['ЖК_рус'].isin(proj)) &
                     (df['Тип помещения'].isin(ap_types)) &
                     (df['Дата регистрации'] >= time_min) &
                     (df['Дата регистрации'] <= time_max)]

    main_df.loc['Итоговые значения'] = [main_df['Количество зарегистрированных ДДУ, шт.'].sum(),  # итоговое количество ДДУ
                      df_filtered[df_filtered['Тип Комнатности'].notna()]['Площадь'].mean(),  # итоговая средняя площадь
                      df_filtered[df_filtered['Тип Комнатности'].notna()]['Оценка цены'].sum() / df_filtered[df_filtered['Тип Комнатности'].notna()]['Площадь'].sum() / 1000,  # итоговая сред. стоимость м2
                      df_filtered[df_filtered['Тип Комнатности'].notna()]['Оценка цены'].mean() / 10**6]  # итоговая средняя цена лота
    main_df['Количество зарегистрированных ДДУ, шт.'] = main_df['Количество зарегистрированных ДДУ, шт.'].apply(int)
    main_df['Средняя стоимость м², тыс. руб.'] = main_df['Средняя стоимость м², тыс. руб.'].apply(round)

    return main_df


# Загрузка xlsx-файла
def download_dataframe_xlsx(x):
    with st.spinner('Загрузка файла...'):
        x.to_excel(f"Экспозиция с {str(time_min)[:-9][-2:]}-{str(time_min)[:-9][-5:-3]}-{str(time_min)[:-9][-10:-6]} по {str(time_max)[:-9][-2:]}-{str(time_max)[:-9][-5:-3]}-{str(time_max)[:-9][-10:-6]}.xlsx", index=False)
        st.success('Файл успешно скачан')



if (len(proj) * len(apart_type) != 0) and (option == 'Конкурентный обзор'):
    st.write('<h4> Итоговая таблица по проектам:</h4>', unsafe_allow_html=True)
    st.write(get_main(apart_type).style.format(precision=1).apply(highlight_last_row))
    st.markdown("&nbsp;")
    st.markdown("---")
    st.markdown("&nbsp;")

    for project in proj:

        st.markdown(f'<h4> 🏢 {project}</h4>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write('<h5> 1️⃣ Количество зарегистрированных ДДУ, шт.</h5>', unsafe_allow_html=True)
            st.dataframe(get_ddu(project, apart_type).style.format(precision=0).apply(highlight_last_row_and_column))
            st.markdown("&nbsp;")
        with col2:
            st.write('<h5> 2️⃣ Средняя площадь, м²</h5>', unsafe_allow_html=True)
            st.dataframe(get_mean_square(project, apart_type).style.format(precision=1).apply(highlight_last_row_and_column))
            st.markdown("&nbsp;")
        with col1:
            st.write('<h5> 3️⃣ Средняя стоимость м², тыс. руб.</h5>', unsafe_allow_html=True)
            st.dataframe(get_mean_m2(project, apart_type).style.format(precision=0).apply(highlight_last_row_and_column))
        with col2:
            st.write('<h5> 4️⃣ Средняя стоимость одного лота, млн руб.</h5>', unsafe_allow_html=True)
            st.dataframe(get_mean_lot(project, apart_type).style.format(precision=1).apply(highlight_last_row_and_column))
        st.markdown("&nbsp;")
        st.markdown('---')
        st.markdown("&nbsp;")
elif option == 'Экспозиция':
    result = []
    final_list = []
    # final_proj = []
    original_list = []

    df_filtered = df[(df['Тип помещения'].isin(apart_type)) &
                     (df['Дата регистрации'] >= time_min) &
                     (df['Дата регистрации'] <= time_max)]

    dummy_exp_df = pd.DataFrame()
    dummy_exp_df['Тип Комнатности'] = sorted(list(map(str, df['Тип Комнатности'].unique())))
    dummy_exp_df['Сред. цена м², тыс. р.'] = [''] * len(sorted(list(map(str, df['Тип Комнатности'].unique()))))
    dummy_exp_df.set_index('Тип Комнатности', inplace=True)

    for project in proj:

        df_filtered = df[(df['ЖК_рус'] == project) &
                         (df['Тип помещения'].isin(apart_type)) &
                         (df['Дата регистрации'] >= time_min) &
                         (df['Дата регистрации'] <= time_max)]

        if (df_filtered['Тип Комнатности'].isnull().sum() == df_filtered.shape[0]) or (
                df_filtered['Площадь'].isnull().sum() == df_filtered.shape[0]) or (
                df_filtered['Оценка цены'].isnull().sum() == df_filtered.shape[0]):
            pass

        else:

            # final_proj.append(project)

            pivot_1 = df_filtered.pivot_table(
                index='Тип Комнатности',
                values='ЖК_рус',
                aggfunc='count')
            pivot_1.rename(columns={'ЖК_рус': 'Кол-во, шт.'}, inplace=True)

            pivot_2 = df_filtered.pivot_table(
                index='Тип Комнатности',
                values='Площадь',
                aggfunc='mean')
            pivot_2.rename(columns={'Площадь': 'Сред. площадь, м²'}, inplace=True)
            pivot_2 = pivot_2.round(1)

            pivot_3 = df_filtered.pivot_table(
                index='Тип Комнатности',
                values='Оценка цены',
                aggfunc='min')
            pivot_3 = pivot_3 / 10 ** 6
            pivot_3.rename(columns={'Оценка цены': 'Мин. цена, млн р.'}, inplace=True)
            pivot_3 = pivot_3.round(1)

            pivot_4 = df_filtered.pivot_table(
                index='Тип Комнатности',
                values='Оценка цены',
                aggfunc='max')
            pivot_4 = pivot_4 / 10 ** 6
            pivot_4.rename(columns={'Оценка цены': 'Макс. цена, млн р.'}, inplace=True)
            pivot_4 = pivot_4.round(1)

            pivot_5 = df_filtered.pivot_table(
                index='Тип Комнатности',
                values='Оценка цены',
                aggfunc='mean')
            pivot_5 = pivot_5 / 10 ** 6
            pivot_5.rename(columns={'Оценка цены': 'Сред. цена, млн р.'}, inplace=True)
            pivot_5 = pivot_5.round(1)

            pivot_6 = df_filtered.pivot_table(
                index='Тип Комнатности',
                values='Цена_м2',
                aggfunc='min')
            pivot_6 = pivot_6 / 1000
            pivot_6.rename(columns={'Цена_м2': 'Мин. цена м², тыс. р.'}, inplace=True)
            pivot_6 = pivot_6.applymap(round)

            pivot_7 = df_filtered.pivot_table(
                index='Тип Комнатности',
                values='Цена_м2',
                aggfunc='max')
            pivot_7 = pivot_7 / 1000
            pivot_7.rename(columns={'Цена_м2': 'Макс. цена м², тыс. р.'}, inplace=True)
            pivot_7 = pivot_7.applymap(round)

            pivot_8 = pd.DataFrame()
            pivot_8['Тип Комнатности'] = df_filtered.pivot_table(index='Тип Комнатности', values='Оценка цены',
                                                                 aggfunc='sum').index
            pivot_8['Сред. цена м², тыс. р.'] = df_filtered.pivot_table(index='Тип Комнатности', values='Оценка цены',
                                                                        aggfunc='sum').values / df_filtered.pivot_table(
                index='Тип Комнатности', values='Площадь', aggfunc='sum').values
            pivot_8['Сред. цена м², тыс. р.'] = pivot_8['Сред. цена м², тыс. р.'] / 1000
            pivot_8.set_index('Тип Комнатности', inplace=True)
            pivot_8 = pivot_8.applymap(round)

            df_test = pd.concat([pivot_1, pivot_2, pivot_3, pivot_4, pivot_5, pivot_6, pivot_7, pivot_8], axis=1)
            original_list.extend([project] + [''] * (df_test.shape[0] - 1))
            # df_test = df_test.set_index(pd.Index([project] + [''] * (df_test.shape[0]-1)))
            result.append(df_test)

    # for sublist in original_list:
    #   final_list.extend(sublist)

    final_exp = pd.concat(result).reset_index()
    final_exp = final_exp.set_index(pd.Index(original_list))
    #st.dataframe(final_exp)
    st.markdown(
        f'<div style="display: flex; justify-content: center;">'
        f'{final_exp.to_html(classes="dataframe", index=True)}'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("&nbsp;")

    download = st.button('Выгрузить таблицу в формате .xlsx')

    if download:
        download_dataframe_xlsx(final_exp)

















