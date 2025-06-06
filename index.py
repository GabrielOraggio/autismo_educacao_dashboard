import dash
from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc

# 1. Carregar e preparar os dados
try:
    df = pd.read_csv('data/autismo_educacao.csv')
    
    # Verificar e padronizar nomes de colunas (case insensitive)
    df.columns = df.columns.str.strip().str.lower()
    column_mapping = {
        'mês_nome': 'mes_nome',
        'escola_publica': 'publica',
        'escola_particular': 'particular'
    }
    df = df.rename(columns=column_mapping)
    
    # Criar colunas calculadas
    df['total_autismo'] = df['publica'] + df['particular']
    df['percentual_publica'] = (df['publica'] / df['total_autismo']) * 100
    df['percentual_particular'] = (df['particular'] / df['total_autismo']) * 100
    
    # Converter mês para nome completo se necessário
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    if 'mes_nome' not in df.columns and 'mês' in df.columns:
        df['mes_nome'] = df['mês'].map(meses)

except Exception as e:
    print(f"Erro ao carregar dados: {str(e)}")
    # Dados de exemplo caso o CSV falhe
    data = {
        'ano': list(range(2010, 2024)),
        'publica': [1200, 1300, 1450, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000, 3200, 3400, 3600],
        'particular': [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950],
        'região': ['Sudeste']*14,
        'estado': ['SP']*14,
        'mes_nome': ['Janeiro']*14
    }
    df = pd.DataFrame(data)
    df['total_autismo'] = df['publica'] + df['particular']

# 2. Função de projeção
def generate_projections(base_df):
    if 'ano' not in base_df.columns:
        return base_df
    
    last_year = base_df['ano'].max()
    projection_years = range(last_year + 1, 2041)
    projected_data = []
    
    for year in projection_years:
        for regiao in base_df['região'].unique():
            subset = base_df[base_df['região'] == regiao].iloc[-1]
            
            new_row = {
                'ano': year,
                'publica': int(subset['publica'] * 1.08),
                'particular': int(subset['particular'] * 1.12),
                'total_autismo': int((subset['publica'] * 1.08) + (subset['particular'] * 1.12)),
                'região': regiao,
                'estado': subset['estado'],
                'mes_nome': 'Janeiro',
                'projeção': True
            }
            projected_data.append(new_row)
    
    return pd.concat([base_df, pd.DataFrame(projected_data)], ignore_index=True)

df_completo = generate_projections(df)

# 3. Inicializar o app com tema escuro
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Configuração de cores para os gráficos
colors = {
    'background': '#222222',
    'text': '#ffffff',
    'publica': '#3498db',
    'particular': '#e74c3c',
    'grid': 'rgba(255, 255, 255, 0.1)'
}

# 4. Layout do dashboard com tema escuro
app.layout = dbc.Container(
    [
        # Título
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Dashboard de Inclusão de Alunos com Autismo",
                    className='text-center my-4',
                    style={'color': colors['text']}
                ),
                width=12
            )
        ),

        # Filtros - Linha 1 (Slider de anos)
        dbc.Row(
            dbc.Col(
                [
                    html.Label("Período:", className='fw-bold mb-2', style={'color': colors['text']}),
                    dcc.RangeSlider(
                        id='ano-slider',
                        min=df_completo['ano'].min(),
                        max=df_completo['ano'].max(),
                        value=[df_completo['ano'].min(), df_completo['ano'].max()],
                        marks={str(ano): {'label': str(ano), 'style': {'color': colors['text'], 'transform': 'rotate(45deg)'}} 
                            for ano in range(df_completo['ano'].min(), 2041, 5)},
                        step=1,
                        tooltip={'placement': 'bottom'}
                    )
                ],
                md=12,
                className='mb-4'
            )
        ),

        # Filtros - Linha 2 (Dropdowns e RadioItems)
        dbc.Row(
            [
                # Filtro de Região
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Região", className='fw-bold', style={'color': colors['text']}),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(
                                            id='regiao-dropdown',
                                            options=[{'label': reg, 'value': reg} for reg in sorted(df_completo['região'].unique())],
                                            value=df_completo['região'].unique()[0],
                                            clearable=False,
                                            style={'backgroundColor': '#444', 'color': colors['text']}
                                        )
                                    ],
                                    style={'padding': '10px'}
                                )
                            ],
                            style={'backgroundColor': '#333', 'border': '1px solid #444'}
                        )
                    ],
                    md=4,
                    className='mb-3'
                ),

                # Filtro de Visualização
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Visualização", className='fw-bold', style={'color': colors['text']}),
                                dbc.CardBody(
                                    [
                                        dcc.RadioItems(
                                            id='tipo-visualizacao',
                                            options=[
                                                {'label': ' Valores Absolutos', 'value': 'absoluto'},
                                                {'label': ' Percentuais', 'value': 'percentual'}
                                            ],
                                            value='absoluto',
                                            inputStyle={'margin-right': '5px'},
                                            labelStyle={'display': 'block', 'margin-bottom': '5px', 'color': colors['text']}
                                        )
                                    ],
                                    style={'padding': '10px'}
                                )
                            ],
                            style={'backgroundColor': '#333', 'border': '1px solid #444'}
                        )
                    ],
                    md=4,
                    className='mb-3'
                ),

                # Filtro de Tipo de Escola
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Tipo de Escola", className='fw-bold', style={'color': colors['text']}),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(
                                            id='tipo-escola-dropdown',
                                            options=[
                                                {'label': ' Todas', 'value': 'todas'},
                                                {'label': ' Pública', 'value': 'publica'},
                                                {'label': ' Particular', 'value': 'particular'}
                                            ],
                                            value='todas',
                                            clearable=False,
                                            style={'backgroundColor': '#444', 'color': colors['text']}
                                        )
                                    ],
                                    style={'padding': '10px'}
                                )
                            ],
                            style={'backgroundColor': '#333', 'border': '1px solid #444'}
                        )
                    ],
                    md=4,
                    className='mb-3'
                )
            ],
            className='mb-4'
        ),

        # Gráficos
        dbc.Row(
            dbc.Col(
                dcc.Graph(id='evolucao-matriculas'),
                width=12,
                className='mb-4'
            )
        ),

        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(id='distribuicao-regiao'),
                    md=6,
                    className='mb-4'
                ),
                dbc.Col(
                    dcc.Graph(id='comparativo-estados'),
                    md=6,
                    className='mb-4'
                )
            ]
        ),

        # Métricas
        dbc.Row(id='metricas-gerais')
    ],
    fluid=True,
    style={'backgroundColor': colors['background'], 'padding': '20px'}
)

# 5. Callbacks com estilos escuros para os gráficos
@app.callback(
    [Output('evolucao-matriculas', 'figure'),
     Output('distribuicao-regiao', 'figure'),
     Output('comparativo-estados', 'figure'),
     Output('metricas-gerais', 'children')],
    [Input('ano-slider', 'value'),
     Input('regiao-dropdown', 'value'),
     Input('tipo-visualizacao', 'value'),
     Input('tipo-escola-dropdown', 'value')]
)
def update_graphs(anos, regiao, visualizacao, tipo_escola):
    # Filtrar dados (igual ao original)
    filtered_df = df_completo[
        (df_completo['ano'] >= anos[0]) & 
        (df_completo['ano'] <= anos[1]) &
        (df_completo['região'] == regiao)
    ]

    # Configuração comum para todos os gráficos
    graph_layout = {
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {'color': colors['text']},
        'xaxis': {'gridcolor': colors['grid']},
        'yaxis': {'gridcolor': colors['grid']}
    }

    # Gráfico 1: Evolução
    if tipo_escola == 'todas':
        cols = ['publica', 'particular']
        title = 'Evolução nas Redes Pública e Particular'
        colors_graph = [colors['publica'], colors['particular']]
    else:
        cols = [tipo_escola]
        title = f'Evolução na Rede {tipo_escola.capitalize()}'
        colors_graph = [colors[tipo_escola]]

    if visualizacao == 'percentual':
        y_cols = ['percentual_publica', 'percentual_particular'] if tipo_escola == 'todas' else [f'percentual_{tipo_escola}']
        y_title = 'Percentual (%)'
    else:
        y_cols = cols
        y_title = 'Número de Matrículas'

    fig1 = px.line(
        filtered_df.groupby('ano')[y_cols].sum().reset_index(),
        x='ano',
        y=y_cols,
        title=title,
        labels={'value': y_title, 'variable': 'Tipo', 'ano': 'Ano'},
        color_discrete_sequence=colors_graph
    )
    fig1.update_layout(graph_layout)

    # Gráfico 2: Distribuição por Região
    fig2 = px.pie(
        df_completo[df_completo['ano'] == anos[1]].groupby('região')['total_autismo'].sum().reset_index(),
        names='região',
        values='total_autismo',
        title=f'Distribuição por Região ({anos[1]})',
        hole=0.4,
        color_discrete_sequence=[colors['publica'], colors['particular'], '#2ecc71', '#f39c12', '#9b59b6']
    )
    fig2.update_layout(graph_layout)

    # Gráfico 3: Comparativo por Estado
    estado_df = filtered_df.groupby(['estado', 'ano']).agg({
        'publica': 'sum',
        'particular': 'sum'
    }).reset_index()
    
    fig3 = px.bar(
        estado_df[estado_df['ano'] == anos[1]],
        x='estado',
        y=['publica', 'particular'],
        barmode='group',
        title=f'Comparativo por Estado ({anos[1]})',
        labels={'value': 'Matrículas', 'variable': 'Tipo de Escola'},
        color_discrete_sequence=[colors['publica'], colors['particular']]
    )
    fig3.update_layout(graph_layout)

    # Métricas com estilo escuro
    total_publica = filtered_df['publica'].sum()
    total_particular = filtered_df['particular'].sum()
    crescimento = ((filtered_df['total_autismo'].iloc[-1] - filtered_df['total_autismo'].iloc[0]) / 
                  filtered_df['total_autismo'].iloc[0]) * 100 if filtered_df['total_autismo'].iloc[0] != 0 else 0

    metricas = dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("Pública", className='metric-label', style={'color': colors['text']}),
                        html.Span(f"{total_publica:,}", className='metric-value', style={'color': colors['publica']})
                    ], className='metric-box', style={'backgroundColor': '#333'})
                ], md=4),

                dbc.Col([
                    html.Div([
                        html.Span("Particular", className='metric-label', style={'color': colors['text']}),
                        html.Span(f"{total_particular:,}", className='metric-value', style={'color': colors['particular']})
                    ], className='metric-box', style={'backgroundColor': '#333'})
                ], md=4),

                dbc.Col([
                    html.Div([
                        html.Span("Crescimento", className='metric-label', style={'color': colors['text']}),
                        html.Span(f"{crescimento:.1f}%", 
                                className='metric-value',
                                style={'color': '#2ecc71' if crescimento >= 0 else '#e74c3c'})
                    ], className='metric-box', style={'backgroundColor': '#333'})
                ], md=4)
            ])
        ])
    ], className='shadow', style={'backgroundColor': '#333'})

    return fig1, fig2, fig3, metricas

# 6. Rodar o aplicativo
if __name__ == '__main__':
    app.run(debug=True)