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
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT fecha, categoria, monto, descripcion FROM gastos")
        filas = cur.fetchall()
        conn.close()

        gastos = []
        for filas in filas:
            fecha_str = filas[0]
            # Convertir el string ISO a datetime
            fecha_dt = datetime.fromisoformat(fecha_str) if isinstance(fecha_str, str) else fecha_str
            gastos.append({
                "fecha": fecha_dt,
                "categoria": filas[1],
                "monto": float(filas[2]),
                "descripcion": filas[3]
            })
        return gastos
    except Exception as e:
        print(f"Error al cargar los gastos: {str(e)}")
        return []

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