from tkinter import Tk, StringVar, Label, IntVar, Checkbutton, Entry, Radiobutton, Button, messagebox, END, tkinter


def been_clicked():
    radioValue = relStatus.get()
    messagebox.showinfo("You clicked ", radioValue)
    return

def change_label(label, new_label):
    str(label).delete(0, END)
    str(label).set(new_label)
    return


class Dashboard:

    def __init__(self, xaxis, yaxis):
        self.xaxis = xaxis
        self.yaxis = yaxis
        self.dashboard = Tk()
        self.dashboard.title("Dashboard")
        self.dashboard.config(background="black")
        self.dashboard.geometry(str(self.xaxis) + "x" + str(self.yaxis) + "+200+200")
        self.widgets = []
        self.dashboard.mainloop()


    def add_widget(self):
        self.widgets.append(Label(self.dashboard, text="Field " + str(self.widgets.__len__())).grid(row=self.widgets.__len__(), column=0, columnspan=4))

    def update_text(self, widget_index, message):
        self.widgets[widget_index] = Label(self.dashboard, text=message.grid(row=widget_index, column=0, columnspan=4))

#dashboard= Dashboard(350,350)
"""
dashboard = Tk()
dashboard.title("Swarm Dashboard")
dashboard.geometry("450x350+200+200")
labelText = StringVar()
labelText.set("Click button")
label1 = Label(dashboard, textvariable=labelText, height=4)
label1.pack()
checkBoxVal = IntVar()
checkBox1 = Checkbutton(dashboard, variable=checkBoxVal, text="Happy?").pack()
custName = StringVar()
yourName = Entry(dashboard, textvariable=custName)
yourName.pack()
relStatus = StringVar()
relStatus.set(None)
radio1 = Radiobutton(dashboard, text="Single", value="Single", variable=relStatus, command=beenClicked).pack()
radio2 = Radiobutton(dashboard, text="Married", value="Married", variable=relStatus, command=beenClicked).pack()
button1 = Button(dashboard, text="Click here", width=20, command=changeLabel)
button1.pack(side='bottom',padx=15,pady=15)
"""



