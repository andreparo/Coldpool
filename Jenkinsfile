pipeline {
    agent none

    options {
        timestamps()
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

        stage('CI_IMAGES') {
            agent { label 'linux-docker' }

            steps {
                sh '''
                    bash ci/setup_images.sh "$BUILD_NUMBER" "$SHORT_SHA"
                '''

                script {
                    def envText = readFile('ci_images.env').trim()
                    def data = [:]

                    envText.split('\n').each { line ->
                        def parts = line.split('=', 2)
                        if (parts.length == 2) {
                            data[parts[0].trim()] = parts[1].trim()
                        }
                    }

                    if (!data['BASE_IMAGE']) {
                        error('BASE_IMAGE missing from ci_images.env')
                    }
                    if (!data['DEPENDENCY_IMAGE']) {
                        error('DEPENDENCY_IMAGE missing from ci_images.env')
                    }
                    if (!data['COMMIT_IMAGE']) {
                        error('COMMIT_IMAGE missing from ci_images.env')
                    }

                    env.BASE_IMAGE = data['BASE_IMAGE']
                    env.DEPENDENCY_IMAGE = data['DEPENDENCY_IMAGE']
                    env.COMMIT_IMAGE = data['COMMIT_IMAGE']
                }
            }
        }

        stage('PRE_TESTS') {
            parallel {
                stage('STRUCTURE') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            docker run --rm \
                              -v "$WORKSPACE":/workspace \
                              -w /workspace \
                              "$COMMIT_IMAGE" \
                              bash ci/structure.sh
                        '''
                    }
                }

                stage('FORMAT') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            docker run --rm \
                              -v "$WORKSPACE":/workspace \
                              -w /workspace \
                              "$COMMIT_IMAGE" \
                              bash ci/format.sh
                        '''
                    }
                }

                stage('LINT_PYTHON') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            docker run --rm \
                              -v "$WORKSPACE":/workspace \
                              -w /workspace \
                              "$COMMIT_IMAGE" \
                              bash ci/lint_python.sh
                        '''
                    }
                }

                stage('LINT_FRONTEND') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            mkdir -p /mnt/1000E/jenkins-agent/cache/eslint
                            mkdir -p /mnt/1000E/jenkins-agent/cache/tsc
                            mkdir -p /mnt/1000E/jenkins-agent/cache/npm

                            chown -R jenkins-agent:jenkins-agent /mnt/1000E/jenkins-agent/cache || true

                            docker run --rm \
                              -e ESLINT_CACHE_FILE=/ci-cache/eslint/.eslintcache \
                              -e TSC_BUILDINFO_FILE=/ci-cache/tsc/tsconfig.app.tsbuildinfo \
                              -e npm_config_cache=/ci-cache/npm \
                              -v "$WORKSPACE":/workspace \
                              -v /mnt/1000E/jenkins-agent/cache/eslint:/ci-cache/eslint \
                              -v /mnt/1000E/jenkins-agent/cache/tsc:/ci-cache/tsc \
                              -v /mnt/1000E/jenkins-agent/cache/npm:/ci-cache/npm \
                              -w /workspace \
                              "$COMMIT_IMAGE" \
                              bash -lc 'cd apps/coldpool_web_app && npm ci && cd /workspace && bash ci/lint_frontend.sh'
                        '''
                    }
                }
            }
        }

        stage('FAST_TESTS') {
            parallel {
                stage('UNIT') {
                    agent { label 'linux-docker' }

                    steps {
                        sh '''
                            docker run --rm \
                              -v "$WORKSPACE":/workspace \
                              -w /workspace \
                              "$COMMIT_IMAGE" \
                              bash ci/unit.sh
                        '''
                    }
                }
            }
        }

        stage('BUILD') {
            agent { label 'linux-docker' }

            steps {
                sh '''
                    docker run --rm \
                      -e VERSION="$VERSION" \
                      -v "$WORKSPACE":/workspace \
                      -w /workspace \
                      "$COMMIT_IMAGE" \
                      bash ci/build.sh
                '''

                sh '''
                    echo "=== WORKSPACE DIST CONTENTS ==="
                    find apps/coldpool_server -maxdepth 3 -type f | sort
                '''
            }

            post {
                success {
                    archiveArtifacts artifacts: 'apps/coldpool_server/dist/*.tar.gz', fingerprint: true
                }
            }
        }

        stage('TEST_IMAGES') {
            agent { label 'linux-docker' }

            steps {
                sh '''
                    export BUILD_NUMBER="$BUILD_NUMBER"
                    export SHORT_SHA="$SHORT_SHA"
                    bash ci/test_images.sh
                '''

                script {
                    def envText = readFile('ci_runtime.env').trim()
                    def data = [:]

                    envText.split('\n').each { line ->
                        def parts = line.split('=', 2)
                        if (parts.length == 2) {
                            data[parts[0].trim()] = parts[1].trim()
                        }
                    }

                    if (!data['RUNTIME_IMAGE']) {
                        error('RUNTIME_IMAGE missing from ci_runtime.env')
                    }

                    env.RUNTIME_IMAGE = data['RUNTIME_IMAGE']
                }
            }
        }

        stage('SMOKE') {
            agent { label 'linux-docker' }

            steps {
                sh '''
                    export BUILD_NUMBER="$BUILD_NUMBER"
                    export RUNTIME_IMAGE="$RUNTIME_IMAGE"
                    bash ci/smoke.sh
                '''
            }
        }
    }

    post {
        always {
            node('linux-docker') {
                sh '''
                    docker rm -f "coldpool-runtime-smoke-$BUILD_NUMBER" || true
                    docker image rm -f "$COMMIT_IMAGE" || true
                '''
            }
        }
    }
}