import pandas as pd
from dash import Dash, callback_context, dcc, html
from dash.dependencies import Input, Output
from dash_daq import BooleanSwitch
from datetime import datetime, timezone
from plotly.graph_objects import Scatter
from plotly.subplots import make_subplots
from pylsl import StreamInlet, resolve_byprop

def search_streams():
    '''Look for EEG streams using LSL protocol.

    Returns:
        Array of LSL streams.
    '''
    print("Searching streams")
    streams = resolve_byprop('type', 'EEG')

    inlets = []
    for stream in streams:
        inlet = StreamInlet(stream)
        inlets.append(inlet)
        print('Stream found: ', inlet.info().source_id())

    return inlets

def start_streaming(inlets, channels = ['TP9', 'AF7', 'AF8', 'TP10'], debug = False):
    '''Convert recordings to MNE format.

    Args:
        inlets : array
            LSL streams captured.
        channels : array
            Channels to draw in graphs.
        debug : bool
            Dash debugging.
    See also:
        search_streams
    '''
    global df, data_shown, playpause, expand_graphs

    cols = []
    df = []

    for inlet in inlets:
        channel = inlet.info().desc().child('channels').first_child()
        all_channels = [channel.child_value('label')]

        while len(all_channels) != inlet.info().channel_count():
            channel = channel.next_sibling()
            all_channels.append(channel.child_value('label'))

        cols.append(all_channels)
        df.append(pd.DataFrame(columns=all_channels))

    data_shown = 1400
    playpause = True
    expand_graphs = False

    app = Dash(__name__)
    app.title = 'Muse streaming'
    app.layout = serve_layout(channels)

    @app.callback(
        Output('interval_component', 'interval'),
        Input('interval_modifier', 'value')
    )
    def update_interval(value):
        return value

    @app.callback(
        Output('graphs', 'children'),
        Input('interval_component', 'n_intervals'),
        Input('channels_selected', 'value'),
        Input('zoom_in', 'n_clicks'),
        Input('zoom_out', 'n_clicks'),
        Input('reset', 'n_clicks'),
        Input('playstop', 'n_clicks'),
        Input('expand_graphs', 'on')
    )
    def draw_graph(in_interval, in_channels_selected, in_zoom_in, in_zoom_out, in_reset, in_playstop, in_expand_graphs):
        global df, data_shown, playpause, expand_graphs

        changed_id = [p['prop_id'] for p in callback_context.triggered][0]

        if 'zoom_in' in changed_id:
            if data_shown != 200:
                data_shown = data_shown - 200
        if 'zoom_out' in changed_id:
            data_shown = data_shown + 200
        if 'reset' in changed_id:
            data_shown = 1400
        if 'playstop' in changed_id:
            playpause = True if playpause == False else False

        graphs = []
        for index, inlet in enumerate(inlets):
            if playpause == True:
                samples, timestamps = inlet.pull_chunk(timeout=0.0, max_samples=1024)
                utc = [datetime.utcfromtimestamp(timestamp).replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%H:%M:%S.%f') for index, timestamp in enumerate(timestamps)]

                df_aux = pd.DataFrame(samples, columns=cols[index], index=utc)
                df[index] = df[index].append(df_aux)
                df_to_show = df[index].tail(data_shown)
                df_to_show = df_to_show[in_channels_selected]
            else:
                df_to_show = df[index].tail(data_shown)
                df_to_show = df_to_show[in_channels_selected]

            channel_qualities = []
            for i in in_channels_selected:
                if abs(df_to_show[i].tail(200).max() - df_to_show[i].tail(200).min()) < 300:
                    channel_qualities.append(i + ' - GOOD ' + u'\u2713')
                else:
                    channel_qualities.append(i + ' - BAD ' + u'\u2716')

            if in_expand_graphs == False:
                if len(df_to_show.columns) % 2 == 0:
                    fig = make_subplots(rows=int(len(df_to_show.columns) / 2), cols=2, subplot_titles=channel_qualities)
                else:
                    fig = make_subplots(rows=int((len(df_to_show.columns) / 2) + 0.5), cols=2, subplot_titles=channel_qualities)
                
                j = [1, 1, 2, 2, 3]
                k = [1, 2, 1, 2, 1]
                for index2, column in enumerate(df_to_show.columns):
                    fig.add_trace(
                        Scatter({
                            'x': df_to_show.index,
                            'y': df_to_show[column]
                        }),
                        row=j[index2],
                        col=k[index2]
                    )
                heights = [500, 500, 800, 800, 1100]
                fig.update_layout(height=heights[len(df_to_show.columns)-1], showlegend=False)
            else:
                fig = make_subplots(rows=len(df_to_show.columns), cols=1, subplot_titles=channel_qualities)
                j = 1
                for i in df_to_show.columns:
                    fig.add_trace(
                        Scatter({
                            'x': df_to_show.index,
                            'y': df_to_show[i]
                        }),
                        row=j,
                        col=1
                    )
                    j += 1
                heights = [500, 900, 1200, 1500, 1600]
                fig.update_layout(height=heights[len(df_to_show.columns)-1], showlegend=False)

            graphs.append(
                html.Div([
                    html.H3(inlet.info().name()),
                    dcc.Graph(
                        id='muse_livestream',
                        config={
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['pan2d','lasso2d']
                        },
                        figure=fig
                    )
                ], style={'margin': 'auto', 'text-align': 'center'})
            )

        return(html.Div(graphs))

    app.run_server(debug=debug)

def serve_layout(channels):
    return html.Div([
        html.Div([
            html.H1('Muse streaming'),

            dcc.Interval(
                id='interval_component',
                interval=1*100,
                n_intervals=0
            ),

            dcc.Checklist(
                id='channels_selected',
                options=[
                    {'label': 'TP9', 'value': 'TP9'},
                    {'label': 'AF7', 'value': 'AF7'},
                    {'label': 'AF8', 'value': 'AF8'},
                    {'label': 'TP10', 'value': 'TP10'},
                    {'label': 'AUX', 'value': 'Right AUX'}
                ],
                value=channels
            ),

            html.Button('Zoom In', id='zoom_in', n_clicks=0),

            html.Button('Zoom Out', id='zoom_out', n_clicks=0),

            html.Button('Reset', id='reset', n_clicks=0),

            html.Button('Play/Stop', id='playstop', n_clicks=0),

            html.P('Expand graphs'),

            BooleanSwitch(id='expand_graphs', on=False),

            html.P('Update interval'),

            dcc.Slider(
                id='interval_modifier',
                min=200,
                max=5000,
                value=200,
                step=200,
                marks={
                    200: {'label': '200 ms'},
                    500: {'label': '500 ms'},
                    750: {'label': '750 ms'},
                    1000: {'label': '1 s'},
                    1500: {'label': '1.5 s'},
                    2000: {'label': '2 s'},
                    3000: {'label': '3 s'},
                    5000: {'label': '5 s'}
                }
            ),

        ], style={'margin': 'auto', 'text-align': 'center'}),

        html.Div(id='graphs')
    ])
