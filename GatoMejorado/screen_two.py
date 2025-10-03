from text_input_box import TextInputBox
from button import Button
from p2p_node import connect_to_peer

class ScreenTwo:
    def __init__(self, screen, gato):
        print("Initializing ScreenTwo")
        self.ip_input = None
        self.port_input = None
        self.play_btn = None
        self.screen = screen
        self.gato = gato

    def on_init(self):
        self.ip_input = TextInputBox(250, 145, 200, 30, label_text="REMOTE IP: ")
        self.port_input = TextInputBox(250, 235, 200, 30, label_text="REMOTE PORT: ")
        self.play_btn = Button(256, 300, 100, 50, "Jugar")

        # Prefill this to avoid enter the same each time
        self.ip_input.text = '127.0.0.1'

    def on_event(self, event):
        result_ip = self.ip_input.handle_event(event)
        if result_ip is not None:
            pass

        result_port = self.port_input.handle_event(event)
        if result_port is not None:
            pass

        if self.play_btn.handle_event(event):
            if self.ip_input.text and self.port_input.text:
                self.gato.connection.append(self.ip_input.text)
                self.gato.label_remote_ip.update("Remote IP: " + str(self.ip_input.text))
                self.gato.connection.append(result_port)
                self.gato.label_remote_port.update("Remote Port: " + str(self.port_input.text))

                self.gato.player = 1
                self.gato.label_player.update("Player: X ")

                connect_to_peer(str(self.ip_input.text), int(self.port_input.text), self.gato)

                if self.gato.CURRENT_SCREEN < 2:
                    self.gato.CURRENT_SCREEN = 2

    def on_render(self):
        self.ip_input.update()
        self.port_input.update()

        self.ip_input.draw(self.screen)
        self.port_input.draw(self.screen)
        self.play_btn.draw(self.screen)