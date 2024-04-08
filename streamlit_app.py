# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie :cup_with_straw:")
st.subheader(
    "Choose the fruits you want in your custom Smoothie!"
)

#
# option = st.selectbox(
#    '**What is your favorite fruit?**',
#    ('Banana', 'Strawberry', 'Peaches'))
#
# st.write('Your favorite fruit is:', option)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

pd_df= my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

name_on_order = st.text_input('Name on Smoothie', 'Name')

ingredient_list = st.multiselect(
    'Choose up to 5 ingredients: ', 
    my_dataframe, 
    max_selections=5
)
ingredient_string = ''

if ingredient_list:
#    st.write(ingredient_list)
#    st.text(ingredient_list)

    ingredient_string = ''

    for fruit_chosen in ingredient_list:
        ingredient_string+= fruit_chosen+' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition info')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+fruit_chosen)
        # st.text(fruityvice_response.json())

        fv_df= st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    st.write(ingredient_string)

if ingredient_string:
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredient_string +  """', '"""+name_on_order+ """')"""

    st.write(my_insert_stmt)

time_to_insert = st.button ('Submit order')
if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
