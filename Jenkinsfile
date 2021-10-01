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
@NonCPS
def printCurrentBuildChangesets() {
  def changeLogSets = currentBuild.changeSets
  for (int i = 0; i < changeLogSets.size(); i++) {
    def entries = changeLogSets[i].items
    for (int j = 0; j < entries.length; j++) {
        def entry = entries[j]
        echo "${entry.commitId} by ${entry.author} on ${new Date(entry.timestamp)}: ${entry.msg}"
        def files = new ArrayList(entry.affectedFiles)
        for (int k = 0; k < files.size(); k++) {
            def file = files[k]
            echo "${file.editType.name} ${file.path}"
        }
    }
  }
}