import pyautogui as pag

def notify(self, title='', message='', app_name='', app_icon='',
           timeout=10, ticker='', toast=False):
    # pylint: disable=too-many-arguments

    self._notify(
        title=title, message=message,
        app_icon=app_icon, app_name=app_name,
        timeout=timeout, ticker=ticker, toast=toast
    )

class standart():
    def wait():
        a = input('')

class Windows():
    def notify(title, message, app_name='Python app', app_icon='none'):
        if app_icon != 'none':
            notify(
                message=message,
                app_name=app_name,
                app_icon=app_icon,
                title=title)
        else:
            notify(
                message=message,
                app_name=app_name,
                title=title)
    def confirm(text):
        a = str(pag.confirm(text))
        x = a
        if a == 'OK':
            x = 1
        elif a == 'Cancel':
            x = 0
        return(x)
    def alert(text):
        pag.alert(text)
    def question(text):
        return(pag.prompt(text))

class cfg():
    def read(file_name):
        file_name += '.cfg'
        dict = {}
        with open(file_name, 'r') as f:
            for a in f.readlines():
                if '\n' in a: a = a[:-1]
                n = ''
                w = ''
                
                n, w = a.split(' = ')
                
                try:
                    dict[n] = int(w)
                except:
                    dict[n] = w
        return(dict)
                
    def write(file_name, what):
        file_name += '.cfg'
        with open(file_name, 'wt') as f:
            for key, value in what.items():
                st = str(key) + ' = ' + str(value) + '\n'
                f.write(st)

class table():
    def reservation(text, x, y=3):
        l = len(text)
        if y == 1:
            text = text + ' ' * (x - l)
            z = text
        elif y == 2:
            text = ' ' * ((x - l) // 2) + text + ' ' * ((x - l) // 2)
            l2 = len(text)
            if text == l2:
                z = text[:x]
            else:
                z = ' ' * (x - l2) + text[:x]
        elif y == 3:
            text = ' ' * (x - l) + text
            z = text
        return (z)

    def table(rows, column1, column2, mode=1):
        l1 = 0
        max1 = 0
        max2 = 0
        for a in column1:
            l1 = len(a)
            if l1 > max1: max1 = l1
        for a in column2:
            l2 = len(a)
            if l2 > max2: max2 = l2

        bc1, bc2 = '#' * max1, '#' * max2
        print('#' + bc1 + '#' + bc2 + '#')
        lc = len(column1) if column1 > column2 else len(column2)
        if mode == 1:
            # try:
            for i in range(lc):
                print('#' + table.reservation(str(column1[i]), max1, 3) + '#' + table.reservation(str(column2[i]), max2,
                                                                                                  1) + '#')
        # except:
        # print('Error number of items in column')
        elif mode == 2:
            try:
                for i in range(lc):
                    print('#' + table.reservation(str(column1[i]), max1, 1) + '#' + table.reservation(str(column2[i]),
                                                                                                      max2, 1) + '#')
            except:
                print('Error number of items in column')
        elif mode == 3:
            try:
                for i in range(lc):
                    print('#' + table.reservation(str(column1[i]), max1, 2) + '#' + table.reservation(str(column2[i]),
                                                                                                      max2, 2) + '#')
            except:
                print('Error number of items in column')
        bc1, bc2 = '#' * max1, '#' * max2
        print('#' + bc1 + '#' + bc2 + '#')