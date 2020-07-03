from flask import Flask,render_template,request,redirect,session,url_for,flash

from datetime import date
import credential as cr
from datetime import datetime
import pandas as pd
import numpy as np
import pickle
import sys
from feature_extraction import generate_url_dataset
import mysql.connector
#------------------------------------------------------------------
mydb=mysql.connector.connect(user=cr.user, password=cr.password,
                              host=cr.host)
mycursor=mydb.cursor()

mycursor.execute("USE PhishingDatabase")
# mycursor.execute("CREATE TABLE PhisingTable(SNo int PRIMARY KEY AUTO_INCREMENT, website varchar(10000), Date date )")
# mycursor.execute(r"show tables")
# for i in mycursor:
#     print(i)

file_in=open("R-F-model.pkl",'rb')
model=pickle.load(file_in)


app=Flask(__name__)
app.secret_key= cr.secretKey
import flask_login
import flask
import datetime
today=date.today()
print(type(today))
@app.before_request
def before_request():
    flask.session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=1)
    flask.session.modified = True
    flask.g.user = flask_login.current_user



@app.route('/')
def home():
    return render_template("main.html")

@app.route('/Aboutus')
def aboutus():
    return render_template("aboutus.html")





@app.route('/Admin',methods=["POST","GET"])
def admin():
    # if request.method=="GET":
    #     return render_template("admin.html")
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        
        query="select * from admin where email ='" + email + "' and password= '" + password + "';"
        mycursor.execute(query)
        
        result= mycursor.fetchall()
        
        if result:  
            session.permanent=True
            session['user_id']=email
          
            return redirect(url_for("adminAccount"))

        else:
            return render_template("admin.html")

    if request.method=="GET":
        if 'user_id' in session:
            return redirect(url_for("adminAccount"))
        return render_template("admin.html")




@app.route('/AdminAccount')
def adminAccount():
    query="select email,date from feedback"
    mycursor.execute(query)
    result=mycursor.fetchall()

    return render_template("adminAccount.html",Result=result,email=session['user_id'])

 
@app.route('/logout')  
def logout():  
    if 'user_id' in session:  
        session.pop('user_id',None)  
        return render_template('admin.html');  
    else:  
        return '<p>user already logged out</p>'


@app.route('/Faq')
def faq():
    return render_template("faq.html")



@app.route('/Feedback',methods=["POST","GET"])
def sendfeedback():
    if request.method=="GET":      
        return render_template("feedback.html")
    values=request.form.values()
    valuesList=[]
    for i in values:
            valuesList.append(i)
            print(i)
        
    try:
        
        query="INSERT INTO Feedback VALUES(%s,%s,%s,%s)"
        val=(valuesList[0],valuesList[1],today,valuesList[2])
        
        mycursor.execute(query,val)
        mydb.commit()
        flash("Thanks for giving your valuable feedback.")
        return render_template("feedback.html")
    except Exception as e:  
        print(e)
        try:
            sql = "UPDATE feedback SET feedback = %s,rating= %s,date=%s WHERE email = %s"
            val=(valuesList[1],valuesList[2],today,valuesList[0] )
            mycursor.execute(sql,val)
            mydb.commit()
            flash("Thanks for updating your feedback")
        except:
            flash(" Submission failed. Please fill all fields.")
            
        return render_template("feedback.html")





@app.route('/main.html',methods=["POST"])
def getvalue(): 
    website =  request.form['website_name']
    url_feature=generate_url_dataset(website)
    url_feature=np.array(url_feature).reshape(1,-1)
    print(website)
    print(url_feature)
    mycursor.execute('''select * from phisingtable where website='%s' '''%website)
    result=mycursor.fetchall()
    
    if result:
        result=f"{website} is Phishing website."
    else:    
        prediction= model.predict(url_feature)
        if(prediction[0]==-1):
            try:      
                Today=date.today() 
                statement="INSERT INTO phisingtable(website,Date) VALUES(%s,%s)"
                val=(website,Today)
                mycursor.execute(statement,val)
                mydb.commit()
            except Exception as e:
                print(e)
                home()
                
            result=f"{website} is Phishing website."            
        else:
            result=f"{website} is Legitimate website."

    return render_template("main.html",Results=result,)



@app.route('/adminAccount/viewFeedback')
def viewFeedback():
    try:
        query="select * from feedback"
        mycursor.execute(query)
        result=mycursor.fetchall()
        return render_template("viewFeedback.html",Feedbacks=result)

    except:
        return render_template("adminAccount.html")

    
@app.route('/adminAccount/blocklist')
def blockList():
    try:
        query="select * from phisingtable"
        mycursor.execute(query)
        result=mycursor.fetchall()
        return render_template("blocklist.html",websites=result)

    except:
        return render_template("adminAccount.html")

@app.route('/adminAccount/blocklist/done',methods=["POST"])
def changeBlocklist():
    add_website=request.form['website']
    try:     
        today=date.today() 
        statement="INSERT INTO phisingtable(website,Date) VALUES(%s,%s)"
        val=(add_website,today)
        mycursor.execute(statement,val)
        mydb.commit()
        flash("Website added successfully",category="insert")
        return redirect(url_for('blockList'))
    except Exception as e:
        print(e)
        flash("The Website is already present.")
        return redirect(url_for('blockList'))

@app.route('/adminAccount/blocklist/removed',methods=["POST"])
def RemoveWebsite():
    webList=request.form.getlist('webcheckbox')
    print(webList)
    # try:  
    for web in webList:      
        print(web)
        val='test'
        statement=""
        mycursor.execute("DELETE FROM phisingtable where website = '" + web + "' ;")
        flash("Successfully Removed",category="remove")
    mydb.commit()
    return redirect(url_for('blockList'))
    # except Exception as e:
    #     print(e)
    #     return redirect(url_for('blockList'))

app.run(debug=True)    