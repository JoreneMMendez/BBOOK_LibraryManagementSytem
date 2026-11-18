from rich.theme import Theme

# each theme is a dictionary of style names (colors only)
# logo1-3 are the logo colors from top to bottom
# good / warn / bad are the status colors
THEMES = {
    "Purple Cyan": {
        "main": "white",
        "border": "medium_purple1",
        "accent": "bold bright_cyan",
        "key": "bold bright_cyan",
        "muted": "grey62",
        "logo1": "bold medium_purple1",
        "logo2": "bold cornflower_blue",
        "logo3": "bold bright_cyan",
        "good": "bold spring_green2",
        "warn": "gold1",
        "bad": "bold bright_red",
    },
    "Amber Retro": {
        "main": "gold1",
        "border": "dark_orange",
        "accent": "bold orange1",
        "key": "bold orange1",
        "muted": "orange4",
        "logo1": "bold dark_orange",
        "logo2": "bold orange1",
        "logo3": "bold gold1",
        "good": "bold green1",
        "warn": "orange1",
        "bad": "bold red",
    },
    "Ocean Blue": {
        "main": "white",
        "border": "dodger_blue2",
        "accent": "bold bright_cyan",
        "key": "bold bright_cyan",
        "muted": "grey62",
        "logo1": "bold dodger_blue2",
        "logo2": "bold deep_sky_blue1",
        "logo3": "bold bright_cyan",
        "good": "bold spring_green2",
        "warn": "gold1",
        "bad": "bold bright_red",
    },
}

default_theme = "Purple Cyan"


# list of the theme names
def getThemeNames():
    return list(THEMES.keys())


# use a theme, unknown names use the default
def applyTheme(console, themeName):
    if themeName not in THEMES:
        themeName = default_theme
    console.push_theme(Theme(THEMES[themeName]))
    return themeName
