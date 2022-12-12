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
  
def insert_row_snowflake(cnx, new_fruit):
  with cnx.cursor() as my_cur:
    sql_cmd = "insert into fruit_load_list values('" + new_fruit + "')"
    #sql_cmd = "delete from fruit_load_list where fruit_name = '" + new_fruit + "'"
    my_cur.execute(sql_cmd)
    return "Thanks for adding " + new_fruit

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

streamlit.write(fruits_to_show['Calories'])

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
  
streamlit.header("View Our Fruit List - Add Your Favorites!")
if streamlit.button('Get Fruit List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  my_data = get_fruit_load_list(my_cnx)
  streamlit.dataframe(my_data)
  my_cnx.close()
 
add_my_fruit = streamlit.text_input('What fruit would you like to add?')
if streamlit.button('Add a Fruit to the List'):
  my_cnx = snowflake.connector.connect(**streamlit.secrets["snowflake"])
  back_from_function = insert_row_snowflake(my_cnx, add_my_fruit)
  streamlit.write(back_from_function)
  my_cnx.close()
  
#streamlit.stop()
