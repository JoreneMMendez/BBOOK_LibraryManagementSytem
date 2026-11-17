from time import sleep

from library import *

class user:
    def __init__(self, name, password):
        self._username = name
        self._userpassword = password

    def getAccount(self):
        return self._username, self._userpassword


class Dashboard:
    def __init__(self, ):
        self.Bookname

console = Console()
layout = Layout()
group = Group()




#Ascii design function



def loginInterface():
    layout = Layout()
    layout.split_column(
        Layout(" ", size=max_height),
        Layout(name="header", size=9),
        Layout(name="UserLogs", size=4),
    )
    layout["header"].update(
        Panel(ascii("2"))
    )
    return layout



def registerInterface():
    layout = Layout()
    layout.split_column()

    return


def DashboardInterface():
    return




