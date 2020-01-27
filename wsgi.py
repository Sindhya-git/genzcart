from flask import Flask, render_template, json, request, session, redirect
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from flask import jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from ibm_watson import SpeechToTextV1
import ibm_boto3
from ibm_botocore.client import Config, ClientError
import os

#Initialize flask
application = Flask(__name__)
# 
socketio = SocketIO(application)
CORS(application)
# Config MySQL
mysql = MySQL()
application.config['MYSQL_HOST']  = "custom-mysql.gamification.svc.cluster.local"
application.config['MYSQL_USER']  = "xxuser"
application.config['MYSQL_PASSWORD'] = "welcome1"
application.config['MYSQL_DB']    = "sampledb"
application.config['MYSQL_PORT']  = int('3306')
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#Intialize fields for IBM COS access
COS_ENDPOINT = "https://s3.us-south.cloud-object-storage.appdomain.cloud" # Current list avaiable at https://control.cloud-object-storage.cloud.ibm.com/v2/endpoints
COS_API_KEY_ID = "_bAzHuCAN1yPz4Rcg5CZY1Tbp0UOpshuMhpoNkIvJAa3" # eg "W00YiRnLW4a3fTjMB-odB-2ySfTrFBIQQWanc--P3byk"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/oidc/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/693fe8ead49b44b192004113d21b15c2:fce26086-5b77-42cc-b1aa-d388aa2853d7::" # eg "crn:v1:bluemix:public:cloud-object-storage:global:a/3bf0d9003abfb5d29761c3e97696b71c:d6f04d83-6c4f-4a62-a165-696756d63903::"

ibm_boto3.set_stream_logger('')

# Create resource
cos = ibm_boto3.resource(service_name='s3',
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    ibm_auth_endpoint=COS_AUTH_ENDPOINT,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)
bucket_name = 'gamification-cos-standard-tkq'

def get_bucket_contents(bucket_name,item_no):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        print("in try",)
        #files = cos.Bucket(bucket_name).objects.all()
        #print("files :",files)
               
        #for file in files:
         #  print("in for",)
         #  print("Item: {0} ({1} bytes).".format(file.key, file.size))
        #item_id = '1002'
        f = item_no + '.jpg'
        isr = cos.Object(bucket_name, f).get()
        imgjpg = isr['Body'].read()
        print("read")
        return imgjpg, {'Content-Type': 'image/jpg'}
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))
        
class my_dictionary(dict): 
  
    # __init__ function 
    def __init__(self): 
        self = dict() 
          
    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value 


# Initialize the app for use with this MySQL class
mysql.init_app(application)


@application.route("/")
def home_page():
  if 'view' in request.args:
    item_number= request.args['view']
    print ("item number is :", item_number)
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER and s.ITEM_NUMBER=%s LIMIT 1", (item_number,))
    product1 = cur2.fetchall()
    print("product1 is :",product1)
    return render_template('product_detail.html', prdtdetail=product1)
  else:
    print("inside home page",)  
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER LIMIT 25")
    shirts = cur1.fetchall()
 # Close Connection
    cur1.close()
    return render_template('home.html', shirts=shirts)
  
@application.route("/home")
def ghome_page():
  return render_template('home.html')

@application.route('/api/speech-to-text', methods=['POST'])
def getTextFromSpeech():
  print ("in speech to text",)

    # initialize speech to text service
  authenticator = IAMAuthenticator('N0-hVj524g0o23sRDYesTJN4DPbZyBffx5ziKMOpOecL')
  speech_to_text = SpeechToTextV1(authenticator=authenticator)


  response = sttService.recognize(
            audio=request.get_data(cache=False),
            content_type='audio/wav',
            timestamps=True,
            word_confidence=True,
            smart_formatting=True).get_result()
  
  # Ask user to repeat if STT can't transcribe the speech
  if len(response['results']) < 1:
    return Response(mimetype='plain/text',response="Sorry, didn't get that. please try again!")

    text_output = response['results'][0]['alternatives'][0]['transcript']
    text_output = text_output.strip()
    print ("response of speech is :",text_output)
    return Response(response=text_output, mimetype='plain/text')
  
@application.route("/women", methods=['POST', 'GET'])
def womens_page():
  print ("in womens page",)
  
  chkbox_val = request.form.getlist('chkw')
  print ("chkbox_val1 is :", chkbox_val)
  chklist = []
  
  if request.method == "POST":
    print ("in post ",)
    chkbox_val = request.form.getlist('chkw')
    print ("chkbox_val is :", chkbox_val)
    
    if (chkbox_val.count('small') > 0 ):
      chklist.append('small')
      chklist.append('Small-Black')
      chklist.append('Small-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('medium') > 0 ):
      chklist.append('Medium')
      chklist.append('Medium-Black')
      chklist.append('Medium-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('large') > 0 ):
      chklist.append('Large')
      chklist.append('Large-Black')
      chklist.append('Large-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('XL') > 0 ):
      chklist.append('XL')
      chklist.append('Xlarge')
      chklist.append('XLarge-Black')
      chklist.append('XLarge-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('XXLarge') > 0 ):
      chklist.append('XXLarge')
      chklist.append('XXLarge-Wine Red')
      chklist.append('XXLarge-Black')
      chklist.append('XXLarge-Dark Green')
      print ("chklist is :", chklist)
      
    
    curwc = mysql.connection.cursor()
    query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT"
    query2 = " FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER"
    query3 = " AND s.SKU_ATTRIBUTE_VALUE1 IN %s AND s.DESCRIPTION LIKE %s"
    curwcquery = query1 + query2 + query3 
    print("curcquery is:",curwcquery) 
    curwc.execute(curwcquery, (chklist,'%Women%'))
    wcolsize = curwc.fetchall()
    print("wcollection is :",wcolsize)
 # Close Connection
    curwc.close()
    return render_template('Womens.html', womcol=wcolsize,cbow=chkbox_val)
  
  if 'view' in request.args:
    bname = request.args['view']
    print ("brand name is :", bname)
    if bname == 'Reflex':
      bname = 'Reflex Women'
    curbw = mysql.connection.cursor()
    query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT"
    query2 = " FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER"
    query3 = " AND s.DESCRIPTION LIKE %s"
    curbwquery = query1 + query2 + query3 
    print("curbwquery is:",curbwquery)
    curbw.execute(curbwquery,('%' + bname + '%',)) 
    bwcollection = curbw.fetchall()
    print("bwcollection is :",bwcollection)
    bwimg_dict = my_dictionary()
    for row in bwcollection:
      print("s.ITEM_NUMBER :" ,row['ITEM_NUMBER'])
      imgdat=get_bucket_contents(bucket_name,row['ITEM_NUMBER'])
      #imgdata = imgdat +'.jpg'
      #bwimg_dict.add(row['ITEM_NUMBER'] ,imgdata)
      bwcollection.add('IMAGE_KEY' ,imgdat)
 # Close Connection
    curbw.close()
    return render_template('Bwomens.html', bwomencol=bwcollection,imgdata1=bwimg_dict)
  else:
    curw = mysql.connection.cursor()
    query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT"
    query2 = " FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER"
    query3 = " AND s.DESCRIPTION LIKE '%Women%'"
    curwquery = query1 + query2 + query3 
    print("curwquery is:",curwquery)
    curw.execute(curwquery) 
    wcollection = curw.fetchall()
 # Close Connection
    curw.close()
    return render_template('Womens.html', womcol=wcollection)
                 
@application.route("/men", methods=['POST', 'GET'])
def mens_page():
  print ("in mens page",)
  chkbox_val = request.form.getlist('check')
  print ("chkbox_val1 is :", chkbox_val)
  chklist = []
  
  if request.method == "POST":
    print ("in post ",)
    chkbox_val = request.form.getlist('check')
    print ("chkbox_val is :", chkbox_val)
    if (chkbox_val.count('38') > 0 ):
      chklist.append('38 Long')
      chklist.append('38 Short')
      print ("chklist is :", chklist)
    if (chkbox_val.count('40') > 0 ):
      chklist.append('40 Long')
      chklist.append('40 Regular')
      print ("chklist is :", chklist)
    if (chkbox_val.count('50') > 0 ):
      chklist.append('50 Long')
      print ("chklist is :", chklist)
    if (chkbox_val.count('small') > 0 ):
      chklist.append('small')
      chklist.append('Small-Black')
      chklist.append('Small-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('medium') > 0 ):
      chklist.append('Medium')
      chklist.append('Medium-Black')
      chklist.append('Medium-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('large') > 0 ):
      chklist.append('Large')
      chklist.append('Large-Black')
      chklist.append('Large-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('XL') > 0 ):
      chklist.append('XL')
      chklist.append('Xlarge')
      chklist.append('XLarge-Black')
      chklist.append('XLarge-Dark Green')
      print ("chklist is :", chklist)
    if (chkbox_val.count('XXLarge') > 0 ):
      chklist.append('XXLarge')
      chklist.append('XXLarge-Wine Red')
      chklist.append('XXLarge-Black')
      chklist.append('XXLarge-Dark Green')
      print ("chklist is :", chklist)
      
    
    curc = mysql.connection.cursor()
    query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT"
    query2 = " FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER"
    query3 = " AND s.SKU_ATTRIBUTE_VALUE1 IN %s AND s.DESCRIPTION NOT LIKE %s"
    curcquery = query1 + query2 + query3 
    print("curcquery is:",curcquery) 
    curc.execute(curcquery, (chklist,'%Women%'))
    mcolsize = curc.fetchall()
    print("mcollection is :",mcolsize)
 # Close Connection
    curc.close()
    return render_template('Mens.html', mencol=mcolsize,cbox=chkbox_val)
    
  
  if 'view' in request.args:
    bname = request.args['view']
    print ("brand name is :", bname)
    if bname == 'Reflex':
      bname = 'Reflex Men'
    curbm = mysql.connection.cursor()
    query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT"
    query2 = " FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER"
    query3 = " AND s.DESCRIPTION LIKE %s"
    curbmquery = query1 + query2 + query3 
    print("curbmquery is:",curbmquery)
    curbm.execute(curbmquery,('%' + bname + '%',)) 
    bmcollection = curbm.fetchall()
    print("bmcollection is :",bmcollection)
 # Close Connection
    curbm.close()
    return render_template('Bmens.html', bmencol=bmcollection)
  else:
    curm = mysql.connection.cursor()
    query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT"
    query2 = " FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER"
    query3 = " AND s.DESCRIPTION not LIKE '%Women%'"
    curmquery = query1 + query2 + query3 
    print("curmquery is:",curmquery)
    curm.execute(curmquery) 
    mcollection = curm.fetchall()
    print("mcollection is :",mcollection)
 # Close Connection
    curm.close()
    return render_template('Mens.html', mencol=mcollection)


    
@application.route("/boys")
def boys_page():
  print ("in boys page",)
  curb = mysql.connection.cursor()
  curbquery = "SELECT FAMILY_NAME,CLASS_NAME,COMMODITY,COMMODITY_NAME FROM XXIBM_PRODUCT_CATALOGUE WHERE COMMODITY_NAME LIKE '%Boys%' "
  curb.execute(curbquery) 
  bcollection = curb.fetchall()
  print("bcollection is :",bcollection)
 # Close Connection
  curb.close()
  return render_template('Boys.html', boyscol=bcollection)

@application.route("/girls")
def girls_page():
  print ("in girls page",)
  curg = mysql.connection.cursor()
  curgquery = "SELECT FAMILY_NAME,CLASS_NAME,COMMODITY,COMMODITY_NAME FROM XXIBM_PRODUCT_CATALOGUE WHERE COMMODITY_NAME LIKE '%girl%' "
  curg.execute(curgquery) 
  gcollection = curg.fetchall()
  print("gcollection is :",gcollection)
 # Close Connection
  curg.close()
  return render_template('Girls.html', girlscol=gcollection)
  

@application.route('/search', methods=['POST', 'GET'])
def search():
    if 'q' in request.args:
        q = request.args['q']
        print ("q is :",q)
        productsrch = ' '
        # Create cursor
        cur3 = mysql.connection.cursor()
   # Get the row count in cur3.rowcount
        qs = q.split()
        qx = q.replace(' ','%')
        qr = qx.replace("womens","women")
        if 'men' in qx and 'wo' not in qx:
          qy = qx.replace("men"," men")
          qr = qy.replace("mens","men")
        
        print("qs is:",qs)
        print("type :",type(qs))
        print("qr is:",qr)
        commo_id = []
        #for j in qs:
        #  print ("j is :," j)
        query_string = "SELECT * FROM XXIBM_PRODUCT_CATALOGUE WHERE COMMODITY_NAME LIKE %s ORDER BY COMMODITY ASC"
        cur3.execute(query_string, ('%' + qr + '%',))
        commosrch1 = cur3.fetchall()
        print("cur3 is :",cur3.rowcount)
        cur3.execute(query_string, ('%' + qr + '%',))
        commosrch = cur3.fetchone()
          
   # Collect all the commodity in dict by looping thru the cursor    
        for i in range(0,cur3.rowcount):
          print ("commo1 is:", commosrch['COMMODITY'])
          commo_id.append(commosrch['COMMODITY'])          
          commosrch = cur3.fetchone()
          
        print("commo_id is :", str(commo_id))
        cur3.close()
        productsrch = ' '
        if commo_id:
          cur4 = mysql.connection.cursor()
          commo_dict = ','.join((str(n) for n in commo_id))
          print ("commo2 is:", commo_dict)
          query = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER and s.CATALOGUE_CATEGORY IN (%s)" % commo_dict
          #if 'men' in qr and 'wo' not in qr:
          #  print("women in qr:",)
          #  query = query + " AND s.DESCRIPTION not LIKE '%Women%'"
            
          cur4.execute(query)
          productsrch = cur4.fetchall()
          print("productsrch1 is :",productsrch)
          cur4.close()
          cur5 = mysql.connection.cursor()
          query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.DESCRIPTION,' ',s.LONG_DESCRIPTION,' ',s.SKU_ATTRIBUTE_VALUE1,' ',s.SKU_ATTRIBUTE_VALUE2) LIKE (%s)"
          query2 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.DESCRIPTION,' ',s.LONG_DESCRIPTION,' ',s.SKU_ATTRIBUTE_VALUE2,' ',s.SKU_ATTRIBUTE_VALUE1) LIKE (%s)"
          query3 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.SKU_ATTRIBUTE_VALUE1,' ',s.SKU_ATTRIBUTE_VALUE2,' ',s.DESCRIPTION,' ',s.LONG_DESCRIPTION) LIKE (%s)"
          query4 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.SKU_ATTRIBUTE_VALUE2,' ',s.SKU_ATTRIBUTE_VALUE1,' ',s.DESCRIPTION,' ',s.LONG_DESCRIPTION) LIKE (%s)"
          #if 'men' in qr and 'wo' not in qr:
          #  print("men in qr:",)
          #  query1 = query1 + " AND s.DESCRIPTION not LIKE '%Women%'"
          #  query2 = query2 + " AND s.DESCRIPTION not LIKE '%Women%'"
          #  query3 = query3 + " AND s.DESCRIPTION not LIKE '%Women%'"
          #  query4 = query4 + " AND s.DESCRIPTION not LIKE '%Women%'"
            
          cur5.execute(query1,('%' + qr + '%',))
          productsrch5 = cur5.fetchall()
          print("prdtsrch5 :",productsrch5)
          if productsrch5:
            print("prod 51 has values",)
          else:
            productsrch5 = " "
            cur5.execute(query2,('%' + qr + '%',))
            productsrch5 = cur5.fetchall()
            print("prdtsrch52 :",productsrch5)
            if productsrch5:
              print("prod 52 has values",)
            else:
              productsrch5 = " "
              cur5.execute(query3,('%' + qr + '%',))
              productsrch5 = cur5.fetchall()
              print("prdtsrch53 :",productsrch5)
              if productsrch5:
                print("prod 53 has values",)
              else:
                productsrch5 = " "
                cur5.execute(query4,('%' + qr + '%',))
                productsrch5 = cur5.fetchall()
                print("prdtsrch54 :",productsrch5)
          
            
          productsrch = productsrch + productsrch5 
          print("prod srh is ",productsrch) 
          cur5.close()
          print("cur4 count :",cur4.rowcount )
          print("cur5 count :",cur5.rowcount)
          if cur4.rowcount == 0:
            if cur5.rowcount == 0:
              product_srch = ' '
              print("here 1",)
              if cur3.rowcount == 0:
                commosrch1 = " "
                print("here 2",)
                return render_template('search.html', product_srch1=commosrch1)
              else:
                print("here 3",)
                return render_template('search.html', product_srch1=commosrch1)
            else:
              print("here 4",)
              return render_template('search.html', product_srch=productsrch)
          else:
            print("here 5",)
            return render_template('search.html', product_srch=productsrch)
        else:
          cur4 = mysql.connection.cursor()
          print("in cur4",)
          query1 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.DESCRIPTION,' ',s.LONG_DESCRIPTION,' ',s.SKU_ATTRIBUTE_VALUE1,' ',s.SKU_ATTRIBUTE_VALUE2) LIKE (%s)"
          query2 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.DESCRIPTION,' ',s.LONG_DESCRIPTION,' ',s.SKU_ATTRIBUTE_VALUE2,' ',s.SKU_ATTRIBUTE_VALUE1) LIKE (%s)"
          query3 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.SKU_ATTRIBUTE_VALUE1,' ',s.SKU_ATTRIBUTE_VALUE2,' ',s.DESCRIPTION,' ',s.LONG_DESCRIPTION) LIKE (%s)"
          query4 = "SELECT s.ITEM_NUMBER, s.DESCRIPTION,s.LONG_DESCRIPTION, s.SKU_ATTRIBUTE_VALUE1,s.SKU_ATTRIBUTE_VALUE2,p.LIST_PRICE,p.DISCOUNT FROM XXIBM_PRODUCT_SKU s INNER JOIN XXIBM_PRODUCT_PRICING p WHERE s.ITEM_NUMBER=p.ITEM_NUMBER AND CONCAT(s.SKU_ATTRIBUTE_VALUE2,' ',s.SKU_ATTRIBUTE_VALUE1,' ',s.DESCRIPTION,' ',s.LONG_DESCRIPTION) LIKE (%s)"
          #if 'men' in qr and 'wo' not in qr:
          #  print("men in qr:",)
          #  query1 = query1 + " AND s.DESCRIPTION not LIKE '%Women%'"
          #  query2 = query2 + " AND s.DESCRIPTION not LIKE '%Women%'"
          #  query3 = query3 + " AND s.DESCRIPTION not LIKE '%Women%'"
          #  query4 = query4 + " AND s.DESCRIPTION not LIKE '%Women%'"
          
            
          cur4.execute(query1,('%' + qr + '%',))
          productsrch = cur4.fetchall()
          print("productsrch2 is :",productsrch)
          
          if productsrch:
            print("prod 1 has values",)
          else:
            productsrch = " "
            cur4.execute(query2,('%' + qr + '%',))
            productsrch = cur4.fetchall()
            print("prdtsrch 2 :",productsrch)
            if productsrch:
              print("prod 2 has values",)
            else:
              productsrch = " "
              cur4.execute(query3,('%' + qr + '%',))
              productsrch = cur4.fetchall()
              print("prdtsrch 3 :",productsrch)
              if productsrch:
                print("prod 3 has values",)
              else:
                productsrch = " "
                cur4.execute(query4,('%' + qr + '%',))
                productsrch = cur4.fetchall()
                print("prdtsrch 4 :",productsrch)
          cur4.close()
          if cur4.rowcount == 0:
            productsrch = ' '
            return render_template('search.html', product_srch=productsrch)  
          else:
            return render_template('search.html', product_srch=productsrch)  

port = os.environ.get("PORT") or os.environ.get("VCAP_APP_PORT") or 5000    
if __name__ == "__main__":
    socketio.run(application)
