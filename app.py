import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', 'https://fonts.googleapis.com/css2?family=Quicksand&display=swap']

app = dash.Dash(__name__,
    external_stylesheets=external_stylesheets,
    title='Aldeias Indígenas',
    update_title=None
)

server = app.server

df = pd.read_csv('data/aldeias_indigenas.csv')

regions = df.NM_REGIAO.unique()

app.layout = html.Div([

    html.Div([

        html.H1('Aldeias Indígenas no Brasil'),
        html.A([
            html.Img(src=app.get_asset_url('github.svg'))
        ], href='https://github.com/mmartiniano/brazilian-indigenous-village-location', target='_blank')

    ], className='navbar'),

    html.Div([

        html.Div([

            html.H1('Localização Geográfica das Aldeias Indígenas Brasileiras'),
            html.P('''
                    O IBGE disponibiliza dados geográficos de localidades brasileiras
                    de acordo com pesquisa feita em 2010. Dentre os locais, foram classificados
                    como "ALDEIA INDÍGENA" os pontos que possuem "casa ou conjunto de casas ou
                    malocas [...] que serve de habitação para o
                    indígena e aloja diversas famílias" e com "no mínimo, 20 habitantes indígenas em
                    uma ou mais moradias".                     
            '''),
            html.P(['A publicação oficial do instituto pode ser acessada clicando ',
                html.A('aqui', target='_blank', href='https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/14126-asi-ibge-disponibiliza-coordenadas-e-altitudes-para-21304-localidades-brasileiras'),
                '''. A localização geográfica em longitude, latitude e altitude das aldeias podem
                ser visualizadas no mapa. Além disso, o gráfico de barras mostra a
                quantidade de aldeias por região.
                Os dados utilizados e as informações de classificação das localidades podem ser acessadas clicando
                ''',
                html.A('aqui', target='blank', href='ftp://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/localidades'),
                '.'
            ]),

            dcc.Dropdown(
                id='regions',
                options=[{'label': region, 'value': region} for region in regions],
                value=regions,
                multi=True,
                className='dropdown'
            )

        ], className='left'),

        html.Div([

            dcc.Graph(
                id='map',
                className='map'
            ),

            dcc.Graph(
                id='bar',
                className='bar'
            )

        ], className='right')

    ], className='main')
                 
])

@app.callback([
    Output('map', 'figure'),
    Output('bar', 'figure'),
    ],
    Input('regions', 'value'))
def update_graph(selected_regions) :
    
    if len(selected_regions) <= 0 :
        selected_regions = regions

    map = px.scatter_mapbox(df[df.NM_REGIAO.isin(selected_regions)], 
                            lat='LAT', 
                            lon='LONG', 
                            color='ALT',
                            text='NM_LOCALID',
                            hover_data=['UF', 'NM_REGIAO'],
                            labels={'NM_LOCALID':'Nome', 'LAT':'Latitude', 'LONG':'Longitude', 'ALT':'Altitude', 'UF':'Estado', 'NM_REGIAO': 'Região'},
                            zoom=2.8,
                            mapbox_style='carto-positron')

    map.update_layout(margin={'r':0,'t':0,'l':0,'b':0}, coloraxis_colorbar={'xanchor':'right', 'x':1})

    count_df = df[['UF', 'UF_SIGLA', 'NM_REGIAO', 'REGIAO_SIGLA', 'ID']].groupby(['UF', 'UF_SIGLA', 'NM_REGIAO', 'REGIAO_SIGLA']).count().reset_index(level=['UF', 'UF_SIGLA', 'NM_REGIAO', 'REGIAO_SIGLA'])
    count_df.rename(columns={'ID': 'ALDEIAS'}, inplace=True)

    bar = go.Figure(data=[go.Bar(
                x=count_df[count_df.NM_REGIAO.isin(selected_regions)]['UF_SIGLA'],
                y=count_df['ALDEIAS'],
                text=count_df['ALDEIAS'],
                textposition='auto')])

    bar.update_layout(showlegend=False,
                    margin={'r':0,'t':0,'l':0,'b':0},
                    yaxis={'visible': False, 'showticklabels': False})

    return map, bar


if __name__ == '__main__':
    app.run_server(debug=True)