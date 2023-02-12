from dash import Dash, dcc, Output, Input, State, dash_table, html, ctx, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from os import path
from find_mp import list_mp

# backend stuff
def update_pair(pair, new_seg):
    # update minimal pair. used when user selects a segment from the inventory
    if '(' in pair:  # first selecting a segment
        return new_seg
    segs = pair.split(',')
    segs = [s.strip() for s in segs]
    pair = segs[-1], new_seg
    return ', '.join(pair)

inventory_path = path.join('assets', 'kor_c.csv')

df = pd.read_csv(inventory_path)

# app
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])
server = app.server

# components
table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        style_cell={'textAlign': 'left'},
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

res_table_header = [
    html.Thead(html.Tr([html.Th("Word1 (orth)"), html.Th("Word1 (IPA)"),
                        html.Th("Word2 (orth)"), html.Th("Word2 (IPA)")], id='res-header'))
]
row1 = html.Tr([html.Td("Arthur"), html.Td("Arthur"), html.Td("Arthur"),html.Td("Dent")])
row2 = html.Tr([html.Td("Ford"), html.Td("Arthur"), html.Td("Arthur"),html.Td("Prefect")])
row3 = html.Tr([html.Td("Zaphod"), html.Td("Arthur"), html.Td("Arthur"),html.Td("Beeblebrox")])
row4 = html.Tr([html.Td("Trillian"), html.Td("Arthur"), html.Td("Arthur"),html.Td("Astra")])

res_table_body = [html.Tbody([row1, row2, row3, row4], id='res-table')]

# layout
app.layout = dbc.Accordion(
[
    dbc.AccordionItem(
        [
            CV_button_group,
            table,
            dbc.Button('Undo selection', id="undo"),
            html.Div(html.H3([html.Br(), 'You selected:', selected_pair]))
        ],
        title="Step 1: Select two segments",

    ),
    dbc.AccordionItem(
        [
            html.Div([html.P("Todo: Parameter setting for frequency, part of speech, word length, etc."),
                     html.P("But for now, click the button below to find minimal pairs in the whole corpus. "
                            "The corpus contains nouns, pronouns, adverbs, interjections and adverbs with the relative frequency of 0.005.")]),
            dbc.Button("Compute minimal pairs!", color="danger", id='compute')

        ],
        title="Step 2: Parameters + start finding",
    ),
    dbc.AccordionItem(
        [
            html.Div(html.H3("You didn't select a pair yet.",id='res-segpair')),
            html.Div(dbc.Table(res_table_header + res_table_body), id='res-div')

        ],
        title="Step 3: Find minimal pairs",
    )
])


# Callbacks
@app.callback([
    Output("res-segpair", "children"),
    Output("res-div", "children"),
    ], [
    Input("pair_selected", "children"),
    Input("compute", "n_clicks")
    ],
    prevent_initial_call=True
)
def compute_minimalpair(pair, compute_btn):
    triggered_id = ctx.triggered_id
    split_pair = pair.split(',')
    split_pair = [sp.strip() for sp in split_pair]

    if triggered_id != 'compute':
        return no_update
    if '(' in pair or len(split_pair) < 2:
        return no_update

    minimal_pair_lists = list_mp(pair, filters={'freq': 1}) #TODO, update to implement filters

    pair_selected_msg = f"Minimal pairs by [{split_pair[0]}] and [{split_pair[1]}]"

    res_table_header = [
        html.Thead(
            html.Tr([html.Th("Word1 (orth)"), html.Th("Word1 (IPA)"), html.Th("Word2 (orth)"), html.Th("Word2 (IPA)")]))
    ]
    output_rows = list()
    by_pair = [word_one + word_two for word_one, word_two in minimal_pair_lists]
    for mp_row in by_pair:
        output_rows.append(html.Tr([html.Td(i) for i in mp_row]))

    res_table_body = [html.Tbody(output_rows)]
    return pair_selected_msg, [dbc.Table(res_table_header + res_table_body)]


@app.callback([
    Output("seg_table", "columns"),
    Output("seg_table", "data"),
    Output("seg_table", "style_cell"),
    Output("seg_table", "is_focused"),
    Output("pair_selected", "children"),
    ], [
    Input('cv_btn', "value"),
    Input('undo', 'n_clicks'),
    Input("seg_table", "active_cell"),
    Input("pair_selected", "children"),
    State("seg_table", "derived_viewport_data"),
    ],
    prevent_initial_call=True
)
def select_segements(cv_value, undo_click, cell, pair, data):
    # select a segment pair, including switching consonant/vowel chart, etc.
    triggered_id = ctx.triggered_id
    pair_msg = pair

    if cv_value == 'v':
        inventory_path = path.join('assets', 'kor_v.csv')
    else:
        inventory_path = path.join('assets', 'kor_c.csv')
    df = pd.read_csv(inventory_path)

    table_col = [{"name": i, "id": i} for i in df.columns]
    table_data = df.to_dict("records")

    if triggered_id == 'cv_btn':
        pair_msg = "(You haven't selected a pair)"

    elif triggered_id == 'undo':
        split_pair = pair_msg.split(',')
        if len(split_pair) == 1:
            pair_msg = "(You haven't selected a pair)"
        else:
            pair_msg = pair_msg.split(',')[0]

    elif triggered_id == 'seg_table':
        if cell:
            selected = data[cell["row"]][cell["column_id"]]
            if selected is not None and len(selected) < 4:
                pair_msg = update_pair(pair, selected)

    return table_col, table_data, {'textAlign': 'left'}, True, pair_msg


if __name__ == "__main__":
    app.run_server(debug=True)
