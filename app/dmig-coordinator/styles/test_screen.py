TEST_SCREEN_CSS = """
Screen {
    align: center top;
    layers: base overlay;
}

.title {
    text-align: center;
    padding: 1;
}

.input-row {
    height: 3;
    margin: 1;
}

#test_container {
    width: 100%;
    height: 100%;
    align: center top;
}

.input-section {
    width: 100%;
    height: auto;
    margin-bottom: 1;
}

Button {
    margin: 1 2;
}

#results_section {
    width: 100%;
    height: 1fr;  /* Toma el espacio restante */
    margin: 1;
}

#results_container {
    width: 100%;
    height: 100%;
    border: solid green;
    background: $surface-darken-1;
}

#results {
    width: 100%;
    padding: 1;
    height: auto;
}

.results-title {
    text-align: center;
    padding-bottom: 1;
    background: $background;
}

.section-title {
    text-align: center;
    padding-top: 1;
    background: $boost;
    width: 100%;
}

.button-row {
    height: 3;
    margin: 1;
    align: center middle;
}
""" 