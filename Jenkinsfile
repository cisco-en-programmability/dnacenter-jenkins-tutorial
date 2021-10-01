pipeline {
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
