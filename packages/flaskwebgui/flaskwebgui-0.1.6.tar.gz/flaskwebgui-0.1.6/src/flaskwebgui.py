import os, time, psutil
import sys, subprocess as sps

from threading import Thread


class FlaskUI:
    """
        This class opens in 3 threads the browser, the flask server, and a thread which closes the server if GUI is not opened
        
        Described Parameters:

        app,                              ==> flask  class instance 
        width=800                         ==> default width 800 
        height=600                        ==> default height 600
        fullscreen=False,                 ==> start app in fullscreen mode
        maximized=False,                 ==> start app in maximized window
        app_mode=True                     ==> by default it will start the application in chrome app mode
        browser_path="",                  ==> full path to browser.exe ("C:/browser_folder/chrome.exe")
                                              (needed if you want to start a specific browser)
        server="flask"                    ==> the default backend framework is flask, but you can add a function which starts 
                                              the desired server for your choosed framework (django, bottle, web2py pyramid etc)
        host="127.0.0.1"                  ==> specify other if needed
        port=5000                         ==> specify other if needed
        socketio                          ==> specify flask-socketio instance if you are using flask with socketio
    
    """

    def __init__(self, app=None, width=800, height=600, fullscreen=False, maximized=False, app_mode=True,  browser_path="", server="flask", host="127.0.0.1", port=5000, socketio=None):
        self.flask_app = app
        self.width = str(width)
        self.height= str(height)
        self.fullscreen = fullscreen
        self.maximized = maximized
        self.app_mode = app_mode
        self.browser_path = browser_path
        self.server = server
        self.host = host
        self.port = port
        self.socketio = socketio
        self.localhost = "http://{}:{}/".format(host, port) # http://127.0.0.1:5000/
        self.flask_thread = Thread(target=self.run_flask, daemon=True) #daemon doesn't work...
        self.browser_thread = Thread(target=self.open_browser)
        self.close_flask_thread = Thread(target=self.close_server)
        self.BROWSER_PROCESS = None
        #TODO Need to find a way to identify the flaskwebgui chrome instance and close that one..
        chrome_pids = [p.info['pid'] for p in psutil.process_iter(attrs=['pid', 'name']) if 'chrome' in p.info['name']]
        [psutil.Process(pid).kill() for pid in chrome_pids]


    def run(self):
        """
            Start the flask and gui threads instantiated in the constructor func
        """

        self.flask_thread.start()
        self.browser_thread.start()
        
        #Wait for the browser to run (1 min)
        count = 0
        while not self.browser_runs():
            time.sleep(1)
            if count > 60:
                break
            count += 1

        self.close_flask_thread.start()

        self.browser_thread.join()
        self.flask_thread.join()
        self.close_flask_thread.join()

    
    def run_flask(self):
        """
            Run flask or other framework specified
        """
        if isinstance(self.server, str):
            if self.server.lower() == "flask":
                if self.socketio:
                    self.socketio.run(self.flask_app, host=self.host, port=self.port)
                else:
                    self.flask_app.run(host=self.host, port=self.port)
            elif self.server.lower() == "django":
                if sys.platform in ['win32', 'win64']:
                    os.system("python manage.py runserver {}:{}".format(self.host, self.port))
                else:
                    os.system("python3 manage.py runserver {}:{}".format(self.host, self.port))
            else:
                raise Exception("{} must be a function which starts the webframework server!".format(self.server))
        else:
            self.server()


    def get_files_from_cwd(self):
        """
            Get a list of files from the current directory
        """

        root_path = os.getcwd()

        allfiles = []
        for root, dirs, files in os.walk(root_path):
            for file in files:
                path_tofile = os.path.join(root, file)
                allfiles.append(path_tofile)

        return allfiles



    def get_default_chrome_path(self):
        """
            Credits for get_instance_path, find_chrome_mac, find_chrome_linux, find_chrome_win funcs
            got from: https://github.com/ChrisKnott/Eel/blob/master/eel/chrome.py
        """
        if sys.platform in ['win32', 'win64']:
            return self.find_chrome_win()
        elif sys.platform == 'darwin':
            return self.find_chrome_mac()
        elif sys.platform.startswith('linux'):
            return self.find_chrome_linux()


    def find_chrome_mac(self):
        default_dir = r'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        if os.path.exists(default_dir):
            return default_dir
        # use mdfind ci to locate Chrome in alternate locations and return the first one
        name = 'Google Chrome.app'
        alternate_dirs = [x for x in sps.check_output(["mdfind", name]).decode().split('\n') if x.endswith(name)] 
        if len(alternate_dirs):
            return alternate_dirs[0] + '/Contents/MacOS/Google Chrome'
        return None


    def find_chrome_linux(self):
        import whichcraft as wch
        chrome_names = ['chromium-browser',
                        'chromium',
                        'google-chrome',
                        'google-chrome-stable']

        for name in chrome_names:
            chrome = wch.which(name)
            if chrome is not None:
                return chrome
        return None


    def find_chrome_win(self):
        import winreg as reg
        reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'

        for install_type in reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE:
            try:
                reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
                chrome_path = reg.QueryValue(reg_key, None)
                reg_key.Close()
            except WindowsError:
                chrome_path = None
            else:
                break

        return chrome_path


    def find_browser(self):
        """
            Find a path to browser
            Chrome/Chromium is prefered because it has a nice 'app' mode which looks like a desktop app
        """

        # Return browser_path param
        if os.path.isfile(self.browser_path):
            return self.browser_path
        # Raise error if browser path param doesn't exist
        if self.browser_path != "":
            raise Exception("Path {} does not exist!".format(self.browser_path))
        # Return browser_path from curent folder if chrome.exe/.app./sh file is found
        files = self.get_files_from_cwd()
        chrome = [fpath for fpath in files if fpath[-4:] in [".exe", ".app"] or fpath[-3:] in [".sh"]]
        if len(chrome) == 1:
            if os.path.isfile(chrome[0]):
                return os.path.relpath(chrome[0])
        # If browser_path not completed and in curent folder portable chrome not found then 
        # try to find default chrome installation
        return self.get_default_chrome_path()
        
 
    def open_browser(self):
        """
            Open the browser selected (by default it looks for chrome)
        """

        browser_path = self.find_browser()
        
        if browser_path:
            try:
                if self.app_mode: 

                    if self.fullscreen:
                        self.BROWSER_PROCESS = sps.Popen([browser_path, "--start-fullscreen", '--app={}'.format(self.localhost)], 
                        stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
                    elif self.maximized:
                        self.BROWSER_PROCESS = sps.Popen([browser_path, "--start-maximized", '--app={}'.format(self.localhost)],
                        stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
                    else:
                        self.BROWSER_PROCESS = sps.Popen([browser_path, "--window-size={},{}".format(self.width, self.height),
                        '--app={}'.format(self.localhost)], 
                        stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
                else:
                    self.BROWSER_PROCESS = sps.Popen([browser_path, self.localhost], 
                    stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
            except:
                self.BROWSER_PROCESS = sps.Popen([browser_path, self.localhost], 
                stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
        else:
            import webbrowser
            webbrowser.open_new(self.localhost)


    def browser_runs(self):
        """
            Check if chrome is opened / Improv daemon not working
        """
        try: 
            if self.BROWSER_PROCESS.poll() == 0:
                return False
            else:
                return True
        except: #Fails untill server and browser starts
            return True

    def close_server(self):
        """
            If browser process is not running close flask server
        """

        while self.browser_runs():
            time.sleep(2)
        #Kill current python process
        psutil.Process(os.getpid()).kill()
        
        

        

        
        


