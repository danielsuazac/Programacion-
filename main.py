# Módulo: main.py
# Propósito: Ejecutar simulación integral de 15 operaciones para demostrar la estabilidad de Software FJ.

from excepciones import ErrorSistemaFJ
from modelos import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from gestion import SistemaSoftwareFJ


def ejecutar_simulacion():
    print("=================================================================")
    print("   SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ (SIN BASE DE DATOS) ")
    print("=================================================================\n")

    sistema = SistemaSoftwareFJ("eventos_software_fj.log")

    print("--- 1. REGISTRO DE CLIENTES (VÁLIDOS E INVÁLIDOS) ---")
    sistema.registrar_cliente("C-01", "Laura Gómez", "laura.gomez@correo.com", "3104567890")
    sistema.registrar_cliente("C-02", "Carlos Méndez", "cmendez@empresa.co", "3209876543")
    sistema.registrar_cliente("C-03", "Ana", "correo_sin_arroba", "123")
    sistema.registrar_cliente("C-01", "Laura Duplicada", "otra@correo.com", "3001112233")

    print("\n--- 2. CREACIÓN DE SERVICIOS ESPECIALIZADOS (POLIMORFISMO) ---")
    sala_juntas = ReservaSala("S-01", "Sala Innovación A", 80000, capacidad_personas=25)
    sistema.registrar_servicio(sala_juntas)

    servidor_portatil = AlquilerEquipo("S-02", "Estación Workstation Dell", 120000, requiere_seguro=True)
    sistema.registrar_servicio(servidor_portatil)

    asesoria_seguridad = AsesoriaEspecializada("S-03", "Auditoría Ciberseguridad", 150000, "Seguridad Informática")
    sistema.registrar_servicio(asesoria_seguridad)

    try:
        servicio_erroneo = ReservaSala("S-04", "Sala Fantasma", -50000, capacidad_personas=10)
        sistema.registrar_servicio(servicio_erroneo)
    except ErrorSistemaFJ as err:
        sistema._registrar_log("ERROR", f"[{err.codigo_error}] Error al instanciar servicio: {err}")
        print(f"X Error controlado al instanciar servicio ({err.codigo_error}): {err}")

    print("\n--- 3. GESTIÓN DE RESERVAS Y SOBRECARGA DE CÁLCULOS ---")
    sistema.crear_reserva("R-101", "C-01", "S-01", duracion=3)
    sistema.crear_reserva("R-102", "C-02", "S-02", duracion=4, impuesto=0.19, descuento=0.10)
    sistema.crear_reserva("R-103", "C-99", "S-03", duracion=2)
    sistema.crear_reserva("R-104", "C-01", "S-01", duracion=20)

    print("\n--- 4. CICLO DE VIDA DE RESERVAS Y CONTROL DE DISPONIBILIDAD ---")
    sistema.gestionar_estado_reserva("R-101", "confirmar")
    sistema.crear_reserva("R-105", "C-02", "S-01", duracion=2)
    sistema.gestionar_estado_reserva("R-101", "procesar")
    sistema.gestionar_estado_reserva("R-101", "cancelar")
    sistema.crear_reserva("R-106", "C-02", "S-01", duracion=2, impuesto=0.0, descuento=0.05)

    print("\n=================================================================")
    print(" Simulación finalizada sin interrupciones.")
    print(" Revisa el archivo 'eventos_software_fj.log' para ver la auditoría.")
    print("=================================================================")


if __name__ == "__main__":
    ejecutar_simulacion()
