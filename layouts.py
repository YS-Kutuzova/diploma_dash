from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_table

def create_layout():
    
    layout = dbc.Container([
        dcc.Location(id='url', refresh=False),
        
        # Заголовок
        html.Div([
            html.H1("🏙️ Информационно-аналитическая система", 
                   className="my-3 text-primary"),
            html.H3("для оценки обеспеченности районов Санкт-Петербурга объектами спортивной инфраструктуры", 
                  className="my-3 text-primary")
        ], className="text-center"),
        
        # Карточка с видами спорта с голубым фоном
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("🎯 Виды спорта", className="mb-0 text-center text-white"),
                    ], className="bg-info"),
                    dbc.CardBody([
                        html.Div(id='sport-types-list', 
                                className="sport-types-container text-center", 
                                style={
                                    'maxHeight': '120px', 
                                    'overflowY': 'auto',
                                    'padding': '5px',
                                    'backgroundColor': '#e3f2fd'
                                })
                    ], className="p-2")
                ], className="shadow-sm border mb-4", style={'width': '50%', 'margin': '0 auto'}),
                width=12
            ),
        ]),
        
        # Основные вкладки
        dbc.Card([
            dbc.CardHeader(
                dcc.Tabs(
                    id='main-tabs',
                    value='tab-map',
                    children=[
                        dcc.Tab(
                            label='🗺️ Карта объектов и инфраструктуры',
                            value='tab-map',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                        dcc.Tab(
                            label='📊 Графики и аналитика',
                            value='tab-charts',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                    ],
                    colors={
                        "border": "white",
                        "primary": "#007bff",
                        "background": "#f8f9fa"
                    }
                )
            ),
            dbc.CardBody([
                # Контейнер для контента вкладок
                html.Div(id='tab-content', className="mt-3"),
                
                # Фильтры для карты
                html.Div(id='map-filters-container', style={'display': 'none'}, children=[
                    dbc.Row([
                        dbc.Col([
                            html.Label("Вид спорта:", className="font-weight-bold"),
                            dcc.Dropdown(
                                id='map-sport-filter',
                                placeholder="Выберите вид спорта...",
                                clearable=True,
                                className="mb-3"
                            ),
                        ], width=4),
                        dbc.Col([
                            html.Label("Тип инфраструктуры:", className="font-weight-bold"),
                            dcc.Dropdown(
                                id='map-infra-filter',
                                placeholder="Выберите тип инфраструктуры...",
                                clearable=True,
                                className="mb-3"
                            ),
                        ], width=4),
                        dbc.Col([
                            html.Label("Район:", className="font-weight-bold"),
                            dcc.Dropdown(
                                id='map-district-filter',
                                placeholder="Выберите район...",
                                clearable=True,
                                className="mb-3"
                            ),
                        ], width=4),
                    ], className="mb-4"),
                    
                    # Таблица объектов под картой
                    html.Div(id='objects-table-container', style={'display': 'none'}, children=[
                        html.H4("Список спортивных объектов", className="mb-3 mt-4"),  # Изменено название
                        dash_table.DataTable(
                            id='objects-table',
                            columns=[
                                {'name': 'Название', 'id': 'Название'},
                                {'name': 'Тип спорта', 'id': 'Тип спорта'},
                                {'name': 'Адрес', 'id': 'Адрес'},
                                {'name': 'Район', 'id': 'Район'},
                                {'name': 'Типы инфраструктуры', 'id': 'Типы инфраструктуры'}
                            ],
                            page_size=10,
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'textAlign': 'left',
                                'padding': '10px',
                                'font-family': 'Arial, sans-serif',
                                'font-size': '14px'
                            },
                            style_header={
                                'backgroundColor': '#f8f9fa',
                                'fontWeight': 'bold',
                                'border': '1px solid #dee2e6'
                            },
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ]
                        )
                    ])
                ]),
            ])
        ]),
        
    ], fluid=True, style={'padding': '20px', 'maxWidth': '1400px'})
    
    return layout