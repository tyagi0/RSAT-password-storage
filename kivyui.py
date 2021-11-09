from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from db import Database



class CreateAccountWindow(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)

    def submit(self):
        if self.username.text != "" and self.username.text != "@" and self.username.text != "=":
            if self.password != "":
                result = db.checkuserexists(self.username.text)

                if result == False:
                    db.storeuserdetails(self.username.text, self.password.text)
                    db.storekeyvalues()
                    self.reset()

                    sm.current = "login"

                else:
                    invalidExists()
            else:
                invalidForm()
        else:
            invalidForm()

    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.password.text = ""
        self.username.text = ""


class LoginWindow(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    def loginBtn(self):
            id = db.getid(self.username.text, self.password.text)
            if id != False :

                MainWindow.current = self.username.text
                db.retrievekeyvalues()
                self.reset()
                sm.current = "main"
            else:
                invalidLogin()

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.username.text = ""
        self.password.text = ""

class StorePassWindow(Screen):
    appname = ObjectProperty(None)
    appuser = ObjectProperty(None)
    apppass = ObjectProperty(None)

    def submit(self):
        if self.appname.text != "" and self.appuser.text != "":
            if self.apppass != "":
                result = db.checkpassnameexists(self.appname.text)
                if result == False:
                    db.storeappdetails(self.appname.text, self.appuser.text, self.apppass.text)
                    self.reset()
                    sm.current = "main"
                else:
                    invalidExsits2()
            else:
                invalidForm()
        else:
            invalidForm()

    def back(self):
        self.reset()
        sm.current = "main"

    def reset(self):
        self.appname.text = ""
        self.appuser.text = ""
        self.apppass.text = ""

class WelcomeWindow(Screen):
    def back(self):
        sm.current = "main"

class AcceptAppInfoWindow(Screen):
    appname = ObjectProperty(None)
    appuser = ObjectProperty(None)
    def submit(self):
        if self.appname.text != "" and self.appuser.text != "":
            if self.appname != "":
                try:
                    exists = db.retrieveappdetails(self.appname.text, self.appuser.text)
                    if exists == True:
                        sm.current = "display"
                    if exists == False:
                        invalidExists1()
                        sm.current = "main"

                except:
                    error()
            else:
                invalidForm()
        else:
            invalidForm()

    def back(self):
        self.reset()
        sm.current = "main"

    def reset(self):
        self.appname.text = ""
        self.appuser.text = ""





class DisplayWindow(Screen):
    appnamee = ObjectProperty(None)
    appuserr = ObjectProperty(None)
    apppasss = ObjectProperty(None)

    def back(self):
        sm.current = "main"

    def on_enter(self, *args):
        appname, appuser, apppass = db.givevalapp()
        self.appnamee.text = "App Name: " + appname
        self.appuserr.text = "Account Name: " + appuser
        self.apppasss.text = "Account password: " + apppass

class MainWindow(Screen):
    current = ""

    def welcomeBtn(self):
        sm.current = "welcome"

    def createappBtn(self):
        sm.current = "store"

    def logOut(self):
        sm.current = "login"
        db.resetk()
        db.resetid()
        db.resetappdetails()
    def acceptinfo(self):
        sm.current = "accept"


class WindowManager(ScreenManager):
    pass

def error():
    pop = Popup(title='error',
                content='data error',
                size_hint=(None, None), size=(400, 400))
    pop.opent()

def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidForm():
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.'),
                  size_hint=(None, None), size=(400, 400))

    pop.open()

def invalidExsits2():
    pop = Popup(title = 'Invalid Exists',
                content=Label(text='Sorry, please choose a different name'),
                size_hint=(None, None), size = (400,400))
    pop.open()


def invalidExists1():
    pop = Popup(title='Invalid Exists',
                content=Label(text='Sorry, the requested data does not exist.'),
                size_hint=(None, None), size=(400, 400))

    pop.open()

def invalidExists():
    pop = Popup(title='Invalid Exists',
                  content=Label(text='Sorry, username already exists. Please try another name.'),
                  size_hint=(None, None), size=(400, 400))

    pop.open()

kv = Builder.load_file("my.kv")

sm = WindowManager()
db = Database()

screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"), MainWindow(name="main"), StorePassWindow(name="store"), WelcomeWindow(name="welcome"), AcceptAppInfoWindow(name="accept"), DisplayWindow(name="display")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"


class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()

