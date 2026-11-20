# Módulo: modelos.py
# Propósito: Implementar abstracción, encapsulación, herencia, polimorfismo y sobrecarga de métodos.

from abc import ABC, abstractmethod
from excepciones import DatoInvalidoError, CalculoInconsistenteError


class EntidadSistema(ABC):
    def __init__(self, id_entidad):
        if not id_entidad or not str(id_entidad).strip():
            raise DatoInvalidoError("El identificador de la entidad no puede estar vacío.")
        self._id = str(id_entidad).strip()

    @property
    def id(self):
        return self._id

    @abstractmethod
    def obtener_resumen(self):
        pass


class Cliente(EntidadSistema):
    def __init__(self, id_cliente, nombre, correo, telefono):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError(f"Nombre de cliente inválido: '{valor}'. Debe tener al menos 3 letras.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or "@" not in valor or "." not in valor.split("@")[-1]:
            raise DatoInvalidoError(f"Formato de correo inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        limpio = str(valor).strip()
        if not limpio.isdigit() or len(limpio) < 7:
            raise DatoInvalidoError(f"Teléfono inválido: '{valor}'. Debe contener al menos 7 dígitos numéricos.")
        self._telefono = limpio

    def obtener_resumen(self):
        return f"Cliente [{self.id}]: {self._nombre} | Email: {self._correo} | Tel: {self._telefono}"


class Servicio(EntidadSistema, ABC):
    def __init__(self, id_servicio, nombre, tarifa_base, disponible=True):
        super().__init__(id_servicio)
        if not nombre or len(str(nombre).strip()) < 3:
            raise DatoInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise CalculoInconsistenteError(f"La tarifa base ({tarifa_base}) debe ser mayor a cero.")
        
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    @disponible.setter
    def disponible(self, estado):
        if not isinstance(estado, bool):
            raise DatoInvalidoError("El estado de disponibilidad debe ser True o False.")
        self._disponible = estado

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0.19, descuento=0.0):
        pass

    def _aplicar_impuestos_y_descuentos(self, subtotal, impuesto, descuento):
        if not (0 <= impuesto <= 1) or not (0 <= descuento < 1):
            raise CalculoInconsistenteError("Impuesto o descuento fuera de rango permitido (0.0 a 1.0).")
        con_descuento = subtotal * (1 - descuento)
        total = round(con_descuento * (1 + impuesto), 2)
        if total <= 0:
            raise CalculoInconsistenteError("El cálculo final arrojó un valor menor o igual a cero.")
        return total


class ReservaSala(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_hora, capacidad_personas, disponible=True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if not isinstance(capacidad_personas, int) or capacidad_personas <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self._capacidad = capacidad_personas

    def validar_parametros(self, duracion):
        if not isinstance(duracion, int) or duracion < 1 or duracion > 12:
            raise DatoInvalidoError(f"Duración inválida para sala ({duracion}h). Debe ser entre 1 y 12 horas enteras.")

    def calcular_costo(self, duracion, impuesto=0.19, descuento=0.0):
        self.validar_parametros(duracion)
        subtotal = self._tarifa_base * duracion
        if self._capacidad > 20:
            subtotal *= 1.10
        return self._aplicar_impuestos_y_descuentos(subtotal, impuesto, descuento)

    def obtener_resumen(self):
        estado = "Disponible" if self._disponible else "Ocupada"
        return f"Sala [{self.id}]: {self._nombre} (Cap: {self._capacidad} pers.) - ${self._tarifa_base}/h [{estado}]"


class AlquilerEquipo(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_dia, requiere_seguro=True, disponible=True):
        super().__init__(id_servicio, nombre, tarifa_dia, disponible)
        self._requiere_seguro = bool(requiere_seguro)

    def validar_parametros(self, duracion):
        if not isinstance(duracion, int) or duracion < 1 or duracion > 30:
            raise DatoInvalidoError(f"Duración inválida para equipo ({duracion} días). Rango permitido: 1 a 30 días.")

    def calcular_costo(self, duracion, impuesto=0.19, descuento=0.0):
        self.validar_parametros(duracion)
        subtotal = self._tarifa_base * duracion
        if self._requiere_seguro:
            subtotal += 15000 * duracion
        return self._aplicar_impuestos_y_descuentos(subtotal, impuesto, descuento)

    def obtener_resumen(self):
        estado = "Disponible" if self._disponible else "Alquilado"
        seguro = "Con seguro" if self._requiere_seguro else "Sin seguro"
        return f"Equipo [{self.id}]: {self._nombre} ({seguro}) - ${self._tarifa_base}/día [{estado}]"


class AsesoriaEspecializada(Servicio):
    def __init__(self, id_servicio, nombre, tarifa_hora, especialidad, disponible=True):
        super().__init__(id_servicio, nombre, tarifa_hora, disponible)
        if not especialidad or len(str(especialidad).strip()) < 3:
            raise DatoInvalidoError("Debe indicar una especialidad técnica válida.")
        self._especialidad = especialidad.strip()

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion < 1 or duracion > 40:
            raise DatoInvalidoError(f"Duración de asesoría inválida ({duracion}h). Debe estar entre 1 y 40 horas.")

    def calcular_costo(self, duracion, impuesto=0.19, descuento=0.0):
        self.validar_parametros(duracion)
        subtotal = self._tarifa_base * duracion
        return self._aplicar_impuestos_y_descuentos(subtotal, impuesto, descuento)

    def obtener_resumen(self):
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Asesoría [{self.id}]: {self._nombre} ({self._especialidad}) - ${self._tarifa_base}/h [{estado}]"
