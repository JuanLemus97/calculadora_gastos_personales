from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
import json
import os
import csv
import io
from db import Gasto, Session

app = Flask(__name__)
ARCHIVO = "gastos.json"

# Cargar datos
def cargar_gastos():
    session = Session()
    gastos = session.query(Gasto).order_by(Gasto.fecha.desc()).all()
    session.close()
    lista = []
    for gasto in gastos:
        fecha = gasto.fecha
        fecha_str = ""
        if fecha:
            if hasattr(fecha, "strftime"):
                fecha_str = fecha.strftime("%d-%m-%Y")
            elif isinstance(fecha, str):
                # Intenta convertir el string a datetime
                try:
                    fecha_dt = datetime.fromisoformat(fecha)
                    fecha_str = fecha_dt.strftime("%d-%m-%Y")
                except Exception:
                    fecha_str = fecha # Si falla, deja el string tal cual
        lista.append({
            "fecha": fecha_str,
            "categoria": gasto.categoria,
            "monto": gasto.monto,
            "descripcion": gasto.descripcion
        })
    return lista
# Guardar datos
def guardar_gastos(gastos):
    with open(ARCHIVO, "w") as f:
        json.dump(gastos, f)

@app.route("/")
def index():
    session = Session()
    gastos = session.query(Gasto).all()
    session.close()
    return render_template("index.html", gastos=gastos)

@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    if request.method == "POST":
        try:
            categoria = request.form["categoria"]
            monto = float(request.form["monto"])
            descripcion = request.form.get("descripcion", "")
            nuevo = Gasto(
                categoria=categoria,
                monto=monto,
                descripcion=descripcion
            )
            session = Session()
            session.add(nuevo)
            session.commit()
            session.close()
        
            return redirect(url_for("agregar"))
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error al agregar el gasto: {str(e)}", 500
        
    return render_template("agregar.html")

@app.route("/gastos")
def gastos():
    try:
        gastos = cargar_gastos()
        return render_template("gastos.html", gastos=gastos)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error al cargar los gastos: {str(e)}", 500

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