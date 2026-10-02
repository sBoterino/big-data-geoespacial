# Guía Fase 2 — Infraestructura y CI/CD de punta a punta

Objetivo (Gate 2): todos los servicios levantan y se comunican, y un push a `main` dispara
Jenkins, que construye, prueba y despliega. Un test fallido bloquea el despliegue.

Tiempo estimado la primera vez: de 2 a 4 horas. La primera descarga de imágenes es lo más lento.

Hacer los pasos **en orden** y marcar cada casilla. Si algo falla, revisar la tabla de
problemas al final antes de seguir.

---

## Paso 0 — Preparación

- [ ] Docker Desktop → Settings → Resources → Memory en **al menos 8 GB** (ideal 10–12 GB).
- [ ] El repositorio de GitHub está creado y tiene la base subida.
- [ ] En Windows, antes de clonar: `git config --global core.autocrlf false`.
      El `.gitattributes` fuerza LF, pero esto evita sorpresas.

```bash
git clone <url-del-repo> && cd <repo>
cp .env.example .env
```

Editar `.env`: poner una contraseña real en `MONGO_ROOT_PASSWORD` y las credenciales de Kaggle.
**Anotar la contraseña**, porque la misma va en Jenkins.

---

## Paso 1 — Levantar la aplicación en local

```bash
docker compose up -d --build
docker compose ps
```

La primera vez tarda varios minutos: descarga imágenes y el build de Spark baja el conector
desde Maven. Todo debe quedar en `running` o `healthy`.

Verificar en el navegador:
- [ ] Spark master en http://localhost:8081, que debe mostrar **1 worker ALIVE**.
- [ ] Dashboard de Dask en http://localhost:8787, que debe mostrar **2 workers** en la pestaña Workers.
- [ ] API en http://localhost:5000/health, que debe devolver `{"mongo":"ok","status":"ok",...}`.

Pruebas de integración entre contenedores:

```bash
docker compose run --rm dask-job python check_cluster.py
#  -> "workers conectados: 2" ... "eventos_semilla = 300" ... "RESULTADO: OK"

docker compose exec spark-master /opt/spark/bin/spark-submit /opt/jobs/check_conexion.py
#  -> tabla con A_times_square=120, B_brooklyn_bridge=80, C_queens=100
#  -> "documentos leídos: 300 (esperado 300)"
```

- [ ] Las dos pruebas terminan bien. **Guardar la salida en `docs/evidencias/`.**

---

## Paso 2 — Levantar Jenkins

```bash
docker compose --profile ci up -d --build jenkins
docker compose exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

1. Abrir http://localhost:8080 y pegar la contraseña.
2. En "Customize Jenkins", elegir **Select plugins to install → None**. Los necesarios ya
   vienen instalados en la imagen.
3. Crear el usuario administrador con una **contraseña fuerte**.
4. Dejar la URL de la instancia en `http://localhost:8080/`.

Comprobar que Jenkins puede usar Docker:

```bash
docker compose exec jenkins docker ps
```

- [ ] Lista los contenedores del proyecto.

---

## Paso 3 — Credenciales en Jenkins

Ir a **Manage Jenkins → Credentials → System → Global credentials → Add Credentials**.
Todas son del tipo **Username with password**:

| ID (exacto) | Username | Password |
|---|---|---|
| `mongo-root` | el mismo `MONGO_ROOT_USER` del `.env` | el mismo `MONGO_ROOT_PASSWORD` del `.env` |
| `kaggle-credentials` | usuario de Kaggle | la API key de Kaggle |
| `github-token` *(solo si el repo es privado)* | usuario de GitHub | un fine-grained token con permiso *Contents: Read* sobre el repo |

- [ ] Las credenciales están creadas con esos IDs exactos. El Jenkinsfile los busca por nombre.

---

## Paso 4 — Crear el job

**New Item** → nombre `bdgeo-main` → tipo **Pipeline** → OK.

- **General:** marcar *GitHub project* y poner la URL del repositorio.
- **Triggers:** marcar ✅ *GitHub hook trigger for GITScm polling*.
- **Pipeline:**
  - *Definition:* Pipeline script from SCM.
  - *SCM:* Git. *Repository URL:* la URL https del repo. *Credentials:* `github-token` si es privado.
  - *Branch Specifier:* `*/main`.
  - *Script Path:* `Jenkinsfile`.

Guardar y pulsar **Build Now** una vez, a mano. El primer build registra los parámetros y el
trigger del webhook. A partir de ahí el botón pasa a ser *Build with Parameters*.

- [ ] El primer build termina en verde, con todas las etapas.
- [ ] http://localhost:5000/health muestra `"version":"<número del build>"`.

---

## Paso 5 — Webhook con smee.io

Se usa smee y no ngrok por seguridad (decisión D8). Con smee, Jenkins **no queda expuesto a
internet**: un cliente local recibe los eventos de GitHub desde smee.io y los reenvía a
Jenkins. Exponer Jenkins, que controla el Docker del host, con una URL pública sería un riesgo.

1. Entrar a https://smee.io y pulsar **Start a new channel**. Copiar la URL (`https://smee.io/XXXX`).
2. Ponerla en `.env` como `SMEE_URL=https://smee.io/XXXX`.
3. Levantar el reenviador y revisar los logs:

```bash
docker compose --profile ci up -d smee
docker compose logs -f smee
#  -> "Forwarding https://smee.io/XXXX to http://jenkins:8080/github-webhook/"
#  -> "Connected https://smee.io/XXXX"
```

4. En GitHub, ir a **Settings → Webhooks → Add webhook**:
   - *Payload URL:* la URL de smee.
   - *Content type:* `application/json`.
   - *Which events:* Just the push event.
   - *Active:* ✅.
5. GitHub envía un evento *ping*. Debe aparecer en la página del canal de smee y en los logs.

- [ ] El ping llega a smee y aparece en los logs.

---

## Paso 6 — Acordar el flujo de `main`

El equipo decidió no activar un ruleset porque la protección técnica de la rama no es un
requisito explícito de la rúbrica. Aun así, el flujo exigido para todo cambio es:
- ✅ trabajar en una rama;
- ✅ abrir un pull request hacia `main`;
- ✅ obtener al menos una revisión de otro integrante antes del merge.

Si el docente solicita protección técnica, se puede activar después mediante un *Ruleset* para
la rama predeterminada con un PR y una aprobación obligatorios.

---

## Paso 7 — Prueba de punta a punta (la misma que en la sustentación)

```bash
git checkout -b feature/prueba-pipeline
# hacer un cambio pequeño, por ejemplo una línea en el README
git commit -am "Prueba del pipeline" && git push -u origin feature/prueba-pipeline
```

Abrir un PR, que otro integrante lo apruebe y hacer merge.

- [ ] Jenkins arranca **solo**, en segundos, sin pulsar nada.
- [ ] Todas las etapas quedan en verde y `/health` muestra el nuevo número de build.
- [ ] **Captura de la vista de etapas → `docs/evidencias/`.**

---

## Paso 8 — Prueba de bloqueo (evidencia clave de la rúbrica)

En Jenkins: **Build with Parameters** → marcar ✅ `FORZAR_FALLO` → Build.

- [ ] El build queda en **rojo** en *Pruebas unitarias (pytest)*.
- [ ] Las etapas siguientes, incluida *Despliegue*, aparecen como **no ejecutadas**.
- [ ] `/health` sigue mostrando la versión **anterior**.
- [ ] **Captura → `docs/evidencias/`.** Esto demuestra "si una prueba falla, no se despliega".

---

## ✅ Gate 2 — Checklist final

- [ ] `docker compose up -d --build` levanta todo en un solo comando.
- [ ] Spark tiene 1 worker ALIVE; Dask tiene 2 workers.
- [ ] `check_cluster.py` y `check_conexion.py` terminan bien.
- [ ] Push o merge a `main` dispara Jenkins automáticamente.
- [ ] El pipeline completo queda en verde y despliega.
- [ ] `FORZAR_FALLO` bloquea el despliegue.
- [ ] No hay ningún secreto en el repositorio. Verificar con `git log -p | grep -i -E "password|key"`.
- [ ] Las evidencias están guardadas.

Con todo marcado, actualizar CONTEXT.md (sección 8) y pasar a las Fases 3–6.

---

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `permission denied ... docker.sock` en Jenkins | Jenkins no corre como root o el socket no está montado | Revisar `user: root` y el volumen del socket en el compose; recrear con `docker compose --profile ci up -d --force-recreate jenkins` |
| `Definir MONGO_ROOT_PASSWORD` | Falta `.env` (local) o la credencial `mongo-root` (Jenkins) | Crear `.env` o la credencial con el ID exacto |
| `Authentication failed` en Mongo | El volumen se creó con otra contraseña | La contraseña queda fijada al crear el volumen. Poner la misma en `.env` y Jenkins, o borrar datos con `docker compose down -v` (**borra todo**) |
| `eventos_semilla = 0` | El volumen de Mongo existía antes de los scripts de inicialización | `docker compose down -v` y volver a levantar |
| El puerto 8080 o 5000 ya está en uso | Otro programa lo ocupa; en macOS, AirPlay usa el 5000 | Cambiar `API_PORT` en `.env`, o cerrar el programa |
| `exec format error` o `/bin/sh^M` | Finales de línea CRLF (Windows) | `git add --renormalize .` y volver a hacer commit; revisar `core.autocrlf false` |
| Contenedor con `Exited (137)` | Se quedó sin memoria (OOM) | Subir la RAM de Docker Desktop o bajar los `*_MEM` en `.env` |
| El webhook no dispara Jenkins | Falta el trigger, smee caído, o la URL no termina en `/` | Revisar el paso 4 (trigger), `docker compose logs smee` y que el target sea `/github-webhook/` con la barra final |
| No aparece *Build with Parameters* | Aún no hubo un primer build | Pulsar **Build Now** una vez |
| El worker de Spark no se registra | El master aún no estaba listo, o hay un conflicto de hostname | `docker compose logs spark-worker`; `docker compose restart spark-worker` |
| Falla el build de la imagen de Spark al descargar jars | Sin internet, o versión inexistente en Maven | Revisar la conexión y los `ARG` de versión en `spark/Dockerfile` |
| `kaggle ... 401 Unauthorized` | Token incorrecto o expirado | Generar un token nuevo en Kaggle y actualizar la credencial y el `.env` |
