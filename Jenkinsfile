pipeline {
    agent any

    options {
        timestamps()
    }

    stages {
        stage('Versioning') {
            steps {
                sh '''
                    python3 ci/versioning/verify_changelog.py
                    python3 ci/versioning/compute_version.py > ci_version.env
                    cat ci_version.env
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

                    env.VERSION = data['VERSION']
                    env.SHORT_SHA = data['SHORT_SHA']
                    env.IS_STABLE = data['IS_STABLE']

                    currentBuild.displayName = "${env.VERSION} | #${env.BUILD_NUMBER} | ${env.SHORT_SHA}"
                }
            }
        }
    }
}