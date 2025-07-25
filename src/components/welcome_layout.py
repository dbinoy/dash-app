from dash import html
import dash_bootstrap_components as dbc

def welcome_layout():
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Welcome to the REcore Dashboards", className="display-4 mb-3"),
                        html.P(
                            "Explore insights from our data warehouse. Select a dashboard below to get started.",
                            className="lead mb-4"
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Button(
                                        "App Usage Telemetry",
                                        href="/app-usage",
                                        color="primary",
                                        size="lg",
                                        className="me-3"
                                    ),
                                    width="auto"
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "Azure Cost Analysis",
                                        href="/azure-cost",
                                        color="secondary",
                                        size="lg"
                                    ),
                                    width="auto"
                                ),
                            ],
                            justify="center",
                            className="mb-4"
                        ),
                        html.Hr(),
                        html.P(
                            "Use the navigation bar above or the buttons here to switch between dashboards.",
                            className="text-muted"
                        ),
                    ],
                    width=8,
                    className="mx-auto text-center"
                )
            )
        ],
        fluid=True,
        className="py-5"
    )