# Módulo: gestion.py
# Propósito: Gestionar reservas, estados, persistencia de logs y manejo avanzado de excepciones.

from datetime import datetime
from excepciones import (
    ErrorSistemaFJ,
    DatoInvalidoError,
    ServicioNoDisponibleError,
    OperacionNoPermitidaError
)
from modelos import EntidadSistema, Cliente, Servicio


class Reserva(EntidadSistema):
    def __init__(self, id_reserva, cliente, servicio, duracion, impuesto=0.19, descuento=0.0):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Cliente.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere una instancia válida de Servicio.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible actualmente.")

        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._estado = "PENDIENTE"
        self._costo_total = servicio.calcular_costo(duracion, impuesto=impuesto, descuento=descuento)

    @property
    def estado(self):
        return self._estado

    @property
    def costo_total(self):
        return self._costo_total

    def confirmar(self):
        if self._estado != "PENDIENTE":
            raise OperacionNoPermitidaError(f"No se puede confirmar una reserva en estado '{self._estado}'.")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self._servicio.nombre}' ya fue ocupado por otra reserva.")
        
        self._estado = "CONFIRMADA"
        self._servicio.disponible = False

    def cancelar(self):
        if self._estado == "PROCESADA":
            raise OperacionNoPermitidaError("No es posible cancelar una reserva que ya fue procesada y facturada.")
        if self._estado == "CANCELADA":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")
        
        if self._estado == "CONFIRMADA":
            self._servicio.disponible = True
        self._estado = "CANCELADA"

    def procesar(self):
        if self._estado != "CONFIRMADA":
            raise OperacionNoPermitidaError(f"Solo se pueden procesar reservas CONFIRMADAS (estado actual: {self._estado}).")
        
        self._estado = "PROCESADA"
        self._servicio.disponible = True

    def obtener_resumen(self):
        return (
            f"Reserva [{self.id}] | Estado: {self._estado} | "
            f"Cliente: {self._cliente.nombre} | Servicio: {self._servicio.nombre} | "
            f"Duración: {self._duracion} | Total: ${self._costo_total:,.2f}"
        )


class SistemaSoftwareFJ:
    def __init__(self, archivo_log="eventos_software_fj.log"):
        self._clientes = []
        self._servicios = []
        self._reservas = []
        self._archivo_log = archivo_log
        self._registrar_log("INFO", "Sistema Software FJ inicializado correctamente en memoria.")

    def _registrar_log(self, nivel, mensaje):
        marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{marca_tiempo}] [{nivel}] {mensaje}\n"
        archivo = None
        try:
            archivo = open(self._archivo_log, "a", encoding="utf-8")
            archivo.write(linea)
        except OSError as e:
            print(f"[ALERTA CRÍTICA DE LOG]: No se pudo escribir en {self._archivo_log}: {e}")
        finally:
            if archivo:
                archivo.close()

    def registrar_cliente(self, id_cliente, nombre, correo, telefono):
        try:
            if any(c.id == str(id_cliente).strip() for c in self._clientes):
                raise DatoInvalidoError(f"Ya existe un cliente registrado con el ID '{id_cliente}'.")
            nuevo_cliente = Cliente(id_cliente, nombre, correo, telefono)
        except ErrorSistemaFJ as err:
            self._registrar_log("ERROR", f"[{err.codigo_error}] Fallo al registrar cliente: {err}")
            print(f"X Error controlado ({err.codigo_error}): {err}")
            return None
        else:
            self._clientes.append(nuevo_cliente)
            self._registrar_log("INFO", f"Cliente registrado exitosamente: {nuevo_cliente.obtener_resumen()}")
            print(f"✓ {nuevo_cliente.obtener_resumen()}")
            return nuevo_cliente
        finally:
            self._registrar_log("TRACE", f"Intento de registro de cliente '{id_cliente}' finalizado.")

    def registrar_servicio(self, servicio):
        try:
            if not isinstance(servicio, Servicio):
                raise DatoInvalidoError("El objeto proporcionado no es un Servicio válido.")
            if any(s.id == servicio.id for s in self._servicios):
                raise DatoInvalidoError(f"Ya existe un servicio con el ID '{servicio.id}'.")
            self._servicios.append(servicio)
            self._registrar_log("INFO", f"Servicio agregado: {servicio.obtener_resumen()}")
            print(f"✓ {servicio.obtener_resumen()}")
            return servicio
        except ErrorSistemaFJ as err:
            self._registrar_log("ERROR", f"[{err.codigo_error}] Fallo al registrar servicio: {err}")
            print(f"X Error controlado ({err.codigo_error}): {err}")
            return None

    def crear_reserva(self, id_reserva, id_cliente, id_servicio, duracion, impuesto=0.19, descuento=0.0):
        try:
            try:
                cliente = next(c for c in self._clientes if c.id == id_cliente)
            except StopIteration as exc:
                raise DatoInvalidoError(f"No se encontró el cliente con ID '{id_cliente}'.") from exc

            try:
                servicio = next(s for s in self._servicios if s.id == id_servicio)
            except StopIteration as exc:
                raise DatoInvalidoError(f"No se encontró el servicio con ID '{id_servicio}'.") from exc

            if any(r.id == id_reserva for r in self._reservas):
                raise DatoInvalidoError(f"El ID de reserva '{id_reserva}' ya está en uso.")

            reserva = Reserva(id_reserva, cliente, servicio, duracion, impuesto, descuento)
            self._reservas.append(reserva)
            self._registrar_log("INFO", f"Reserva creada: {reserva.obtener_resumen()}")
            print(f"✓ {reserva.obtener_resumen()}")
            return reserva

        except ErrorSistemaFJ as err:
            causa = f" | Causa original: {type(err.__cause__).__name__}" if err.__cause__ else ""
            self._registrar_log("ERROR", f"[{err.codigo_error}] Error en reserva '{id_reserva}': {err}{causa}")
            print(f"X Error controlado en reserva ({err.codigo_error}): {err}")
            return None

    def gestionar_estado_reserva(self, id_reserva, accion):
        try:
            reserva = next((r for r in self._reservas if r.id == id_reserva), None)
            if reserva is None:
                raise DatoInvalidoError(f"La reserva '{id_reserva}' no existe en el sistema.")

            accion_norm = accion.strip().lower()
            if accion_norm == "confirmar":
                reserva.confirmar()
            elif accion_norm == "cancelar":
                reserva.cancelar()
            elif accion_norm == "procesar":
                reserva.procesar()
            else:
                raise OperacionNoPermitidaError(f"Acción desconocida '{accion}'. Use confirmar, cancelar o procesar.")

            self._registrar_log("INFO", f"Reserva '{id_reserva}' actualizada a estado {reserva.estado}.")
            print(f"✓ Reserva [{id_reserva}] ahora está en estado: {reserva.estado}")
        except ErrorSistemaFJ as err:
            self._registrar_log("ERROR", f"[{err.codigo_error}] Fallo al {accion} reserva '{id_reserva}': {err}")
            print(f"X Error controlado ({err.codigo_error}): {err}")
