#NEw branch

#test git

import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dcc import Store
from dash.dependencies import Input, Output
from dash_extensions.enrich import Dash, ServersideOutput, Output, Input, Trigger
import Dash_demo_Read_Data

# df = pd.read_excel("D:\\Sample.xlsx")
# df=pd.DataFrame()
# print(df.head())
PAGE_SIZE = 10
# Proj = df['PROJ']

app = dash.Dash()
# global df, dff
# df=pd.DataFrame()
# Proj = []
# Emp = []
# def data_in():
#     df = pd.read_excel("D:\\Sample.xlsx")
#     Proj = df.PROJ.unique()
#     Emp = df.Emp.unique()
#     print(df)
# data_in()
def serve_layout():
    # data_in()
    df = Dash_demo_Read_Data.DataPrep()
    # df = pd.read_excel("D:\\Sample.xlsx")
    df = df.reset_index().rename(columns={'Project_Name': 'PROJ', 'Employee_ID': 'Emp'})

    # df['PROJ'] = df['Project_Name']
    # df['Emp'] = df['Employee_ID']

    Proj = df.PROJ.unique()
    Emp = df.Emp.unique()

    # For Emp Dropdown
    lEmp = []
    lEmp = [{'label': i, 'value': i} for i in Emp]
    dEmpAll = {'label': 'All Emp', 'value': 'All Emp'}
    lEmp.append(dEmpAll.copy())

    # For Proj Dropdown
    lproj = []
    lproj = [{'label': i, 'value': i} for i in Proj]
    dprojAll = {'label': 'All Proj', 'value': 'All Proj'}
    lproj.append(dprojAll.copy())

    # Proj = df.PROJ.unique()
    # Emp = df.Emp.unique()
    # store = Store(id = "mystore", data = df.to_json()) # The store must be added to the layout

    return html.Div([
        html.Div([]),
        html.Br(),
        html.Div(children=[
    # dcc.Input(value='', id='filter-input', placeholder='Filter', debounce=True),
    dcc.Dropdown(
        id='PROJ_DD',
        options=lproj,
        value='All Proj',
        multi=True
    ),
    dcc.Dropdown(
        id='Emp_DD',
        options= lEmp,
        value='All Emp',
        # value=Emp[0],
        multi=True
    ),
    dcc.Store(id='Dataframe',
              data= df.to_json(orient='split'))]),
            # data= df.to_json(orient='split'))], style = dict(display='flex')),
    html.Br(),
    # dcc.Dropdown(
    #     id='Skill_DD',
    #     options=[{'label': i, 'value': i} for i in Skill],
    #     value='All Skill',
    #     multi=True
    # ),

    dash_table.DataTable(
        id='datatable-paging',
        columns=[
            {"name": i, "id": i} for i in df.columns  # sorted(df.columns)
        ],
        page_current=0,
        page_size=PAGE_SIZE,
        page_action='custom',

        sort_action='custom',
        sort_mode='single',
        sort_by=[]
    )


])

app.layout = serve_layout

@app.callback(
    Output('datatable-paging', 'data'),
    [Input('datatable-paging', 'page_current'),
     Input('datatable-paging', 'page_size'),
     Input('datatable-paging', 'sort_by'),
     Input('PROJ_DD', 'value'),
     Input('Emp_DD', 'value'),
     Input('Dataframe','data')
     # Input('Skill_DD', 'value')
     ])
def update_table(page_current, page_size, sort_by, filter_Proj, filter_Emp, dataframe):
    df=pd.read_json(dataframe,orient='split')

    if type(filter_Proj) == str:
        filter_Proj = [filter_Proj]
    if type(filter_Emp) == str:
        filter_Emp = [filter_Emp]


    if 'All Proj' in filter_Proj:
        dfprj = df.copy()
    else:
        dfprj = df[df['PROJ'].isin(filter_Proj)]

    if 'All Emp' in filter_Emp:
        dfEmp = df.copy()
    else:
        dfEmp = df[df['Emp'].isin(filter_Emp)]

    dff = pd.concat([dfprj, dfEmp], ignore_index=True)

    # Add one Elif for new Dropdown
    if 'All Proj' in filter_Proj:
        dff = pd.concat([dfprj[dfprj['Emp'].isin(filter_Emp)], dfEmp], ignore_index=True).drop_duplicates()
    elif 'All Emp' in filter_Emp:
        dff = pd.concat([dfprj, dfEmp[dfEmp['PROJ'].isin(filter_Proj)]], ignore_index=True).drop_duplicates()
    else:
        dff = dff[(dff['PROJ'].isin(filter_Proj)) & (dff['Emp'].isin(filter_Emp))].drop_duplicates()


    if len(sort_by):
        dff = dff.sort_values(
            sort_by[0]['column_id'],
            ascending=sort_by[0]['direction'] == 'asc',
            inplace=False
        )
    return dff.iloc[
           page_current * page_size:(page_current + 1) * page_size
           ].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)

