import win32gui
import win32con
import pyautogui
def enumHandler(hwnd, lParam):
    if win32gui.IsWindowVisible(hwnd):
        if 'VideoEdge' in win32gui.GetWindowText(hwnd):
            win32gui.PostMessage(hwnd,win32con.WM_CLOSE,0,0)

i = pyautogui.confirm(text='Do you want to auto close cams?', title='Run Program', buttons=['Yes', 'Cancel'])
if i == 'Yes':
    print('Running')
while i == 'Yes':
    win32gui.EnumWindows(enumHandler, None)

