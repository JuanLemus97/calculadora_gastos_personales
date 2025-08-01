from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
import json
import os
import csv
import io

app = Flask(__name__)
ARCHIVO = "gastos.json"

# Cargar datos
def cargar_gastos():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    return []

# Guardar datos
def guardar_gastos(gastos):
    with open(ARCHIVO, "w") as f:
        json.dump(gastos, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        categoria = request.form["categoria"]
        monto = float(request.form["monto"])
        fecha = datetime.today().strftime("%d-%m-%Y")
        descripcion = request.form["descripcion"]
        gastos = cargar_gastos()
        gastos.append({"categoria": categoria, "monto": monto, "fecha": fecha, "descripcion": descripcion})
        guardar_gastos(gastos)
        return redirect(url_for("gastos"))
    return render_template("agregar.html")

@app.route("/gastos")
def gastos():
    gastos = cargar_gastos()
    return render_template("gastos.html", gastos=gastos)

@app.route("/eliminar/<int:idx>")
def eliminar(idx):
    gastos = cargar_gastos()
    # Validar índice
    if 0 <= len(gastos):
        gastos.pop(idx)
        guardar_gastos(gastos)
    return redirect(url_for("gastos"))

@app.route("/totales")
def totales():
    gastos = cargar_gastos()
    resumen = {}
    for gasto in gastos:
        categoria = gasto["categoria"]
        monto = gasto["monto"]
        resumen[categoria] = resumen.get(categoria, 0) + monto
    return render_template("totales.html", resumen=resumen)

@app.route("/descargar")
def descargar():
    gastos = cargar_gastos()

    # Usamos StringIO como buffer temporal
    output = io.StringIO()
    writer = csv.writer(output)

    # Encabezados
    writer.writerow(["Fecha", "Categoría", "Monto", "Descripción"])

    # Filas con los datos
    for gasto in gastos:
            writer.writerow([
                gasto.get("fecha", ""),
                gasto.get("categoria", ""),
                gasto.get("monto", ""),
                gasto.get("descripcion", "")
            ])

    # Retrocedemos al inicio y preparamos la respuesta
    output.seek(0)
    return Response(
        output.read(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=gastos.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)