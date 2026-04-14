pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Compute version') {
            steps {
                sh '''
                    python3 ci/versioning/compute_version.py > ci_version.env
                    cat ci_version.env
                '''
                script {
                    def data = readProperties file: 'ci_version.env'
                    env.VERSION = data.VERSION
                    env.SHORT_SHA = data.SHORT_SHA
                    env.IS_STABLE = data.IS_STABLE

                    currentBuild.displayName = "${env.VERSION} | #${env.BUILD_NUMBER} | ${env.SHORT_SHA}"
                    currentBuild.description = "pending"
                }
            }
        }

        stage('Style checks') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD":/workspace \
                      -w /workspace \
                      python:3.12-slim \
                      bash ci/runners/run_style_checks.sh
                '''
            }
        }

        stage('Smoke tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD":/workspace \
                      -w /workspace \
                      python:3.12-slim \
                      bash ci/runners/run_smoke_tests.sh
                '''
            }
        }

        stage('Unit tests') {
            steps {
                sh '''
                    docker run --rm \
                      -v "$PWD":/workspace \
                      -w /workspace \
                      python:3.12-slim \
                      bash ci/runners/run_unit_tests.sh
                '''
            }
        }
    }

    post {
        success {
            script {
                currentBuild.description = "testable"
            }
        }
        failure {
            script {
                currentBuild.description = "failed"
            }
        }
    }
}