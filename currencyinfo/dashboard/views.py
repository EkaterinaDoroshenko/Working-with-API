import requests
import xml.etree.ElementTree as ET
from django.shortcuts import render
from django.http import HttpResponse
from plotly.graph_objs import Scatter, Figure
from plotly.offline import plot
from plotly.io import write_image
import json
import openpyxl
from openpyxl.drawing.image import Image
import io


def index(request):
    response = requests.get(
        'https://cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/2023&date_req2=31/12/2023&VAL_NM_RQ=R01235')
    root = ET.fromstring(response.content)
    dates = []
    values = []

    for record in root.findall('.//Record'):
        date = record.get('Date')
        dates.append(date)
        value = record.find('Value').text
        values.append(float(value.replace(',', '.')))

    fig = Figure(data=[Scatter(x=dates, y=values, mode='lines', name='Value')])
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    if dates and values:
        return render(request, 'index.html', {'plot_div': plot_div})
    else:
        return render(request, 'index.html', {'error': 'Failed to find records in XML response'})


def generate_excel_report(request):
    # Fetch the data
    response = requests.get(
        'https://cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/2023&date_req2=31/12/2023&VAL_NM_RQ=R01235')
    root = ET.fromstring(response.content)
    dates = []
    values = []

    for record in root.findall('.//Record'):
        date = record.get('Date')
        dates.append(date)
        value = record.find('Value').text
        values.append(float(value.replace(',', '.')))

    fig = Figure(data=[Scatter(x=dates, y=values, mode='lines', name='Value')])
    img_bytes = io.BytesIO()
    write_image(fig, file=img_bytes, format='png')
    img_bytes.seek(0)

    # Create an Excel workbook and sheet using openpyxl
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Load the image into openpyxl
    image = Image(img_bytes)
    image.anchor = 'A1'
    sheet.add_image(image)

    # Save the workbook to a BytesIO object
    virtual_file = io.BytesIO()
    workbook.save(virtual_file)
    virtual_file.seek(0)

    # Create a response object with the appropriate Excel content type
    response = HttpResponse(virtual_file.read(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=exchange_rates.xlsx'
    return response


def home(request):
    response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
    valute = response['Valute']
    nominal = valute['USD']['Nominal']
    value = valute['USD']['Value']
    return render(request, 'home.html', {'response': valute, 'nominal': nominal, 'value': value})

def checkdollar(request):
    if request.method == 'POST':
        min_value = request.POST.get('min')
        max_value = request.POST.get('max')
    else:
        return render(request, 'checkdollar.html', {'error': 'Invalid request method'})

    base_url = 'https://cbr.ru/scripts/XML_dynamic.asp'
    params = {
        'date_req1': f'01/01/{min_value}',
        'date_req2': f'31/12/{max_value}',
        'VAL_NM_RQ': 'R01235'
    }
    response = requests.get(base_url, params=params)
    root = ET.fromstring(response.content)
    dates = []
    values = []

    for record in root.findall('.//Record'):
        date = record.get('Date')
        dates.append(date)
        value = record.find('Value').text
        values.append(float(value.replace(',', '.')))

    fig = Figure(data=[Scatter(x=dates, y=values, mode='lines', name='Value')])
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)

    return render(request, 'chart_fragment.html', {'plot_div': plot_div})
