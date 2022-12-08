import streamlit
import pandas
import requests
import snowflake.connector
from urllib.error import URLError

def get_fruityvice_data(this_fruit_choice):
  fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
  fruityvice_normalized = pandas.json_normalize(fruityvice_response.json())
  return fruityvice_normalized

def get_fruit_load_list(cnx):
  with cnx.cursor() as my_cur:
    my_cur.execute("select * from fruit_load_list")
    return my_cur.fetchall()

streamlit.title('My Parents New Healthy Diner')
streamlit.header('Breakfast Menu')
streamlit.text('🥣 Omega 3 & Blueberry Oatmeal')
streamlit.text('🥗 Kale, Spinach & Rocket Smoothie')
streamlit.text('🐔 Hard-Boiled Free-Range Egg')
streamlit.text('🥑🍞 Avocado Toast')
streamlit.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

my_fruit_list = pandas.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit') # Changing the index from int to Fruit column

# Let's put a pick list here so they can pick the fruit they want to include 
fruits_selected = streamlit.multiselect("Pick some fruits:", list(my_fruit_list.index), ['Orange','Strawberries'])
fruits_to_show = my_fruit_list.loc[fruits_selected]

# Distplay the tables on the page
streamlit.dataframe(fruits_to_show)

streamlit.header("Fruityvice Fruit Advice!")
try:
  fruit_choice = streamlit.text_input('What fruit would you like information about?')
  if not fruit_choice:
    streamlit.error('Please select a fruit to get information.')
  else:
    back_from_function = get_fruityvice_data(fruit_choice)
    if back_from_function.columns[0] != 'error':
      back_from_function = back_from_function.set_index('name') # Changing the index from int to Fruit column
      # printing the dataframe
      streamlit.dataframe(back_from_function)
    else:
      error_message = fruit_choice + ' - ' + back_from_function.loc[0]['error']
      streamlit.error(error_message)
except URLError as e:
  stremlit.error()

streamlit.header("The fruit load list contains:")
if streamlit.buttom('Get Fruit Load List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data = get_fruit_load_list(my_cnx)
  streamlit.dataframe(my_data)

streamlit.stop()
  
add_my_fruit = streamlit.text_input('What fruit would you like to add?','jackfruit')
streamlit.write('Thanks for adding', add_my_fruit)

sql_comm = "insert into fruit_load_list values('" + add_my_fruit + "')"
streamlit.write(sql_comm)
my_cur.execute(sql_comm)
