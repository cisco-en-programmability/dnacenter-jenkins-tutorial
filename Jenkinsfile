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
                       def changedFiles = []
            for (changeLogSet in currentBuild.changeSets) { 
                for (entry in changeLogSet.getItems()) { 
                    for (file in entry.getAffectedFiles()) {
                        changedFiles.add(file.getPath())
                    }
                }
            }
            echo changedFiles
       }
        stage('Test') {
            steps {
                sh 'python --version'
            }
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
