import wx
import datetime
import os

class Kalendarz(wx.Frame):
    def __init__(self, title):
        super().__init__(parent = None, title = title, style = wx.DEFAULT_FRAME_STYLE, size = (1280, 720))
        self.Center()
        self.panel = wx.Panel(self)

        self.sizer = wx.GridSizer(rows=6, cols=7, gap=(5, 5))
        self.panel.SetSizer(self.sizer)
        self.buttons_with_notes = []

        self.RefreshWindow()
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.Destroy()

    def RefreshWindow(self):

        self.sizer.Clear(True)
        self.panel.Layout()

        now = datetime.datetime.now()
        day = now.day
        month = now.month
        year = now.year

        weekday_background_colour_past = 211, 211, 211
        weekend_background_colour_past = 173, 173, 173
        weekday_background_colour_now = 173, 216, 230
        weekend_background_colour_now = 30, 144, 255

        offset = self.Offset(year, month)

        days_in_month_now = self.Ile_dni_w_miesaicu(year, month)
        days_in_month_past = self.Ile_dni_w_miesaicu(year, month - 1)
        days_in_month_future = self.Ile_dni_w_miesaicu(year, month + 1)
        weekend_detector = 1



        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for weekday in weekdays:
            label = wx.StaticText(self.panel, label=weekday)
            self.sizer.Add(label, flag=wx.ALIGN_CENTER)

        for offsets in range(0, offset):
            button = wx.Button(self.panel, label=str(days_in_month_past - (offset - offsets - 1)))
            button.Bind(wx.EVT_BUTTON, self.DzienGenerator)
            if weekend_detector % 6 == 0 or weekend_detector % 7 == 0:
                button.SetBackgroundColour(wx.Colour(weekend_background_colour_past))
            else:
                button.SetBackgroundColour(wx.Colour(weekday_background_colour_past))
            if weekend_detector == 7:
                weekend_detector = 0
            weekend_detector += 1
            self.sizer.Add(button, flag=wx.EXPAND)

        for dzien_miesiaca in range(1, days_in_month_now + 1):
            if dzien_miesiaca == day:
                button = wx.Button(self.panel, label=str(dzien_miesiaca))
                button.Bind(wx.EVT_BUTTON, self.DzienGenerator)
                button.SetBackgroundColour(wx.Colour(232, 244, 248))
            else:
                button = wx.Button(self.panel, label=str(dzien_miesiaca))
                button.Bind(wx.EVT_BUTTON, self.DzienGenerator)
                if weekend_detector % 6 == 0 or weekend_detector % 7 == 0:
                    button.SetBackgroundColour(wx.Colour(weekend_background_colour_now))
                else:
                    button.SetBackgroundColour(wx.Colour(weekday_background_colour_now))
            if weekend_detector == 7:
                weekend_detector = 0
            weekend_detector += 1
            self.sizer.Add(button, flag=wx.EXPAND)
            widowz = DodatkoweOkno(parent=self, day=dzien_miesiaca, kalendarz=self)
            if os.path.exists(os.path.join(widowz.folder_name, f"note_day_{dzien_miesiaca}.txt")):
                self.buttons_with_notes.append(button)

        for dzien_miesiaca_za_miesiac in range(1, (35 - (offset + days_in_month_now)) + 1):
            button = wx.Button(self.panel, label=str(dzien_miesiaca_za_miesiac))
            button.Bind(wx.EVT_BUTTON, self.DzienGenerator)
            if weekend_detector % 6 == 0 or weekend_detector % 7 == 0:
                button.SetBackgroundColour(wx.Colour(weekend_background_colour_past))
            else:
                button.SetBackgroundColour(wx.Colour(weekday_background_colour_past))
            if weekend_detector == 7:
                weekend_detector = 0
            weekend_detector += 1
            self.sizer.Add(button, flag=wx.EXPAND)

        self.panel.Layout()
        self.update_button_indicators()

    def DzienGenerator(self, event):
        button = event.GetEventObject()
        dzien = int(str(button.GetLabel()).replace('*', ''))
        print(f"Clicked day: {dzien}")
        window = DodatkoweOkno(parent=self, day=dzien, kalendarz=self)
        window.Bind(wx.EVT_CLOSE, self.OnAdditionalWindowClose)
        window.Show()

    def OnAdditionalWindowClose(self, event):
        self.RefreshWindow()
        event.Skip()



    def Ile_dni_w_miesaicu(self, year, month):
        if month == 2:
            return 28
        elif month in [4, 6, 9, 11]:
            return 30
        else:
            return 31
    def Offset(self, year, month):
        datez = datetime.datetime(year, month, 1)
        offset = datez.weekday()
        return offset

    def update_button_indicators(self):
        valid_buttons = []
        for button in self.buttons_with_notes:
            try:
                if not button.IsBeingDeleted():
                    valid_buttons.append(button)
            except RuntimeError:
                continue

        self.buttons_with_notes = valid_buttons

        for button in self.buttons_with_notes:
            label = button.GetLabel()
            if "*" not in label:
                new_label = f"{label} *"
                button.SetLabel(new_label)
            else:
                new_label = label
            button.SetLabel(new_label)
            button.SetBackgroundColour(wx.Colour(255, 255, 0))




class DodatkoweOkno(wx.Frame):
    def __init__(self, parent,  day, kalendarz):
        super().__init__(parent=None, title="Informacjie dnia(wstempna nazwa)", style=wx.DEFAULT_FRAME_STYLE, size=(600,1000))
        self.Center()
        self.panel = wx.Panel(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.day = day
        self.note_file = f"note_day_{self.day}.txt"
        self.folder_name = "ZapiskiKalendarza"

        self.create_folder()
        font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD, faceName="Arial")
        self.text_ctrl = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.text_ctrl.SetFont(font)
        self.load_note()

        save_button = wx.Button(self.panel, label="Save")
        save_button.Bind(wx.EVT_BUTTON, self.save_note)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.text_ctrl, proportion=1, flag=wx.EXPAND)
        sizer.Add(save_button, flag=wx.ALIGN_RIGHT)
        self.panel.SetSizer(sizer)

        self.kalendarz = kalendarz

    def create_folder(self):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    def load_note(self):
        try:
            with open(os.path.join(self.folder_name, self.note_file), "r") as file:
                note = file.read()
                self.text_ctrl.SetValue(note)
        except FileNotFoundError:
            self.text_ctrl.SetValue("")

    def save_note(self, event):
        note = self.text_ctrl.GetValue()
        with open(os.path.join(self.folder_name, self.note_file), "w") as file:
            file.write(note)
        for note_file in os.listdir(self.folder_name):
            file_path = os.path.join(self.folder_name, self.note_file)
            if os.path.isfile(file_path) and os.path.getsize(file_path) == 0:
                os.remove(file_path)
                print(f"Deleted empty note: {note_file}")
        self.Close()

    def OnClose(self, event):
        self.kalendarz.RefreshWindow()
        self.Destroy()

app = wx.App()
Okno = Kalendarz("ELLLO")
Okno.Show()
app.MainLoop()
