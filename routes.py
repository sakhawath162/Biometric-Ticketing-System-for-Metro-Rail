from app import app, db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, User_travel_history
from app.forms import LoginForm, RegistrationForm
from flask import jsonify, render_template, request, flash, redirect, url_for
from pyfingerprint.pyfingerprint import PyFingerprint
import json
from array import *
import glob
import os
import time

@app.route('/')
@app.route('/index_old', methods=['GET', 'POST'])
def index_old():
    try:      
        f = PyFingerprint('COM6', 57600, 0xFFFFFFFF, 0x00000000)
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    try:
        print('Waiting for finger...')

        while ( f.readImage() == False ):
            pass

        f.convertImage(0x01)
        cr = f.downloadCharacteristics(0x01)
        #print(f.downloadCharacteristics(0x01))
 

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)
    a = request.args.get('a', 0, type=int)
    if a == 1 :
        return jsonify(result = "Put your same finger on the sensor again !")
    elif a == 2:
        return jsonify(result = "Completed")    

    return jsonify(result = str(cr))



@app.route('/authenticate', methods=['GET', 'POST'])                                                                                                    
def authenticate():   
                                                                                                                               
    far = [[0,50,100],[20,0,60],[150,40,0]]
    station_names = ['Uttara North', 'Uttara Centre', 'Uttara South','Pallabi','Mirpur 11','Mirpur-10','Kazipara','Shewrapara','Agargaon','Bijoy Sarani','Farmgate','Karwan Bazar','Shahbag','Dhaka University','Bangladesh Secretariat','Motijheel']
    
    data = request.get_json()
    

    try:
        f = PyFingerprint('COM6', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        data = {'s' : 'Exception message: ' + str(e), 'bool_found' : '0'}
        return json.dumps(data)


    try:
        
        data = request.get_json()
        chrr = json.loads(data)
        chr = chrr["tem"]
        c = list()
        for i in range(0, len(chr)): 
            c.append(int(chr[i]))    
        
        
        f.uploadCharacteristics(0x01, chr)
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if ( positionNumber == -1 ):
            #del f
            #f.__del__()
            print("ok1")
            data = {'s' : 'No match found!', 'bool_found' : '0'}
            #f.loadTemplate(0, 0x01)
            #result = f.searchTemplate()
            print("ok2")
            print('No match found!')
            data = {'s' : 'No match found!', 'bool_found' : '0'}
            # exit(0)
        else:
            #f.__del__()
            #del f
            print("first else")
            if(chrr["entry_exit"] == 0 ):
                f.loadTemplate(0, 0x01)
                result = f.searchTemplate()
                f.__del__()
                u = User.query.filter_by(id=positionNumber).first()

                exit_station_number = int(chrr["station_number"])
                exit_station_name = station_names[exit_station_number]
                exit_time = chrr["scaned_time"]
                date = chrr["date"]
                entry_station_name = station_names[u.start_station]

                
                
                db_start_station =int(u.start_station)
                
                try:


                    fa = int(u.money)-far[db_start_station][exit_station_number]
                    u.money = fa
                    print(far)
                    info = User_travel_history(date=str(date),entry_station=entry_station_name,
                                                exit_station=exit_station_name,entry_time = u.entry_time,
                                                fare=str(far[db_start_station][exit_station_number]),exit_time=exit_time,human = u)   
                    db.session.add(info)
                    db.session.commit()
                    #print("hi")
                    print('Found template'  )
                    data = {'s' : 'Found template at position #' + str(positionNumber), 'bool_found' : '1'}
                    # print('The accuracy score is: ' + str(accuracyScore))
                except Exception as e:
                    print('Exception message: ' + str(e))
                    data = {'s' : 'No match found!', 'bool_found' : '0'}


            if(chrr["entry_exit"] == 1 ):
                f.loadTemplate(0, 0x01)
                result = f.searchTemplate()
                f.__del__()
                u = User.query.filter_by(id=positionNumber).first()
                if(u.money > 70):
                    u.start_station = int(chrr["station_number"])
                    u.entry_time = chrr["scaned_time"]
                    db.session.commit()
                    data = {'s' : 'Enough money', 'bool_found' : '1'}
                else:
                    data = {'s' : 'Insufficent balance !', 'bool_found' : '0'}    
  
        #f.loadTemplate(0, 0x01)
        #result = f.searchTemplate()

        #f.__del__()
    

    except Exception as e:
        f.__del__()
        print('Operation failed!')
        print('Exception message: ' + str(e))
        data = {'s' : 'No match found!', 'bool_found' : '0'}

  
    return json.dumps(data)


@app.route('/reg_one', methods=['GET', 'POST'])
def reg_one():
    #return jsonify(result = "its working")
    return render_template('recharge.html')


@app.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')  


@app.route('/first_page')
def first_page():
    return render_template('first_page.html')

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    data = request.get_json()
    print(data)
    chrr = json.loads(data)
    chr = chrr["tem"]
    c = list()
    for i in range(0, len(chr)): 
        c.append(int(chr[i]))

    return jsonify(result = "its working") 


#website user login page 
@app.route('/user/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('test'))
    form = LoginForm()
        
    if form.validate_on_submit():
        user = User.query.filter_by(phonenumber=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('user_index'))   
    return render_template('user_login.html', title='Sign In', form=form)       


#WEBSITE INDEX PAGE
@app.route('/user/user_index')
@login_required
def user_index():
    return render_template('web_home.html') 


#WEBSITE RECHARGE
@app.route('/web_recharge' )
@login_required
def web_recharge():
    return render_template('web_recharge_window.html')


@app.route('/web_home' )
@login_required
def web_home():
    return render_template('web_home.html')


#WEBSITE CURRENT BALANCE PAGE
@app.route('/web_user_balance')
@login_required
def web_user_balance():
    return render_template('web_user_balance.html') 


#WEBSITE TRAVEL HISTORY
@app.route('/web_travel_history')
@login_required
def web_travel_history():
    station_names = ['Uttara North', 'Uttara Centre', 'Uttara South','Pallabi','Mirpur 11','Mirpur-10','Kazipara','Shewrapara','Agargaon','Bijoy Sarani','Farmgate','Karwan Bazar','Shahbag','Dhaka University','Bangladesh Secretariat','Motijheel']
    items = current_user.rel.all()
    return render_template('web_travel_history.html', items=items, station_names=station_names) 

#WEBSITE LOGOUT
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    a = request.args.get('a', 0, type=int)
    try:      
        f = PyFingerprint('COM6', 57600, 0xFFFFFFFF, 0x00000000)
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        del f
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        #exit(1)

    try:
        if a == 1:
            print('Waiting for finger...')       
            while ( f.readImage() == False ):
                pass
        
            f.convertImage(0x01)
            result = f.searchTemplate()
            positionNumber = result[0]

            if ( positionNumber >= 0 ):
                print('Template already exists at position #' + str(positionNumber))
                return jsonify(result = '1')
                #return render_template('recharge.html')
                #exit(0)
            return jsonify(result = "Put your same finger on the sensor again !")    
        if a == 2:
            print('Remove finger...')
            #time.sleep(2)

            print('Waiting for same finger again...')

            ## Wait that finger is read again
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 2
            f.convertImage(0x02)

            ## Compares the charbuffers
            if ( f.compareCharacteristics() == 0 ):
                raise Exception('Fingers do not match')

            ## Creates a template
            f.createTemplate()

            ## Saves template at new position number
            positionNumber = f.storeTemplate()
            print('Finger enrolled successfully!')
            print('New template position #' + str(positionNumber))
            return jsonify(result = "Completed", id = str(positionNumber) ) 
 

    except Exception as e:
        del f
        #f.__del__()
        print('Operation failed!')
        print('Exception message: ' + str(e))
        #exit(1)
    
    if a == 1: 
        return jsonify(result = "Put your same finger on the sensor again !")
    elif a == 2:
        return jsonify(result = "Completed")    

    return jsonify(result = str(cr))





#registration page after successful fingerprint registration
@app.route('/register/<id>', methods=['GET', 'POST'])
def register(id):
    #if current_user.is_authenticated:
       # return redirect(url_for('index'))
    try:      
        f = PyFingerprint('COM6', 57600, 0xFFFFFFFF, 0x00000000)
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        f.__del__()
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1) 

    positionNumber = int(id)
    f.loadTemplate(positionNumber, 0x01)
    temm = f.downloadCharacteristics(0x01)
    tem = str(temm)

    form = RegistrationForm()
    if form.validate_on_submit():
        print("working")
        user = User(id=positionNumber, phonenumber=form.phonenumber.data, name=form.name.data, email=form.email.data, template=tem, money=0)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return render_template('booth_login_first.html')
    else:
        print(form.errors)    
    return render_template('register.html', title='Register', form=form)
    


#booth login page
@app.route('/booth_login' )
def booth_login():
    return render_template('booth_login_first.html')

#booth login auth
@app.route('/finger_login', methods=['GET', 'POST'])
def finger_login():
    try:      
        f = PyFingerprint('COM6', 57600, 0xFFFFFFFF, 0x00000000)
        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        del f
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        return jsonify(result='-1')
    try:
        print('Waiting for finger...')

        ## Wait that finger is read
        while ( f.readImage() == False ):
            pass

        ## Converts read image to characteristics and stores it in charbuffer 1
        f.convertImage(0x01)

        ## Searchs template
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]
        #del f
        f.__del__()
        if ( positionNumber == -1 ):
            
            print('No match found!')
            return jsonify(result='-1')
            
        else:
            
            print('Found template at position #' + str(positionNumber))
            return jsonify(result=positionNumber)
            
    except Exception as e:
        
        
        print('Operation failed!')
        print('Exception message: ' + str(e))
        return jsonify(result='-1')       
            

#booth recharge window after successful login
@app.route('/booth_recharge_window/<id>')
def booth_recharge_window(id):
    user_id = int(id)
    user = User.query.filter_by(id=user_id).first()
    return render_template('booth_recharge_window.html', user=user)




# PAYMENT TESTING
@app.route('/payment/<amount>/<id>', methods=['GET', 'POST'])                                                                                                    
def payment(amount, id):    
    a = request.args.get('a')
    b = request.args.get('b')
    phonenumber = str(a)+'.'
    trxid = str(b)                                                                                                                          
    path1 ="/Users/Administrator/Downloads"
    path2 ="/Users/Administrator/Desktop/metro_backend/app/static/data"
    os.chdir(path1)
    f_name = max(glob.glob('*.json'),key=os.path.getctime)

    with open(f_name ) as f:
        data = json.load(f)


    
    segments = data[1].split()
    


    os.chdir(path2)

    with open('data.json') as json_file: 
        data = json.load(json_file)

    #print(phonenumber)  
    #print(data[phonenumber])
    if phonenumber in data:
        print("ok")
        l = data[phonenumber]  
        index = 0
        for m in l:
            print("for loop  db trx " + l[index]["TrxId"]+ "given trx " +  trxid)
            if (l[index]["TrxId"] == trxid):
                return jsonify(result ="This Transction ID has already been used !")
            index = index + 1    
        if (int(amount) == int(float(segments[4])) and trxid == segments[14]):    
              
            user = User.query.filter_by(id=int(id)).first()
            old_balance = int(user.money)
            new_balance = old_balance + int(amount)
            user.money = new_balance
            db.session.commit()     
            data[phonenumber].append(({"TrxId" : segments[14], "Amount" : segments[4], "Date" : segments[16]}))
    else:
        if (int(amount) == int(float(segments[4])) and trxid == segments[14]):
            user = User.query.filter_by(id=int(id)).first()
            old_balance = int(user.money)
            new_balance = old_balance + int(amount)
            user.money = new_balance
            db.session.commit()   
            data[segments[6]]= [{"TrxId" : segments[14], "Amount" : segments[4], "Date" : segments[16]}] 
        else:
            return jsonify(result = "Invalid Transction ID. Enter carefully phonenumber and transction id")    
        

    with open('data.json','w') as f: 
        json.dump(data, f, indent=4)
    time.sleep(2)    
    return jsonify(result = "SUCCESSFULL! Account refilled "+ amount + " Tk")
 
# PAYMENT TESTING
@app.route('/payment_front_end/<amount>/<id>')                                                                                                    
def payment_front_end(amount,id):                                                                                                                              
    #Sdata = request.get_json()
    #print(data)
    
    return render_template("bkash.html",amount=amount,id=id)
 
