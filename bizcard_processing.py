import os
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector as sql
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# ------------------------------------STREAMLIT UI SET UP --------------------------------------------#
icon = Image.open("C:/Users/91897/Downloads/ocr_icon.jpeg")
st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR",
                   page_icon=icon,
                   layout="wide",
                   initial_sidebar_state="expanded",
                   menu_items={'About': """BizCardX using easyOCR!"""})
st.markdown("<h1 style='text-align: left; color: blue;'>BizCardX: Extracting Business Card Data with OCR</h1>",
            unsafe_allow_html=True)


# ---------------------------------------BACKGROUND IMAGE SET UP----------------------------------------------------------#
def set_background():
    st.markdown(f""" <style>.stApp {{
                        background: url("https://cdn.pixabay.com/photo/2019/04/24/11/27/flowers-4151900_960_720.jpg");
                        background-size: cover}}
                     </style>""", unsafe_allow_html=True)


set_background()

selected = option_menu(None, ["Upload & Extract", "View and Modify"],
                       icons=["cloud-upload", "pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "20px", "text-align": "centre", "margin": "10px",
                                            "--hover-color": "#6695ED"},
                               "icon": {"font-size": "20px"},
                               "container": {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6675ED"}})

# ------INITIALIZING THE READER CLASS of easyOCR and setting the language to ENGLISH--------------------------------#
reader = easyocr.Reader(['en'])

# -----------------------ESTABLISHING CONNECTION TO THE LOCAL MYSQL DATABASE----------------------------------#
mydb = sql.connect(host="localhost",
                   user="root",
                   password="mp141534",
                   database="biz_db"
                   )
mycursor = mydb.cursor(buffered=True)


# -----------CREATION OF TABLE TO STORE EXTRACTED INFORMATION FROM THE BUSINESS CARD UPLOADED-------------------------#
mycursor.execute('''CREATE TABLE IF NOT EXISTS business_cards_data_tbl
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    company_name TEXT,
                    card_holder TEXT,
                    designation TEXT,
                    mobile_number VARCHAR(50),
                    email TEXT,
                    website TEXT,
                    area TEXT,
                    city TEXT,
                    state TEXT,
                    pin_code VARCHAR(10),
                    image LONGBLOB
                    )''')

# -----------------------UPLOAD OF BUSINESS CARD AND EXTRACTING REQUIRED INFORMATION------------------#

if selected == "Upload & Extract":
    st.markdown("### Upload a Business Card")
    uploaded_card = st.file_uploader("upload here", label_visibility="collapsed", type=["png", "jpeg", "jpg"])

    if uploaded_card is not None:

        def save_card(uploaded_card):
            with open(os.path.join("business_cards_uploads", uploaded_card.name), "wb") as f:
                f.write(uploaded_card.getbuffer())


        save_card(uploaded_card)


        def image_preview(image, res):
            for (bbox, text, prob) in res:
                # unpack the bounding box
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0]), int(tl[1]))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0]), int(br[1]))
                bl = (int(bl[0]), int(bl[1]))
                cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                cv2.putText(image, text, (tl[0], tl[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            plt.rcParams['figure.figsize'] = (15, 15)
            plt.axis('off')
            plt.imshow(image)


        # DISPLAYING THE UPLOADED CARD--------------#
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown("#     ")
            st.markdown("#     ")
            st.markdown("### You have uploaded the card")
            st.image(uploaded_card)

        with col2:
            st.markdown("#     ")
            st.markdown("#     ")
            with st.spinner("Please wait processing image..."):
                st.set_option('deprecation.showPyplotGlobalUse', False)
                saved_img = os.getcwd() + "\\" + "business_cards_uploads" + "\\" + uploaded_card.name
                image = cv2.imread(saved_img)
                res = reader.readtext(saved_img)
                st.markdown("### Image Processed and Data Extracted")
                st.pyplot(image_preview(image, res))

                # easy OCR
        saved_img = os.getcwd() + "\\" + "business_cards_uploads" + "\\" + uploaded_card.name
        result = reader.readtext(saved_img, detail=0, paragraph=False)


        # FUNCTION TO CONVERT THE IMAGE INTO BINARY FORMAT TO BE ABLE TO STORE IN LONGBLOB datatype of MYSQL#
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData

        # DATA DICTIONARY ---> EMPTY-----#
        data = {"company_name": [],
                "card_holder": [],
                "designation": [],
                "mobile_number": [],
                "email": [],
                "website": [],
                "area": [],
                "city": [],
                "state": [],
                "pin_code": [],
                "image": img_to_binary(saved_img)
                }


        def get_data(res):
            for ind, i in enumerate(res):

                if "www " in i.lower() or "www." in i.lower():
                    data["website"].append(i)
                elif "WWW" in i:
                    data["website"] = res[4] + "." + res[5]

                # FINDING emailID
                elif "@" in i:
                    data["email"].append(i)

                # FINDING CONTACT NUMBER
                elif "-" in i:
                    data["mobile_number"].append(i)
                    if len(data["mobile_number"]) == 2:
                        data["mobile_number"] = " & ".join(data["mobile_number"])

                # EXTRACTING COMPANY NAME
                elif ind == len(res) - 1:
                    data["company_name"].append(i)

                # EXTRACTING THE COMPANY HOLDER'S NAME
                elif ind == 0:
                    data["card_holder"].append(i)

                # EXTRACTING DESIGNATION OF THE CARD HOLDER
                elif ind == 1:
                    data["designation"].append(i)

                # EXTRACTING THE LOCATION OR AREA MENTIONED ON THE BUSINESS CARD oOF THE CARDHOLDER#
                if re.findall('^[0-9].+, [a-zA-Z]+', i):
                    data["area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', i):
                    data["area"].append(i)

                # EXTRACTING CITY NAME
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*', i)
                if match1:
                    data["city"].append(match1[0])
                elif match2:
                    data["city"].append(match2[0])
                elif match3:
                    data["city"].append(match3[0])

                # EXTRACTING STATE NAME
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                if state_match:
                    data["state"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                    data["state"].append(i.split()[-1])
                if len(data["state"]) == 2:
                    data["state"].pop(0)

                # EXTRACTING THE PINCODE
                if len(i) >= 6 and i.isdigit():
                    data["pin_code"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                    data["pin_code"].append(i[10:])


        get_data(result)


        # FUNCTION TO CONVERT EXTRACTED DATA INTO A PANDAS'S DATAFRAME
        def create_df(data):
            df = pd.DataFrame(data)
            return df


        df = create_df(data)
        st.success("### Data Extracted!")
        st.write(df)

        if st.button("Upload to Database"):
            for i, row in df.iterrows():
                sql = """INSERT INTO business_cards_data_tbl(company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code,image)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                mycursor.execute(sql, tuple(row))
                mydb.commit()
            st.success("#### Uploaded to database successfully!")

# MODIFICATION  OF THE EXTRACTED INFORMATION
if selected == "View and Modify":
    col1, col2, col3 = st.columns([3, 3, 2])
    col2.markdown("## View and Modify Data")
    column1, column2 = st.columns(2, gap="large")
    try:
        with column1:
            mycursor.execute("SELECT card_holder FROM business_cards_data_tbl")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select a card holder name to update", list(business_cards.keys()))
            st.markdown("#### Update or modify any data below")
            mycursor.execute(
                "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from business_cards_data_tbl WHERE card_holder=%s",
                (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING THE EXTRACTED INFO FROM THE UPLOADED BUSINESS CARD IMAGE
            company_name = st.text_input("Company_Name", result[0])
            card_holder = st.text_input("Card_Holder", result[1])
            designation = st.text_input("Designation", result[2])
            mobile_number = st.text_input("Mobile_Number", result[3])
            email = st.text_input("Email", result[4])
            website = st.text_input("Website", result[5])
            area = st.text_input("Area", result[6])
            city = st.text_input("City", result[7])
            state = st.text_input("State", result[8])
            pin_code = st.text_input("Pin_Code", result[9])

            if st.button("Commit changes to DB"):
                mycursor.execute("""UPDATE business_cards_data_tbl SET company_name=%s,card_holder=%s,designation=%s,mobile_number=%s,email=%s,website=%s,area=%s,city=%s,state=%s,pin_code=%s
                                    WHERE card_holder=%s""", (
                    company_name, card_holder, designation, mobile_number, email, website, area, city, state, pin_code,
                    selected_card))
                mydb.commit()
                st.success("Information updated in database successfully.")

        with column2:
            mycursor.execute("SELECT card_holder FROM business_cards_data_tbl")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            selected_card = st.selectbox("Select card holder name for modification or deletion", list(business_cards.keys()))
            st.write(f"### You have selected :blue[**{selected_card}'s**] card for Modifications!")
            st.write("#### Proceed to delete this card?")

            if st.button("Delete Business Card"):
                mycursor.execute(f"delete from business_cards_data_tbl WHERE card_holder='{selected_card}'")
                mydb.commit()
                st.success("Business card information deleted from database.")
    except:
        st.warning("There is related data in the database")

    if st.button("View updated data"):
        mycursor.execute(
            "select company_name,card_holder,designation,mobile_number,email,website,area,city,state,pin_code from business_cards_data_tbl")
        updated_df = pd.DataFrame(mycursor.fetchall(),
                                  columns=["Company Name", "Name of the Card Holder", "Designation", "Mobile/Contact Details",
                                           "Email Address","Website", "Area", "City", "State", "Pincode"])
        st.write(updated_df)
