import unittest

import numpy as np

from lsml.feature.provided import shape


class TestShapeFeatures(unittest.TestCase):

    def test_size_2d(self):

        x, dx = np.linspace(-2, 2, 701, retstep=True)
        y, dy = np.linspace(-2, 2, 901, retstep=True)

        xx, yy = np.meshgrid(x, y)

        z = 1 - np.sqrt(xx**2 + yy**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        size = shape.Size(ndim=2)
        area = size(u=z, mask=mask, dx=[dx, dy])

        self.assertAlmostEqual(np.pi, area[0, 0], places=2)

    def test_size_3d(self):

        x, dx = np.linspace(-2, 2, 401, retstep=True)
        y, dy = np.linspace(-2, 2, 301, retstep=True)
        z, dz = np.linspace(-2, 2, 501, retstep=True)

        xx, yy, zz = np.meshgrid(x, y, z)

        w = 1 - np.sqrt(xx**2 + yy**2 + zz**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        size = shape.Size(ndim=3)
        volume = size(u=w, mask=mask, dx=[dx, dy, dz])

        self.assertAlmostEqual(4 * np.pi / 3, volume[0, 0, 0], places=2)

    def test_boundary_size_2d(self):

        x, dx = np.linspace(-2, 2, 501, retstep=True)
        y, dy = np.linspace(-2, 2, 701, retstep=True)

        xx, yy = np.meshgrid(x, y)

        z = 1 - np.sqrt(xx**2 + yy**2)
        mask = np.zeros(z.shape, dtype=np.bool)
        mask.ravel()[0] = True

        boundary_size = shape.BoundarySize(ndim=2)
        curve_length = boundary_size(u=z, mask=mask, dx=[dx, dy])

        self.assertAlmostEqual(2*np.pi, curve_length[0, 0], places=4)

    def test_boundary_size_3d(self):

        x, dx = np.linspace(-2, 2, 501, retstep=True)
        y, dy = np.linspace(-2, 2, 401, retstep=True)
        z, dz = np.linspace(-2, 2, 601, retstep=True)

        xx, yy, zz = np.meshgrid(x, y, z)

        w = 1 - np.sqrt(xx**2 + yy**2 + zz**2)
        mask = np.zeros(w.shape, dtype=np.bool)
        mask.ravel()[0] = True

        boundary_size = shape.BoundarySize(ndim=3)
        surface_area = boundary_size(u=w, mask=mask, dx=[dx, dy, dz])

        self.assertAlmostEqual(4*np.pi, surface_area[0, 0, 0], places=0)

    def test_isoperimetric_2d(self):

        x, dx = np.linspace(-2, 2, 701, retstep=True)
        y, dy = np.linspace(-2, 2, 901, retstep=True)

        xx, yy = np.meshgrid(x, y)

        z = 1 - np.sqrt(xx**2 + yy**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        isoperm = shape.IsoperimetricRatio(ndim=2)
        ratio = isoperm(u=z, mask=mask, dx=[dx, dy])

        self.assertAlmostEqual(1, ratio[0, 0], places=3)

    def test_isoperimetric_3d(self):

        x, dx = np.linspace(-2, 2, 201, retstep=True)
        y, dy = np.linspace(-2, 2, 201, retstep=True)
        z, dz = np.linspace(-2, 2, 901, retstep=True)

        xx, yy, zz = np.meshgrid(x, y, z)

        w = 1 - np.sqrt(xx**2 + yy**2 + zz**2)
        mask = np.zeros(w.shape, dtype=np.bool)
        mask.ravel()[0] = True

        isoperm = shape.IsoperimetricRatio(ndim=3)
        ratio = isoperm(u=w, mask=mask, dx=[dx, dy, dz])

        self.assertAlmostEqual(1, ratio[0, 0, 0], places=2)

    def test_moment2d_order1(self):

        x, dx = np.linspace(-2, 2, 301, retstep=True)
        y, dy = np.linspace(-2, 2, 501, retstep=True)

        xx, yy = np.meshgrid(x, y)

        z = 1 - np.sqrt(xx**2 + yy**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        moments = shape.Moments(ndim=2, axes=[0, 1], orders=[1])

        center_of_mass = moments(u=z, mask=mask, dx=[dy, dx])
        center_of_mass = center_of_mass[mask].squeeze()

        self.assertAlmostEqual(2.0, center_of_mass[0], places=3)
        self.assertAlmostEqual(2.0, center_of_mass[1], places=3)

    def test_moment2d_order1_off_center(self):

        x, dx = np.linspace(-2, 2, 301, retstep=True)
        y, dy = np.linspace(-2, 2, 501, retstep=True)

        xx, yy = np.meshgrid(x, y)

        z = 1 - np.sqrt((xx-0.25)**2 + (yy+0.25)**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        moments = shape.Moments(ndim=2, axes=[0, 1], orders=[1])

        center_of_mass = moments(u=z, mask=mask, dx=[dy, dx])
        center_of_mass = center_of_mass[mask].squeeze()

        self.assertAlmostEqual(1.75, center_of_mass[0], places=3)
        self.assertAlmostEqual(2.25, center_of_mass[1], places=3)

    def test_moment2d_order2(self):

        x, dx = np.linspace(-2, 2, 301, retstep=True)
        y, dy = np.linspace(-2, 2, 201, retstep=True)

        xx, yy = np.meshgrid(x, y)

        z = 1 - np.sqrt(xx**2 + yy**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        moments = shape.Moments(ndim=2, axes=[0, 1], orders=[2])

        spread = moments(u=z, mask=mask, dx=[dy, dx])
        spread = spread[mask].squeeze()

        self.assertAlmostEqual(0.25, spread[0], places=2)
        self.assertAlmostEqual(0.25, spread[1], places=2)

    def test_moment3d_order1(self):

        x, dx = np.linspace(-2, 2, 301, retstep=True)
        y, dy = np.linspace(-2, 2, 501, retstep=True)
        z, dz = np.linspace(-2, 2, 401, retstep=True)

        xx, yy, zz = np.meshgrid(x, y, z)

        w = 1 - np.sqrt(xx**2 + yy**2 + zz**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        moments = shape.Moments(ndim=3, axes=[0, 1, 2], orders=[1])

        center_of_mass = moments(u=w, mask=mask, dx=[dy, dx, dz])
        center_of_mass = center_of_mass[mask].squeeze()

        self.assertAlmostEqual(2.0, center_of_mass[0], places=3)
        self.assertAlmostEqual(2.0, center_of_mass[1], places=3)
        self.assertAlmostEqual(2.0, center_of_mass[2], places=3)

    def test_moment3d_order1_off_center(self):

        x, dx = np.linspace(-2, 2, 301, retstep=True)
        y, dy = np.linspace(-2, 2, 501, retstep=True)
        z, dz = np.linspace(-2, 2, 401, retstep=True)

        xx, yy, zz = np.meshgrid(x, y, z)

        w = 1 - np.sqrt((xx-0.25)**2 + (yy+0.25)**2 + (zz-0.5)**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        moments = shape.Moments(ndim=3, axes=[0, 1, 2], orders=[1])

        center_of_mass = moments(u=w, mask=mask, dx=[dy, dx, dz])
        center_of_mass = center_of_mass[mask].squeeze()

        self.assertAlmostEqual(1.75, center_of_mass[0], places=3)
        self.assertAlmostEqual(2.25, center_of_mass[1], places=3)
        self.assertAlmostEqual(2.50, center_of_mass[2], places=3)

    def test_moment3d_order2(self):

        x, dx = np.linspace(-2, 2, 301, retstep=True)
        y, dy = np.linspace(-2, 2, 201, retstep=True)
        z, dz = np.linspace(-2, 2, 401, retstep=True)

        xx, yy, zz = np.meshgrid(x, y, z)

        w = 1 - np.sqrt(xx**2 + yy**2 + zz**2)
        mask = np.zeros(xx.shape, dtype=np.bool)
        mask.ravel()[0] = True

        moments = shape.Moments(ndim=3, axes=[0, 1, 2], orders=[2])

        spread = moments(u=w, mask=mask, dx=[dy, dx, dz])
        spread = spread[mask].squeeze()

        self.assertAlmostEqual(0.2, spread[0], places=2)
        self.assertAlmostEqual(0.2, spread[1], places=2)
        self.assertAlmostEqual(0.2, spread[2], places=2)
