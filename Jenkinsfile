pipeline {
    agent none

    options {
        timestamps()
    }

    stages {
        stage('VERSIONING') {
            agent {
                docker {
                    label 'linux-docker'
                    image 'coldpool-ci-base:1'
                }
            }
            steps {
                sh 'bash ci/versioning.sh'

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

        stage('STRUCTURE') {
            agent {
                docker {
                    label 'linux-docker'
                    image 'coldpool-ci-base:1'
                }
            }
            steps {
                sh 'bash ci/structure.sh'
            }
        }

        stage('FORMAT') {
            agent {
                docker {
                    label 'linux-docker'
                    image 'coldpool-ci-base:1'
                }
            }
            steps {
                sh 'bash ci/format.sh'
            }
        }
    }
}