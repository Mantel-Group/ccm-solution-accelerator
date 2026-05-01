from dash import Dash
from layout import get_layout
from dotenv import load_dotenv
import os

app = Dash(__name__, use_pages=True, external_stylesheets=[
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
], assets_folder='assets')
app.layout = get_layout()
server = app.server  # For deployment (WSGI)
load_dotenv('../.env')

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=os.environ.get('PORT',8050))
