from flask import Flask, render_template, request, redirect, url_for, Response
from datetime import datetime
import csv
import io
from db import Gasto, Session

app = Flask(__name__)

# Cargar datos
def cargar_gastos():
    session = Session()
    gastos = session.query(Gasto).order_by(Gasto.fecha.desc()).all()
    session.close()
    lista = []
    for gasto in gastos:
        fecha = gasto.fecha
        if fecha is None:
            fecha_str = ""
        elif hasattr(fecha, "strftime"):
            fecha_str = fecha.strftime("%d-%m-%Y")
        else:
            # Si llega como string tipo "2025-08-21 01:06:24.381924"
            try:
                fecha_dt = datetime.fromisoformat(str(fecha))
                fecha_str = fecha_dt.strftime("%d-%m-%Y")
            except Exception:
                fecha_str = str(fecha) # Si falla, deja el string tal cual
        lista.append({
            "id": gasto.id,
            "fecha": fecha_str,
            "categoria": gasto.categoria,
            "monto": gasto.monto,
            "descripcion": gasto.descripcion
        })
    return lista

@app.route("/")
def index():
    session = Session()
    gastos = session.query(Gasto).order_by(Gasto.fecha.desc()).all()
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
    session = Session()
    query = session.query(Gasto)
    # Filtros por GET o POST
    categoria = request.values.get("categoria", "")
    descripcion = request.values.get("descripcion", "")
    fecha_inicio = request.values.get("fecha_inicio", "")
    fecha_fin = request.values.get("fecha_fin", "")

    if categoria:
        query = query.filter(Gasto.categoria.ilike(f"%{categoria}%"))
    if descripcion:
        query = query.filter(Gasto.descripcion.ilike(f"%{descripcion}%"))
    if fecha_inicio:
        try:
            fecha_dt = datetime.fromisoformat(fecha_inicio)
            query = query.filter(Gasto.fecha >= fecha_dt)
        except Exception:
            pass
    if fecha_fin:
        try:
            fecha_dt = datetime.fromisoformat(fecha_fin)
            query = query.filter(Gasto.fecha <= fecha_dt)
        except Exception:
            pass
    
    gastos = query.order_by(Gasto.fecha.desc()).all()
    session.close()
    # Formatea fechas como antes
    lista = []
    for gasto in gastos:
        fecha = gasto.fecha
        if fecha is None:
            fecha_str = ""
        elif hasattr(fecha, "strftime"):
            fecha_str = fecha.strftime("%d-%m-%Y")
        else:
            try:
                fecha_dt = datetime.fromisoformat(str(fecha))
                fecha_str = fecha_dt.strftime("%d-%m-%Y")
            except Exception:
                fecha_str = str(fecha)
        lista.append({
            "id": gasto.id,
            "fecha": fecha_str,
            "categoria": gasto.categoria,
            "monto": gasto.monto,
            "descripcion": gasto.descripcion
        })
    return render_template("gastos.html", gastos=lista,
                           categoria=categoria, descripcion=descripcion,
                           recha_inicio=fecha_inicio, fecha_fin=fecha_fin)

@app.route("/eliminar/<int:gasto_id>")
def eliminar(gasto_id):
    session = Session()
    gasto = session.query(Gasto).filter_by(id=gasto_id).first()
    if gasto:
        session.delete(gasto)
        session.commit()
    session.close()
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