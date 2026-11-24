import sqlite3
import tkinter as tk

BASE = "miBaseDeDatos.db"
ARCHIVO = "asistentes.csv"

eventos = ["Concierto Kanye West", "Concierto Taylor Swift", "Concierto Peso Pluma", "Master Class Temach"]
tipos = ["VIP", "Fan", "General"]
estados = ["Confirmado", "Pendiente", "Cancelado"]

seleccion = {"evento": "", "tipo": ""}


def crearTabla():
    db = sqlite3.connect(BASE)
    cursor = db.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS asistentes (folio INTEGER PRIMARY KEY, nombre TEXT, evento TEXT, tipo TEXT, estado TEXT)")
    db.commit()
    db.close()


def agregar(nombre, evento, tipo, estado):
    db = sqlite3.connect(BASE)
    cursor = db.cursor()
    cursor.execute("INSERT INTO asistentes (nombre, evento, tipo, estado) VALUES (?,?,?,?)", (nombre, evento, tipo, estado))
    folio = cursor.lastrowid
    db.commit()
    db.close()
    return folio


def obtenerRegistros():
    db = sqlite3.connect(BASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM asistentes")
    registros = cursor.fetchall()
    db.close()
    return registros


def consultarFolio(folio):
    db = sqlite3.connect(BASE)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM asistentes WHERE folio = ?", (folio,))
    registros = cursor.fetchall()
    db.close()
    return registros


def actualizarEstado(folio, estado):
    db = sqlite3.connect(BASE)
    cursor = db.cursor()
    cursor.execute("UPDATE asistentes SET estado = ? WHERE folio = ?", (estado, folio))
    db.commit()
    db.close()


def guardarArchivo():
    registros = obtenerRegistros()
    archivo = open(ARCHIVO, "w")
    archivo.write("folio,nombre,evento,tipo,estado\n")
    for r in registros:
        archivo.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n")
    archivo.close()


def buscarOpcion(texto, opciones):
    texto = texto.strip().lower()
    for opcion in opciones:
        if texto == opcion.lower():
            return opcion
    return None


def formatoRegistro(r):
    return f"Folio: {r[0]} | Nombre: {r[1]} | Evento: {r[2]} | Entrada: {r[3]} | Estado: {r[4]}"


def elegirEvento(evento):
    seleccion["evento"] = evento
    etiquetaEvento.config(text="Evento elegido: " + evento)


def elegirTipo(tipo):
    seleccion["tipo"] = tipo
    etiquetaTipo.config(text="Tipo elegido: " + tipo)


def registrarAsistente():
    nombre = entradaNombre.get().strip().title()
    evento = seleccion["evento"]
    tipo = seleccion["tipo"]
    estado = buscarOpcion(entradaEstado.get(), estados)
    if not nombre.replace(" ", "").isalpha():
        resultado.config(text="Nombre inválido: escribe solo letras")
    elif evento == "":
        resultado.config(text="Elige un evento")
    elif tipo == "":
        resultado.config(text="Elige un tipo de entrada")
    elif estado is None:
        resultado.config(text="Estado inválido. Opciones: " + ", ".join(estados))
    else:
        folio = agregar(nombre, evento, tipo, estado)
        guardarArchivo()
        resultado.config(text=f"Asistente registrado con el folio {folio}")
        for entrada in [entradaNombre, entradaEstado]:
            entrada.delete(0, tk.END)
        seleccion["evento"] = ""
        seleccion["tipo"] = ""
        etiquetaEvento.config(text="Evento elegido: ninguno")
        etiquetaTipo.config(text="Tipo elegido: ninguno")


def mostrarRegistros():
    registros = obtenerRegistros()
    if len(registros) == 0:
        resultado.config(text="No hay asistentes registrados")
    else:
        lineas = []
        for r in registros:
            lineas.append(formatoRegistro(r))
        resultado.config(text="\n".join(lineas))


def buscarAsistente():
    try:
        folio = int(entradaFolio.get())
    except ValueError:
        resultado.config(text="Folio inválido: escribe solo números enteros")
        return
    registros = consultarFolio(folio)
    if len(registros) == 0:
        resultado.config(text="No se encontró ningún asistente con ese folio")
    else:
        resultado.config(text=formatoRegistro(registros[0]))


def modificarEstado():
    try:
        folio = int(entradaFolio.get())
    except ValueError:
        resultado.config(text="Folio inválido: escribe solo números enteros")
        return
    estado = buscarOpcion(entradaNuevoEstado.get(), estados)
    if estado is None:
        resultado.config(text="Estado inválido. Opciones: " + ", ".join(estados))
    elif len(consultarFolio(folio)) == 0:
        resultado.config(text="No se encontró ningún asistente con ese folio")
    else:
        actualizarEstado(folio, estado)
        guardarArchivo()
        resultado.config(text=f"Estado del folio {folio} actualizado a {estado}")


def resumenPorTipo():
    registros = obtenerRegistros()
    conteo = {}
    for t in tipos:
        conteo[t] = 0
    for r in registros:
        conteo[r[3]] += 1
    texto = f"Total de asistentes registrados: {len(registros)}\nAsistentes por tipo de entrada:"
    for t in tipos:
        texto += f"\n{t}: {conteo[t]}"
    resultado.config(text=texto)


def salir():
    ventana.destroy()


crearTabla()
guardarArchivo()

ventana = tk.Tk()
ventana.title("Registro de asistentes a eventos")

tk.Label(ventana, text="Sistema de registro de asistentes a eventos").grid(row=0, column=0, columnspan=5, pady=10)

tk.Label(ventana, text="Nombre").grid(row=1, column=0, sticky="w", padx=5, pady=3)
entradaNombre = tk.Entry(ventana, width=30)
entradaNombre.grid(row=1, column=1, padx=5, pady=3)

tk.Label(ventana, text="Evento").grid(row=2, column=0, sticky="w", padx=5, pady=3)
columna = 1
for nombreEvento in eventos:
    tk.Button(ventana, text=nombreEvento, command=lambda opcion=nombreEvento: elegirEvento(opcion)).grid(row=2, column=columna, padx=5, pady=3)
    columna += 1
etiquetaEvento = tk.Label(ventana, text="Evento elegido: ninguno")
etiquetaEvento.grid(row=3, column=1, columnspan=4, sticky="w", padx=5)

tk.Label(ventana, text="Tipo de entrada").grid(row=4, column=0, sticky="w", padx=5, pady=3)
columna = 1
for nombreTipo in tipos:
    tk.Button(ventana, text=nombreTipo, command=lambda opcion=nombreTipo: elegirTipo(opcion)).grid(row=4, column=columna, padx=5, pady=3)
    columna += 1
etiquetaTipo = tk.Label(ventana, text="Tipo elegido: ninguno")
etiquetaTipo.grid(row=5, column=1, columnspan=4, sticky="w", padx=5)

tk.Label(ventana, text="Estado de registro").grid(row=6, column=0, sticky="w", padx=5, pady=3)
entradaEstado = tk.Entry(ventana, width=30)
entradaEstado.grid(row=6, column=1, padx=5, pady=3)
tk.Label(ventana, text=" / ".join(estados)).grid(row=6, column=2, columnspan=3, sticky="w", padx=5)

tk.Button(ventana, text="Registrar asistente", command=registrarAsistente).grid(row=7, column=0, columnspan=5, pady=8)

tk.Label(ventana, text="Folio").grid(row=8, column=0, sticky="w", padx=5, pady=3)
entradaFolio = tk.Entry(ventana, width=30)
entradaFolio.grid(row=8, column=1, padx=5, pady=3)
tk.Button(ventana, text="Buscar por folio", command=buscarAsistente).grid(row=8, column=2, sticky="w", padx=5)

tk.Label(ventana, text="Nuevo estado").grid(row=9, column=0, sticky="w", padx=5, pady=3)
entradaNuevoEstado = tk.Entry(ventana, width=30)
entradaNuevoEstado.grid(row=9, column=1, padx=5, pady=3)
tk.Button(ventana, text="Actualizar estado", command=modificarEstado).grid(row=9, column=2, sticky="w", padx=5)

tk.Button(ventana, text="Mostrar registros", command=mostrarRegistros).grid(row=10, column=0, pady=8)
tk.Button(ventana, text="Resumen por tipo de entrada", command=resumenPorTipo).grid(row=10, column=1, pady=8)
tk.Button(ventana, text="Salir", command=salir).grid(row=10, column=2, pady=8)

resultado = tk.Label(ventana, text="", justify="left")
resultado.grid(row=11, column=0, columnspan=5, padx=5, pady=10)

ventana.mainloop()