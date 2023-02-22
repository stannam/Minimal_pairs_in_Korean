import dash_bootstrap_components as dbc
import pandas as pd
from dash import html, dcc, dash_table
from os import path


inventory_path = path.join('assets', 'kor_c.csv')

df = pd.read_csv(inventory_path)

table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left', 'font-family': 'serif', 'fontSize': 20},
        data=df.to_dict("records"),
        is_focused=True,
        id="seg_table"
    )
CV_button_group = dbc.RadioItems(
    className='btn-group',
    inputClassName="btn-check",
    labelClassName="btn btn-outline-primary",
    options=[
        {"label": "Consonants", "value": 'c'},
        {"label": "Vowels", "value": 'v'},
    ],
    value='c',
    id='cv_btn',
)
selected_pair = html.P(children="(You haven't selected a pair)",
                       id="pair_selected")


POS_selector = [dbc.Checklist(
        options=[
            {"label": "Nouns (명사)", "value": True}
        ],
        value=[True],
        id='switch-noun',
        switch=True
    ),
    dbc.Checklist(
        options=[
            {"label": "Common nouns (일반명사)", "value": 'NNG', "disabled": False},
            {"label": "Proper nouns (고유명사)", "value": 'NNP', "disabled": False},
            {"label": "Counting words (수사)", "value": 'NR', "disabled": False},
            {"label": "Pronouns (대명사)", "value": 'NP', "disabled": False},
            {"label": "Bound nouns (의존명사)", "value": 'NNB', "disabled": False},
        ],
        value=['NNG', 'NNP', 'NR', 'NP', 'NNB'],
        id="input-nouns",
        inline=True,
    ),
    html.Br(),

    dbc.Checklist(
        options=[
            {"label": "Adverbs (부사)", "value": True}
        ],
        value=[True],
        id='switch-adverb',
        switch=True
    ),

    dbc.Checklist(
        options=[
            {"label": "Conjunctions(접속부사)", "value": 'MAJ', "disabled": False},
            {"label": "Other adverbs (일반부사)", "value": 'MAG', "disabled": False},
            {"label": "Interjections (감탄사)", "value": 'IC', "disabled": False},
        ],
        value=['MAJ', 'MAG', 'IC'],
        id="input-adverbs",
        inline=True,
    )]


etymology_selector = [dbc.Checklist(
        options=[
            {"label": "Use this feature", "value": True}
        ],
        value=[],
        id='switch-etymology',
        switch=True
    ),
    dbc.Checklist(
        options=[
            {"label": "Native (고유어)", "value": 'native', "disabled": True},
            {"label": "Sino (한자어)", "value": 'sino', "disabled": True},
            {"label": "Foreign (외래어)", "value": 'foreign', "disabled": True},
        ],
        value=[],
        id="input-etymology",
        inline=True,
    )]


step_one = [
    html.H3("Select a pair from either consonants or vowels (cross-selecting unavailable)."),
    html.Br(),

    CV_button_group,
    table,
    dbc.Button('Undo selection', id="undo"),

    html.Div([html.H4([html.Br(), 'You selected:', selected_pair])])
]


step_two = [
    html.H4("Minimum frequency"),
    html.P("(Consider only words that occur more than 100 times out of 16m token. Default=100)",
           id="slider-msg"),
    dcc.Slider(0, 5, 0.01,
               marks={i: f'{10 ** i}' for i in range(6)},
               value=2,
               included=False,
               id='freq-slider'),

    html.Br(),

    html.H4("Part of speech"),
    html.P("Select parts of speech."),

    html.Div(POS_selector, style={'padding-left': '50px'}),

    html.Br(),
    html.H4("Etymology"),
    html.P("Limit the search to native/Sino/foreign (experimental)"),

    html.Div(etymology_selector, style={'padding-left': '50px'}),

    html.Br(),
    html.Br(),
    dbc.Button("Compute minimal pairs!", color="danger", id='compute')
]
