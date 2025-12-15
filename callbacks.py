from dash import Input, Output, State, callback_context, html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from data_loader import sport_data

def setup_callbacks(app): 
    
    # Карточка
    @app.callback(
        Output('sport-types-list', 'children'),
        Input('url', 'pathname')
    )
    def update_sport_types_card(pathname):
        if not sport_data.load():
            return html.P("Данные не загружены", className="text-muted text-center")
        
        types_data = sport_data.get_sport_types_with_counts()
        
        if not types_data:
            return html.P("Нет данных о видах спорта", className="text-muted text-center")
        
        # Создаем список видов спорта
        items = []

        for item in types_data[:3]: 
            sport_type = item['type']
            count = item['count']
    
            items.append(
                html.Div(
                    f"{sport_type} ({count} объектов)",
                    style={
                        'fontSize': '17px',
                        'fontWeight': 'bold',
                        'marginBottom': '10px',
                        'color': '#2C3E50'
                    }
                )
            )

        return html.Div(items, className="text-center")

    # Фильтры
    @app.callback(
        [Output('map-sport-filter', 'options'),
         Output('map-infra-filter', 'options'),
         Output('map-district-filter', 'options')],
        Input('url', 'pathname')
    )
    def update_filter_options(pathname):
        if not sport_data.load():
            return [[] for _ in range(3)]
        
        # Фильтр видов спорта
        types_data = sport_data.get_sport_types_with_counts()
        sport_options = [{'label': 'Все виды спорта', 'value': 'all'}]
        if types_data:
            for item in types_data:
                sport_type = item['type']
                count = item['count']
                sport_options.append({
                    'label': f"{sport_type} ({count})",
                    'value': sport_type
                })
        
        # Фильтр типов инфраструктуры
        infra_types = sport_data.get_infrastructure_types()
        infra_options = [{'label': 'Все типы инфраструктуры', 'value': 'all'}]
        infra_options += [{'label': t, 'value': t} for t in infra_types[:15]]
        
        # Фильтр районов
        districts = sport_data.get_districts()
        district_options = [{'label': 'Все районы', 'value': 'all'}]
        district_options += [{'label': d, 'value': d} for d in districts]
        
        return [sport_options, infra_options, district_options]
    
    # Список спортивных объектов
    @app.callback(
        Output('objects-table', 'data'),
        [Input('map-sport-filter', 'value'),
         Input('map-infra-filter', 'value'),
         Input('map-district-filter', 'value')]
    )
    def update_table_data(sport_filter, infra_filter, district_filter):
        sport_data.load()
        df = sport_data.get_objects()
        
        filtered_df = df.copy()
        
        if sport_filter and sport_filter != 'all':
            filtered_df = filtered_df[filtered_df['sport_object_type'] == sport_filter]
        
        if district_filter and district_filter != 'all':
            filtered_df = filtered_df[filtered_df['district'] == district_filter]
        
        # Фильтрация по инфраструктуре
        if infra_filter and infra_filter != 'all':
            full_df = sport_data.get_full_data()
            infra_filtered = full_df[full_df['infrastructure_type'] == infra_filter]
            valid_ids = infra_filtered['sport_object_id'].unique()
            filtered_df = filtered_df[filtered_df['sport_object_id'].isin(valid_ids)]
        
        # Создаем данные для таблицы
        table_data = []
        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                obj_id = row['sport_object_id']
                infra_list = sport_data.get_infrastructure_by_object(obj_id)
                
                # Получаем уникальные типы инфраструктуры
                infra_types = set()
                for item in infra_list:
                    if 'type' in item:
                        infra_types.add(item['type'])
                
                infra_types_str = ', '.join(sorted(infra_types)) if infra_types else 'Нет инфраструктуры'
                
                table_data.append({
                    'Название': str(row.get('sport_object_name', 'Без названия'))[:40],
                    'Тип спорта': str(row.get('sport_object_type', 'Не указан')),
                    'Адрес': str(row.get('sport_object_address', 'Без адреса'))[:50],
                    'Район': str(row.get('district', 'Не указан')),
                    'Типы инфраструктуры': infra_types_str[:60] + ('...' if len(infra_types_str) > 60 else '')
                })
        
        return table_data
    
    # Вкладки
    @app.callback(
        [Output('tab-content', 'children'),
         Output('map-filters-container', 'style'),
         Output('objects-table-container', 'style')],
        [Input('main-tabs', 'value'),
         Input('map-sport-filter', 'value'),
         Input('map-infra-filter', 'value'),
         Input('map-district-filter', 'value')]
    )
    def handle_tabs(selected_tab, sport_filter, infra_filter, district_filter):
        
        # Фильтры карты
        filter_style = {'display': 'block'} if selected_tab == 'tab-map' else {'display': 'none'}
        table_style = {'display': 'block'} if selected_tab == 'tab-map' else {'display': 'none'}
        
        # Загружаем данные
        sport_data.load()
        df = sport_data.get_objects()
        full_df = sport_data.get_full_data()
        
        # Обработка контента для каждой вкладки
        if selected_tab == 'tab-map':
            # Фильтрация данных для карты
            filtered_df = df.copy()
            filtered_infra_df = full_df.copy()
            
            if sport_filter and sport_filter != 'all':
                filtered_df = filtered_df[filtered_df['sport_object_type'] == sport_filter]
                filtered_infra_df = filtered_infra_df[filtered_infra_df['sport_object_type'] == sport_filter]
            
            if infra_filter and infra_filter != 'all':
                filtered_infra_df = filtered_infra_df[filtered_infra_df['infrastructure_type'] == infra_filter]
            
            if district_filter and district_filter != 'all':
                filtered_df = filtered_df[filtered_df['district'] == district_filter]
                filtered_infra_df = filtered_infra_df[filtered_infra_df['district'] == district_filter]
            
            # Карта с маркерами
            combined_map = create_combined_map_with_colors(filtered_df, filtered_infra_df)
            
            content = html.Div([
                html.H4("Карта спортивных объектов и инфраструктуры", className="mb-3"),
                html.P([
                    html.Span(f"Спортивных объектов: {len(filtered_df)}", className="mr-3"),
                    html.Span(f" | Объектов инфраструктуры: {len(filtered_infra_df)}", className="mr-3"),
                ], className="text-muted mb-2"),
                dcc.Graph(
                    figure=combined_map,
                    style={'height': '500px', 'border': '1px solid #ddd', 'borderRadius': '5px'}
                ),
            ])
            
        elif selected_tab == 'tab-charts':
            # Создаем аналитические графики
            fig1 = create_chart_sport_type_distribution(df)
            fig2 = create_chart_schedule_by_sport(df)
            fig3 = create_chart_density_vs_objects(full_df)
            fig4 = create_chart_salary_vs_objects(full_df)
            fig5 = create_chart_infra_vs_objects(full_df)
            fig6 = create_chart_gender_vs_objects(full_df)
            
            content = html.Div([
                html.H4("Аналитика данных", className="mb-4"),
                
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig1, style={'height': '400px'}), width=12),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig2, style={'height': '400px'}), width=12),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig3, style={'height': '400px'}), width=12),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig4, style={'height': '400px'}), width=12),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig5, style={'height': '400px'}), width=12),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col(dcc.Graph(figure=fig6, style={'height': '400px'}), width=12),
                ]),
            ])
        
        else:
            content = html.Div("Выберите вкладку для отображения данных")
        
        return [content, filter_style, table_style]

# Графики

def create_combined_map_with_colors(sport_df, infra_df):
    if sport_df.empty and infra_df.empty:
        return create_empty_chart("Нет данных для карты")
    
    fig = go.Figure()
    
    # Маркеры
    sport_colors = [
        '#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF',
        '#FF4500', '#32CD32', '#1E90FF', '#FFD700', '#DA70D6', '#00CED1',
        '#FF6347', '#7CFC00', '#4169E1', '#FFA500', '#BA55D3', '#5F9EA0'
    ]
    
    # Разные цвета для разных типов инфраструктуры - иначе сливается
    infra_colors = {
        'кафе': '#FF6B6B',           # Красный
        'торговый_центр': '#4ECDC4',  # Бирюзовый
        'супермаркет': '#FFD166',     # Желтый
        'фитнес': '#06D6A0',         # Зеленый
        'остановка': '#118AB2',       # Синий
        'офис': '#EF476F',           # Розовый
        'метро': '#073B4C',          # Темно-синий
        'магазин': '#4361EE',        # Голубой
        'ресторан': '#4CC9F0',       # Светло-голубой
    }
    
    # Добавляем спортивные объекты
    if not sport_df.empty and 'sport_object_lat' in sport_df.columns:
        sport_with_coords = sport_df.dropna(subset=['sport_object_lat', 'sport_object_lon'])
        
        if not sport_with_coords.empty:
            # Группируем по типам спорта для разных цветов
            sport_types = sport_with_coords['sport_object_type'].unique()
            
            for i, sport_type in enumerate(sport_types[:8]):  # Ограничиваем 8 типами
                type_data = sport_with_coords[sport_with_coords['sport_object_type'] == sport_type]
                color = sport_colors[i % len(sport_colors)]
                
                fig.add_trace(go.Scattermapbox(
                    lat=type_data['sport_object_lat'],
                    lon=type_data['sport_object_lon'],
                    mode='markers',
                    marker=dict(size=12, color=color, opacity=0.9),
                    name=f'{sport_type}',
                    hovertext=type_data['sport_object_name'],
                    hoverinfo='text'
                ))
    
   # Добавляем инфраструктуру (разные цвета по типам инфраструктуры)
    if not infra_df.empty and 'infrastructure_lat' in infra_df.columns:
        infra_with_coords = infra_df.dropna(subset=['infrastructure_lat', 'infrastructure_lon'])
    
        if not infra_with_coords.empty:
        # Группируем по типам инфраструктуры
            infra_types = infra_with_coords['infrastructure_type'].unique()
        
            for infra_type in infra_types:
                type_data = infra_with_coords[infra_with_coords['infrastructure_type'] == infra_type]
            
            # Ограничиваем количество маркеров каждого типа для производительности
                type_sample = type_data.head(50)
            
                if not type_sample.empty:
                # Получаем цвет для данного типа инфраструктуры
                    color = infra_colors.get(infra_type, '#808080')  # Серый по умолчанию
                
                fig.add_trace(go.Scattermapbox(
                    lat=type_sample['infrastructure_lat'],
                    lon=type_sample['infrastructure_lon'],
                    mode='markers',
                    marker=dict(size=8, color=color, opacity=0.7),
                    name=infra_type,  # Убрали эмодзи из названия
                    hovertext=type_sample['infrastructure_name'] + ' - ' + type_sample['infrastructure_type'],
                    hoverinfo='text'
                ))

    # Настройки карты
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=59.94, lon=30.31),
            zoom=10
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            font=dict(size=8),
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='black',
            borderwidth=1
        )
    )
    
    return fig
# Количество объектов по видам спорта
def create_chart_sport_type_distribution(df):
    if df.empty:
        return create_empty_chart("Нет данных")
    
    type_counts = df['sport_object_type'].value_counts()
    
    fig = go.Figure(data=[
        go.Bar(
            x=type_counts.index,
            y=type_counts.values,
            marker_color='#1E90FF', 
            text=type_counts.values,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Количество объектов по видам спорта",
        xaxis_title="Вид спорта",
        yaxis_title="Количество объектов",
        height=400,
        showlegend=False,
        xaxis_tickangle=-45,
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    return fig

# График работы объектов
def create_chart_schedule_by_sport(df):
    if df.empty or 'schedule' not in df.columns:
        return create_empty_chart("Нет данных о графике работы")
    
    schedule_data = df.groupby(['sport_object_type', 'schedule']).size().unstack(fill_value=0)
    
    fig = go.Figure()
    
    if 1 in schedule_data.columns:
        fig.add_trace(go.Bar(
            x=schedule_data.index,
            y=schedule_data[1],
            name='Круглосуточно',
            marker_color='#32CD32'
        ))
    
    if 0 in schedule_data.columns:
        fig.add_trace(go.Bar(
            x=schedule_data.index,
            y=schedule_data[0],
            name='Не круглосуточно',
            marker_color='#FF4500'
        ))
    
    fig.update_layout(
        title="График работы объектов",
        xaxis_title="Вид спорта",
        yaxis_title="Количество объектов",
        height=400,
        barmode='group',
        xaxis_tickangle=-45,
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    return fig

# Плотность населения и количество спортивных объектов по районам
def create_chart_density_vs_objects(df):
    if df.empty or 'district' not in df.columns or 'Плотность_населения' not in df.columns:
        return create_empty_chart("Нет данных для анализа")
    
    # Получаем данные по районам
    district_stats = sport_data.get_district_statistics()
    
    if district_stats.empty:
        return create_empty_chart("Нет данных о районах")
    
    # Считаем количество спортивных объектов по районам
    sport_objects = sport_data.get_objects()
    if sport_objects.empty or 'district' not in sport_objects.columns:
        return create_empty_chart("Нет данных о спортивных объектах")
    
    object_counts = sport_objects.groupby('district').size().reset_index(name='sport_objects_count')
    
    # Объединяем с данными о плотности
    merged_data = pd.merge(district_stats[['district', 'Плотность_населения']], 
                          object_counts, on='district')
    
    if merged_data.empty:
        return create_empty_chart("Нет данных для анализа")
    
    # Сортируем по плотности
    merged_data = merged_data.sort_values('Плотность_населения', ascending=False)
    
    fig = go.Figure()
    
    # Столбцы для спортивных объектов
    fig.add_trace(go.Bar(
        x=merged_data['district'],
        y=merged_data['sport_objects_count'],
        name='Спортивные объекты',
        marker_color='#1E90FF', 
        text=merged_data['sport_objects_count'],
        textposition='auto'
    ))
    
    # Линия для плотности населения
    fig.add_trace(go.Scatter(
        x=merged_data['district'],
        y=merged_data['Плотность_населения'],
        name='Плотность населения',
        yaxis='y2',
        marker=dict(color='#FF4500', size=10),
        line=dict(color='#FF4500', width=3),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title="Плотность населения и количество спортивных объектов по районам",
        xaxis_title="Район",
        yaxis_title="Количество спортивных объектов",
        yaxis2=dict(
            title="Плотность населения (чел/км²)",
            overlaying='y',
            side='right'
        ),
        height=400,
        xaxis_tickangle=-45,
        margin=dict(l=50, r=80, t=50, b=100),
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

# Зарплата и количество спортивных объектов по районам
def create_chart_salary_vs_objects(df):
    if df.empty or 'district' not in df.columns or 'Зарплата' not in df.columns:
        return create_empty_chart("Нет данных для анализа")
    
    # Получаем данные по районам
    district_stats = sport_data.get_district_statistics()
    
    if district_stats.empty:
        return create_empty_chart("Нет данных о районах")
    
    # Считаем количество спортивных объектов по районам
    sport_objects = sport_data.get_objects()
    if sport_objects.empty or 'district' not in sport_objects.columns:
        return create_empty_chart("Нет данных о спортивных объектах")
    
    object_counts = sport_objects.groupby('district').size().reset_index(name='sport_objects_count')
    
    # Объединяем с данными о зарплате
    merged_data = pd.merge(district_stats[['district', 'Зарплата']], 
                          object_counts, on='district')
    
    if merged_data.empty:
        return create_empty_chart("Нет данных для анализа")
    
    # Сортируем по зарплате
    merged_data = merged_data.sort_values('Зарплата', ascending=False)
    
    fig = go.Figure()
    
    # Столбцы для спортивных объектов
    fig.add_trace(go.Bar(
        x=merged_data['district'],
        y=merged_data['sport_objects_count'],
        name='Спортивные объекты',
        marker_color='#32CD32', 
        text=merged_data['sport_objects_count'],
        textposition='auto'
    ))
    
    # Линия для зарплаты
    fig.add_trace(go.Scatter(
        x=merged_data['district'],
        y=merged_data['Зарплата'],
        name='Средняя зарплата',
        yaxis='y2',
        marker=dict(color='#FFD700', size=10),  # Золотой
        line=dict(color='#FFD700', width=3),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title="Зарплата и количество спортивных объектов по районам",
        xaxis_title="Район",
        yaxis_title="Количество спортивных объектов",
        yaxis2=dict(
            title="Средняя зарплата (руб)",
            overlaying='y',
            side='right'
        ),
        height=400,
        xaxis_tickangle=-45,
        margin=dict(l=50, r=80, t=50, b=100),
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

# Количество объектов инфраструктуры и спортивных объектов по районам
def create_chart_infra_vs_objects(df):
    if df.empty or 'district' not in df.columns:
        return create_empty_chart("Нет данных для анализа")
    
    # Считаем количество инфраструктуры по районам
    infra_counts = df.groupby('district').size().reset_index(name='infra_count')
    
    # Считаем количество спортивных объектов по районам
    sport_objects = sport_data.get_objects()
    if sport_objects.empty or 'district' not in sport_objects.columns:
        return create_empty_chart("Нет данных о спортивных объектах")
    
    object_counts = sport_objects.groupby('district').size().reset_index(name='sport_objects_count')
    
    # Объединяем данные
    merged_data = pd.merge(infra_counts, object_counts, on='district')
    
    if merged_data.empty:
        return create_empty_chart("Нет данных для анализа")
    
    # Сортируем по количеству спортивных объектов
    merged_data = merged_data.sort_values('sport_objects_count', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=merged_data['district'],
        y=merged_data['sport_objects_count'],
        name='Спортивные объекты',
        marker_color='#1E90FF'
    ))
    
    fig.add_trace(go.Bar(
        x=merged_data['district'],
        y=merged_data['infra_count'],
        name='Объекты инфраструктуры',
        marker_color='#FF8C00'
    ))
    
    fig.update_layout(
        title="Количество объектов инфраструктуры и спортивных объектов по районам",
        xaxis_title="Район",
        yaxis_title="Количество объектов",
        height=400,
        barmode='group',
        xaxis_tickangle=-45,
        margin=dict(l=50, r=50, t=50, b=100)
    )
    
    return fig

# Соотношение мужчин/женщин и количество спортивных объектов по районам
def create_chart_gender_vs_objects(df):
    if df.empty or 'district' not in df.columns or 'Соотношение_М_Ж' not in df.columns:
        return create_empty_chart("Нет данных для анализа")
    
    # Получаем данные по районам
    district_stats = sport_data.get_district_statistics()
    
    if district_stats.empty:
        return create_empty_chart("Нет данных о районах")
    
    # Считаем количество спортивных объектов по районам
    sport_objects = sport_data.get_objects()
    if sport_objects.empty or 'district' not in sport_objects.columns:
        return create_empty_chart("Нет данных о спортивных объектах")
    
    object_counts = sport_objects.groupby('district').size().reset_index(name='sport_objects_count')
    
    # Объединяем с данными о соотношении полов
    merged_data = pd.merge(district_stats[['district', 'Соотношение_М_Ж']], 
                          object_counts, on='district')
    
    if merged_data.empty:
        return create_empty_chart("Нет данных для анализа")
    
    # Рассчитываем процент мужчин
    merged_data['Процент_мужчин'] = merged_data['Соотношение_М_Ж'] * 100
    
    # Сортируем по проценту мужчин
    merged_data = merged_data.sort_values('Процент_мужчин', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=merged_data['district'],
        y=merged_data['sport_objects_count'],
        name='Спортивные объекты',
        marker_color='#9370DB', 
        text=merged_data['sport_objects_count'],
        textposition='auto'
    ))
    
    # Линия для процента мужчин
    fig.add_trace(go.Scatter(
        x=merged_data['district'],
        y=merged_data['Процент_мужчин'],
        name='Процент мужчин',
        yaxis='y2',
        marker=dict(color='#FF69B4', size=10), 
        line=dict(color='#FF69B4', width=3),
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title="Соотношение мужчин/женщин и количество спортивных объектов по районам",
        xaxis_title="Район",
        yaxis_title="Количество спортивных объектов",
        yaxis2=dict(
            title="Процент мужчин (%)",
            overlaying='y',
            side='right'
        ),
        height=400,
        xaxis_tickangle=-45,
        margin=dict(l=50, r=80, t=50, b=100),
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

def create_empty_chart(message):
    fig = go.Figure()
    fig.update_layout(
        height=400,
        annotations=[{
            'text': message,
            'x': 0.5,
            'y': 0.5,
            'showarrow': False,
            'font': {'size': 16, 'color': 'gray'}
        }],
        margin=dict(l=50, r=50, t=50, b=50)
    )
    return fig