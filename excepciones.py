# Módulo: excepciones.py
# Propósito: Definir la jerarquía de excepciones personalizadas para el sistema Software FJ.

class ErrorSistemaFJ(Exception):
    def __init__(self, mensaje, codigo_error="ERR-000"):
        super().__init__(mensaje)
        self.codigo_error = codigo_error


class DatoInvalidoError(ErrorSistemaFJ):
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo_error="ERR-DATO")


class ServicioNoDisponibleError(ErrorSistemaFJ):
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo_error="ERR-DISP")


class OperacionNoPermitidaError(ErrorSistemaFJ):
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo_error="ERR-OPER")


class CalculoInconsistenteError(ErrorSistemaFJ):
    def __init__(self, mensaje):
        super().__init__(mensaje, codigo_error="ERR-CALC")
