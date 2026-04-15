pipeline {
    agent none

    options {
        timestamps()
    }

    environment {
        NPM_CACHE_DIR = '/mnt/1000E/jenkins-cache/npm'
    }

    stages {
        stage('PRE_TESTS') {
            parallel {
                stage('VERSIONING') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            mkdir -p "$NPM_CACHE_DIR"

                            docker run --rm \
                              -e HOST_WORKSPACE="$WORKSPACE" \
                              -v "$WORKSPACE":/workspace \
                              -v "$NPM_CACHE_DIR":/root/.npm \
                              -w /workspace \
                              coldpool-ci-base:1 \
                              bash ci/versioning.sh
                        '''
                    }
                }

                stage('STRUCTURE') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            mkdir -p "$NPM_CACHE_DIR"

                            docker run --rm \
                              -e HOST_WORKSPACE="$WORKSPACE" \
                              -v "$WORKSPACE":/workspace \
                              -v "$NPM_CACHE_DIR":/root/.npm \
                              -w /workspace \
                              coldpool-ci-base:1 \
                              bash ci/structure.sh
                        '''
                    }
                }

                stage('FORMAT') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            mkdir -p "$NPM_CACHE_DIR"

                            docker run --rm \
                              -e HOST_WORKSPACE="$WORKSPACE" \
                              -v "$WORKSPACE":/workspace \
                              -v "$NPM_CACHE_DIR":/root/.npm \
                              -w /workspace \
                              coldpool-ci-base:1 \
                              bash ci/format.sh
                        '''
                    }
                }

                stage('LINT') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            mkdir -p "$NPM_CACHE_DIR"

                            docker run --rm \
                              -e HOST_WORKSPACE="$WORKSPACE" \
                              -v "$WORKSPACE":/workspace \
                              -v "$NPM_CACHE_DIR":/root/.npm \
                              -w /workspace \
                              coldpool-ci-base:1 \
                              bash ci/lint.sh
                        '''
                    }
                }
            }
        }

        stage('SET_BUILD_METADATA') {
            agent { label 'linux-docker' }

            steps {
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

        /*
        stage('TEST_RUN_1') {
            parallel {
                stage('SMOKE') {
                    agent { label 'linux-docker' }
                    steps {
                        sh 'echo TODO: bash ci/smoke.sh'
                    }
                }

                stage('UNIT') {
                    agent { label 'linux-docker' }
                    steps {
                        sh 'echo TODO: bash ci/unit.sh'
                    }
                }

                stage('COMPONENT') {
                    agent { label 'linux-docker' }
                    steps {
                        sh 'echo TODO: bash ci/component.sh'
                    }
                }

                stage('TACTICAL_INTEGRATION') {
                    agent { label 'linux-docker' }
                    steps {
                        sh 'echo TODO: bash ci/integration.sh'
                    }
                }
            }
        }

        stage('TEST_BUILD_GENERATION_AND_DEPLOYMENT') {
            agent { label 'linux-docker' }

            steps {
                sh 'echo TODO: bash ci/build.sh'
            }
        }

        stage('TEST_RUN_2') {
            parallel {
                stage('ACCEPTANCE') {
                    agent { label 'linux-docker' }
                    steps {
                        sh 'echo TODO: bash ci/acceptance.sh'
                    }
                }

                stage('LONG_INTEGRATION') {
                    agent { label 'linux-docker' }
                    steps {
                        sh 'echo TODO: bash ci/long_integration.sh'
                    }
                }

                stage('REPORTS') {
                    agent { label 'linux-docker' }
                    steps {
                        sh 'echo TODO: bash ci/reports.sh'
                    }
                }
            }
        }
        */
    }
}