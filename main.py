# main.py
from app import create_app

# Crear la aplicación Flask
app = create_app()

if __name__ == "__main__":
    # Ejecutar servidor
    app.run(host="127.0.0.1", port=8000, debug=True)


