import dash_bootstrap_components as dbc
from dash import Dash, dcc, html,callback,dash_table,callback_context
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import warnings
import random as rd
import pandas as pd
from dash import no_update
import dash_daq as daq
from sqlalchemy.exc import SQLAlchemyError
import numpy as np
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

external_stylesheets = [dbc.themes.BOOTSTRAP]  
warnings.filterwarnings('ignore')

app = Dash(__name__, suppress_callback_exceptions=True,external_stylesheets=external_stylesheets)
server = app.server

data = pd.read_excel("assets/Data/Registro Conferencia de WiDS Guayaquil@ESPOL 2024 (respuestas).xlsx",engine="openpyxl")

import pandas as pd
from sqlalchemy import create_engine, exc

# Configuración de la conexión a la base de datos
USER = "root"
PASSWORD = "UAxgbfibezWmZpWKvXBANZtRbWuvcObR"
HOST = "viaduct.proxy.rlwy.net"
PORT = "49882"
BD = "railway"
db_url = f"mysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{BD}"
engine = create_engine(db_url)

try:
    connection = engine.connect()
    print("Conexión exitosa")
    connection.close()
except Exception as e:
    print(f"Error de conexión: {e}")

def formatDf(df):
    df = df.rename(columns={
        'Nombres': 'nombre',
        'Apellidos': 'apellido',
        'Teléfono (Móvil)': 'telefono_movil',
        'Correo electrónico:': 'correo_electronico',
        'Carrera': 'carrera',
        'Universidad': 'universidad',
        'Organización': 'organizacion',
        'Trabajo': 'trabajo',
        'Ocupación': 'ocupacion'
    })
    df = df.drop(["Marca temporal", "¿Desea recibir notificaciones de futuros eventos?", "¿Estás seguro de que podrás asistir al evento de forma presencial?"], axis=1)
    return df

def check_and_insert(df, table_name):
    existing_data = pd.read_sql_table(table_name, engine)
    merge_key = 'correo_electronico' if table_name == 'personas' else 'id_persona'
    # Comprobación de duplicados
    df_new = df[~df[merge_key].isin(existing_data[merge_key])]
    if not df_new.empty:
        df_new.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Inserted new data into {table_name}.")
    else:
        print(f"No new data to insert into {table_name}.")

data = pd.read_excel("assets/Data/Registro Conferencia de WiDS Guayaquil@ESPOL 2024 (respuestas).xlsx", engine="openpyxl")
data = data.drop_duplicates(subset='Correo electrónico:', keep='first')
data['id_persona'] = np.arange(len(data))
df = formatDf(data)


estudiantes = df[df['ocupacion'] == 'Estudiante'][['nombre', 'apellido', 'telefono_movil', 'correo_electronico', 'carrera', 'universidad']]
profesionales = df[df['ocupacion'] == 'Profesional'][['nombre', 'apellido', 'telefono_movil', 'correo_electronico', 'organizacion', 'trabajo']]


check_and_insert(df[['nombre', 'apellido', 'telefono_movil', 'ocupacion', 'correo_electronico']], 'personas')

df_ids = pd.read_sql("SELECT id_persona, correo_electronico FROM personas", con=engine)

estudiantes = estudiantes.merge(df_ids, on='correo_electronico')
profesionales = profesionales.merge(df_ids, on='correo_electronico')

check_and_insert(estudiantes[['id_persona', 'carrera', 'universidad']], 'estudiantes')
check_and_insert(profesionales[['id_persona', 'organizacion', 'trabajo']], 'profesionales')

navbar = html.Div([
    html.Div([
        html.Img(src='/assets/images/Logo_wids2024.png', className='logo')
        ],className='w1_2'),
    html.Div([
        html.H1("DASHBOARD ASSISTANCE",className="text-responsive"),
        html.H1("WiDS ESPOL 2025",className="text-responsive")
    ],className='w1_2 col_center')
],className="navbar pagdding_navbar border-b-green")
app.layout = html.Div([
    navbar
],className='body all')


# Leer Data
df = pd.read_sql("""
SELECT 
    P.id_persona, 
    P.nombre, 
    P.apellido,
    P.telefono_movil, 
    P.correo_electronico, 
    P.ocupacion,
    E.carrera,
    E.universidad,
    Pr.organizacion,
    Pr.trabajo,
    P.asistencia,
    P.comida
FROM personas P
LEFT JOIN estudiantes E ON P.id_persona = E.id_persona
LEFT JOIN profesionales Pr ON P.id_persona = Pr.id_persona
    """, con=engine)

def get_Registros():
    df=pd.read_sql('''       
                   SELECT * FROM historial
                   ''',con=engine)
    return df

def get_df():
    df = pd.read_sql("""    
SELECT 
    P.id_persona, 
    P.nombre, 
    P.apellido,
    P.telefono_movil, 
    P.correo_electronico, 
    P.ocupacion,
    E.carrera,
    E.universidad,
    Pr.organizacion,
    Pr.trabajo,
    P.asistencia,
    P.comida
FROM personas P
LEFT JOIN estudiantes E ON P.id_persona = E.id_persona
LEFT JOIN profesionales Pr ON P.id_persona = Pr.id_persona
    """, con=engine)
    return df


def dagAgGrid():
    df = pd.read_sql("""
        SELECT 
            P.id_persona, 
            P.nombre, 
            P.apellido,
            P.telefono_movil, 
            P.correo_electronico, 
            P.ocupacion,
            E.carrera,
            E.universidad,
            Pr.organizacion,
            Pr.trabajo,
            P.asistencia,
            P.comida
        FROM personas P
        LEFT JOIN estudiantes E ON P.id_persona = E.id_persona
        LEFT JOIN profesionales Pr ON P.id_persona = Pr.id_persona
            """, con=engine)
    
    return dag.AgGrid(
        id='quickstart-grid',
        rowData=df.to_dict("records"),
        columnDefs=[{"field": i, "sortable": True, "filter": True, "resizable": True} for i in df.columns],
        defaultColDef={"sortable": True, "resizable": True, "filter": True},
        dashGridOptions={"rowSelection": "single"},
        style={'height': '300px', 'width': '100%'}
    )


def dagAgGrid_df(df):
    return dag.AgGrid(
        id='quickstart-grid',
        rowData=df.to_dict("records"),
        columnDefs=[{"field": i, "sortable": True, "filter": True, "resizable": True} for i in df.columns],
        defaultColDef={"sortable": True, "resizable": True, "filter": True},
        dashGridOptions={"rowSelection": "single"},
        style={'height': '300px', 'width': '100%'}
    )

cantDatos=0
varBoolean=False

grid_table = html.Div([
     dcc.Interval(
        id='interval-component',
        interval=5000,  
        n_intervals=0
    ),html.Div([
        dagAgGrid()
        ],id="div_table")
    ],className="div_table")

@app.callback(
    Output('quickstart-grid', 'rowData',allow_duplicate=True),
    Input('interval-component', 'n_intervals'),prevent_initial_call=True)
def update_table(n): 
    global cantDatos,varBoolean
    df=get_df()
    df_regis=get_Registros()
    rowData=df.to_dict('records')
    rowData_re = df_regis.to_dict("records")
    if n==0 or cantDatos==len(df_regis) or varBoolean :
        cantDatos=len(rowData_re)
        return
    cantDatos=len(rowData_re)
    return rowData

div_filtrar = html.Div([
    html.Div([
        dcc.Dropdown(['nombre', 'apellido', 'telefono_movil', 'correo_electronico', 'carrera', 'universidad'],id="type_filter",value="nombre",className="drodown_style"),
    ],className="dropdown"),
    dcc.Input(
            id="input_filter",
            type="text",
            placeholder="Search",
            className="input_filter"
        )
],className="row_filtrar")  

@app.callback(
    Output("div_table", "children", allow_duplicate=True), 
    [Input("type_filter", "value"),Input("input_filter","value")],
    prevent_initial_call='initial_duplicate',
)
def  filterTable(type,input):
    global varBoolean
    varBoolean=False
    table = dagAgGrid()
    df = get_df()
    if type and input:
        filter = df[type].astype(str).str.lower().str.contains(input.lower())
        filtered_df = df[filter]
        table = dagAgGrid_df(filtered_df)
        varBoolean=True
    return table


form = dbc.Container([
    html.Div([
        html.H2("Información del Usuario", className="mb-4 mt-4"),
    ],className="Info_Usuario"),
    dbc.Form([
        dbc.Row([
            dbc.Col([
                dbc.Label("Nombre", html_for="nombre", className="form-label"),
                dbc.Input(type="text", id="nombre", placeholder="Ingrese su nombre",className="height50")
            ], width=6),
            dbc.Col([
                dbc.Label("Apellido", html_for="apellido", className="form-label"),
                dbc.Input(type="text", id="apellido", placeholder="Ingrese su apellido",className="height50")
            ], width=6)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Teléfono Móvil", html_for="telefono_movil", className="form-label"),
                dbc.Input(type="text", id="telefono_movil", placeholder="Ingrese su teléfono móvil",className="height50")
            ], width=6),
            dbc.Col([
                dbc.Label("Correo Electrónico", html_for="correo_electronico", className="form-label"),
                dbc.Input(type="email", id="correo_electronico", placeholder="Ingrese su correo electrónico",className="height50")
            ], width=6)
        ], className="mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Ocupación", html_for="ocupacion", className="form-label"),
                dcc.Dropdown(['Estudiante','Profesional'],value=None,id="dropdown_ocupacion")
            ], width=6),
            dbc.Col([
                html.Div([
                    dbc.Label("Asistencia"),
                    daq.BooleanSwitch(id='asistencia', on=False),
                ],className="div_col"),
                html.Div([
                    dbc.Label("Comida"),
                    daq.BooleanSwitch(id='comida', on=False),
                ],className="div_col")
            ],width=6,className="col_row")
        ], className="mb-3"),
        dbc.Row([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Carrera", html_for="carrera", className="form-label"),
                    dbc.Input(type="text", id="carrera", placeholder="Ingrese su carrera",className="height50")
                ], width=6,style={'display': 'none'},id="d_carrera"),
                dbc.Col([
                    dbc.Label("Universidad", html_for="universidad", className="form-label"),
                    dbc.Input(type="text", id="universidad", placeholder="Ingrese su universidad",className="height50")
                ], width=6,style={'display': 'none'},id="d_universidad")
            ], className="mb-3",id="estudiante"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Organización", html_for="organizacion", className="form-label"),
                    dbc.Input(type="text", id="organizacion", placeholder="Ingrese su organizacion",className="height50")
                ], width=6,style={'display': 'none'},id="d_organizacion"),
                dbc.Col([
                    dbc.Label("Trabajo", html_for="trabajo", className="form-label"),
                    dbc.Input(type="text", id="trabajo", placeholder="Ingrese su trabajo",className="height50")
                ], width=6,style={'display': 'none'},id="d_trabajo")
            ], className="mb-3 info_row",id="profesional")
        ], className="mb-3"),
        html.Div([
            dbc.Button("Enviar Actualización", color="primary", className="mt-2", id="submit_button",size="lg"),
            dbc.Button("Eliminar Registro", color="primary", className="mt-2", id="eliminar_registro",size="lg"),
            dbc.Button("Limpiar Campos", color="primary", className="mt-2", id="limpiar_campos",size="lg")
        ],className="mb-3 row_button")

    ]),
], fluid=True, className="py-3")


@app.callback(
    [
        Output('d_carrera', 'style'),
        Output('d_universidad', 'style'),
        Output('d_organizacion', 'style'),
        Output('d_trabajo', 'style')
    ],
    [Input("dropdown_ocupacion", "value")]
)
def toggle_field_visibility(ocupacion):
    if ocupacion == "Estudiante":
        return [{'display': 'block'}, {'display': 'block'}, {'display': 'none'}, {'display': 'none'}]
    elif ocupacion == "Profesional":
        return [{'display': 'none'}, {'display': 'none'}, {'display': 'block'}, {'display': 'block'}]
    return [{'display': 'none'}, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}]


@app.callback(
    [
        Output('nombre', 'value',allow_duplicate=True),
        Output('apellido', 'value',allow_duplicate=True),
        Output('telefono_movil', 'value',allow_duplicate=True),
        Output('correo_electronico', 'value',allow_duplicate=True),
        Output('dropdown_ocupacion', 'value',allow_duplicate=True),
        Output('asistencia', 'on',allow_duplicate=True),
        Output('comida', 'on',allow_duplicate=True),
        Output('carrera', 'value',allow_duplicate=True),
        Output('universidad', 'value',allow_duplicate=True),
        Output('organizacion', 'value',allow_duplicate=True),
        Output('trabajo', 'value',allow_duplicate=True),
        Output("toast-container", "children",allow_duplicate=True),
        Output("div_table", "children", allow_duplicate=True), 
    ],
    [
        Input('quickstart-grid', 'selectedRows'),
        Input("limpiar_campos", "n_clicks"),
        Input("eliminar_registro","n_clicks")]
    ,
    prevent_initial_call='initial_duplicate'
)
def populate_form_from_selection(selected_rows, limpiar_clicks, eliminar_clicks):
    ctx = callback_context
    if not ctx.triggered:
        return no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == "limpiar_campos":
        return ("", "", "", "", "", False, False, "", "", "", "",no_update,no_update)
    elif button_id == "quickstart-grid" and selected_rows:
        row = selected_rows[0]
        asistencia_bool = bool(int(row['asistencia']))
        comida_bool = bool(int(row['comida']))
        lista = [
            row['nombre'],
            row['apellido'],
            row['telefono_movil'],
            row['correo_electronico'],
            row['ocupacion'],
            asistencia_bool,
            comida_bool,
            row['carrera'] if row['ocupacion'] == "Estudiante" else "",
            row['universidad'] if row['ocupacion'] == "Estudiante" else "",
            row['organizacion'] if row['ocupacion'] != "Estudiante" else "",
            row['trabajo'] if row['ocupacion'] != "Estudiante" else ""
        ]
        return lista+[html.Div(),no_update]
    elif button_id == "eliminar_registro" and selected_rows:
        row = selected_rows[0]
        id_persona = row['id_persona']
        try:
            with engine.connect() as conn:
                with conn.begin() as transaction:
                    if row['ocupacion'] == "Estudiante":
                        conn.execute(
                            text("DELETE FROM estudiantes WHERE id_persona = :id_persona"),
                            {'id_persona': id_persona}
                        )
                    elif row['ocupacion'] == "Profesional":
                        conn.execute(
                            text("DELETE FROM profesionales WHERE id_persona = :id_persona"),
                            {'id_persona': id_persona}
                        )
                    conn.execute(
                        text("DELETE FROM personas WHERE id_persona = :id_persona"),
                        {'id_persona': id_persona}
                    )
                toast = dbc.Toast("Registro Eliminado Exitosamente", header="Éxito", is_open=True, dismissable=True, icon="success", duration=3000, style={"position": "fixed", "top": 10, "right": 10, "width": 350})
                return ("", "", "", "", "", False, False, "", "", "", "",toast,dagAgGrid())
        except IntegrityError as e:
            toast = dbc.Toast(
                f"Error: {str(e.orig)}", 
                header="Fracaso",
                is_open=True,
                dismissable=True,
                icon="danger",
                duration=3000, 
                style={"position": "fixed", "top": 10, "right": 10, "width": 350}
            )
            return "", "", "", "", "", False, False, "", "", "", "", no_update, toast

    return no_update


@app.callback(
    [ Output('nombre', 'value'),
    Output('apellido', 'value'),
    Output('telefono_movil', 'value'),
    Output('correo_electronico', 'value'),
    Output('dropdown_ocupacion', 'value'),
    Output('asistencia', 'on'),
    Output('comida', 'on'),
    Output('carrera', 'value'),
    Output('universidad', 'value'),
    Output('organizacion', 'value'),
    Output('trabajo', 'value'),
    Output("div_table", "children"),
    Output("toast-container", "children")],
    Input("submit_button", "n_clicks"),
    [
        State("nombre", "value"),
        State("apellido", "value"),
        State("telefono_movil", "value"),
        State("correo_electronico", "value"),
        State("dropdown_ocupacion", "value"),
        State("asistencia", "on"),
        State("comida", "on"),
        State("carrera", "value"),
        State("universidad", "value"),
        State("organizacion", "value"),
        State("trabajo", "value"),
    ]
)
def insert_or_update_data(n_clicks, nombre, apellido, telefono_movil, correo_electronico, ocupacion, asistencia, comida, carrera, universidad, organizacion, trabajo):
    if n_clicks is None:
        raise PreventUpdate

    asistencia = 1 if asistencia else 0
    comida = 1 if comida else 0

    with engine.connect() as conn:
        transaction = conn.begin()
        try:
            existing_id = conn.execute(
                text("SELECT id_persona FROM personas WHERE correo_electronico = :correo"),
                {'correo': correo_electronico}
            ).scalar()
            existing_id_nombre_apellido = conn.execute(
                text("SELECT id_persona FROM personas WHERE nombre = :nombre and apellido = :apellido"),
                {'nombre': nombre,'apellido':apellido}
            ).scalar()
            if existing_id:
                conn.execute(
                    text("""
                        UPDATE personas SET nombre=:nombre, apellido=:apellido, telefono_movil=:telefono,
                        ocupacion=:ocupacion, asistencia=:asistencia, comida=:comida
                        WHERE correo_electronico=:correo
                    """), {
                        'nombre': nombre, 'apellido': apellido, 'telefono': telefono_movil,
                        'ocupacion': ocupacion, 'asistencia': asistencia, 'comida': comida,
                        'correo': correo_electronico
                    })
                persona_id = existing_id
            elif existing_id_nombre_apellido:
                conn.execute(
                    text("""
                        UPDATE personas SET telefono_movil=:telefono,ocupacion=:ocupacion, correo_electronico=:correo, asistencia=:asistencia, comida=:comida
                        WHERE nombre=:nombre and apellido=:apellido
                    """), {
                        'nombre': nombre, 'apellido': apellido, 'telefono': telefono_movil,
                        'ocupacion': ocupacion, 'asistencia': asistencia, 'comida': comida,
                        'correo': correo_electronico
                    })
                persona_id = existing_id
            else:
                conn.execute(
                    text("""
                        INSERT INTO personas (nombre, apellido, telefono_movil, correo_electronico, ocupacion, asistencia, comida)
                        VALUES (:nombre, :apellido, :telefono, :correo, :ocupacion, :asistencia, :comida)
                    """), {
                        'nombre': nombre, 'apellido': apellido, 'telefono': telefono_movil,
                        'correo': correo_electronico, 'ocupacion': ocupacion, 'asistencia': asistencia, 'comida': comida
                    })
                persona_id = conn.execute(text("SELECT LAST_INSERT_ID()")).scalar()

            if ocupacion == "Estudiante":
                handle_student_data(conn, persona_id, carrera, universidad)
            elif ocupacion== "Profesional":
                handle_professional_data(conn, persona_id, organizacion, trabajo)
            toast = dbc.Toast("Ingreso Exitoso", header="Éxito", is_open=True, dismissable=True, icon="success", duration=3000, style={"position": "fixed", "top": 10, "right": 10, "width": 350})
            transaction.commit()
            return "", "", "", "", "",False,False, "", "", "", "",dagAgGrid(),toast
        except Exception as e:
            toast = dbc.Toast(
                f"Error: {str(e.orig)}", 
                header="Fracaso",
                is_open=True,
                dismissable=True,
                icon="danger",
                duration=3000, 
                style={"position": "fixed", "top": 10, "right": 10, "width": 350}
            )
            transaction.rollback()
            return "", "", "", "", "",False,False, "", "", "", "",dagAgGrid(),toast
        
def handle_student_data(conn, persona_id, carrera, universidad):
    existing_student = conn.execute(
        text("SELECT id_persona FROM estudiantes WHERE id_persona = :persona_id"),
        {'persona_id': persona_id}
    ).fetchone()
    
    if existing_student:
        conn.execute(
            text("UPDATE estudiantes SET carrera = :carrera, universidad = :universidad WHERE id_persona = :persona_id"),
            {'carrera': carrera, 'universidad': universidad, 'persona_id': persona_id}
        )
    else:
        conn.execute(
            text("INSERT INTO estudiantes (id_persona, carrera, universidad) VALUES (:persona_id, :carrera, :universidad)"),
            {'persona_id': persona_id, 'carrera': carrera, 'universidad': universidad}
        )

def handle_professional_data(conn, persona_id, organizacion, trabajo):
    existing_professional = conn.execute(
        text("SELECT id_persona FROM profesionales WHERE id_persona = :persona_id"),
        {'persona_id': persona_id}
    ).fetchone()
    
    if existing_professional:
        conn.execute(
            text("UPDATE profesionales SET organizacion = :organizacion, trabajo = :trabajo WHERE id_persona = :persona_id"),
            {'organizacion': organizacion, 'trabajo': trabajo, 'persona_id': persona_id}
        )
    else:
        conn.execute(
            text("INSERT INTO profesionales (id_persona, organizacion, trabajo) VALUES (:persona_id, :organizacion, :trabajo)"),
            {'persona_id': persona_id, 'organizacion': organizacion, 'trabajo': trabajo}
        )


body = html.Div([
    div_filtrar,grid_table,form
],className="body")

app.layout = html.Div([
    html.Div(id='toast-container', style={'position': 'fixed', 'top': 0, 'width': '100%', 'z-index': '9999'}),navbar,body
],className="page")


if __name__ == '__main__':
    app.run_server(host='127.0.0.2',port=8020 ,debug=True)