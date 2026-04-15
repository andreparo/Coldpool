pipeline {
    agent none

    options {
        timestamps()
    }

    environment {
        PROJECT_CI_IMAGE = "coldpool-project-ci:${env.BUILD_NUMBER}"
    }

    stages {
        stage('VERSIONING') {
            agent { label 'linux-docker' }

            steps {
                sh '''
                    docker run --rm \
                      -e HOST_WORKSPACE="$WORKSPACE" \
                      -v "$WORKSPACE":/workspace \
                      -w /workspace \
                      coldpool-ci-base:1 \
                      bash ci/versioning.sh
                '''

                script {
                    def envText = readFile('ci_version.env').trim()
                    def data = [:]

                    envText.split('\n').each { line ->
                        def parts = line.split('=', 2)
                        if (parts.length == 2) {
                            data[parts[0].trim()] = parts[1].trim()
                        }
                    }

                    if (!data['VERSION']) {
                        error('VERSION missing from ci_version.env')
                    }
                    if (!data['SHORT_SHA']) {
                        error('SHORT_SHA missing from ci_version.env')
                    }
                    if (!data['IS_STABLE']) {
                        error('IS_STABLE missing from ci_version.env')
                    }

                    env.VERSION = data['VERSION']
                    env.SHORT_SHA = data['SHORT_SHA']
                    env.IS_STABLE = data['IS_STABLE']

                    currentBuild.displayName = "${env.VERSION} | #${env.BUILD_NUMBER} | ${env.SHORT_SHA}"
                }
            }
        }

        stage('PREPARE_CI_IMAGE') {
            agent { label 'linux-docker' }

            steps {
                sh '''
                    bash ci/prepare_ci_image.sh "$PROJECT_CI_IMAGE"
                '''
            }
        }

        stage('PRE_TESTS') {
            parallel {
                stage('STRUCTURE') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            docker run --rm \
                              -w /workspace \
                              "$PROJECT_CI_IMAGE" \
                              bash ci/structure.sh
                        '''
                    }
                }

                stage('FORMAT') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            docker run --rm \
                              -w /workspace \
                              "$PROJECT_CI_IMAGE" \
                              bash ci/format.sh
                        '''
                    }
                }

                stage('LINT') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            docker run --rm \
                              -w /workspace \
                              "$PROJECT_CI_IMAGE" \
                              bash ci/lint.sh
                        '''
                    }
                }
            }
        }
    }

    post {
        always {
            node('linux-docker') {
                sh '''
                    docker image rm -f "$PROJECT_CI_IMAGE" || true
                '''
            }
        }
    }
}