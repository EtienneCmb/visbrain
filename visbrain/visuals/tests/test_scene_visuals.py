"""Integration checks for visuals hosted on a scene canvas."""

from __future__ import annotations

import numpy as np
import pytest

# Skip the module entirely when VisPy's GL bindings are unavailable.  Importing
# :mod:`visbrain.visuals.brain_visual` pulls :mod:`vispy.gloo`, which raises when
# the platform lacks an OpenGL library (common on CI).
try:  # pragma: no cover - exercised only when OpenGL is missing.
    import vispy.gloo  # noqa: F401 - imported for side effects
except Exception as exc:  # pragma: no cover - defensive import guard
    pytest.skip(
        f"VisPy gloo backend unavailable ({exc})",
        allow_module_level=True,
    )

import vispy.visuals.transforms as vist

from visbrain.visuals import scene_canvas
from visbrain.visuals.brain_visual import BrainMesh, BrainVisual, LIGHT_POSITION
from visbrain.visuals.grid_signal_visual import GridSignal, GridSignalVisual
from visbrain.visuals.topo_visual import TopoMesh


@pytest.fixture
def brain_inputs() -> dict[str, np.ndarray]:
    """Return deterministic mesh data for the :class:`BrainVisual`."""

    vertices = np.array(
        [
            [-0.5, -0.5, 0.0],
            [0.5, -0.5, 0.0],
            [0.0, 0.5, 0.0],
            [0.0, 0.0, 0.75],
        ],
        dtype=np.float32,
    )
    faces = np.array(
        [
            [0, 1, 2],
            [0, 1, 3],
            [1, 2, 3],
            [2, 0, 3],
        ],
        dtype=np.uint32,
    )
    normals = np.tile(np.array([[0.0, 0.0, 1.0]], dtype=np.float32), (4, 1))
    return {"vertices": vertices, "faces": faces, "normals": normals}


@pytest.fixture
def topo_inputs() -> dict[str, np.ndarray]:
    """Return deterministic coordinates for the :class:`TopoMesh`."""

    xyz = np.array(
        [
            [0.0, 0.0, 1.0],
            [0.5, 0.0, 1.0],
            [0.0, 0.5, 1.0],
        ],
        dtype=np.float32,
    )
    data = np.array([0.25, -0.5, 0.75], dtype=np.float32)
    return {"xyz": xyz, "data": data}


@pytest.fixture
def grid_inputs() -> dict[str, np.ndarray]:
    """Return deterministic time series for :class:`GridSignalVisual`."""

    timeline = np.linspace(-1.0, 1.0, 20, dtype=np.float32)
    # Shape (n_rows, n_time) so the visual configures a 1x1 grid deterministically.
    return {"data": timeline.reshape(1, -1)}


def test_brain_visual_attaches_to_scene(brain_inputs: dict[str, np.ndarray]) -> None:
    """The scene helper should host :class:`BrainVisual` nodes."""

    with scene_canvas(force_app=True) as ctx:
        brain = BrainMesh(parent=ctx.scene, **brain_inputs)

        assert brain.parent is ctx.scene
        assert isinstance(brain.visual, BrainVisual)
        np.testing.assert_allclose(
            brain.visual.shared_program.frag["u_light_position"],
            np.array(LIGHT_POSITION, dtype=np.float32),
        )


def test_topo_mesh_nodes_expose_expected_transforms(
    topo_inputs: dict[str, np.ndarray],
) -> None:
    """The topography graph should register its transforms on the scene."""

    with scene_canvas(force_app=True) as ctx:
        topo = TopoMesh(
            xyz=topo_inputs["xyz"],
            channels=["Cz", "Pz", "Fz"],
            cbar=False,
            parent=ctx.scene,
        )
        topo.set_data(topo_inputs["data"])

        assert topo.node.parent is ctx.scene
        assert isinstance(topo.node.transform, vist.STTransform)
        np.testing.assert_allclose(topo.node.transform.scale, np.full(3, 800.0))
        np.testing.assert_allclose(
            topo.node_chan.transform.translate,
            np.array([0.0, 0.0, -10.0]),
        )


def test_grid_signal_uniforms_reflect_scene_state(
    grid_inputs: dict[str, np.ndarray],
) -> None:
    """The grid-signal visual should update its uniforms upon creation."""

    with scene_canvas(force_app=True) as ctx:
        grid = GridSignal(parent=ctx.scene, **grid_inputs)

        assert grid.parent is ctx.scene
        assert isinstance(grid.visual, GridSignalVisual)
        assert grid.visual.g_size == (1, 1)
        np.testing.assert_allclose(
            grid.visual.shared_program.vert["u_size"],
            np.array([1.0, 1.0], dtype=np.float32),
        )
