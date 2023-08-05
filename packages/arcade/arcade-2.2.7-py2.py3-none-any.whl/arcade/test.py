import arcade


class Master(arcade.Window):
    def __init__(self):
        arcade.Window.__init__(self, 800,  600)

    def on_draw(self):
        arcade.start_render()
        color = (255, 255, 255, 255)
        arcade.draw_text("Hi there", 10, 10, color, 24)
        color = (255, 255, 255, 127)
        arcade.draw_text("Hi there", 10, 40, color, 24)
        color = (255, 255, 255, 22)
        arcade.draw_text("Hi there", 10, 70, color, 24)

if __name__ == '__main__':
    app = Master()
    arcade.run()