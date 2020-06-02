import numpy as np


class Transform:
    def __init__(self, C_ba, r_ab_inb):
        self.C_ba = C_ba
        self.r_ab_inb = r_ab_inb

    def __mul__(self, other):
        if other.__class__ == Transform:
            return Transform(self.C_ba.dot(other.C_ba), self.r_ab_inb + self.C_ba.dot(other.r_ab_inb))
        elif other.__class__ == np.ndarray:
            if other.shape in [(3, 1), (3,)]:
                return self.C_ba.dot(other) + self.r_ab_inb
            elif other.shape == (1, 3):
                return self.C_ba.dot(other.T) + self.r_ab_inb
            else:
                raise NotImplementedError("Cannot multiply with array of shape " + str(other.shape))
        else:
            raise NotImplementedError("Cannot multiply with type " + str(other.__class__))

    def inv(self):
        return Transform(self.C_ba.T, -self.C_ba.T.dot(self.r_ab_inb))

    @property
    def matrix(self):
        rval = np.eye(4)
        rval[:3, :3] = self.C_ba
        rval[:3, 3] = self.r_ab_inb

        return rval

    def __repr__(self):
        return str(self.matrix)

    @property
    def phi(self):
        # Get angle
        phi_ba = np.arccos(0.5*(self.C_ba.trace()-1.0))
        sinphi_ba = np.sin(phi_ba)

        if abs(sinphi_ba) > 1e-9:

            # General case, angle is NOT near 0, pi, or 2*pi
            axis = np.array([self.C_ba[2, 1] - self.C_ba[1, 2],
                             self.C_ba[0, 2] - self.C_ba[2, 0],
                             self.C_ba[1, 0] - self.C_ba[0, 1]])
            return (0.5*phi_ba/sinphi_ba)*axis

        elif abs(phi_ba) > 1e-9:
            # Angle is near pi or 2*pi
            # ** Note with this method we do not know the sign of 'phi', however since we know phi is
            #    close to pi or 2*pi, the sign is unimportant..

            # Find the eigenvalues and eigenvectors
            y, v = np.linalg.eig(self.C_ba)

            # Try each eigenvalue
            for i in range(3):
                # Check if eigen value is near +1.0
                if abs(y[i] - 1.0) < 1e-6:
                    # Get corresponding angle-axis
                    return phi_ba*v[i]

            # Runtime error
            raise RuntimeError("so3 logarithmic map failed to find an axis-angle, "
                               "angle was near pi, or 2*pi, but no eigenvalues were near 1")

        else:
            # Angle is near zero
            return np.zeros((3,))
