"""Main module."""

from math import sqrt, sin, cos, pi, atan
import math
import numpy as np


class NotEnoughArgumentError(Exception):
    """Exception raised when too few arguments where passed to function."""

    pass


class OverDeterminedError(Exception):
    """Raised when too many arguments where passed.
    So the system is over-determined."""

    pass


class Material2D:
    class NotAnisotropicError(Exception):
        pass

    class NotIsotropicError(Exception):
        pass

    def __init__(self, rho, E_para, E_ortho, G, v_para_ortho, label="material"):
        super().__init__()
        self.rho = rho
        self.label = label
        self.E_para = E_para
        self.E_ortho = E_ortho
        self.G = G
        self.v_para_ortho = v_para_ortho
        self.calc_poissonRatio_ortho_pata()
        self.calc_stiffness_compliance_matrices()

    def calc_poissonRatio_ortho_pata(self):
        self.v_ortho_para = self.v_para_ortho * self.E_ortho / self.E_para

    def calc_stiffness_compliance_matrices(self):
        s_para = 1 / self.E_para
        s_ortho = 1 / self.E_ortho
        s_para_ortho = -self.v_ortho_para / self.E_ortho
        s_ortho_para = -self.v_para_ortho / self.E_para
        s_shear = 1 / self.G

        self.complianceMatrix = np.array(
            [[s_para, s_para_ortho, 0], [s_para_ortho, s_ortho, 0], [0, 0, s_shear]]
        )
        self.stiffnessMatrix = np.linalg.inv(self.complianceMatrix)


class IsotropicMaterial(Material2D):
    def __init__(self, rho, E=None, G=None, v=None, label="material"):
        if (G is not None) and (v is not None) and (E is not None):
            raise OverDeterminedError()
        elif (
            ((G is None) and (v is None))
            or ((G is None) and (E is None))
            or ((E is None) and (v is None))
        ):
            raise NotEnoughArgumentError()
        elif G is None:
            G = E / (2 * (1 + v))
        elif E is None:
            E = 2 * G * (1 + v)
        elif v is None:
            v = E / (2 * G) - 1
        super().__init__(rho=rho, E_para=E, E_ortho=E, G=G, v_para_ortho=v, label=label)


class AnisotropicMaterial(Material2D):
    pass


GLOBAL_FRM_LIST = []


class FiberReinforcedMaterialUD(Material2D):

    system = "hsb"  # "prismatic_jones" or "hsb"
    possible_systems = ["prismatic_jones", "hsb"]

    def __init__(
        self,
        matFib,
        matMat,
        fibVolRatio=0.5,
        kapa=[1.0, 1.0, 1.0],
        label="FRM_material",
    ):
        """Fiber Reinforced Material containing of isotropic matrix and anisotropic fiber.

        :param matFib: fiber material
        :type matFib: AnisotropicMaterial
        :param matMat: matrix material
        :type matMat: IsotropicMaterial
        :param fibVolRatio: fiber-volume-ratio [0,1], defaults to 0.5
        :type fibVolRatio: float, optional
        :param kapa: manufactoring reduction factor. \
            kapa[0]: reduction for E_para (Youngs modulus in fiber axis). \
            kapa[1]: reduction for E_ortho. \
            kapa[2]: reduction for G (shear modulus). \
            Values in range (0,1]., defaults to [1, 1, 1]
        :type kapa: list, optional
        :param label: description of material, defaults to "FRM_material"
        :type label: str, optional
        :raises ValueError: Not defined value for this input
        :raises Material2D.NotAnisotropicError: AnisotropicMaterial required
        :raises Material2D.NotIsotropicError: IsotropicMaterial required
        """
        GLOBAL_FRM_LIST.append(self)
        self.check_matFib(matFib)
        self.matFib = matFib
        self.check_matMat(matMat)
        self.matMat = matMat
        self.fibVolRatio = fibVolRatio
        self.kapa = kapa
        self.update()
        super().__init__(
            rho=self.rho,
            E_para=self.E_para,
            E_ortho=self.E_ortho,
            G=self.G,
            v_para_ortho=self.v_para_ortho,
            label=label,
        )

    @classmethod
    def set_system(cls, system):
        if system not in cls.possible_systems:
            raise ValueError("'{system}'-system is not implemented")
        cls.system = system
        for elem in GLOBAL_FRM_LIST:
            elem.update()

    def set_fibWgRatio(self, fibWgRatio):
        self.fibVolRatio = (fibWgRatio * self.matMat.rho) / (
            fibWgRatio * self.matMat.rho + (1 - fibWgRatio) * self.matFib.rho
        )
        self.update()

    def set_fibVolRatio(self, fibVolRatio):
        self.fibVolRatio = fibVolRatio
        self.update()

    def set_matFib(self, matFib):
        self.check_matFib(matFib)
        self.matFib = matFib
        self.update()

    def set_matMat(self, matMat):
        self.check_matMat(matMat)
        self.matMat = matMat
        self.update()

    def set_kapa(self, kapa):
        if isinstance(kapa, list):
            if len(kapa) == 3:
                self.kapa = kapa
            else:
                raise IndexError()
        else:
            raise TypeError()
        self.update()

    def check_matFib(self, matFib):
        if not isinstance(matFib, AnisotropicMaterial):
            raise Material2D.NotAnisotropicError()

    def check_matMat(self, matMat):
        if not isinstance(matMat, IsotropicMaterial):
            raise Material2D.NotIsotropicError()

    def update(self):
        if self.system == self.possible_systems[0]:
            self.prismatic_jones_model()
        elif self.system == self.possible_systems[1]:
            self.hsb_model()
        self.calc_stiffness_compliance_matrices()

    def prismatic_jones_model(self):
        self.E_para = self.matFib.E_para * self.fibVolRatio + self.matMat.E_para * (
            1 - self.fibVolRatio
        )
        self.E_ortho = (self.matFib.E_ortho * self.matMat.E_para) / (
            self.matMat.E_para * self.fibVolRatio
            + self.matFib.E_ortho * (1 - self.fibVolRatio)
        )
        self.G = (self.matFib.G * self.matMat.G) / (
            self.matMat.G * self.fibVolRatio + self.matFib.G * (1 - self.fibVolRatio)
        )
        self.v_para_ortho = (
            self.fibVolRatio * self.matFib.v_para_ortho
            + (1 - self.fibVolRatio) * self.matMat.v_para_ortho
        )
        self.calc_poissonRatio_ortho_pata()
        self.calc_density()

    def hsb_model(self):
        # helping variables
        v = sqrt(self.fibVolRatio / pi)
        e = 1 - self.matMat.E_para / self.matFib.E_ortho
        g = 1 - self.matMat.G / self.matFib.G
        q_G = (1 + 2 * g * v) / (1 - 2 * g * v)
        q_E = (1 + 2 * e * v) / (1 - 2 * e * v)

        self.E_para = self.kapa[0] * (
            self.matFib.E_para * self.fibVolRatio
            + self.matMat.E_para * (1 - self.fibVolRatio)
        )
        self.E_ortho = (
            self.kapa[1]
            * self.matMat.E_para
            * (
                1
                - 2 * v
                - pi / (2 * e)
                + ((2 * atan(sqrt(q_E))) / (e * sqrt(1 - math.pow(2 * e * v, 2))))
            )
        )
        self.G = (
            self.kapa[2]
            * self.matMat.G
            * (
                1
                - 2 * v
                - pi / (2 * g)
                + ((2 * atan(sqrt(q_G))) / (g * sqrt(1 - math.pow(2 * g * v, 2))))
            )
        )
        self.v_para_ortho = (
            self.matFib.v_para_ortho * self.fibVolRatio
            + self.matMat.v_para_ortho * (1 - self.fibVolRatio)
        )
        self.calc_poissonRatio_ortho_pata()
        self.calc_density()

    def calc_density(self):
        self.rho = (
            self.fibVolRatio
            + self.matMat.rho / self.matFib.rho * (1 - self.fibVolRatio)
        ) * self.matFib.rho


class Ply:
    def __init__(self, material, thickness=1.0, rotation=0.0):
        """Ply for building Laminates.

        :param reinforcedMat: Material for ply (reinforced, isotropic)
        :type reinforcedMat: {FiberReinforcedMaterialUD, IsotropicMaterial}
        :param thickness: Thickness of layer/ply in mm, defaults to 1
        :type thickness: float, optional
        :param rotation: Rotation of ply in relation to laminate axis. \
            Unit=[°], defaults to 0
        :type rotation: float, optional
        """
        super().__init__()
        self.check_materialType(material)
        self.mat = material
        self.thickness = thickness
        self.rotRad = math.radians(rotation)
        self.update()

    def set_rotation(self, rotation):
        self.rotRad = math.radians(rotation)
        self.update()

    def update(self):
        self.calc_rotationElongationMatrix()
        self.calc_rotationStressMatrix()
        self.calc_stiffnessMatrix()
        self.calc_complianceMatrix()
        self.calc_engineer_constantes()

    def check_materialType(self, material):
        if isinstance(material, FiberReinforcedMaterialUD):
            self.matType = "fibReinfMat"
        elif isinstance(material, IsotropicMaterial):
            self.matType = "isotropicMat"
        else:
            raise TypeError(
                "material must either 'FiberReinforcedMaterialUD' or 'IsotropicMaterial'"
            )

    def calc_rotationStressMatrix(self):
        self.rotStress = np.array(
            [
                [
                    (cos(self.rotRad)) ** 2,
                    (sin(self.rotRad)) ** 2,
                    2 * sin(self.rotRad) * cos(self.rotRad),
                ],
                [
                    (sin(self.rotRad)) ** 2,
                    (cos(self.rotRad)) ** 2,
                    -2 * sin(self.rotRad) * cos(self.rotRad),
                ],
                [
                    -sin(self.rotRad) * cos(self.rotRad),
                    sin(self.rotRad) * cos(self.rotRad),
                    (cos(self.rotRad)) ** 2 - (sin(self.rotRad)) ** 2,
                ],
            ]
        )

    def calc_rotationElongationMatrix(self):
        self.rotElongation = np.array(
            [
                [
                    (cos(self.rotRad)) ** 2,
                    (sin(self.rotRad)) ** 2,
                    sin(self.rotRad) * cos(self.rotRad),
                ],
                [
                    (sin(self.rotRad)) ** 2,
                    (cos(self.rotRad)) ** 2,
                    -sin(self.rotRad) * cos(self.rotRad),
                ],
                [
                    -2 * sin(self.rotRad) * cos(self.rotRad),
                    2 * sin(self.rotRad) * cos(self.rotRad),
                    (cos(self.rotRad)) ** 2 - (sin(self.rotRad)) ** 2,
                ],
            ]
        )

    def calc_complianceMatrix(self):
        self.S = np.matmul(
            self.rotElongation,
            np.matmul(self.mat.complianceMatrix, np.linalg.inv(self.rotStress)),
        )

    def calc_stiffnessMatrix(self):
        self.Q = np.matmul(
            self.rotStress,
            np.matmul(self.mat.stiffnessMatrix, np.linalg.inv(self.rotElongation)),
        )

    def calc_engineer_constantes(self):
        self.E_1 = 1 / self.S[0, 0]
        self.E_2 = 1 / self.S[1, 1]
        self.G = 1 / self.S[2, 2]
        self.v_12 = -self.E_1 * self.S[0, 1]


class Laminate:
    def __init__(self, symetric=False):
        super().__init__()
        self.symetric = symetric
        self.stack = []
        self.stack2 = []
        self.core = False
        self.move_reference_plane = True
        self.update()

    def addPly(self, ply):
        if isinstance(ply, Ply):
            if not self.core:
                self.stack.append(ply)
            else:
                self.stack2.append(ply)
        else:
            raise TypeError()
        self.update()

    def addCore(self, ply):
        if isinstance(ply, Ply):
            self.corePly = ply
        else:
            raise TypeError()
        self.core = True
        self.update()

    def update(self):
        self.create_finalStack()
        self.calc_z_positions()
        self.calc_completeStiffnessmatrix()

    def set_move_reference_plane(self, boolean):
        self.move_reference_plane = boolean
        self.update()

    def create_finalStack(self):
        if self.core and self.symetric:
            self.finalStack = self.stack + [self.corePly] + self.stack[::-1]
        elif self.symetric:
            self.finalStack = self.stack + self.stack[::-1]
        elif self.core:
            self.finalStack = self.stack + [self.corePly] + self.stack2
        else:
            self.finalStack = self.stack

    def get_finalStack(self):
        return self.finalStack

    def calc_z_positions(self):
        z = [0]
        for ply in self.finalStack:
            z.append(ply.thickness + z[-1])
        if self.move_reference_plane:
            t_ges = z[-1] - z[0]
            self.z_position = [(z_i - t_ges / 2) for z_i in z]
        else:
            self.z_position = z

    def get_z_positions(self):
        return self.z_position

    def calc_completeStiffnessmatrix(self):
        # A matrix: extensional stiffnesses
        A = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                for k_ply in range(len(self.finalStack)):
                    A[i, j] += self.finalStack[k_ply].Q[i, j] * (
                        self.z_position[k_ply + 1] - self.z_position[k_ply]
                    )

        # B matrix: bending-extension coupling stiffnesses
        B = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                for k_ply in range(len(self.finalStack)):
                    B[i, j] += (
                        -self.finalStack[k_ply].Q[i, j]
                        * 0.5
                        * (
                            self.z_position[k_ply + 1] ** 2
                            - self.z_position[k_ply] ** 2
                        )
                    )
        # D matrix: bending stiffnesses
        D = np.zeros((3, 3))
        for i in range(3):
            for j in range(3):
                for k_ply in range(len(self.finalStack)):
                    D[i, j] += (
                        self.finalStack[k_ply].Q[i, j]
                        * 1
                        / 3
                        * (
                            self.z_position[k_ply + 1] ** 3
                            - self.z_position[k_ply] ** 3
                        )
                    )

        self.stiffnessMatrix = np.block([[A, B], [B, D]])

    def get_stiffnessMatrix(self):
        return self.stiffnessMatrix
