# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt

import flask
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os
from random import randint
# from matplotlib import pyplot as plt

# from utils.heatmap_minmax import getRGB, rescale_score_by_abs

import pickle


# matplotlib.use("agg")
# app = dash.Dash("attr")
# server = app.server

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

# with open("data1/label_dict.pickle", "rb") as pfile:
#     label_dict = pickle.load(pfile)
#
# with open("data1/word_attr_list.pickle","rb") as pfile:
#     attr_word_df_list = pickle.load(pfile)
#
# with open("data1/ngram_attr_list.pickle", "rb") as pfile:
#     attr_ngram_df_list = pickle.load(pfile)
#
# with open("data1/raw_text.pickle", "rb") as pfile:
#     raw_text = pickle.load(pfile)
#
# prob_df = pd.read_csv("data1/prob.csv")

app = dash.Dash('app', server=server)
app.scripts.config.serve_locally = False

# DOC_ID = 0
# CLASS_ID = 0

# cmap_name="bwr"
# colormap  = plt.get_cmap(cmap_name)


def rescale_score_by_abs(score, max_score, min_score):
    """
    rescale positive score to the range [0.5, 1.0], negative score to the range [0.0, 0.5],
    using the extremal scores max_score and min_score for normalization
    """

    # CASE 1: positive AND negative scores occur --------------------
    if max_score > 0 and min_score < 0:

        if max_score >= abs(min_score):  # deepest color is positive
            if score >= 0:
                return 0.5 + 0.5 * (score / max_score)
            else:
                return 0.5 - 0.5 * (abs(score) / max_score)

        else:  # deepest color is negative
            if score >= 0:
                return 0.5 + 0.5 * (score / abs(min_score))
            else:
                return 0.5 - 0.5 * (score / min_score)

                # CASE 2: ONLY positive scores occur -----------------------------
    elif max_score > 0 and min_score >= 0:
        if max_score == min_score:
            return 1.0
        else:
            return 0.5 + 0.5 * (score / max_score)

    # CASE 3: ONLY negative scores occur -----------------------------
    elif max_score <= 0 and min_score < 0:
        if max_score == min_score:
            return 0.0
        else:
            return 0.5 - 0.5 * (score / min_score)

def getRGB (c_tuple):
    return "#%02x%02x%02x"%(int(c_tuple[0]*255), int(c_tuple[1]*255), int(c_tuple[2]*255))


def ConditionalTable(df, max_value, min_value):
    # max_value = df.max(numeric_only=True).max()
    # min_value = df.min(numeric_only=True).max()
    rows = []
    for i in range(len(df)):
        row = {}
        for col in ['Feature']:
            value = df.iloc[i][2]
            score = rescale_score_by_abs(value, max_value, min_value)
            style = {'backgroundColor': getRGB(colormap(score))}
            row['Feature Highlight'] = html.Div(
                df.iloc[i][col],
                style=dict({
                    'height': '100%'
                }, **style)
            )
            row[col] = df.iloc[i][col]
        for col in ['Index','Attribution Score']:
            row[col] = df.iloc[i][col]

        rows.append(row)

    return rows

app.layout = html.Div([
    #html.H2("Feature Attribution Analyzer"),
    html.Div([html.Span('Feature Attribution Analyzer',
              style = {'padding': '5px', 'fontSize': '34px','color':'#5E5E5E'})],
             style = {"text-align": "center"})
    # html.Div([
    #     html.Div([
    #         html.H4("Choose a document from class"),
    #         dcc.Dropdown(
    #             id='class-input',
    #             options=[{'label': k, 'value': np.argmax(v)}
    #                      for k, v in label_dict.items()],
    #             value=0,
    #             clearable=False
    #         )
    #         # html.Button("Random", id = 'random-button')
    #     ],
    #     style= {"margin-bottom": 10, "margin-top": 0}),
    #     # dcc.Textarea(
    #     #     placeholder = 'Enter a document...',
    #     #     value = ' ',
    #     #     id = 'text-input',
    #     #     style={'overflowY': 'scroll', 'height': 200, 'width': '100%'}
    #     # ),
    #     html.Button("Random", id = 'random-button'),
    #
    #     html.Div(
    #         id='text-input',
    #         style={'overflowY': 'scroll', 'height': 200, "margin-bottom": 10, "margin-top": 5,'border': 'thin lightgrey solid'}
    #     ),
    #     dcc.Graph(
    #         id="prob"
    #     )
    # ],
    #     style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'top'}),
    # html.Div(style={'width': '2%', 'display': 'inline-block','vertical-align': 'middle'}),
    #
    # html.Div([
    #     html.H4("Choose a class to compute attribution scores"),
    #     dcc.Dropdown(
    #         id='class-input-right',
    #         options=[{'label': k, 'value': np.argmax(v)}
    #                  for k, v in label_dict.items()],
    #         value=0,
    #         clearable=False
    #     ),
    #     #html.H3("Highlighted Document"),
    #     html.Div(
    #         id='high-light',
    #         style={'overflowY': 'scroll', 'height': 200, "margin-top": 36, 'border': 'thin lightgrey solid'}
    #     ),
    #     html.H4("Type of attributions"),
    #     dcc.Dropdown(
    #         id = 'attr-method',
    #         options=[{'label': "Attributions on words", 'value': 0,},
    #                  {'label': "Attributions on ngram", 'value': 1, },
    #                  {'label': "Attribution differences on words", 'value': 2, },
    #                  {'label': "Attributions differences on words", 'value': 3, }],
    #         value=0,
    #         clearable=False
    #         ),
    #     dt.DataTable(
    #         # Initialise the rows
    #         rows=[{}],
    #         #row_selectable=True,
    #         filterable=True,
    #         sortable=True,
    #         #selected_row_indices=[],
    #         id='table-display'
    #     )
    # ],
    #     style={'width': '45%', 'display': 'inline-block','vertical-align': 'middle'}),
    #
    # # hidden divs
    # html.Div(id = 'doc-id', style = {'display': "nne"})
])

# @app.callback(
#     Output("doc-id", "children"),
#     [Input('class-input', "value"),
#      Input('random-button', 'n_clicks')]
# )
# def update_doc_id(n_class, n_clicks):
#     temp_df = prob_df[prob_df['true_class']==n_class]
#     id_list = temp_df['doc_id'].tolist()
#     temp_id = id_list[randint(0,len(id_list)-1)]
#     #temp_id = 148
#     return temp_id
#
#
# @app.callback(
#     Output("text-input", "children"),
#     [Input('doc-id',"children")]
# )
# def update_input_text(doc_id):
#     return html.P(raw_text[doc_id])
# # def update_input_text(doc_id):
# #     attr_df = attr_word_df_list[doc_id]
# #     x_string = attr_df['word'].tolist()
# #     return ' '.join(x_string)
#
#
# @app.callback(
#     Output('high-light', 'children'),
#     [Input('doc-id', "children"),
#      Input('class-input-right', 'value')]
# )
# def update_highlight(doc_id,class_n):
#     attr_df = attr_word_df_list[doc_id]
#     x_string = attr_df['word'].tolist()
#     scores =  attr_df['attr_%d'% int(class_n)].tolist()
#     max_v = max(scores)
#     min_v = min(scores)
#     span_list = []
#     for word, s in zip(x_string, scores):
#         score_scale = rescale_score_by_abs(s, max_v, min_v)
#         style = {'backgroundColor': getRGB(colormap(score_scale)),
#         'display': 'inline-block'}
#         span_list.append(
#             html.Span(word, style = style)
#         )
#         span_list.append(html.Span(" "))
#
#     return html.Div(span_list)
#
#
# @app.callback(
#     Output('table-display', 'rows'),
#     [Input('class-input-right', 'value'),
#      Input('attr-method', 'value'),
#      Input('doc-id', "children")])
# def update_table(class_n, method, doc_id):
#     true_class = prob_df.loc[doc_id, "true_class"]
#     if method == 0: # word
#         attr_df = attr_word_df_list[doc_id]
#         attr_df['Feature'] = attr_df['word']
#         attr_df['Index'] = attr_df['index']
#         attr_df['Attribution Score'] = attr_df['attr_%d'% int(class_n)]
#     elif method == 2: # diff word
#         attr_df = attr_word_df_list[doc_id]
#         attr_df['Feature'] = attr_df['word']
#         attr_df['Index'] = attr_df['index']
#         attr_df['Attribution Score'] = attr_df['attr_%d' % int(class_n)] - attr_df['attr_%d' % int(true_class)]
#     elif method == 1: # ngram
#         attr_df = attr_ngram_df_list[doc_id]
#         attr_df['Feature'] = attr_df.index
#         attr_df['Index'] = attr_df['pos']
#         attr_df['Attribution Score'] = attr_df['attr_%d' % int(class_n)]
#     else: # diff ngram
#         attr_df = attr_ngram_df_list[doc_id]
#         attr_df['Feature'] = attr_df.index
#         attr_df['Index'] = attr_df['pos']
#         attr_df['Attribution Score'] = attr_df['attr_%d' % int(class_n)] - attr_df['attr_%d' % int(true_class)]
#
#     attr_df = attr_df[['Index','Feature','Attribution Score']]
#     max_v = attr_df['Attribution Score'].max()
#     min_v = attr_df['Attribution Score'].min()
#     attr_df = attr_df[attr_df['Attribution Score'] != 0]
#     return ConditionalTable(attr_df, max_v, min_v)
#
#
#
# @app.callback(
#     Output("prob", "figure"),
#     [Input('doc-id', "children")]
# )
# def update_figure(doc_id):
#     prob_bar = [go.Bar(
#         x = list(label_dict.keys()),
#         y = prob_df.loc[int(doc_id),"prob_0":"prob_10"].tolist(),
#         opacity = 0.6
#     )]
#
#     return {
#         'data': prob_bar,
#         'layout': go.Layout(
#             xaxis={'title': "Class"},
#             yaxis={'title': "Probability"},
#             title= "Predicted Probability for each class"
#         )
#     }

if __name__ == '__main__':
    app.run_server()