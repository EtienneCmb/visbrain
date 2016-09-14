import numpy as np

from vispy.scene.cameras import *
from vispy import app, gloo, visuals, scene, io
from vispy.visuals import Visual
from vispy.geometry import MeshData
from vispy.visuals.transforms import *

from visbrain.vbrain.utils import color2vb, array2colormap, dynamic_color


__all__ = ['BrainMeshVisual']

############################################################
# Atlas inputs :
atlas = np.load('/home/etienne/anaconda3/lib/python3.5/site-packages/visbrain/vbrain/elements/templates/atlasGL_B1.npz')
facesI = atlas['faces']
normalsI = atlas['a_normal'].astype(np.float32)
verticesI = 10*atlas['a_position'].astype(np.float32)
colorI = atlas['a_color'].astype(np.float32)

# vertices = 10*data['a_position']
# color = data['a_color']
# normals = data['a_normal']

scale_factor = 10

# print(normals.shape, faces.shape, vertices.shape, colorI.shape)
# Light inputs :
# l_position
# l_color
# l_coefAmbient
# L_coefSpecular

############################################################

VERT_SHADER = """
#version 120
varying vec3 v_position;
varying vec4 v_color;
varying vec3 v_normal;

void main() {
    v_position = $a_position;
    v_normal = $a_normal;
    v_color = $a_color * $u_color;
    gl_Position = $transform(vec4($a_position, 1));
}
"""


FRAG_SHADER = """
#version 120
varying vec3 v_position;
varying vec4 v_color;
varying vec3 v_normal;

void main() {

    // ----------------- Ambient light -----------------
    vec3 ambientLight = $u_coefAmbient * v_color.rgb * $u_light_intensity;


    // ----------------- Diffuse light -----------------
    // Calculate the vector from this pixels surface to the light source
    vec3 surfaceToLight = $u_light_position - v_position;

    // Calculate the cosine of the angle of incidence
    float brightness = dot(v_normal, surfaceToLight) / (length(surfaceToLight) * length(v_normal));
    brightness = clamp(brightness, 0, 1);
    // brightness = max(min(brightness,1.0),0.0);

    // Get diffuse light :
    vec3 diffuseLight =  v_color.rgb * brightness * $u_light_intensity;


    // ----------------- Specular light -----------------
    vec3 surfaceToCamera = vec3(0.0, 0.0, 1.0) - v_position;
    vec3 K = normalize(normalize(surfaceToLight) + normalize(surfaceToCamera));
    float specular = clamp(pow(abs(dot(v_normal, K)), 40.), 0.0, 1.0);
    vec3 specularLight = $u_coefSpecular * specular * vec3(1., 1., 1.) * $u_light_intensity;


    // ----------------- Attenuation -----------------
    // float att = 0.01;
    // float distanceToLight = length($u_light_position - v_position);
    // float attenuation = 1.0 / (1.0 + att * pow(distanceToLight, 2));


    // ----------------- Linear color -----------------
    // Without attenuation :
    vec3 linearColor = ambientLight + specularLight + diffuseLight;

    // With attenuation :
    // vec3 linearColor = ambientLight + attenuation*(specularLight + diffuseLight);
    

    // ----------------- Gamma correction -----------------
    // vec3 gamma = vec3(1.0/1.2);


    // ----------------- Final color -----------------
    // Without gamma correction :
    gl_FragColor = vec4(linearColor, v_color.a);

    // With gamma correction :
    // gl_FragColor = vec4(pow(linearColor, gamma), v_color.a);
}
"""


class BrainMeshVisual(Visual):
    """Main visual class from brain mesh

    Args:
        name: type
            description

    Kargs:
        name: type, optional, (def: default)
            description 

    Return
        name: description
    """

    def __len__(self):
        return len(self._vertFaces)

    def __iter__(self):
        pass

    def __getitem__(self):
        pass

    def __init__(self, vertices=None, faces=None, normals=None, vertex_colors=None, camera=None,
                 meshdata=None, l_position=(1., 1., 1.), l_color=(1., 1., 1., 1.), l_intensity=(1., 1., 1.),
                 l_coefAmbient=0.11, l_coefSpecular=0.5):
        Visual.__init__(self, vcode=VERT_SHADER, fcode=FRAG_SHADER)

        # Define buffers
        self._vertices = gloo.VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        self._normals = None
        self._faces = gloo.IndexBuffer()
        self._colors = gloo.VertexBuffer(np.zeros((0, 4), dtype=np.float32))
        self._normals = gloo.VertexBuffer(np.zeros((0, 3), dtype=np.float32))
        self._color_changed = False

        # Set the data :
        BrainMeshVisual.set_data(self, vertices=vertices, faces=faces, normals=normals,
                                 meshdata=meshdata, vertex_colors=vertex_colors)

        # Set the light :
        BrainMeshVisual.set_light(self, l_position=l_position, l_color=l_color, l_intensity=l_intensity,
                                  l_coefAmbient=l_coefAmbient, l_coefSpecular=l_coefSpecular)

        # Set camera :
        BrainMeshVisual.set_camera(self, camera)


        self.set_gl_state('translucent', depth_test=True, cull_face=False, blend=True,
                          blend_func=('src_alpha', 'one_minus_src_alpha'))
        self._draw_mode = 'triangles'

        self.freeze()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # Methods when data/camera/light changed
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def mesh_data_changed(self):
        """Tell if data changed"""
        self._data_changed = True
        self.update()

    def mesh_color_changed(self):
        """Tell if color changed"""
        self._color_changed = True
        self.update()

    def mesh_light_changed(self):
        """Tell if light changed"""
        self._light_changed = True
        self.update()

    def mesh_camera_changed(self):
        """Tell if camera changed"""
        self._camera_changed = True
        self.update()

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # Set data/light/camera
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def set_data(self, vertices=None, faces=None, normals=None,
                 meshdata=None, vertex_colors=None, color=(1., 1., 1., 1.)):
        """Set data to the mesh

        Kargs:
            vertices: ndarray, optional, (def: None)
                Vertices to set of shape (Nx3)

            faces: ndarray, optional, (def: None)
                Faces to set of shape (Mx3)

            vertex_colors: ndarray, optional, (def: None)
                Vertex color of shape (Nx4)

            meshdata: vispy.meshdata, optional, (def: None)
                Custom vispy mesh data
        """
        # Custom template :
        if meshdata is not None:
            vertices = meshdata.get_vertices()
            faces = meshdata.get_faces()
            normals = meshdata.get_vertex_normals()

        # Color management :
        if vertex_colors is None:
            vertex_colors = np.tile(color, (L, 1))

        # Assign elements :
        self._vertFaces = vertices.astype(np.float32)
        self._colFaces = vertex_colors.astype(np.float32)
        self._normFaces = normals.astype(np.float32)
        self._tri = faces

        self.mesh_data_changed()


    def set_color(self, data=None, color='white', cmap='viridis', dynamic=None,
                  alpha=1.0, vmin=None, vmax=None, under='dimgray', over='darkred'):
        """Set specific colors on the brain

        Args:
            data: None
                Data to use for the color. If data is None

        Kargs:
            data: np.ndarray, optional, (def: None)
                Data to use for the color. If data is None, the color will
                be uniform using the color parameter. If data is a vector,
                the color is going to be deduced from this vector. If data
                is a (N, 4) it will be interprated as a color. 

            color: tuple/string/hex, optional, (def: 'white')
                The default uniform color

            cmap: string, optional, (def: 'viridis')
                Colormap to use if data is a vector

            dynamic: float, optional, (def: None)
                Control the dynamic of colors

            alpha: float, optional, (def: 1.0)
                Opacity to use if data is a vector

            vmin/vmax: float, optional, (def: None)
                Minimum/maximum value for clipping

            under/over: tuple/string/hex, optional, (def: 'dimgray'/'darkred')
                Color to use under/over respectively vmin/max
        """ 
        # Color to RGBA :
        color = color2vb(color, len(self))

        # Color management :
        if data is None: # uniform color
            col = np.tile(color, (len(self), 1)).astype(np.float32)
        elif data.ndim == 1: # data vector
            col = array2colormap(data.copy(), cmap=cmap, alpha=alpha, vmin=vmin, vmax=vmax,
                                 under=under, over=over).astype(np.float32)
            # Dynamic color :
            if dynamic is not None:
                col = dynamic_color(col, data)
        elif (data.ndim > 1) and (data.shape[1] == 4):
            col = data.astype(np.float32)
        else:
            raise ValueError("data is not recognized.")

        # Adapt for faces :
        col = np.transpose(np.tile(col[..., np.newaxis], (1, 1, 3)), (0, 2, 1))

        self._colFaces = np.ascontiguousarray(col, dtype=np.float32)
        self.mesh_color_changed()


    def set_light(self, l_position=None, l_color=None, l_intensity=None,
                  l_coefAmbient=None, l_coefSpecular=None):
        """Set light properties

        l_position: tuple, optional, (def: (1., 1., 1.))
            Position of the light

        l_color: tuple, optional, (def: (1., 1., 1., 1.))
            Color of the light (RGBA)

        l_intensity: tuple, optional, (def: (1., 1., 1.))
            Intensity of the light

        l_coefAmbient: float, optional, (def: 0.11)
            Coefficient for the ambient light

        l_coefSpecular: float, optional, (def: 0.5)
            Coefficient for the specular light
        """
        # Get lights :
        if l_position is not None:
            self._l_position = l_position
        if l_color is not None:
            self._l_color = l_color
        if l_coefAmbient is not None:
            self._l_coefAmbient = l_coefAmbient
        if l_coefSpecular is not None:
            self._l_coefSpecular = l_coefSpecular
        if l_intensity is not None:
            self._l_intensity = l_intensity
        self.mesh_light_changed()


    def set_camera(self, camera=None):
        """Set a camera to the mesh

        Args:
            name: type
                description

        Kargs:
            camera: vispy.camera, optional, (def: None)
                Set a camera to the Mesh for light adaptation 

        Return
            name: description
        """
        if camera is None:
            camera = TurntableCamera()
        self._camera = camera
        self._camera_transform = self._camera.transform
        self.mesh_camera_changed()


    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # Update data/color/light/camera
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _update_data(self):
        """Update faces/vertices/normals only"""

        # Define buffers
        self._faces = gloo.IndexBuffer(self._tri)
        self._colors = gloo.VertexBuffer(self._colFaces.astype(np.float32))
        self._vertices = gloo.VertexBuffer(self._vertFaces.astype(np.float32))
        self._normals = gloo.VertexBuffer(self._normFaces.astype(np.float32))

        # Mesh data :
        self.shared_program.vert['a_position'] = self._vertices
        self.shared_program.vert['a_color'] = self._colors
        self.shared_program.vert['a_normal'] = self._normals
        self._data_changed = False

    def _update_color(self):
        """Update clor only"""
        self._colors = gloo.VertexBuffer(self._colFaces.astype(np.float32))
        self.shared_program.vert['a_color'] = self._colors
        self._color_changed = False
        # self._update_data()

    def _update_light(self):
        """Update light only"""

        # Define colors and light :
        self.shared_program.vert['u_color'] = self._l_color
        self.shared_program.frag['u_coefAmbient'] = self._l_coefAmbient
        self.shared_program.frag['u_light_position'] = self._l_position
        self.shared_program.frag['u_light_intensity'] = self._l_intensity
        self.shared_program.frag['u_coefSpecular'] = self._l_coefSpecular
        self._light_changed = False


    def _update_camera(self):
        self._camera_changed = False


    @property
    def mesh_data(self):
        """The mesh data"""
        return self._vertFaces


    def switch_internal_external(self, projection):
        """
        """
        if projection == 'internal':
            self.set_gl_state('translucent', depth_test=False, cull_face=True, blend=True,
                              blend_func=('src_alpha', 'one_minus_src_alpha'))
        else:
            self.set_gl_state('translucent', depth_test=True, cull_face=False, blend=True,
                              blend_func=('src_alpha', 'one_minus_src_alpha'))
        self.update_gl_state()


    def draw(self, *args, **kwds):
        """This is call when drawing only
        """
        Visual.draw(self, *args, **kwds)


    def _prepare_draw(self, view=None):
        """This is call everytime there is an interaction with the mesh
        """
        # Need data update :
        if self._data_changed:
            if self._update_data() is False:
                return False
            self._data_changed = False
        # Need color update :
        if self._color_changed:
            if self._update_color() is False:
                return False
            self._color_changed = False
        # Need light update :
        if self._light_changed:
            if self._update_light() is False:
                return False
            self._light_changed = False
        # Need camera update :
        if self._camera_changed:
            if self._update_camera() is False:
                return False
            self._camera_changed = False
        view_frag = view.view_program.frag
        view_frag['u_light_position'] = self._camera_transform.map(self._l_position)[0:-1]


    @staticmethod
    def _prepare_transforms(view):
        """This is call because the first rendering
        """
        tr = view.transforms
        transform = tr.get_transform()

        view_vert = view.view_program.vert
        view_vert['transform'] = transform












# Auto-generate a Visual+Node class for use in the scenegraph.
BrainMesh = scene.visuals.create_visual_node(BrainMeshVisual)


# Finally we will test the visual by displaying in a scene.

canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='w', size=(2000,1000))

# Add a ViewBox to let the user zoom/rotate
cam = TurntableCamera()
view = canvas.central_widget.add_view()
view.camera = cam
# view.camera.fov = 1.
view.camera.distance = 15
view.camera.azimuth = 0.


mesh = BrainMesh(verticesI, facesI, vertex_colors=colorI, normals=normalsI, parent=view.scene,
                 camera=cam, l_position=(10., 10., 10.), l_coefSpecular=0.8)
# mesh.camera = cam

axis = scene.visuals.XYZAxis(parent=view.scene)
# cam.set_range(x=(-10,10), y=(-0.5,0.5))


# mesh.set_light(l_color=(1, 0, 0 , 1))
# color = np.random.rand(len(mesh), 4)
# color[:, 3] = 1
# mesh.set_color(data=color, cmap='inferno')

@canvas.events.mouse_double_click.connect
def on_mouse_double_click(event):
    color = np.arange(len(mesh))
    # color[:, 3] = 1
    mesh.set_color(cmap='Spectral', dynamic=None, data=color)
    canvas.update()


# ..and optionally start the event loop
if __name__ == '__main__':
    import sys
    if sys.flags.interactive != 1:
        app.run()
