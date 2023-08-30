# BizCardX_Extracting_using_easyOCR
BizCardX: Extracting Business Card Data with OCR (EXTRACTING and STORING THE BUSINESS CARD INFO IN THE DATABASE(MySQL)
The App : GUI Interface using the Streamlit GUI functionalities and Python and easyOCR, regular Expressions of Python
Allowing the User to upload a Business Card Image in JPG, PNG etc Format.
App extracts Information from the Business Card 
  1) Company Name
  2) Card Holder Name
  3) Designation
  4) Mobile Number
  5) Email Address
  6) Website URL
  7) Area
  8) City
  9) State
  10) Pincode

The user is allowed to View the Extracted information, and if required can make changes to the Extracted Data.
Once the Data is Extracted from the uploaded business card, App allows the user to Commit the Changes/Insert the data in the Database(Mysql)
Option: View & Modify : Allows the User to view the Uploaded data and make changes if necessary and Commit the Changes back to the database.
GUI is designed in a very user friendly Manner, the Buttons naming convention is such that they explain thier functionality themselves.
The whole image is stored a BLOB data type in mysql database in a Table along with the other information like Company Name etc which have been mentioned above as pointers.



