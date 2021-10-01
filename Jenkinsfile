pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '10')) // Retain history on the last 10 builds
        timestamps() // Append timestamps to each line
        timeout(time: 20, unit: 'MINUTES') // Set a timeout on the total execution time of the job
    }
    agent {
        docker { 
            image 'python:latest' 
        }
    }

    stages {
        stage('Checkout'){
           steps {
            checkout scm
           }
        }
        stage('Test') {
            steps {
                sh 'python --version'
                script {

        }
        stage('Build') {
            steps {
                withEnv(["HOME=${env.WORKSPACE}"]) {
                    echo 'Building....'
                    sh 'pip install -r requirements.txt'
                    echo "${DNAC_PASSWORD}"
                }
            }
        }
    }
  post {
    cleanup {
      cleanWs()
    }
  }
}
//@NonCPS
def getChangesSinceLastSuccessfulBuild() {
    def changes = []
    def build = currentBuild

    while (build != null && build.result != 'SUCCESS') {
        changes += (build.changeSets.collect { changeSet ->
            (changeSet.items.collect { item ->
                (item.affectedFiles.collect { affectedFile ->
                    affectedFile.path
                }).flatten()
            }).flatten()
        }).flatten()

        build = build.previousBuild
    }

    return changes.unique()
}