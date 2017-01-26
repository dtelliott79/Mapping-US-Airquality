import sqlite3
import pandas
import numpy
import urllib
import json
import plotly.plotly as py

# Read in Air Quality data
conn = sqlite3.connect('airqual.sqlite3')
df = pandas.read_sql_query('''SELECT Airquality.id, Airquality.Airquality, 
                           Measure.units, Measure.measure, State.state, 
                           County.county, Year.year FROM Airquality 
                           JOIN Measure JOIN State JOIN County JOIN Year 
                           ON Airquality.Measure_ID = Measure.id AND 
                           Airquality.State_ID = State.id AND 
                           Airquality.County_ID = County.id AND 
                           Airquality.Year_ID = Year.id;''', conn)
                      
# Read in county border data. May not be accurate in some cases 
# (for example, IL and MI counties extend into great lakes). 
# Check and replace with better coordinates data once found.
url = 'https://bubinga.co/wp-content/uploads/jsoncounties.min_.js'
response = urllib.urlopen(url)
counties = json.load(response)
#with open('US_counties.geojson') as f:
#    counties = json.load(f)

# Select one (or average all) year(s) of Air Quality data & seperate measures
df = df.groupby(['measure', 'state', 'county'], as_index=False).mean()

# Abbreviate df states to match GEOJSON states
us_state_abbrev = {'Alabama': 'AL','Alaska': 'AK','Arizona': 'AZ','Arkansas': 'AR',
'California': 'CA','Colorado': 'CO','Connecticut': 'CT','Delaware': 'DE',
'Florida': 'FL','Georgia': 'GA','Hawaii': 'HI','Idaho': 'ID','Illinois': 'IL',
'Indiana': 'IN','Iowa': 'IA','Kansas': 'KS','Kentucky': 'KY','Louisiana': 'LA',
'Maine': 'ME','Maryland': 'MD','Massachusetts': 'MA','Michigan': 'MI',
'Minnesota': 'MN','Mississippi': 'MS','Missouri': 'MO','Montana': 'MT',
'Nebraska': 'NE','Nevada': 'NV','New Hampshire': 'NH','New Jersey': 'NJ',
'New Mexico': 'NM','New York': 'NY','North Carolina': 'NC','North Dakota': 'ND',
'Ohio': 'OH','Oklahoma': 'OK','Oregon': 'OR','Pennsylvania': 'PA',
'Rhode Island': 'RI','South Carolina': 'SC','South Dakota': 'SD','Tennessee': 'TN',
'Texas': 'TX','Utah': 'UT','Vermont': 'VT','Virginia': 'VA','Washington': 'WA',
'West Virginia': 'WV','Wisconsin': 'WI','Wyoming': 'WY','District of Columbia': 'DC',
'District of Columbia': 'DC',}

df = df.replace({"state": us_state_abbrev})

# Add state, county, and geom to geo_dict
geo_dict = {}

for x in range(len(counties['features'])):
    state = counties['features'][x]['properties']['state']
    for y in range(len(counties['features'][x]['counties'])):
        county = counties['features'][x]['counties'][y]['name']
        geom = counties['features'][x]['counties'][y]['geometry']
        if state in df['state'].unique():
            if county in df['county'].unique():
                county = county+', '+state
                geo_dict[county] = geom
            else:
                county = county+', '+state
                #print 'not in: ', county
        else:
            #print 'not in: ', state
            continue

del(counties)

# Convert geo_dict into a Pandas series
ser = pandas.Series(geo_dict.values(), index = geo_dict.keys())
ser.name = 'coordinates'
del(geo_dict)

# Join the geodata series to the means_df
df["county"] = df["county"] + ', ' + df["state"]
df = df.join(ser, on='county')
del(ser)

# Set and assign color scale for each measure type
colors = ['#ffffe0','#fffddb','#fffad7','#fff7d1','#fff5cd','#fff2c8',
          '#fff0c4','#ffedbf','#ffebba','#ffe9b7','#ffe5b2','#ffe3af',
          '#ffe0ab','#ffdda7','#ffdba4','#ffd9a0','#ffd69c','#ffd399',
          '#ffd196','#ffcd93','#ffca90','#ffc88d','#ffc58a','#ffc288',
          '#ffbf86','#ffbd83','#ffb981','#ffb67f','#ffb47d','#ffb17b',
          '#ffad79','#ffaa77','#ffa775','#ffa474','#ffa172','#ff9e70',
          '#ff9b6f','#ff986e','#ff956c','#fe916b','#fe8f6a','#fd8b69',
          '#fc8868','#fb8567','#fa8266','#f98065','#f87d64','#f77a63',
          '#f67862','#f57562','#f37261','#f37060','#f16c5f','#f0695e',
          '#ee665d','#ed645c','#ec615b','#ea5e5b','#e85b59','#e75859',
          '#e55658','#e45356','#e35056','#e14d54','#df4a53','#dd4852',
          '#db4551','#d9434f','#d8404e','#d53d4d','#d43b4b','#d2384a',
          '#cf3548','#cd3346','#cc3045','#ca2e43','#c72b42','#c52940',
          '#c2263d','#c0233c','#be213a','#bb1e37','#ba1c35','#b71933',
          '#b41731','#b2152e','#b0122c','#ac1029','#aa0e27','#a70b24',
          '#a40921','#a2071f','#a0051c','#9d0419','#990215','#970212',
          '#94010e','#91000a','#8e0006','#8b0000', '#8b0000']

scl = dict(zip(range(0, 101), colors))

df["color"] = numpy.round((100 * df["Airquality"]/
   df.groupby("measure")["Airquality"].transform(max)),0)

df = df.replace({"color": scl})



# Seperate data frames for each measure type
while True:
    print 'Map:'
    print '(1) Average PM2.5'
    print '(2) Days Ozone Concentration Above Standard'
    print '(3) % Days Pm2.5 Above Standard'
    select = raw_input('Please enter number for selection: ')
    try: select = float(select)
    except:
        print 'Invalid selection'
        continue
    if select != 3.0 and select != 2.0 and select != 1.0:
        print 'Invalid selection'
        continue
    else: break

select = int(select-1)
df = df.loc[df['measure'] == df['measure'].unique()[select]]
df = df[['county','Airquality','coordinates','color']]
df = df.reset_index()
    
# Begin plot development in Plotly
mapbox_access_token = #Insert your own here

layers_ls = []
for x in df.index:
    item_dict = dict(sourcetype = 'geojson',
                     source = df.ix[x]['coordinates'],
                     type = 'fill',
                     color = df.ix[x]['color'])
    layers_ls.append(item_dict)

colorscl = [[i * .01, v] for i,v in enumerate(colors)]

import plotly.graph_objs as go

data = go.Data([
            go.Scattermapbox(
                            lat = [0],
                            lon = [0],
                            marker = go.Marker(
                                               cmax=df['Airquality'].max(),
                                               cmin=df['Airquality'].min(),
                                               colorscale = colorscl,
                                               showscale = True,
                                               autocolorscale=False,
                                               color=range(0,101),
                                               colorbar= go.ColorBar(
                                                                     len = .89
                                                                     )
                                               ),
                            mode = 'markers')
])
                                               
descr = ['Average Annual (1999-2013) PM2.5 concentration (ug/m^3)',
'Year-days ozone concentration above National Standard (NAAQS)',
'% of days PM2.5 above National Standard (NAAQS)']
title = descr[select]
                                               
layout = go.Layout(
    title = title,
    height=1050,
    width=800,
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        layers= layers_ls,
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=38.03,
            lon=-95.7
        ),
        pitch=0,
        zoom=2.7,#5.5,
        style='light'
    ),
)
        
fig = dict(data = data, layout=layout)
py.image.save_as(fig, filename='3.jpeg',
                 width = 750, height= 575)