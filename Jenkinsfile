pipeline {
    agent any

    stages {
       stage('Checkout'){
           steps {
            checkout scm
           }
       }
        stage('Test') {
            steps {
                echo 'Testing..'
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
