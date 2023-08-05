class standart():
    def wait() #wait until pressed ENTER

class Windows():
    def notify(title, message, app_name='Python app', app_icon='none') #create a notification message

    def confirm(text) #create a notification message with select(OK or CANScEL)

    def alert(text) #create a alert message

    def question(text) #create a question message

class cfg():
    def read(file_name) #read cfg file to dict from type: {what} = {value}
                
    def write(file_name, what) #write cfg file from dict with type: {what} = {value}

class table():
    def reservation(text, x, mode=3) #create reservation for x symbols with assignment(1 - LEFT, 2 - MIDDLE, 3 - RIGHT)

    def table(column1, column2, mode=1) #create table from list column1, column2