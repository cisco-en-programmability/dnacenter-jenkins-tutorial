pipeline {
    options {
        buildDiscarder(logRotator(numToKeepStr: '10')) // Retain history on the last 10 builds
        ansiColor('xterm') // Enable colors in terminal
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
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
                sh 'dnac.sh'
            }
        }
    }
}
