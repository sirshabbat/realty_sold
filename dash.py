import pandas as pd
import numpy as np
import streamlit as st
from streamlit_option_menu import option_menu
import calendar
import datetime
import plotly.express as px



# ПАРАМЕТРЫ СТРАНИЦЫ

st.set_page_config(page_title='Nikoliers · Конкурентный обзор',
                  page_icon='https://nikoliers.ru/favicon.ico',
                  layout='wide')
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ЗАГРУЗКА ДАННЫХ



# REALTY_SOLD SPB
@st.cache_data()
def load_realty_sold_spb():
    df = pd.read_pickle('realty_sold_06082024_SPB_LO.gz')
    df = df[(df['Купил лотов в ЖК'].isin(np.arange(1, 6))) & (df['Покупатель ЮЛ'].isna())]  # лотов [1;5] + ЮЛ - NaN
    df = df.rename(columns={"ЖК рус": "ЖК_рус"})
    df = df.replace('Шипилевский', 'Шепилевский')  # переименуем на "Шепилевский"
    df = df[df['Уступка'] == 0]  # уберём уступки
    df['Цена_м2'] = df['Оценка цены'] / df['Площадь']
    df['Тип Комнатности'].dropna(inplace=True)
    df['Дата'] = df['Дата регистрации'].dt.to_period('M')
    return df

# NEW HISTORY SPB
@st.cache_data()
def load_new_history_spb():
    df1 = pd.read_pickle('new_history_02082024_SPB_LO.gz')
    df1 = df1.rename(columns={"ЖК рус": "ЖК_рус"})
    df1['Дата актуализации'] = pd.to_datetime(df1['Дата актуализации'])
    df1 = df1.replace('Шипилевский', 'Шепилевский')
    df1['Комнат'].dropna(inplace=True)
    df1['ЖК_рус'] = df1['ЖК_рус'].str.strip()
    return df1

# REALTY_SOLD MOSCOW
@st.cache_data()
def load_realty_sold_moscow():
    df = pd.read_pickle('realty_sold_05082024_M.gz')
    df = df[(df['Купил лотов в ЖК'].isin(np.arange(1, 6))) & (df['Покупатель ЮЛ'].isna())]  # лотов [1;5] + ЮЛ - NaN
    df = df.rename(columns={"ЖК рус": "ЖК_рус"})
    df = df[df['Уступка'] == 0]  # уберём уступки
    df['Цена_м2'] = df['Оценка цены'] / df['Площадь']
    df['Тип Комнатности'].dropna(inplace=True)
    df['Дата'] = df['Дата регистрации'].dt.to_period('M')
    return df

# NEW HISTORY MOSCOW
@st.cache_data()
def load_new_history_moscow():
    df1 = pd.read_pickle('new_history_02082024_M.gz')
    df1 = df1.rename(columns={"ЖК рус": "ЖК_рус"})
    df1['Дата актуализации'] = pd.to_datetime(df1['Дата актуализации'])
    df1['Комнат'].dropna(inplace=True)
    return df1

# АКЦИИ (СПБ)
def load_promo():
    df = pd.read_excel('Акции_16.01.xlsx')[['ЖК', 'Название акции', 'Размер скидки', 'Дата начала акции', 'Дата окончания акции', 'Условия акции', 'Кол-во апартаментов под акцией']]
    df['ЖК'] = df['ЖК'].str.strip()
    return df

# ИПОТЕКА (СПБ)
@st.cache_data()
def load_mortgage():
    df = pd.read_excel('Ипотека_16.01.xlsx')[['ЖК', 'Банк', 'Название ипотеки', 'Ставка min', 'Период (лет)', 'Первый платёж (от %)']]
    df['ЖК'] = df['ЖК'].str.strip()
    return df

# РАССРОЧКА (СПБ)
@st.cache_data()
def load_split():
    df = pd.read_excel('Рассрочка_16.01.xlsx')[['ЖК', 'Ставка', 'Первый взнос', 'Годовых', 'Макс. Срок']]
    df['ЖК'] = df['ЖК'].str.strip()
    return df

# ТАБЛИЦА С СООТВЕТСТВИЕМ НАЗВАНИЙ ПРОЕКТОВ (ДЛЯ ИПОТЕК, АКЦИЙ И РАССРОЧЕК)
@st.cache_data()
def load_help():
    help = pd.read_excel('test.xlsx')
    help['demand'] = help['demand'].str.strip()
    help['source'] = help['source'].str.strip()
    return help



# ОПРЕДЕЛЕНИЕ ВТОРОСТЕПЕННЫХ ФУНКЦИЙ
# ПУСТАЯ ТАБЛИЦА
@st.cache_data
def get_dummy_df():
    dummy_df = pd.DataFrame()
    dummy_df['Общий итог'] = ['']
    dummy_df.loc['Итог по месяцам'] = ['']
    return dummy_df



# ВЫДЕЛЕНИЕ ПОСЛЕДНЕГО СТОЛБЦА И ПРЕДПОСЛЕДНЕЙ СТРОКИ ТАБЛИЦЫ
@st.cache_data
def highlight_last_row_and_column(s):
    return ['background-color: #FFFFFF' if (i == (len(s) - 2) or s.name == 'Общий итог') else 'background-color: #FFFFFF' if (i == len(s) - 1) else '' for i in range(len(s))] # ещё хороший цвет: #82C4DE



# ВЫДЕЛЕНИЕ ЦВЕТОМ ЗНАЧЕНИЙ В ТЕМПЕ
@st.cache_data
def color_negative_red(val):
    color = 'red' if str(val).startswith('-') else 'green'
    return f'color: {color}'



# ПОКРАСКА СТРОКИ С ДЕВЕЛОПЕРОМ ELEMENT
@st.cache_data
def color_element(row):
    if row['Девелопер/Застройщик'] == 'Element':
        return ['background-color: #e4ecf5'] * len(row)
    else:
        return [''] * len(row)



# ОКРАСКА СТОИМОСТИ М2 В ПУЛЬСЕ
@st.cache_data
def color_price_m2(column):
    if column.name == f'Стоимость м² на {prev_month}/{prev_year}, тыс. руб' \
            or column.name == f'Стоимость м² на {today_month}/{today_year}, тыс. руб':
            #or column.name == 'Изменение (стоимость м²)':
        return ['background-color: #defbdf'] * len(column)
    else:
        return [''] * len(column)


# ОКРАСКА ИТОГОВ ПО СТОИМОСТИ М2 В ПУЛЬСЕ
@st.cache_data
def color_price_m2_result(column):
    if column.name == 'Изменение (стоимость м²)':
        return ['background-color: #b4f7b7'] * len(column)
    else:
        return [''] * len(column)



# ОКРАСКА КОЛИЧЕСТВА В ПУЛЬСЕ
@st.cache_data
def color_number(column):
    if column.name == f'Кол-во на {prev_month}/{prev_year}' \
            or column.name == f'Кол-во на {today_month}/{today_year}':
            #or column.name == 'Изменение (кол-во)':
        return ['background-color: #f5fbda'] * len(column)
    else:
        return [''] * len(column)



# ОКРАСКА ИТОГОВ ПО КОЛИЧЕСТВУ В ПУЛЬСЕ
@st.cache_data
def color_number_result(column):
    if column.name == "Изменение (кол-во)":
        return ['background-color: #e8f9a2'] * len(column)
    else:
        return [''] * len(column)




# ВЫГРУЗКА ТАБЛИЦЫ В XLSX
@st.cache_data
def download_dataframe_xlsx(x):
    with st.spinner('Загрузка файла...'):
        x.to_excel(f"Экспозиция.xlsx", index=True)
        st.success('Файл успешно скачан')



# ПОЛУЧЕНИЕ 3 ПРЕДЫДУЩИХ МЕСЯЦЕВ ОТ СЕГОДНЯШНЕГО ДЛЯ РАБОТЫ С ДАТАМИ
def get_3_prev_months(x):
    if x == 1:
        return 1, 12, 11, 10
    if x == 2:
        return 2, 1, 12, 11
    if x == 3:
        return 3, 2, 1, 12
    else:
        return x, x-1, x-2, x-3





today_month = get_3_prev_months(datetime.datetime.today().month)[1]
prev_month = get_3_prev_months(datetime.datetime.today().month)[2]

if datetime.datetime.today().day > 5:
    today_month = get_3_prev_months(datetime.datetime.today().month)[1]
    prev_month = get_3_prev_months(datetime.datetime.today().month)[2]
else:
    today_month = get_3_prev_months(datetime.datetime.today().month)[2]
    prev_month = get_3_prev_months(datetime.datetime.today().month)[3]
if today_month == 1:
    today_year = datetime.datetime.today().year
    prev_year = today_year - 1
elif today_month == 12:
    today_year = prev_year = datetime.datetime.today().year - 1
else:
    today_year = prev_year = datetime.datetime.today().year






# ПРОЕКТЫ ELEMENT DEVELOPMENT
proj_dict = {"Берег Курортный": [#'Глоракс Балтийская',
                                 'Глоракс Василеостровский', 'Глоракс Премиум Василеостровский',
                                 'Резиденция Рощино', 'Лисино', 'Морская Набережная', 'Нева Резиденс', 'Аквилон Залив',
                                 'Форест Аквилон', 'Панорама Парк Сосновка', 'Репино парк', 'Модум', 'Ариосто',
                                 'Берег.Курортный',
                                 'Морская Ривьера', 'Русские сезоны', 'Е.Квартал Мир Внутри', 'Лахта Парк'],

             "1919/Shepilevskiy": ['Куинджи', 'Дефанс', 'Таленто', 'Миръ', 'Империал Клаб', 'Ай Ди Московский',
                                   'Ай Ди Парк Победы', 'Виктори Плаза', 'Эволюций', 'Шепилевский',
                                   'Коллекционный дом 1919',
                                   'Астра Марин', 'Акцент', 'Авант', 'Квартал Че'],

             "17/33 Петровский остров": ['Нева Резиденс', 'Нева Хаус', 'Дзен Гарден', 'Аструм', 'Гранд Вью', 'Уан',
                                         'Уан Тринити Плейс', 'Крестовский 4', 'Парусная 1', 'Петровская Коса',
                                         'Петровская доминанта', 'Петровский остров 1733', 'Императорский яхт-клуб',
                                         'Резиденция на Малой Невке', 'Три грации', 'Северная корона']}


# ВТОРОСТЕПЕННЫЕ СЛОВАРИ/СПИСКИ


months = {'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
          'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
          'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12}


# ПОЛЗУНКИ / ФИЛЬТРЫ

st.title("Nikoliers · Конкурентный обзор")

st.sidebar.image('https://nikoliers.ru/assets/img/nikoliers_logo.png')

st.sidebar.markdown("&nbsp;")



#password = st.sidebar.text_input('**Введите пароль:**',  type='password')
#if password != 'EDN2024':
#    st.sidebar.warning('Введён неверный пароль')
#else:

with st.sidebar:
    city = option_menu('Выбор города:', ('Санкт-Петербург', 'Москва'), icons=[' ', ' '], menu_icon='building-check', default_index=0, styles={
                        "container": {"padding": "0!important", "background-color": "#F6F6F7"},
                        "nav-link": {
                            "font-size": "15px",
                            "text-align": "left",
                            "margin": "0px",
                            "--hover-color": "#EEEEEE",
                        },
                        "nav-link-selected": {"background-color": "#3250C0"},
                    })
    option = option_menu('Выбор опции:', ['Пульс продаж', 'Анализ спроса', 'Анализ предложения'],
                         icons=[' ', ' ', ' ', ' '], menu_icon='filter-right', default_index=0, styles={
            "container": {"padding": "0!important", "background-color": "#F6F6F7"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#EEEEEE",
            },
            "nav-link-selected": {"background-color": "#3250C0"},
        })
    st.sidebar.markdown("&nbsp;")
#    if city == 'Санкт-Петербург':
#        option = option_menu('Выбор опции:', ['Пульс продаж', 'Анализ спроса', 'Анализ предложения'], icons=[' ', ' ', ' '], menu_icon='filter-right', default_index=0, styles={
#                        "container": {"padding": "0!important", "background-color": "#F6F6F7"},
#                        "nav-link": {
#                            "font-size": "15px",
#                            "text-align": "left",
#                            "margin": "0px",
#                            "--hover-color": "#EEEEEE",
#                        },
#                        "nav-link-selected": {"background-color": "#3250C0"},
#                    })
#    else:
#        option = option_menu('Выбор опции:', ['Пульс продаж', 'Анализ спроса', 'Анализ предложения'],
#                             icons=[' ', ' ', ' ', ' '], menu_icon='filter-right', default_index=0, styles={
#                "container": {"padding": "0!important", "background-color": "#F6F6F7"},
#                "nav-link": {
#                    "font-size": "15px",
#                    "text-align": "left",
#                    "margin": "0px",
#                    "--hover-color": "#EEEEEE",
#                },
#                "nav-link-selected": {"background-color": "#3250C0"},
#            })
#    st.sidebar.markdown("&nbsp;")




    #option = st.sidebar.radio('**Выберите опцию**:', ('Анализ спроса', 'Анализ предложения'), index=0)

    #st.sidebar.markdown("&nbsp;")



if city == 'Санкт-Петербург' and option != 'Пульс продаж':
        df = load_realty_sold_spb()
        df1 = load_new_history_spb()
        proj_ed = st.sidebar.selectbox('**Выберите проект ED:**', proj_dict.keys(), index=None)

else:
        df = load_realty_sold_moscow()
        df1 = load_new_history_moscow()
        proj_ed = ''




if option == 'Анализ спроса':

        st.subheader('Анализ спроса')
        st.markdown("&nbsp;")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            year_min = st.selectbox('**:calendar:Выберите начальный год**',
                                sorted(list(map(int, df['Дата регистрации'].dt.year.dropna().unique())),
                                       reverse=True),
                                index=0)
        with col2:
            month_min = st.selectbox('**:spiral_calendar_pad:Выберите начальный месяц**', months.keys())

        with col3:
            year_max = st.selectbox('**:calendar:Выберите конечный год**',
                                    sorted(list(map(int, df['Дата регистрации'].dt.year.dropna().unique())),
                                           reverse=True),
                                    index=0)
        with col4:
            month_max = st.selectbox('**:spiral_calendar_pad:Выберите конечный месяц**', months.keys(), index=(datetime.datetime.today().month - 1))


        st.markdown("&nbsp;")
        #df = load_realty_sold_spb()
        if proj_ed:
            proj = st.sidebar.multiselect('**Выберите проект:**', sorted(df['ЖК_рус'].unique()), default=sorted(list(set(proj_dict[proj_ed]).intersection(df['ЖК_рус'].unique()))))
            df = df[df['ЖК_рус'].isin(proj)]
            apart_type = st.sidebar.multiselect('**Выберите тип помещения:**', sorted(df['Тип помещения'].unique()))
            df = df[df['Тип помещения'].isin(apart_type)]



            date_max = pd.to_datetime(f"{year_max}-{months[month_max]}-{calendar.monthrange(int(year_max), int(months[month_max]))[1]}")
            date_min = pd.to_datetime(f"{year_min}-{months[month_min]}-{1}")

            #date_min = df[(df['Дата регистрации'].dt.year == year_min) & (df['Дата регистрации'].dt.month == months[month_min])]['Дата регистрации'].min()
            #date_max = df[(df['Дата регистрации'].dt.year == year_max) & (df['Дата регистрации'].dt.month == months[month_max])]['Дата регистрации'].max()


            df = df[(df['Дата регистрации'] >= date_min) & (df['Дата регистрации'] <= date_max)]


        else:
            proj = st.sidebar.multiselect('**Выберите проект:**', sorted(df['ЖК_рус'].unique()))
            df = df[df['ЖК_рус'].isin(proj)]
            apart_type = st.sidebar.multiselect('**Выберите тип помещения:**', sorted(df['Тип помещения'].unique()))
            df = df[df['Тип помещения'].isin(apart_type)]

            date_max = pd.to_datetime(f"{year_max}-{months[month_max]}-{calendar.monthrange(int(year_max), int(months[month_max]))[1]}")
            date_min = pd.to_datetime(f"{year_min}-{months[month_min]}-{1}")

            #date_min = df[(df['Дата регистрации'].dt.year == year_min) & (df['Дата регистрации'].dt.month == months[month_min])]['Дата регистрации'].min()
            #date_max = df[(df['Дата регистрации'].dt.year == year_max) & (df['Дата регистрации'].dt.month == months[month_max])]['Дата регистрации'].max()


            df = df[(df['Дата регистрации'] >= date_min) & (df['Дата регистрации'] <= date_max)]


        def get_ddu(name):
            project_ddu = df[df['ЖК_рус'] == name].pivot_table(
                index='Тип Комнатности',
                values='ЖК_рус',
                columns=df['Дата'],
                aggfunc='count')

            if project_ddu.shape[0] == 0:
                return get_dummy_df()
            else:
                project_ddu = project_ddu.assign(total=project_ddu.sum(axis=1))
                project_ddu.rename(columns={'total': 'Общий итог'}, inplace=True)
                project_ddu.loc['Итог по месяцам'] = project_ddu.sum()
                temp = ['']
                result = list(project_ddu.loc['Итог по месяцам'])
                for i in range(len(result)-1):
                    temp.append(f'{round((result[i + 1] - result[i]) / result[i] * 100)}%')
                temp[-1] = ''
                project_ddu.loc['Динамика'] = temp
                # project_ddu.rename(columns=month_map, inplace=True)
                #project_ddu.replace(0, '', inplace=True)

                return project_ddu  # .style.format(precision=0).apply(highlight_last_row_and_column)
        def get_mean_m2(name):
            df_filtered = df[(df['ЖК_рус'] == name) & (df['Дата регистрации'] >= date_min) & (df['Дата регистрации'] <= date_max)]
            df_filtered = df_filtered[['Тип Комнатности', 'Оценка цены', 'Дата', 'Площадь', 'ЖК_рус']].dropna()
            project_mean_m2_price = df_filtered[df_filtered['ЖК_рус'] == name].pivot_table(
                index='Тип Комнатности',
                values='Оценка цены',
                columns=df_filtered['Дата'],
                aggfunc='sum')

            project_mean_m2_price['Общий итог'] = project_mean_m2_price.sum(axis=1)

            project_mean_m2_square = df_filtered[df_filtered['ЖК_рус'] == name].pivot_table(
                index='Тип Комнатности',
                values='Площадь',
                columns=df_filtered['Дата'],
                aggfunc='sum')

            project_mean_m2_square['Общий итог'] = project_mean_m2_square.sum(axis=1)

            if project_mean_m2_price.shape[0] == 0:
                return get_dummy_df()
                # return st.write('<h6>Невозможно составить таблицу с заданными фильтрами</h6>', unsafe_allow_html=True)
            else:
                new_mean_m2 = project_mean_m2_price / project_mean_m2_square / 1000
                # new_mean_m2['Общий итог'] = project_mean_m2_price.sum(axis=1) / project_mean_m2_square.sum(axis=1) / 1000
                new_mean_m2.loc['Итог по месяцам'] = project_mean_m2_price.sum(axis=0) / project_mean_m2_square.sum(axis=0) / 1000
                # new_mean_m2.loc['Итог по месяцам'] = new_mean_m2.sum(axis=0)
                new_mean_m2.fillna(0, inplace=True)
                temp = ['']
                new_mean_m2.loc['Итог по месяцам'] = new_mean_m2.loc['Итог по месяцам'].replace(0.0, np.nan)
                result = list(new_mean_m2.loc['Итог по месяцам'])
                #new_mean_m2.loc['Итог по месяцам'] = new_mean_m2.loc['Итог по месяцам'].replace(0.0, np.nan)
                for i in range(len(result) - 1):
                    temp.append(f'{np.round((result[i + 1] - result[i]) / result[i] * 100)}%')
                temp[-1] = ''
                new_mean_m2.loc['Динамика'] = temp
                # new_mean_m2.rename(columns=month_map, inplace=True)
                #new_mean_m2.replace(0, '', inplace=True)
                return new_mean_m2  # .style.format(precision=0).apply(highlight_last_row_and_column)
        def get_mean_square(name):
            df_filtered = df[(df['ЖК_рус'] == name) & (df['Дата регистрации'] >= date_min) & (df['Дата регистрации'] <= date_max)]
            df_filtered = df_filtered[df_filtered['Тип Комнатности'].notna()]
            project_mean_square = df_filtered[df_filtered['ЖК_рус'] == name].pivot_table(
                index='Тип Комнатности',
                values='Площадь',
                columns='Дата',
                aggfunc='mean')

            #df_filtered = df[(df['ЖК_рус'] == name) & (df['Дата регистрации'] >= date_min) & (df['Дата регистрации'] <= date_max)]

            if project_mean_square.shape[0] == 0:
                return get_dummy_df()
                # return st.write('<h6>Невозможно составить таблицу с заданными фильтрами</h6>', unsafe_allow_html=True)
            else:
                project_mean_square.loc['Итог по месяцам'] = [df_filtered[df_filtered['Дата'] == date]['Площадь'].mean() for date in sorted(project_mean_square.columns)]#sorted(df_filtered['Дата'].unique())]
                project_mean_square['Общий итог'] = [df_filtered[df_filtered['Тип Комнатности'] == apart]['Площадь'].mean() for apart in sorted(df_filtered['Тип Комнатности'].dropna().unique())] + [df_filtered['Площадь'].mean()]

                #project_mean_square = round(project_mean_square, 1)
                project_mean_square.fillna(0, inplace=True)
                temp = ['']
                result = list(project_mean_square.loc['Итог по месяцам'])
                for i in range(len(result) - 1):
                    temp.append(f'{round((result[i + 1] - result[i]) / result[i] * 100)}%')
                temp[-1] = ''
                project_mean_square.loc['Динамика'] = temp

                #project_mean_square.replace(0, '', inplace=True)
                return project_mean_square
        def get_mean_lot(name):
            df_filtered = df[(df['ЖК_рус'] == name) & (df['Дата регистрации'] >= date_min) & (df['Дата регистрации'] <= date_max)]

            project_mean_lot = df_filtered[df_filtered['ЖК_рус'] == name].pivot_table(
                index='Тип Комнатности',
                values='Оценка цены',
                columns='Дата',
                aggfunc='mean')

            #df_filtered = df[(df['ЖК_рус'] == name) & (df['Дата регистрации'] >= date_min) & (df['Дата регистрации'] <= date_max)]

            if project_mean_lot.shape[0] == 0:
                return get_dummy_df()
                # return st.write('<h6>Невозможно составить таблицу с заданными фильтрами</h6>', unsafe_allow_html=True)
            else:

                df_filtered = df_filtered[['Тип Комнатности', 'Тип помещения', 'Оценка цены', 'Дата']].dropna()

                project_mean_lot.loc['Итог по месяцам'] = [df_filtered[df_filtered['Дата'] == date]['Оценка цены'].mean() for date in sorted(project_mean_lot.columns)]
                project_mean_lot['Общий итог'] = [df_filtered[df_filtered['Тип Комнатности'] == apart]['Оценка цены'].mean() for apart in sorted(df_filtered['Тип Комнатности'].dropna().unique())] + [df_filtered['Оценка цены'].mean()]

                project_mean_lot.fillna(0, inplace=True)
                project_mean_lot = project_mean_lot / 10 ** 6

                temp = ['']
                result = list(project_mean_lot.loc['Итог по месяцам'])
                for i in range(len(result) - 1):
                    temp.append(f'{round((result[i + 1] - result[i]) / result[i] * 100)}%')
                temp[-1] = ''
                project_mean_lot.loc['Динамика'] = temp
                # project_mean_lot.rename(columns=month_map, inplace=True)
                #project_mean_lot = round(project_mean_lot, 1)
                #project_mean_lot.replace(0, '', inplace=True)
                return project_mean_lot
        def get_main():
            main_df = pd.DataFrame(columns=['Название проекта',
                                            'Количество зарегистрированных ДДУ, шт.',
                                            'Средняя площадь, м²',
                                            'Средняя стоимость м², тыс. руб.',
                                            'Средняя стоимость одного лота, млн руб.'])

            main_df['Название проекта'] = proj
            main_df['Количество зарегистрированных ДДУ, шт.'] = [get_ddu(name)['Общий итог'].loc['Итог по месяцам'] for name in proj]
            main_df['Средняя площадь, м²'] = [get_mean_square(name)['Общий итог'].loc['Итог по месяцам'] for name in proj]
            main_df['Средняя стоимость м², тыс. руб.'] = [get_mean_m2(name)['Общий итог'].loc['Итог по месяцам'] for name in proj]
            main_df['Средняя стоимость одного лота, млн руб.'] = [get_mean_lot(name)['Общий итог'].loc['Итог по месяцам'] for name in proj]
            main_df = main_df.set_index('Название проекта').replace('', '0').astype(float)


            a = sum(main_df['Количество зарегистрированных ДДУ, шт.'] * main_df['Средняя стоимость одного лота, млн руб.'])
            b = sum(main_df['Количество зарегистрированных ДДУ, шт.'] * main_df['Средняя площадь, м²'])

            main_df['Количество зарегистрированных ДДУ, шт.'] = main_df['Количество зарегистрированных ДДУ, шт.'].apply(int)
            main_df['Средняя стоимость м², тыс. руб.'] = main_df['Средняя стоимость м², тыс. руб.'].apply(round)


            if b != 0 and sum(main_df['Количество зарегистрированных ДДУ, шт.']) != 0:
                mean_m2 = a / b * 1000
                ddu = sum(main_df['Количество зарегистрированных ДДУ, шт.'])
                mean_square = b / ddu
                mean_lot = a / ddu
                return main_df, ddu, mean_square, mean_m2, mean_lot
            else:
                return main_df, 0, np.nan, np.nan, np.nan


        if len(proj) * len(apart_type) != 0:
            st.write('<h4> Итоговая таблица по проектам:</h4>', unsafe_allow_html=True)
            st.markdown("&nbsp;")
            main_filter = st.selectbox('**Выберите показатель для фильтрации итоговой таблицы:**',
                                       ['Количество зарегистрированных ДДУ, шт.', 'Средняя площадь, м²', 'Средняя стоимость м², тыс. руб.', 'Средняя стоимость одного лота, млн руб.'],
                                       index=0)
            st.markdown("&nbsp;")

            st.write(get_main()[0].sort_values(by=main_filter, ascending=False).reset_index().style.format(precision=1).to_html(), unsafe_allow_html=True)
            st.markdown("&nbsp;")
            st.subheader('Итоговые метрики:')
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(f"**Количество зарегистрированных ДДУ, шт.**", get_main()[1])
            with col2:
                st.metric(f"**Средняя площадь, м²**", "{:.1f}".format(get_main()[2]))
            with col3:
                st.metric(f"**Средняя стоимость м², тыс. руб.**", "{:.0f}".format(get_main()[3]))
            with col4:
                st.metric(f"**Средняя стоимость одного лота, млн руб.**", "{:.1f}".format(get_main()[4]))
            st.markdown('---')
            st.markdown("&nbsp;")

            for project in proj:

                st.markdown(f'<h4> 🏢 {project}</h4>', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.write('<h5> 1️⃣ Количество зарегистрированных ДДУ, шт.</h5>', unsafe_allow_html=True)
                    st.write(get_ddu(project).replace(0, np.nan).style.format(precision=0).apply(highlight_last_row_and_column).applymap(color_negative_red, subset=pd.IndexSlice[get_ddu(project).index[-1], :]))
                    df_ddu = get_ddu(project).replace(0, np.nan)
                    with st.expander('**Развернуть график**'):
                        if len(df_ddu.columns[:-1]) >= 2:
                            fig_ddu = px.line(x=list(map(str, df_ddu.iloc[df_ddu.shape[0] - 2][:-1].index)),
                                                  y=df_ddu.iloc[df_ddu.shape[0] - 2][:-1],
                                                  labels={'x': 'Временной период', 'y': 'Количество зарегистриорванных ДДУ, шт.'},
                                                  title=f'Динамика количества зарегистрированных ДДУ, шт. <br>{list(map(str, df_ddu.iloc[df_ddu.shape[0] - 2][1:-1].index))[0]} - {list(map(str, df_ddu.iloc[df_ddu.shape[0] - 2][1:-1].index))[-1]}',
                                                  template='presentation')
                            fig_ddu.update_traces(mode='markers+lines+text', text=["{:.0f}".format(x) for x in list(map(float, df_ddu.iloc[df_ddu.shape[0] - 2][:-1]))],
                                                       textposition='top center', textfont=dict(size=13, color='black'))
                            st.plotly_chart(fig_ddu)
                    st.markdown("&nbsp;")
                with col2:
                    st.write('<h5> 2️⃣ Средняя площадь, м²</h5>', unsafe_allow_html=True)
                    st.write(get_mean_square(project).replace(0, np.nan).style.format(precision=1).apply(highlight_last_row_and_column).applymap(color_negative_red, subset=pd.IndexSlice[get_ddu(project).index[-1], :]))
                    df_mean_square = get_mean_square(project).replace(0, np.nan)
                    with st.expander('**Развернуть график**'):
                        if len(df_mean_square[:-1]) >= 2:
                            fig_mean_square = px.line(x=list(map(str, df_mean_square.iloc[df_mean_square.shape[0] - 2][:-1].index)),
                                                  y=df_mean_square.iloc[df_mean_square.shape[0] - 2][:-1],
                                                  labels={'x': 'Временной период', 'y': 'Средняя площадь, м²'},
                                                  title=f'Динамика средней площади, м² <br>{list(map(str, df_mean_square.iloc[df_mean_square.shape[0] - 2][1:-1].index))[0]} - {list(map(str, df_mean_square.iloc[df_mean_square.shape[0] - 2][1:-1].index))[-1]}',
                                                  template='presentation')
                            fig_mean_square.update_traces(mode='markers+lines+text', text=["{:.1f}".format(x) for x in list(map(float, df_mean_square.iloc[df_mean_square.shape[0] - 2][:-1]))],
                                                       textposition='top center', textfont=dict(size=13, color='black'))
                            st.plotly_chart(fig_mean_square)
                    st.markdown("&nbsp;")
                with col1:
                    st.write('<h5> 3️⃣ Средняя стоимость м², тыс. руб.</h5>', unsafe_allow_html=True)
                    st.write(get_mean_m2(project).replace(0, np.nan).style.format(precision=0).apply(highlight_last_row_and_column).applymap(color_negative_red, subset=pd.IndexSlice[get_ddu(project).index[-1], :]))
                    df_mean_m2 = get_mean_m2(project).replace(0, np.nan)
                    with st.expander('**Развернуть график**'):
                        if len(df_mean_m2.columns[:-1]) >= 2:
                            fig_mean_m2 = px.line(x=list(map(str, df_mean_m2.iloc[df_mean_m2.shape[0] - 2][:-1].index)),
                                                  y=df_mean_m2.iloc[df_mean_m2.shape[0] - 2][:-1],
                                                  labels={'x': 'Временной период', 'y': 'Средняя стоимость м², тыс. руб.'},
                                                  title=f'Динамика средней стоимости м², тыс. руб. <br>{list(map(str, df_mean_m2.iloc[df_mean_m2.shape[0] - 2][1:-1].index))[0]} - {list(map(str, df_mean_m2.iloc[df_mean_m2.shape[0] - 2][1:-1].index))[-1]}',
                                                  template='presentation')
                            fig_mean_m2.update_traces(mode='markers+lines+text', text=["{:.0f}".format(x) for x in list(map(float, df_mean_m2.iloc[df_mean_m2.shape[0] - 2][:-1]))],
                                                       textposition='top center', textfont=dict(size=13, color='black'))
                            st.plotly_chart(fig_mean_m2)
                with col2:
                    st.write('<h5> 4️⃣ Средняя стоимость одного лота, млн руб.</h5>', unsafe_allow_html=True)
                    st.write(get_mean_lot(project).replace(0, np.nan).style.format(precision=1).apply(highlight_last_row_and_column).applymap(color_negative_red, subset=pd.IndexSlice[get_ddu(project).index[-1], :]))
                    df_mean_lot = get_mean_lot(project).replace(0, np.nan)
                    if len(df_mean_lot.columns[:-1]) >= 2:
                        with st.expander('**Развернуть график**'):
                            fig_mean_lot = px.line(x=list(map(str, df_mean_lot.iloc[df_mean_lot.shape[0] - 2][:-1].index)),
                                              y=df_mean_lot.iloc[df_mean_lot.shape[0] - 2][:-1],
                                              labels={'x': 'Временной период', 'y': 'Средняя стоимость лота, млн руб.'},
                                              title=f'Динамика средней стоимости одного лота «{project}»<br>{list(map(str, df_mean_lot.iloc[df_mean_lot.shape[0] - 2][1:-1].index))[0]} - {list(map(str, df_mean_lot.iloc[df_mean_lot.shape[0] - 2][1:-1].index))[-1]}',
                                              template='presentation')
                            fig_mean_lot.update_traces(mode='markers+lines+text', text=["{:.1f}".format(x) for x in list(map(float, df_mean_lot.iloc[df_mean_lot.shape[0] - 2][:-1]))],
                                                       textposition='top center', textfont=dict(size=13, color='black'))
                            st.plotly_chart(fig_mean_lot)
                st.markdown("&nbsp;")
                st.markdown('---')


if option == 'Анализ предложения':

        st.subheader('Анализ предложения')
        #df = load_new_history_spb()
        st.markdown("&nbsp;")
        if proj_ed:
            proj = st.sidebar.multiselect('**Выберите проект:**', sorted(df1['ЖК_рус'].unique()), default=sorted(list(set(proj_dict[proj_ed]).intersection(df1['ЖК_рус'].unique()))))
            df1 = df1[df1['ЖК_рус'].isin(proj)]
            apart_type = st.sidebar.multiselect('**Выберите тип помещения:**', sorted(df1['Тип помещения'].unique()))
            df1 = df1[df1['Тип помещения'].isin(apart_type)]
        else:
            proj = st.sidebar.multiselect('**Выберите проект:**', sorted(df1['ЖК_рус'].unique()))
            df1 = df1[df1['ЖК_рус'].isin(proj)]
            apart_type = st.sidebar.multiselect('**Выберите тип помещения:**', sorted(df1['Тип помещения'].unique()))
            df1 = df1[df1['Тип помещения'].isin(apart_type)]

        if len(proj) * len(apart_type) != 0:

            result = []
            final_list = []
            original_list = []

            df_filtered = df1[df1['Тип помещения'].isin(proj)]

            dummy_exp_df = pd.DataFrame()
            dummy_exp_df['Комнат'] = sorted(df_filtered['Комнат'].unique())
            dummy_exp_df['Сред. цена м², тыс. р.'] = [''] * len(sorted(df_filtered['Комнат'].unique()))
            dummy_exp_df.set_index('Комнат', inplace=True)

            for project in proj:

                df_filtered = df1[(df1['ЖК_рус'] == project) &
                                  (df1['Тип помещения'].isin(apart_type))]

                if (df_filtered['Комнат'].isnull().sum() == df_filtered.shape[0]) or (
                        df_filtered['Площадь'].isnull().sum() == df_filtered.shape[0]) or (
                        df_filtered['Цена'].isnull().sum() == df_filtered.shape[0]):
                    pass

                else:

                    pivot_1 = df_filtered.pivot_table(
                        index='Комнат',
                        values='ЖК_рус',
                        aggfunc='count')
                    pivot_1.rename(columns={'ЖК_рус': 'Кол-во, шт.'}, inplace=True)

                    pivot_2 = df_filtered.pivot_table(
                        index='Комнат',
                        values='Площадь',
                        aggfunc='mean')
                    pivot_2.rename(columns={'Площадь': 'Сред. площадь, м²'}, inplace=True)
                    pivot_2 = pivot_2.round(1)

                    pivot_3 = df_filtered.pivot_table(
                        index='Комнат',
                        values='Цена',
                        aggfunc='min')
                    pivot_3 = pivot_3 / 10 ** 6
                    pivot_3.rename(columns={'Цена': 'Мин. цена, млн р.'}, inplace=True)
                    pivot_3 = pivot_3.round(1)

                    pivot_4 = df_filtered.pivot_table(
                        index='Комнат',
                        values='Цена',
                        aggfunc='max')
                    pivot_4 = pivot_4 / 10 ** 6
                    pivot_4.rename(columns={'Цена': 'Макс. цена, млн р.'}, inplace=True)
                    pivot_4 = pivot_4.round(1)

                    pivot_5 = df_filtered.pivot_table(
                        index='Комнат',
                        values='Цена',
                        aggfunc='mean')
                    pivot_5 = pivot_5 / 10 ** 6
                    pivot_5.rename(columns={'Цена': 'Сред. цена, млн р.'}, inplace=True)
                    pivot_5 = pivot_5.round(1)

                    pivot_6 = df_filtered.pivot_table(
                        index='Комнат',
                        values='Цена кв м',
                        aggfunc='min')
                    pivot_6 = pivot_6 / 1000
                    pivot_6.rename(columns={'Цена кв м': 'Мин. цена м², тыс. р.'}, inplace=True)
                    pivot_6 = pivot_6.applymap(round)

                    pivot_7 = df_filtered.pivot_table(
                        index='Комнат',
                        values='Цена кв м',
                        aggfunc='max')
                    pivot_7 = pivot_7 / 1000
                    pivot_7.rename(columns={'Цена кв м': 'Макс. цена м², тыс. р.'}, inplace=True)
                    pivot_7 = pivot_7.applymap(round)

                    pivot_8 = pd.DataFrame()
                    pivot_8['Тип Комнатности'] = df_filtered.pivot_table(index='Комнат', values='Цена', aggfunc='sum').index
                    pivot_8['Сред. цена м², тыс. р.'] = df_filtered.pivot_table(index='Комнат', values='Цена', aggfunc='sum').values / df_filtered.pivot_table(index='Комнат', values='Площадь', aggfunc='sum').values
                    pivot_8['Сред. цена м², тыс. р.'] = pivot_8['Сред. цена м², тыс. р.'] / 1000
                    pivot_8.set_index('Тип Комнатности', inplace=True)
                    pivot_8 = pivot_8.applymap(round)

                    df_test = pd.concat([pivot_1, pivot_2, pivot_3, pivot_4, pivot_5, pivot_6, pivot_7, pivot_8], axis=1)
                    original_list.extend([project] + [''] * (df_test.shape[0] - 1))
                    result.append(df_test)


            final_exp = pd.concat(result).reset_index()
            final_exp = final_exp.set_index(pd.Index(original_list))
            final_exp = final_exp.rename(columns={"index": "Тип Комнатности"})
            st.write(final_exp.to_html(), unsafe_allow_html=True)

            st.markdown("&nbsp;")

            download = st.button('Загрузить в формате .xlsx',
                                 help=f'Таблица составлена за период с {str(df1["Дата актуализации"].min())[:-9]} по {str(df1["Дата актуализации"].max())[:-9]}')
            if download:
                download_dataframe_xlsx(final_exp)


if option == 'Анализ условий покупки':

    st.subheader('Анализ условий покупки')
    st.markdown("&nbsp;")
    help = load_help()
    df_mortgage = load_mortgage()
    df_split = load_split()
    df_promo = load_promo()




    if proj_ed:
        proj = st.sidebar.multiselect('**Выберите проект:**', sorted(proj_dict[proj_ed]), default=sorted(proj_dict[proj_ed]))
        df1 = df1[df1['ЖК_рус'].isin(proj)]
        apart_type = st.sidebar.multiselect('**Выберите тип помещения:**', sorted(df1['Тип помещения'].unique()))
        df1 = df1[df1['Тип помещения'].isin(apart_type)]
    else:
        proj = st.sidebar.multiselect('**Выберите проект:**', sorted(df1['ЖК_рус'].unique()))
        df1 = df1[df1['ЖК_рус'].isin(proj)]
        apart_type = st.sidebar.multiselect('**Выберите тип помещения:**', sorted(df1['Тип помещения'].unique()))
        df1 = df1[df1['Тип помещения'].isin(apart_type)]

    if len(proj) * len(apart_type) != 0:


        df1 = df1[(df1['ЖК_рус'].isin(proj)) & (df1['Тип помещения'].isin(apart_type))]

        for project in proj:
            df_proj = df1[df1['ЖК_рус'] == project]

            pivot_1 = df_proj.pivot_table(index='Комнат', values='Цена кв м', aggfunc='min') / 1000
            pivot_1.rename(columns={'Цена кв м': 'Мин. цена м², тыс. р.'}, inplace=True)
            pivot_1 = pivot_1.applymap(round)

            pivot_2 = df_proj.pivot_table(index='Комнат', values='Площадь', aggfunc='min')
            pivot_2.rename(columns={'Площадь': 'Мин. площадь, м²'}, inplace=True)
            pivot_2 = pivot_2.round(1)

            pivot_3 = df_proj.pivot_table(index='Комнат', values='Цена', aggfunc='min')
            pivot_3 = pivot_3 / 10 ** 6
            pivot_3.rename(columns={'Цена': 'Мин. цена, млн р.'}, inplace=True)
            pivot_3 = pivot_3.round(1)

            df_test = pd.concat([pivot_1, pivot_2, pivot_3], axis=1)



            try:
                name = help[help['source'] == project.strip()]['demand'].iloc[0]
                st.write(f'<h4> {project} </h4>', unsafe_allow_html=True)
                st.write(df_test)
                with st.expander(f'**Данные по ипотеке:**'):
                    st.table(df_mortgage[df_mortgage['ЖК'].str.strip() == name.strip()])
                with st.expander(f'**Данные по рассрочке:**'):
                    st.table(df_split[df_split['ЖК'].str.strip() == name.strip()])
                with st.expander(f'**Данные по акциям:**'):
                    st.table(df_promo[df_promo['ЖК'].str.strip() == name.strip()])
                st.markdown("---")
                st.markdown("&nbsp;")
            except IndexError:
                st.write(f'<h4> {project}</h4>', unsafe_allow_html=True)
                st.write(f'<h5>🚫 Нет информации по проекту </h5>', unsafe_allow_html=True)
                st.markdown("---")
                st.markdown("&nbsp;")


if option == 'Пульс продаж':
    st.subheader('Пульс продаж')
    st.markdown("&nbsp;")
    if city == 'Санкт-Петербург':
        df = load_realty_sold_spb()
    else:
        df = load_realty_sold_moscow()

    pulse_prev = df[(df['Дата регистрации'].dt.year == prev_year) & (df['Дата регистрации'].dt.month == prev_month)]
    pulse_prev = pd.DataFrame(pulse_prev.groupby(by=['ЖК_рус', 'Застройщик ЖК', 'класс', 'АТД']).count()['Тип Комнатности']).sort_values(
        by='Тип Комнатности', ascending=False).reset_index().set_index('ЖК_рус')

    pulse_prev_m2 = df[
        (df['Дата регистрации'].dt.year == prev_year) & (df['Дата регистрации'].dt.month == prev_month)]
    pulse_prev_m2 = pd.DataFrame(pulse_prev_m2.groupby(by=['ЖК_рус', 'Застройщик ЖК', 'класс', 'АТД'])[['Оценка цены', 'Площадь']].sum()).reset_index().set_index('ЖК_рус')
    pulse_prev_m2['Стоимость м2'] = pulse_prev_m2['Оценка цены'] / pulse_prev_m2['Площадь']
    pulse_prev_m2 = pulse_prev_m2.drop(['Оценка цены', 'Площадь'], axis=1)

    pulse_current = df[
        (df['Дата регистрации'].dt.year == today_year) & (df['Дата регистрации'].dt.month == today_month)]
    pulse_current = pd.DataFrame(
        pulse_current.groupby(by=['ЖК_рус', 'Застройщик ЖК', 'класс', 'АТД']).count()['Тип Комнатности']).sort_values(
        by='Тип Комнатности', ascending=False).reset_index().set_index('ЖК_рус')

    pulse_current_m2 = df[
        (df['Дата регистрации'].dt.year == today_year) & (df['Дата регистрации'].dt.month == today_month)]
    pulse_current_m2 = pd.DataFrame(pulse_current_m2.groupby(by=['ЖК_рус', 'Застройщик ЖК', 'класс', 'АТД'])[['Оценка цены', 'Площадь']].sum()).reset_index().set_index('ЖК_рус')
    pulse_current_m2['Стоимость м2'] = pulse_current_m2['Оценка цены'] / pulse_current_m2['Площадь']
    pulse_current_m2 = pulse_current_m2.drop(['Оценка цены', 'Площадь'], axis=1)

    pulse = pd.DataFrame()
    pulse['Проект'] = df[df['Дата регистрации'].dt.year == today_year]['ЖК_рус'].unique()
    pulse['Застройщик'] = [0] * len(pulse.index)
    pulse['Класс'] = [0] * len(pulse.index)
    pulse['Район'] = [0] * len(pulse.index)
    pulse.set_index('Проект', inplace=True)
    try:
        pulse.loc[pulse_prev.index] = pulse_prev[['Застройщик ЖК', 'класс', 'АТД']].values
        pulse.loc[pulse_current.index] = pulse_current[['Застройщик ЖК', 'класс', 'АТД']].values
        pulse['Кол-во 1'] = [0] * len(pulse.index)
        pulse['Кол-во 2'] = [0] * len(pulse.index)
        pulse['м2 1'] = [0] * len(pulse.index)
        pulse['м2 2'] = [0] * len(pulse.index)
        pulse['м2 1'].loc[pulse_prev_m2['Стоимость м2'].index] = pd.Series(pulse_prev_m2['Стоимость м2']) / 10 ** 3
        pulse['м2 2'].loc[pulse_current_m2['Стоимость м2'].index] = pd.Series(pulse_current_m2['Стоимость м2']) / 10 ** 3
        pulse[['м2 1', 'м2 2']] = pulse[['м2 1', 'м2 2']].applymap(int)
        pulse['Кол-во 1'].loc[pulse_prev['Тип Комнатности'].index] = pd.Series(pulse_prev['Тип Комнатности'])
        pulse['Кол-во 2'].loc[pulse_current['Тип Комнатности'].index] = pd.Series(pulse_current['Тип Комнатности'])
        pulse.columns = ['Девелопер/Застройщик', 'Класс', 'Район',
                         f'Кол-во на {prev_month}/{prev_year}', f'Кол-во на {today_month}/{today_year}',
                         f'Стоимость м² на {prev_month}/{prev_year}, тыс. руб', f'Стоимость м² на {today_month}/{today_year}, тыс. руб']
        pulse = pulse[pulse['Девелопер/Застройщик'] != 0]
        pulse = pulse.sort_values(f'Кол-во на {today_month}/{today_year}', ascending=False)
        pulse = pulse.reset_index()

        pulse['Изменение (кол-во)'] = pd.Series((pulse[pulse.columns[-3]] / pulse[pulse.columns[-4]] - 1) * 100).round(2)
        pulse['Изменение (кол-во)'].fillna(0, inplace=True)
        pulse['Изменение (кол-во)'] = pulse['Изменение (кол-во)'].apply(lambda x: f"{x}%")

        pulse['Изменение (стоимость м²)'] = pd.Series(
            (pulse[pulse.columns[-2]] / pulse[pulse.columns[-3]] - 1) * 100).round(2)
        pulse['Изменение (стоимость м²)'].fillna(0, inplace=True)
        pulse['Изменение (стоимость м²)'] = pulse['Изменение (стоимость м²)'].apply(lambda x: f"{x}%")

        pulse = pulse[['Проект', 'Девелопер/Застройщик', 'Класс', 'Район', f'Кол-во на {prev_month}/{prev_year}',
                       f'Кол-во на {today_month}/{today_year}', 'Изменение (кол-во)', f'Стоимость м² на {prev_month}/{prev_year}, тыс. руб',
                       f'Стоимость м² на {today_month}/{today_year}, тыс. руб', 'Изменение (стоимость м²)']]

        pulse = pulse.set_index(np.arange(1, pulse.shape[0] + 1))
        #st.table(pulse.set_index(np.arange(1, pulse.shape[0] + 1)))
        pulse = pulse.applymap(str)
        pulse[['Изменение (стоимость м²)', 'Изменение (кол-во)']] = pulse[['Изменение (стоимость м²)', 'Изменение (кол-во)']].replace('inf%', '?%')

        col1, col2 = st.columns(2)
        with col1:
            df_vis = pd.DataFrame(pulse.groupby(by='Район')[f'Кол-во на {today_month}/{today_year}'].count())
            df_vis = df_vis.sort_values(by=f'Кол-во на {today_month}/{today_year}')
            fig = px.bar(df_vis, x=f'Кол-во на {today_month}/{today_year}',
                         y=df_vis.index,
                         title=f'Распределение продаж по районам города<br><sup>{today_month}/{today_year}</sup>',
                         template='seaborn',
                         labels={f'Кол-во на {today_month}/{today_year}': 'Количество юнитов', 'Район': 'Район'})
            st.plotly_chart(fig)
        with col2:
            df_vis = pd.DataFrame(pulse.groupby(by='Класс')[f'Кол-во на {today_month}/{today_year}'].count())
            df_vis = df_vis.sort_values(by=f'Кол-во на {today_month}/{today_year}')
            fig = px.bar(df_vis, x=f'Кол-во на {today_month}/{today_year}',
                         y=df_vis.index,
                         title=f'Распределение продаж по классам<br><sup>{today_month}/{today_year}</sup>',
                         template='seaborn',
                         labels={f'Кол-во на {today_month}/{today_year}': 'Количество юнитов', 'Класс': 'Класс'})
            st.plotly_chart(fig)
        st.table(pulse.style.apply(color_price_m2).apply(color_number).apply(color_number_result).apply(color_price_m2_result).apply(color_element, axis=1))
    except KeyError:
        st.subheader(":gear: Нет возможности собрать данные")



























