# Bienvenido a mistral chat poc!

Bienvenido al repositorio 2 en 1(puedes usar solo la api y consumirla con otro front si quieres )  de la API de chat avanzada basada en Mixtral(**Puedes usar otros modelos**). Este proyecto, desarrollado en Python y utilizando **Largraph**, está diseñado para proporcionar una experiencia de conversación fluida y contextualmente rica mediante la integración de agentes especializados.


# Componentes principales
## Agentes

### `apiAgent`

El **`apiAgent.py`** está especializado en la recuperación de tasas de cambio y la conversión de divisas. Utiliza la API de [ExchangeRate-API](https://v6.exchangerate-api.com/v6/) para acceder a datos de tasas de cambio actualizados en tiempo real. Este agente es ideal para consultas relacionadas con la conversión de monedas y la obtención de información financiera específica.

**Funciones Clave:**

-   Recuperar tasas de cambio actuales entre diferentes monedas.
-   Realizar conversiones de divisas basadas en tasas de cambio en tiempo real.
-   Proporcionar datos precisos y actualizados para necesidades financieras.

### `coneAgent`

El **`coneAgent.py`** se encarga del almacenamiento y gestión de vectores utilizando **Pinecone**. Este agente se especializa en la organización y recuperación de información a partir de datos vectoriales, facilitando una búsqueda semántica eficiente y la recomendación de contenido relevante.

**Funciones Clave:**

-   Almacenar y gestionar vectores de datos utilizando Pinecone.
-   Realizar búsquedas semánticas avanzadas para encontrar información relacionada.
-   Optimizar la recuperación de datos basada en similitud vectorial.

### `generalAgent`

El **`generalAgent.py`** está diseñado para manejar consultas generales y proporcionar respuestas amplias y contextualmente relevantes. Este agente se especializa en ofrecer respuestas a preguntas comunes y proporcionar información general sobre una amplia gama de temas, actuando como el recurso principal para consultas no específicas.

**Funciones Clave:**

-   Responder a preguntas generales y proporcionar información útil.
-   Manejar una variedad de temas y consultas no especializadas.
-   Ofrecer respuestas coherentes y contextualizadas para mejorar la interacción general.
 ## prompt templates
El archivo **`prompts.py`** está diseñado para simplificar la creación de prompts y mejorar la legibilidad del código. Este componente proporciona plantillas que definen las lógicas avanzadas de generación de texto para las técnicas de **Chain of Thought (CoT)**, **Few-Shot Learning**, y **Tree of Thought**, facilitando su integración en el sistema de chat.
fácil de usar 
 ```
 from prompts import BASE_PROMPT_TU_PROMPT
```

## CLI_APP

El archivo **`cli_app.py`** es un script de línea de comandos (CLI) diseñado para interactuar con la aplicación mediante la carga de archivos PDF Este script utiliza el módulo `argparse` para manejar la entrada del usuario desde la línea de comandos, facilitando la integración de archivos PDF en el sistema de almacenamiento vectorial.

### Descripción de Funcionalidades

-   **Captura de Archivo PDF**: Permite al usuario especificar el archivo PDF que desea cargar. El script gestiona la carga del archivo y lo prepara para su procesamiento.
   

Ejemplo de Uso
Para ejecutar el script, utiliza la línea de comandos con los siguientes parámetros:
```
python cli_app.py --file_path /ruta/al/archivo.pdf 
                                             
```

## Como usar el chat en tu equipo local
Es importante tener a la mano estas 4 API_KEY y agregarlas como variables de entorno en tu equipo, con estos nombres respectivamente
- **`PINECONE_APIKEY`**: La clave de API utilizada para autenticar y acceder a Pinecone, un servicio de almacenamiento vectorial
 - **`EXCHANGERATE_APIKEY`**: La clave de API necesaria para acceder al servicio de tasas de cambio y conversión de divisas. 
  - **`LLM_APIKEY`**: La clave de API utilizada para autenticar y acceder a un modelo de lenguaje (LLM) proporcionado por un servicio de inteligencia artificial ( **de momento solo mistral**). 
- **`API_ENDPOINT`**: url de la API en este caso el valor seria http://127.0.0.1:8000/chat/v1

**es primordial tener creado un env con virtualenv o con conda en el cual tienes que instalar los paquetes en el archivo requirements.txt y ejecutar los siguientes pasos en ese ambiente**

 ###  opción #1 de configuración
sobre la raíz del repositorio encontraras un archivo llamado chatrun.py
ejecuta ese archivo y listo y puedes chatear(asi de facil)

 ###  opción #2 de configuración
 dado el caso la primera opción no te funcionara puedes usar esta, es un método mas manual pero seguro
1)  ejecuta primero el servicio de  la API, para esto debes de ubicarte en la raíz del repositorio y ejecutar el siguiente comando
```
uvicorn main:app --host "127.0.0.1" --port 8000
```

2) ejecuta el servicio de frontEnd(chat)

bash:
```
cd django_chatbot && python manage.py runserve
```
powershell:
```
cd django_chatbot; python manage.py runserver

```


###  **ya ejecutado en front debes ir a la pagina /register y registrarte**