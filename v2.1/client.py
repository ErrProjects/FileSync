from fs_client import FileSyncClient
from fs_lib.fs_aux_classes import Logging
from fs_lib.fs_consts import FileSyncRequests
import tkinter as tk
import tkinter.font as tkFont
import threading

# Created from: https://visualtk.com/
class App:
    def __init__(self, root, client_obj: FileSyncClient):
        # set client object
        self.client_obj = client_obj

        # setting title
        root.title("Client UI")
        
        # setting window size
        width = 500
        height = 480
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        root["bg"] = "#2b2b2b"

        Send_Btn = tk.Button(root)
        Send_Btn["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=10)
        Send_Btn["font"] = ft
        Send_Btn["fg"] = "#000000"
        Send_Btn["justify"] = "center"
        Send_Btn["text"] = "Send"
        Send_Btn.place(x=210,y=420,width=91,height=30)
        Send_Btn["command"] = self.Send_Btn_Fn

        self.UserInput = tk.Entry(root)
        self.UserInput["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.UserInput["font"] = ft
        self.UserInput["fg"] = "#333333"
        self.UserInput["justify"] = "center"
        self.UserInput["text"] = "Entry"
        self.UserInput.place(x=170,y=370,width=263,height=30)

        UserInput_Lbl = tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        UserInput_Lbl["font"] = ft
        UserInput_Lbl["fg"] = "#333333"
        UserInput_Lbl["justify"] = "center"
        UserInput_Lbl["text"] = "Type here:"
        UserInput_Lbl.place(x=90,y=370,width=71,height=30)

        self.MessageBox = tk.Listbox(root)
        self.MessageBox["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.MessageBox["font"] = ft
        self.MessageBox["fg"] = "#333333"
        self.MessageBox["justify"] = "center"
        self.MessageBox.place(x=60,y=80,width=394,height=268)

        scrollbar = tk.Scrollbar(self.MessageBox)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        self.MessageBox.config(yscrollcommand = scrollbar.set)
        scrollbar.config(command = self.MessageBox.yview)

        TitleText = tk.Label(root)
        ft = tkFont.Font(family='Times',size=16)
        TitleText["font"] = ft
        TitleText["fg"] = "#333333"
        TitleText["justify"] = "center"
        TitleText["text"] = "Client UI"
        TitleText["relief"] = "raised"
        TitleText.place(x=80,y=10,width=353,height=65)

        # Seperate Thread for receiving messages
        t = threading.Thread(target=self.Update_MessageBox)
        t.daemon = True
        t.start()

    def Send_Btn_Fn(self):
        try:
            # Get User Input
            input_str = self.UserInput.get().strip()

            self.Parse_Request(input_str)
            
        except Exception as ex:
            Logging.log(
                f"Exception occurred: {ex}",
                Logging.ERROR
            )
    
    def Parse_Request(self, request_input: str):
        m_tokens = request_input.split('||')

        if len(m_tokens) != 2:
            Logging.log(f"Invalid Request", Logging.WARNING)
            return
        
        if m_tokens[0].strip() == "SetAlias":
            self.client_obj.handle_sending('', FileSyncRequests.CHANGE_ALIAS, m_tokens[1].strip())

        elif m_tokens[0].strip() == "SendFile":
            sub_tokens = m_tokens[1].split('>>')
            if len(sub_tokens) != 2:
                Logging.log(f"Invalid SendFile Request", Logging.WARNING)
                return
            self.client_obj.handle_sending(sub_tokens[0].strip(), FileSyncRequests.SEND_FILE, sub_tokens[1].strip())
        
        self.MessageBox.insert(tk.END, f"[From Client] {request_input}")
        
    def Update_MessageBox(self):
        while True:
            res_ls = self.client_obj.handle_receiving()
            for res in res_ls:
                self.MessageBox.insert(tk.END, f"[From Server] {res}")
    



if __name__ == "__main__":
    client_obj = FileSyncClient()
    client_obj.connect_to_server(('192.168.1.4', 9999))

    root = tk.Tk()
    app = App(root, client_obj)
    root.mainloop()

    client_obj.close_connection()