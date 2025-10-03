import threading

from text_input_box import TextInputBox
from button import Button
from p2p_node import start_server

class ScreenOne():
    def __init__(self, screen, gato):
        print("Initializing ScreenOne")
        self.port_input = None
        self.init_btn = None
        self.screen = screen
        self.gato = gato

    def on_init(self):
        self.port_input = TextInputBox(162, 145, 200, 30, label_text="PORT: ")
        self.init_btn = Button(206, 200, 100, 50, "Iniciar")

    def on_event(self, event):
        result_port = self.port_input.handle_event(event)
        if result_port is not None:
            self.gato.connection.append(result_port)
            self.gato.label_self_port.update("Port: " + str(result_port) )
            self.start(str(result_port))
            self.gato.CURRENT_SCREEN = 1

        if self.init_btn.handle_event(event):
            self.gato.connection.append(result_port)
            self.gato.label_self_port.update("Port: " + str(self.port_input.text))
            self.start(str(self.port_input.text))
            self.gato.CURRENT_SCREEN = 1

    def start(self, port):
        thread = threading.Thread(target=start_server, args=(port,self.gato), daemon=True)
        thread.start()

    def on_render(self):
        self.port_input.update()
        self.port_input.draw(self.screen)
        self.init_btn.draw(self.screen)