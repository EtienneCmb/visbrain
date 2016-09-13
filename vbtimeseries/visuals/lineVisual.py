import numpy as np
from vispy import gloo
from vispy import app
from vispy.util.transforms import perspective, translate, rotate, scale
from vispy.visuals.transforms import STTransform

from ...vbrain.utils import normalize

W, H = 4000, 4000

N = 1000
phi = 4

sf = 1000
time = np.arange(N)/sf
data = np.sin(2*np.pi*phi*time)
a_position = np.array([time, data, np.zeros_like(data)]).T

a_position[:, 0] = normalize(a_position[:, 0], tomin=-0.5, tomax=0.5)
a_position[:, 1] = normalize(a_position[:, 1], tomin=-0.5, tomax=0.5)
a_position = a_position.astype(np.float32)
print(data.min(), data.max())



# a_position[:, 2] = 0.0 # p.random.rand(N, 3).astype(np.float32) #
a_color = np.random.rand(N, 4).astype(np.float32)
# st = STTransform(scale=(1/a_position[:, 0].max(), 1/a_position[:, 1].max(), 1), translate=(0, 0, 0))
# a_position = st.map(a_position)[:, 0:-1].astype(np.float32)
# a_position = scale()

VERT_SHADER = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
attribute vec3 a_position;
attribute vec4 a_color;
varying vec4 v_color;
void main (void) {
    v_color = a_color;
    gl_Position = u_projection * u_view * u_model * vec4(a_position,1.0);
}
"""

FRAG_SHADER = """
varying vec4 v_color;
void main()
{
    gl_FragColor = v_color;
}
"""


class CanvasTest(app.Canvas):

    # ---------------------------------
    def __init__(self, ):
        app.Canvas.__init__(self, keys='interactive', resizable=False, fullscreen=True)

        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)

        # Set uniform and attribute
        # self.program['a_id'] = gloo.VertexBuffer(a_id)
        self.program['a_color'] = gloo.VertexBuffer(a_color)
        self.program['a_position'] = gloo.VertexBuffer(a_position)

        self.translate = 2*1.3
        self.scale = 3.5/2
        self.view = np.dot(translate((0, 0, -self.translate)), scale((self.scale, 1, 1))).astype(np.float32)
        self.model = np.eye(4, dtype=np.float32)

        gloo.set_viewport(0, 0, self.physical_size[0], self.physical_size[1])
        self.projection = perspective(45.0, self.size[0] /
                                      float(self.size[1]), 1.0, 1000.0)
        self.program['u_projection'] = self.projection

        self.program['u_model'] = self.model
        self.program['u_view'] = self.view

        self.theta = 0
        self.phi = 0

        self.context.set_clear_color('white')
        self.context.set_state('translucent')
        self.context.set_line_width(7)

        self.show()

    def on_mouse_move(self, event):
        if event.is_dragging and not event.modifiers:
            zoom = np.abs(np.exp(10-self.translate))
            zoom = min(max(30, zoom), 2000)

            x0, y0 = normalize(event.press_event.pos)
            x1, y1 = normalize(event.last_event.pos)
            x, y = normalize(event.pos)
            dx, dy = x - x1, -(y - y1)
            button = event.press_event.button

            x0, y0 = event.press_event.pos
            x1, y1 = event.last_event.pos
            x, y = event.pos
            dx, dy = x - x1, -(y - y1)

            print('Last: ', x1, 'Press: ')

            if button == 1:
                self.view = translate(((x-x0)/zoom, 0, -self.translate))
                self.program['u_view'] = self.view
                self.update()


    # ---------------------------------
    def on_key_press(self, event):
        pass
        # if event.text == ' ':
        #     if self.timer.running:
        #         self.timer.stop()
        #     else:
        #         self.timer.start()

    # ---------------------------------
    def on_resize(self, event):
        gloo.set_viewport(0, 0, event.physical_size[0], event.physical_size[1])
        self.projection = perspective(45.0, event.size[0] /
                                      float(event.size[1]), 1.0, 1000.0)
        self.program['u_projection'] = self.projection

    # def on_mouse_move(self, event):
    #     self.view = translate((event.pos[0]/1915, -event.pos[1]/1000, -self.translate))
    #     self.program['u_view'] = self.view
    #     self.update()

    # ---------------------------------
    def on_mouse_wheel(self, event):
        self.scale += event.delta[1]/2
        self.scale = max(3.5, self.scale)
        A = np.dot(translate((0, 0, -self.translate)), scale((self.scale, 1, 1)))
        self.view = A.astype(np.float32)
        self.program['u_view'] = self.view
        self.update()

    # ---------------------------------
    def on_draw(self, event):
        self.context.clear()
        self.program.draw('line_strip')


# if __name__ == '__main__':
#     c = Canvas()
#     app.run()