from dash import Dash, Output, Input, State, html, ctx, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from os import path
from worker import list_mp, update_pair, clean_seg_pair, batch_btn_operation
import layout



# app
app = Dash(__name__, external_stylesheets=[dbc.themes.LUMEN])
app.title = 'Minimal Pairs in Korean'
server = app.server

# components

res_table_header = [
    html.Thead(html.Tr([html.Th("Word1 (orth)"), html.Th("Word1 (IPA)"),
                        html.Th("Word2 (orth)"), html.Th("Word2 (IPA)")], id='res-header'))
]
row1 = html.Tr([html.Td("You"), html.Td("didn't"), html.Td("select"), html.Td("a pair")])

res_table_body = [html.Tbody([row1], id='res-table')]

# layout
app.layout = dbc.Accordion(
[
    dbc.AccordionItem(
        layout.step_one,
        title="Step 1: Select two segments",

    ),
    dbc.AccordionItem(
        layout.step_two,
        title="Step 2: Parameters + start finding",
    ),
    dbc.AccordionItem(
        [
            dbc.Spinner(
                html.Div([
                    dbc.Alert(
                        "The 'download' function has not been implemented yet. :( Sorry about that!",
                        id="alert",
                        dismissable=True,
                        fade=True,
                        is_open=False,
                        color="danger",
                    ),
                    html.Div(html.H3("You didn't select a pair yet.",id='res-segpair')),
                    dbc.ButtonGroup([
                        dbc.Button('Download as .csv',
                                   disabled=True,
                                   id="download-btn",),
                        dbc.Button('Start over',
                                   href='.',
                                   external_link=True),
                    ]),
                    html.Div(dbc.Table(res_table_header + res_table_body),
                             id='res-div',
                             style={"maxHeight": "70vh", "overflow": "scroll"})])
            )
        ],
        title="Step 3: Find minimal pairs",
    )
])


# Callbacks
# 1. the main function: compute minimal pair
@app.callback([
    Output("res-segpair", "children"),
    Output("res-div", "children"),
    Output("download-btn", "disabled"),
    ], [
    Input("compute", "n_clicks")
    ], [
    State("pair_selected", "children"),
    State("freq-slider", "value"),
    State("input-nouns","value"),
    State("input-adverbs","value"),
    State("input-etymology","value"),
    ],
    prevent_initial_call=True
)
def compute_minimalpair(compute_btn, pair, freq_filter, noun_filter, adv_filter, ety_filter):
    # this function returns minimal pairs as a table and also count the number of minimal pairs
    triggered_id = ctx.triggered_id
    split_pair = clean_seg_pair(pair)


    if triggered_id != 'compute':
        return no_update
    if '(' in pair or len(split_pair) < 2:
        return no_update

    minimal_pair_lists = list_mp(pair,
                                 filters={
                                     # the actual frequency value should be 10 to the power of slider frequency
                                     'freq': 10 ** freq_filter,
                                     'pos': noun_filter + adv_filter,
                                     'etymology': ety_filter
                                 })
    mp_count = len(minimal_pair_lists)

    pair_selected_msg = f"Minimal pairs by [{split_pair[0]}] and [{split_pair[1]}] (N = {mp_count})"

    res_table_header = [
        html.Thead(
            html.Tr([html.Th("Word1 (orth)"), html.Th("Word1 (IPA)"), html.Th("Word2 (orth)"), html.Th("Word2 (IPA)")]))
    ]
    output_rows = list()
    by_pair = [word_one + word_two for word_one, word_two in minimal_pair_lists]
    for mp_row in by_pair:
        output_rows.append(html.Tr([html.Td(i) for i in mp_row]))

    res_table_body = [html.Tbody(output_rows)]

    result_table = [dbc.Table(res_table_header + res_table_body)]

    disable_download_btn_bool = False
    if mp_count < 1:
        disable_download_btn_bool = True
        pair_selected_msg = f"No minimal pairs by [{split_pair[0]}] and [{split_pair[1]}].  " \
                            f"Please try different parameter settings."

    return pair_selected_msg, result_table, disable_download_btn_bool


# 2. select segment pair
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
def select_segments(cv_value, undo_click, cell, pair, data):
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

    return table_col, table_data, {'textAlign': 'left', 'font-family': 'san-serif', 'fontSize': 20}, True, pair_msg


# 3. slider update
@app.callback([
    Output("slider-msg", "children"),
    Input("freq-slider", "value"),
    ],
    prevent_initial_call=True
)
def update_slider_msg(slider_value):
    converted_freq = 10 ** slider_value
    return [f'(Consider only words that occur more than {converted_freq:.2f} times out of 16m token '
            f'(or, {converted_freq * 100 / 16568543:.2f}%). Default=100)']


# 4. download button
@app.callback(
    Output("alert", "is_open"),
    Input("download-btn", "n_clicks"),
)
def download_btn(n):
    if n:
        return True


# 5. parameter switch noun
@app.callback([
    Output("input-nouns", "value"),
    Output("input-nouns", "options"),
    Input('switch-noun', 'value'),
    State('input-nouns', 'options')
    ],
    prevent_initial_call=True
)
def noun_switch_fn(switch, value_list):
    disabled = True
    if switch:  # if noun switch is turned on
        disabled = False
    return batch_btn_operation(value_list, disabled)


# 6. parameter switch adv
@app.callback([
    Output("input-adverbs", "value"),
    Output("input-adverbs", "options"),
    Input('switch-adverb', 'value'),
    State('input-adverbs', 'options')
    ],
    prevent_initial_call=True
)
def adv_switch_fn(switch, value_list):
    disabled = True
    if switch:  # if noun switch is turned on
        disabled = False
    return batch_btn_operation(value_list, disabled)


# 7. parameter switch etymology
@app.callback([
    Output("input-etymology", "value"),
    Output("input-etymology", "options"),
    Input('switch-etymology', 'value'),
    State('input-etymology', 'options')
    ],
    prevent_initial_call=True
)
def ety_switch_fn(switch, value_list):
    disabled = True
    if switch:  # if noun switch is turned on
        disabled = False
    return batch_btn_operation(value_list, disabled)

if __name__ == "__main__":
    app.run_server(debug=True)
