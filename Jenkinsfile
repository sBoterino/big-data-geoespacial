// Pipeline CI/CD — Big Data Geoespacial
//
// Flujo: checkout -> build -> pytest -> [Kaggle] -> levantar servicios -> integración
//        -> API en staging + smoke tests -> DESPLIEGUE -> verificación.
// Si cualquier etapa falla, las siguientes no se ejecutan: un fallo NUNCA llega a producción.
//
// Credenciales requeridas en Jenkins (ver docs/guia_fase2.md):
//   mongo-root          (Username with password)  usuario/contraseña root de MongoDB
//   kaggle-credentials  (Username with password)  usuario de Kaggle / API key

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
    }

    environment {
        API_TAG        = "${env.BUILD_NUMBER}"
        STAGING        = "bdgeo-api-staging-${env.BUILD_NUMBER}"
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
                    docker compose build
                    docker build --target test -t bdgeo-api-test:${API_TAG} api
                '''
            }
        }

        stage('Pruebas unitarias (pytest)') {
            steps {
                sh 'docker run --rm -e FORZAR_FALLO=${FORZAR_FALLO} bdgeo-api-test:${API_TAG}'
            }
        }

        stage('Verificar acceso a Kaggle') {
            when { expression { params.VERIFICAR_KAGGLE } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'kaggle-credentials',
                        usernameVariable: 'KAGGLE_USERNAME', passwordVariable: 'KAGGLE_KEY')]) {
                    // -e VAR sin valor: Docker toma el valor del entorno sin mostrarlo en el log
                    sh 'docker run --rm -e KAGGLE_USERNAME -e KAGGLE_KEY bdgeo-dask:latest kaggle datasets files "${KAGGLE_DATASET}"'
                }
            }
        }

        // Fase 4: aquí se agrega la etapa "Ingesta (idempotente)":
        //   docker compose run --rm dask-job python -m pipeline_ingesta

        stage('Levantar servicios') {
            steps {
                sh '''
                    . jenkins/ci-env.sh
                    docker compose up -d --wait --wait-timeout 240 ${INFRA}
                    docker compose ps
                '''
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
            '''
        }
        success {
            // Conserva solo las últimas 5 versiones de la API para no llenar el disco
            sh '''
                docker images bdgeo-api --format '{{.Tag}}' | grep -E '^[0-9]+$' | sort -n | head -n -5 \
                  | xargs -r -I{} docker image rm bdgeo-api:{} >/dev/null 2>&1 || true
            '''
            echo "OK: build ${env.BUILD_NUMBER} desplegado."
        }
        failure {
            echo "FALLO: el pipeline se detuvo y NO se desplegó la versión ${env.BUILD_NUMBER}. La versión anterior sigue activa."
        }
    }
}
