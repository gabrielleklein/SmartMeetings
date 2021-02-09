from slacktastic.client import SlackClient
from slacktastic.template import (
    Message, PieChart, BarChart, LineChart, RadarChart, RadialGauge,
    OuterPieChart)

client = SlackClient(
    webhook_url='https://hooks.slack.com/services/'
                'TBWAF1BH7/BLTGSMRNK/40X6YJP7czgUX4OgSfGvFlUR')

test_1 = PieChart(
    "Test data", labels=['Ride', 'Reservation'], values=[22, 55])

test_2 = BarChart(
    "Test data", labels=['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    data={
        'Test 1': [1, 2, 4, 8, 16],
        'Test 2': [7, 3, 45, 1, 12],
    }
)

test_3 = LineChart(
    "Test data", labels=['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    data={
        'Test 1': [1, 2, 4, 8, 16],
        'Test 2': [7, 3, 45, 1, 12],
    })

test_4 = RadarChart(
    "Test data", labels=['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    data={
        'Test 1': [1, 2, 4, 8, 16],
        'Test 2': [7, 3, 45, 1, 12],
    })

test_5 = OuterPieChart(
    "Test data",
    labels=[
        'Color 1',
        'Color 2',
        'Color 3',
        'Color 4',
    ],
    values=[
        22,
        55,
        55,
        22,
    ])

test_6 = RadialGauge(
    title='Radial',
    percentage=45.4,
    radial_color='purple',
    color='#4323ab'
)

message = Message(text='This is a *test*', attachments=[
    # test_1,
    # test_2,
    # test_3,
    # test_4,
    # test_5,
    test_6,
])
client.send_message(message)
