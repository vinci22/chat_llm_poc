import subprocess
import time
import requests
import os

def run_django():
    """Ejecutar el servidor Django en el puerto 8001."""
    return ["python", "manage.py", "runserver", "8001"]

def run_fastapi():
    """Ejecutar el servidor FastAPI en el puerto 8000."""
    return ["uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]

def get_fastapi_url(timeout=60):
    """Obtener la URL del servidor FastAPI una vez que esté en funcionamiento."""
    start_time = time.time()
    api_url = None
    while True:
        try:
            response = requests.get("http://127.0.0.1:8000")  # Intentar conexión al puerto estándar
            if response.status_code == 200:
                api_url = response.url
                print(f"Servidor FastAPI está funcionando en {api_url}.")
                return api_url
        except requests.ConnectionError:
            pass
        
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            print("Timeout esperando por el servidor FastAPI.")
            raise RuntimeError("Servidor FastAPI no está disponible.")
        
        print("Esperando a que el servidor FastAPI esté disponible...")
        time.sleep(2)

if __name__ == "__main__":
    # Ejecutar el servidor FastAPI primero
    fastapi_process = subprocess.Popen(run_fastapi(), cwd=".")

    try:
        # Obtener la URL del servidor FastAPI
        api_url = get_fastapi_url()

        # Usar la URL obtenida para las siguientes operaciones
        print(f"URL de FastAPI: {api_url}")

        # Luego, ejecutar el servidor Django
        django_process = subprocess.Popen(run_django(), cwd="django_chatbot")

        # Esperar indefinidamente para que los servidores sigan corriendo
        django_process.wait()
        fastapi_process.wait()
    except KeyboardInterrupt:
        # Permitir la parada de ambos servidores si se interrumpe el script
        print("Interrumpido por el usuario")
        django_process.terminate()
        fastapi_process.terminate()
