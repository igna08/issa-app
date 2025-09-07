# Plataforma de Inscripción Online para Colegio

## Descripción

Esta es una plataforma de inscripción online completa, desarrollada con Python y Flask. Permite a los estudiantes inscribirse en cursos, realizar pagos a través de Mercado Pago y recibir notificaciones por correo electrónico. También incluye un panel de administración para gestionar usuarios, cursos y notificaciones.

## Características Principales

-   **Formulario de Inscripción Público:** Una página de inscripción (`/inscripcion`) responsive para móviles y desktop.
-   **Integración con Mercado Pago:** Flujo de pago completo. Después de enviar el formulario, los usuarios son redirigidos a Mercado Pago para completar la transacción.
-   **Notificaciones por Email (Gmail):**
    -   Email de confirmación al usuario tras un pago exitoso.
    -   Email de notificación al colegio sobre una nueva inscripción.
-   **Panel de Administración Simple:**
    -   Login seguro para un único administrador.
    -   Dashboard (`/admin/dashboard`) con tablas para visualizar usuarios, cursos y notificaciones.
    -   **Gestión de Cursos:** Funcionalidad completa de Crear, Leer, Actualizar y Eliminar (CRUD) para los cursos.
-   **Seguridad:**
    -   Contraseñas hasheadas con `bcrypt`.
    -   Protección contra inyección SQL a través del ORM SQLAlchemy.
    -   Protección contra ataques CSRF en todos los formularios.
-   **Base de Datos:** Estructura de base de datos relacional con tablas para usuarios, cursos, pagos, notificaciones y administrador.
-   **API para Cursos:** Un endpoint (`/api/courses/<type>`) que proporciona los cursos en formato JSON para el frontend.
-   **Tests:** Suite de tests unitarios para verificar las funcionalidades principales.

## Tecnologías Utilizadas

-   **Backend:** Python 3, Flask
-   **Base de Datos:** SQLAlchemy (con SQLite por defecto)
-   **Frontend:** HTML5, Bootstrap 5
-   **Pagos:** Mercado Pago SDK
-   **Emails:** Flask-Mail (con Gmail)
-   **Seguridad:** Flask-Bcrypt, Flask-WTF (para CSRF)
-   **Testing:** unittest

## Instrucciones de Instalación

Sigue estos pasos para ejecutar la aplicación en tu entorno local.

**1. Clonar el Repositorio (o descargar los archivos)**

```bash
git clone <url-del-repositorio>
cd <nombre-del-repositorio>
```

**2. Crear un Entorno Virtual**

Es una buena práctica usar un entorno virtual para aislar las dependencias del proyecto.

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

**3. Instalar Dependencias**

Instala todas las librerías necesarias usando el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

**4. Configurar Variables de Entorno**

Abre el archivo `app.py` y reemplaza los valores de placeholder con tus credenciales reales.

```python
# En app.py

# ...
app.config['SECRET_KEY'] = 'una_clave_secreta_muy_dificil'  # ¡Cámbiala!
app.config['MERCADOPAGO_ACCESS_TOKEN'] = 'TU_ACCESS_TOKEN_DE_MERCADOPAGO'

# ...
app.config['MAIL_USERNAME'] = 'tu_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'tu_contraseña_de_aplicacion_de_gmail'
app.config['MAIL_DEFAULT_SENDER'] = 'tu_email@gmail.com'
# ...
```
**Nota sobre Gmail:** Si usas autenticación de dos factores (2FA) en tu cuenta de Gmail, necesitas generar una "Contraseña de aplicación" para usarla en `MAIL_PASSWORD`.

**5. Crear la Base de Datos**

Ejecuta el siguiente script para crear el archivo de base de datos (`school.db`) y todas las tablas.

```bash
python create_db.py
```

**6. (Opcional) Poblar la Base de Datos con Datos de Ejemplo**

Para tener algunos cursos de ejemplo, puedes ejecutar:

```bash
python seed_db.py
```

**7. Crear el Usuario Administrador**

Ejecuta este script para crear el primer administrador. Por defecto, las credenciales son `admin@example.com` / `password`. Puedes cambiarlas en el script `create_admin.py`.

```bash
python create_admin.py
```

**8. Iniciar la Aplicación**

¡Todo listo! Ahora puedes iniciar el servidor de desarrollo de Flask.

```bash
python app.py
```

La aplicación estará corriendo en `http://127.0.0.1:5000`.

## Modo de Uso

-   **Inscripción:** Ve a `http://127.0.0.1:5000/inscripcion` para ver el formulario de inscripción.
-   **Panel de Administración:** Ve a `http://127.0.0.1:5000/admin/login` para iniciar sesión con las credenciales de administrador. Una vez dentro, serás redirigido al dashboard donde podrás gestionar los cursos y ver los usuarios registrados.

## Cómo Ejecutar los Tests

Para asegurarte de que todo funciona como se espera, puedes correr la suite de tests.

```bash
python test_app.py
```
