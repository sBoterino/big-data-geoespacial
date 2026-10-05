// Pipeline CI/CD — Big Data Geoespacial
//
// Flujo: checkout -> build -> pytest -> [Kaggle] -> levantar servicios -> integración
//        -> API en staging + smoke tests -> DESPLIEGUE -> verificación.
// Si cualquier etapa falla, las siguientes no se ejecutan: un fallo NUNCA llega a producción.
//
// Credenciales requeridas en Jenkins (ver docs/guia_fase2.md):
//   mongo-root          (Username with password)  usuario/contraseña root de MongoDB
//   kaggle-api-token    (Secret text)             token KGAT_... de Kaggle

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()        // dos builds a la vez pelearían por los mismos contenedores
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    triggers {
        githubPush()                     // disparado por el webhook de GitHub (vía smee)
    }

    parameters {
        booleanParam(name: 'FORZAR_FALLO', defaultValue: false,
            description: 'Activa un test que falla a propósito para demostrar que NO se despliega')
        booleanParam(name: 'VERIFICAR_KAGGLE', defaultValue: true,
            description: 'Comprueba que la credencial de Kaggle funciona y el dataset es accesible')
        booleanParam(name: 'FORCE_RELOAD', defaultValue: false,
            description: 'Fuerza la recarga completa del dataset aunque ya exista una ingesta válida')
    }

    environment {
        // Solo bdgeo-main usa etiquetas numéricas de producción. Los jobs temporales de ramas
        // usan un prefijo para no sobrescribir imágenes que sirven como rollback.
        API_TAG        = "${env.JOB_NAME == 'bdgeo-main' ? env.BUILD_NUMBER : 'validation-' + env.BUILD_NUMBER}"
        STAGING        = "bdgeo-api-staging-${env.JOB_BASE_NAME}-${env.BUILD_NUMBER}"
        // La rama se prueba primero con una muestra; el job de producción cumple la carga completa.
        INGEST_MAX_ROWS = "${env.JOB_NAME == 'bdgeo-main' ? '0' : '50000'}"
        MONGO_CRED     = credentials('mongo-root')   // expone MONGO_CRED_USR y MONGO_CRED_PSW (enmascarados)
        KAGGLE_DATASET = 'muzammilrizvi1/motor-vehicle-collisions-crashes'
        INFRA          = 'mongodb spark-master spark-worker dask-scheduler dask-worker-1 dask-worker-2'
        DOCKER_BUILDKIT = '1'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --pretty="Commit %h de %an: %s"'
            }
        }

        stage('Construir imágenes') {
            steps {
                sh '''
                    . jenkins/ci-env.sh
                    reintentar() {
                        intento=1
                        hasta=3
                        until "$@"; do
                            if [ "$intento" -ge "$hasta" ]; then
                                echo "El comando falló después de ${hasta} intentos."
                                return 1
                            fi
                            espera=$((intento * 10))
                            echo "Fallo transitorio; reintento $((intento + 1))/${hasta} en ${espera}s..."
                            sleep "$espera"
                            intento=$((intento + 1))
                        done
                    }
                    reintentar docker compose build
                    reintentar docker build --target test -t bdgeo-api-test:${API_TAG} api
                    reintentar docker build --target test -t bdgeo-ingest-test:${API_TAG} ingest
                '''
            }
        }

        stage('Pruebas unitarias (pytest)') {
            steps {
                sh 'docker run --rm -e FORZAR_FALLO=${FORZAR_FALLO} bdgeo-api-test:${API_TAG}'
                sh 'docker run --rm bdgeo-ingest-test:${API_TAG}'
            }
        }

        stage('Verificar acceso a Kaggle') {
            when { expression { params.VERIFICAR_KAGGLE } }
            steps {
                withCredentials([string(credentialsId: 'kaggle-api-token',
                        variable: 'KAGGLE_API_TOKEN')]) {
                    // -e VAR sin valor: Docker toma el valor del entorno sin mostrarlo en el log
                    sh 'docker run --rm -e KAGGLE_API_TOKEN bdgeo-dask:latest kaggle datasets files "${KAGGLE_DATASET}"'
                }
            }
        }

        stage('Levantar servicios') {
            steps {
                sh '''
                    . jenkins/ci-env.sh
                    docker compose up -d --wait --wait-timeout 240 ${INFRA}
                    docker compose ps
                '''
            }
        }

        stage('Ingesta (idempotente)') {
            steps {
                withCredentials([string(credentialsId: 'kaggle-api-token',
                        variable: 'KAGGLE_API_TOKEN')]) {
                    sh '''
                        . jenkins/ci-env.sh
                        FORCE_RELOAD=${FORCE_RELOAD} docker compose run --rm \
                            -e KAGGLE_API_TOKEN dask-job python pipeline_ingesta.py
                    '''
                }
            }
        }

        stage('Pruebas de integración') {
            steps {
                sh '''
                    . jenkins/ci-env.sh
                    echo "== Dask: 2 workers + MongoDB =="
                    docker compose run --rm dask-job python check_cluster.py
                    echo "== Spark: MongoDB Spark Connector =="
                    docker compose exec -T spark-master /opt/spark/bin/spark-submit /opt/jobs/check_conexion.py
                '''
            }
        }

        stage('Pruebas contra la API (staging)') {
            when { expression { env.JOB_NAME == 'bdgeo-main' } }
            steps {
                sh '''
                    . jenkins/ci-env.sh
                    docker run -d --name ${STAGING} --network bdgeo-net \
                        -e MONGO_ROOT_USER -e MONGO_ROOT_PASSWORD \
                        -e MONGO_HOST=mongodb -e MONGO_DB=geo -e APP_VERSION=${API_TAG}-staging \
                        bdgeo-api:${API_TAG}
                    bash scripts/smoke_api.sh http://${STAGING}:5000
                '''
            }
        }

        stage('Despliegue') {
            when { expression { env.JOB_NAME == 'bdgeo-main' } }
            steps {
                sh '''
                    . jenkins/ci-env.sh
                    docker compose up -d --no-deps --no-build api
                    bash scripts/smoke_api.sh http://api:5000
                    echo "Versión desplegada: ${API_TAG}"
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f ${STAGING} >/dev/null 2>&1 || true
                docker image rm bdgeo-api-test:${API_TAG} >/dev/null 2>&1 || true
                docker image rm bdgeo-ingest-test:${API_TAG} >/dev/null 2>&1 || true
            '''
        }
        success {
            // Conserva solo las últimas 5 versiones de la API para no llenar el disco
            sh '''
                docker images bdgeo-api --format '{{.Tag}}' | grep -E '^[0-9]+$' | sort -n | head -n -5 \
                  | xargs -r -I{} docker image rm bdgeo-api:{} >/dev/null 2>&1 || true
            '''
            script {
                if (env.JOB_NAME == 'bdgeo-main') {
                    echo "OK: build ${env.BUILD_NUMBER} desplegado."
                } else {
                    echo "OK: validación ${env.JOB_NAME} #${env.BUILD_NUMBER} aprobada; producción no fue modificada."
                }
            }
        }
        failure {
            echo "FALLO: el pipeline se detuvo y NO se desplegó la versión ${env.BUILD_NUMBER}. La versión anterior sigue activa."
        }
    }
}
