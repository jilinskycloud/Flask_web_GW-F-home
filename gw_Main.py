
#!/usr/bin/python3
from flask import Flask
from flask import escape
from flask import url_for
from flask import request
from flask import render_template
#from flask import abort
from flask import redirect
from flask import session
#from flask import flash
from flask import jsonify
#from flask_mysqldb import MySQL
import psutil
import time
#from _include.dbClasses import mysqldb as _mysql
import json
import sqlite3
import os

import redis 
import subprocess                                           
                                                       
r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#mysql = _mysql.initMysql_(MySQL, app)


conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
print("Opened database successfully");
'''
conn.execute('CREATE TABLE login (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)')
print("Table created successfully");
# Insert Data to Login table
conn.execute("INSERT INTO login (username,password) VALUES (?,?)",('admin', 'pass123') )
conn.commit()
msg = "Record successfully added"
'''
conn.close()

#rec = conn.execute("SELECT * FROM login WHERE username=? and password=?", ('admin', 'pass123'))
'''
for row in conn.execute("SELECT * FROM login WHERE username=? and password=?", ('admin', 'pass123')):
	print(row)
'''
#print(rec.fetchall())

'''
print("here is the curser....")
cur = conn.execute("SELECT * FROM students")
rows = cur.fetchall(); 
print(rows)
uname = ('admin',)
cur = conn.execute('SELECT * FROM students WHERE username=?', uname)
rows = cur.fetchone()
print("where clause")
print(type(rows))
'''
@app.route('/getcmd', methods=['GET', 'POST'])
def getcmd():
	if request.method == 'POST':
		print("Get Command Function.......")
		input_json = request.get_json(force=True)
		os.system(input_json)
	dictToReturn = {'answer':42}
	return jsonify(dictToReturn)


@app.route('/reboot')
def reboot():
	print("System Reboot Function......")
	os.system("reboot")
	return "Device Going to Reboot! To Access web page Pleage Refresh Page After 2 minutes..."

# ===================MYSQL FUNCTIONS==========================

@app.route('/delProfile/<ids>')
def delProfile(ids=None):
	conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
	f = conn.execute("DELETE FROM login where id=?", (ids))
	conn.commit()
	conn.close()
	print("Delete Login User Function......")
	return redirect(url_for('settings'))

#=============================================================
#=====================WEB-PAGE FUNCTIONS======================
#=============================================================

# ============================================================INDEX
@app.route('/')
@app.route('/index/')
@app.route('/index')
def index():
	if 'username' in session:
		print("Index Page Function......")
		return redirect(url_for('dashboard'))
	return redirect(url_for('login'))

# ============================================================DASHBOARD
@app.route('/dashboard')
@app.route('/dashboard/')
def dashboard():
	if 'username' in session:
		print("Dashboard Page Function......")
		u_name = escape(session['username'])
		print(session.get('device1'))
		#while(1):
		data = {}
		data['cpu'] = psutil.cpu_percent()
		data['stats'] = psutil.cpu_stats()
		data['cpu_freq'] = psutil.cpu_freq()
		data['cpu_load'] = psutil.getloadavg()
		data['ttl_memo'] = psutil.virtual_memory()
		data['swp_memo'] = psutil.swap_memory()
		data['hostname'] =cm("hostname")
		data['routeM'] = 'TC0981'
		data['FirmV'] = 'v3.0.11_sniffer_TainCloud_r864'
		data['lTime'] = cm('date')
		data['runTime'] = cm('uptime')
		data['network'] = cm('ifconfig')
		data['mount'] = psutil.disk_partitions(all=False)
		data['disk_io_count'] = psutil.disk_io_counters(perdisk=False, nowrap=True)
		data['net_io_count'] = psutil.net_io_counters(pernic=False, nowrap=True)
		data['nic_addr'] = psutil.net_if_addrs()
		data['tmp'] = psutil.sensors_temperatures(fahrenheit=False)
		data['boot_time'] = psutil.boot_time()
		data['c_user'] = psutil.users()
		data['reload'] = time.time()
		return render_template('dashboard.html', data=data)
		#return 'Logged in as %s' % escape(session['username'])
	else:
		return redirect(url_for('login'))

@app.route('/devices')
def devices():
	if 'username' in session:
		print("Dashboard Page Function......")
		obj = r.scan_iter()
		blk_ble = r.lrange("Black_listed", 0, -1)
		#for key in r.scan_iter():                                                                                                                              
			#print(key)      
			#data = r.hgetall(key)                                                                                                                                     
			#print(type(data))   
		return render_template('devices.html', data=obj, r_obj=r, blk_ble=blk_ble)
	else:
		return redirect(url_for('login'))

def cm(dt):
	print("Inner CMD Function......Dashboard Page")
	klog = subprocess.Popen(dt, shell=True, stdout=subprocess.PIPE).stdout
	klog1 =  klog.read()
	pc = klog1.decode()
	return pc
# ============================================================MQTT-CONSOLE
@app.route('/console-logs')
@app.route('/console-logs/')
def mqtt_on():
    if 'username' in session:
        print("Console Logs Function......")
        klog = subprocess.Popen("dmesg", shell=True, stdout=subprocess.PIPE).stdout
        klog1 =  klog.read()
        pc = klog1.decode()
        #print(klog)
        return render_template('console-logs.html', data=pc)
    else:
        return redirect(url_for('login'))


# =============================================================BLE CONNECT

@app.route('/network', methods=['GET', 'POST'])
def network():
	if 'username' in session:
		print("Network Page Function......")
		if request.method == 'POST':
			#print("000000000000000000000000000000000000000000000000000000000000000000000000")
			#print(request.form.to_dict())
			if request.form['sniffer_type'] == 'IBeacon':
				print("Its Beacon---------------")
				result = request.form.to_dict()
				print(result)
				with open("/www/web/_netw/conf/ble_conf.text", "w") as f:
					json.dump(result, f, indent=4)
			elif request.form['sniffer_type'] == 'Wifi':
				print("Its Wifi---------------")
				result = request.form.to_dict()
				print(result)
				with open("/www/web/_netw/conf/wifi_conf.text", "w") as f:
					json.dump(result, f, indent=4)
			else:
				print("form data error")
			print("restart hb!")
			print(os.system("cat /var/run/heartbeat.pid"))
			pi = open("/var/run/heartbeat.pid", 'r')
			pid_ = pi.read()
			pi.close()
			#print(pid_)
			os.system('kill -s 10 ' + pid_)
			print("restart ble_post_________________________________________________")
			#if os.path.exists("/var/run/ble_post.pid") == 'True':
			#	print(os.system("cat /var/run/ble_post.pid"))
			if 'a' == 'a':
				pi1 = open("/var/run/ble_post.pid", 'r')
				pid_1 = pi1.read()
				print("this is the post pid fffff")
				print(pid_1)
				pi1.close()
				os.system('kill -s 10 ' + pid_1)
			else:
				 proc = subprocess.Popen(["python3 /www/web/_netw/_httplib.py"], stdout=subprocess.PIPE, shell=True)
				 print(proc)



		d1 = json.load(open('/www/web/_netw/conf/ble_conf.text','r'))
		d2 = json.load(open('/www/web/_netw/conf/wifi_conf.text','r'))

		return render_template('network.html', d1=d1, d2=d2)
	else:
		return redirect(url_for('login'))

		
@app.route('/blk_list', methods=['GET', 'POST'])
def blk_list():
	if 'username' in session:
		if request.method == 'POST':
			print("blacklisted Bacons Page!")
			blk_mac = request.form['blacklisted']
			r.rpush("Black_listed", blk_mac)
		return redirect(url_for('devices'))
	else:
		return redirect(url_for('login'))

@app.route('/white_list_get/<wht_mac>')
def white_list_get(wht_mac=None):
	if 'username' in session:
		print("blacklisted Bacons Page!")
		print(wht_mac)
		obj = r.scan_iter()
		blk_ble = r.lrange("Black_listed", 0, -1)
		print(blk_ble)
		if not wht_mac in blk_ble:
				r.rpush("Black_listed", wht_mac)
		return redirect(url_for('devices'))
	else:
		return redirect(url_for('login'))

@app.route('/blk_del/<blk_del_mac>')
def blk_del(blk_del_mac=None):
	if 'username' in session:
		r.lrem("Black_listed", -1, blk_del_mac)
		return redirect(url_for('devices'))
	else:
		return redirect(url_for('login'))






# =============================================================Settings
@app.route('/settings/', methods=['GET', 'POST'])
def settings():
	error = None
	data = []
	rec=[]
	if 'username' in session:
		if request.method == 'POST':
			print("Posted********************************************")
			data.append(request.form['name'])
			data.append(request.form['pass'])
			print(data)
			#print(_mysql.editProfile_(mysql, data))
			conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
			conn.execute("INSERT INTO login (username,password) VALUES (?,?)",(data[0], data[1]) )
			conn.commit()
			conn.close()
			msg = "Record successfully added"
		

		conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
		f = conn.execute("SELECT * FROM login")
		rec = f.fetchall()
		print(rec)
		conn.close()
		print(rec)
		return render_template('settings.html', error=error, data=data, rec=rec)
	else:
		return redirect(url_for('login'))

# ============================================================SCAN BLE PAGE
@app.route('/scan_ble')
def scan_ble():
	os.system("python3 /www/web/_netw/scan_ble.py")
	return redirect(url_for('devices')) 



# ============================================================LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	#print(_mysql.initLogin_(mysql))
	if request.method == 'POST':
		u_name = request.form['username']
		u_pass = request.form['password']
		flag = 0
		conn = sqlite3.connect('/www/web/gw_FlaskDb.db')
		f = conn.execute("SELECT * FROM login WHERE username=? and password=?", (u_name, u_pass))
		print(f)
		v = f.fetchall()
		if(len(v) > 0):
			flag = 0
		else:
			flag = -1
		print(v)
		conn.close()
		if(flag == -1):
			error = 'Invalid Credentials. Please try again.'
		else:
			session['username'] = request.form['username']
			return redirect(url_for('index'))
	return render_template('login.html', error=error)

# ============================================================LOGOUT PAGE
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


if  __name__  ==  '__main__' : 
    app.run(host = '0.0.0.0',  port = 5000) #, debug = True) #, threaded = True, ssl_context='adhoc') #Ssl_context = Context ,