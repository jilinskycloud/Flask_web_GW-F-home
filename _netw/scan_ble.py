import subprocess
import redis

r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True)
r1 = redis.StrictRedis(host='localhost', port=6370, db=1, charset="utf-8", decode_responses=True)

def data_split(data):
  a = data
  a = a.split()
  #print(a)
  mac_ = [3,4,5,6,7,8]
  rssi_ = [9]
  adv_ = [10,11,12,13,14,15,16,17,18]
  uuid_ = [19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34]
  maj_ = [35,36]
  min_ = [37,38]
  tx_ = [39]
  st = ""
  mac = st.join(list(map(a.__getitem__, mac_)))
  rssi = st.join(list(map(a.__getitem__, rssi_)))
  adv = st.join(list(map(a.__getitem__, adv_)))
  uuid = st.join(list(map(a.__getitem__, uuid_)))
  maj = st.join(list(map(a.__getitem__, maj_)))
  mina = st.join(list(map(a.__getitem__, min_)))
  tx = st.join(list(map(a.__getitem__, tx_)))
  received = {'mac':mac, 'rssi':rssi, 'adv':adv, 'uuid':uuid, 'maj':maj, 'mina':mina, 'tx':tx} 
  return received

def verify_mac(v_mac):
    obj = r.scan_iter()
    blk_ble = r.lrange("Black_listed", 0, -1)
    print(blk_ble)
    if v_mac in blk_ble:
      #r.rpush("Black_listed", wht_mac)
      return 1
    else:
      return 0

def insert_r1(data1):
    print("This is R1 data insert Function!--------------------------------------------------------------------------00000000000000000000000000000000000000000000000000")
    r1.hmset(data1['mac'], {'mac':data1['mac'], 'rssi':data1['rssi'], 'adv':data1['adv'], 'uuid':data1['uuid'], 'maj':data1['maj'], 'mina':data1['mina'], 'tx':data1['tx']})
    r1.expire(data1['mac'], 300)
    print(r1.hgetall(data1['mac']))

a=1
while(a != 100):
  proc = subprocess.Popen(["/www/web/_netw/ble_read"], stdout=subprocess.PIPE, shell=True)
  (out, err) = proc.communicate()
  data = out.decode()
  #print(data)
  if len(data) > 0:
    data1 = data_split(data)	
    r.hmset(data1['mac'], {'mac':data1['mac'], 'rssi':data1['rssi'], 'adv':data1['adv'], 'uuid':data1['uuid'], 'maj':data1['maj'], 'mina':data1['mina'], 'tx':data1['tx']})
    r.expire(data1['mac'], 1000)
    print(r.hgetall(data1['mac']))
    v_chk = verify_mac(data1['mac'])
    if v_chk == 1:
      print("White listed mac address")
      insert_r1(data1)
    else:
      print("this is the black listed mac address")



    #print(data1['mac'])
    a=a+1
for key in r.scan_iter():
  print(key)
  if key != 'Black_listed':
    print(r.hgetall(key))
