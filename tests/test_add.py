import sys
# sys hacks to get imports to work
sys.path.append("./")
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_study_config():
    response = client.post(
        "/config/add",
        data={
            "learning.displayDuration" : "1",
            "learning.pauseDuration" : "1",
            "learning.displayMethod" : "sequential",
            "waiting.displayDuration" : "1",
            "experiment.displayDuration" : "1",
            "experiment.pauseDuration" : "1",
            "experiment.displayMethod" : "random",
            "experiment.responseMethod" : "binary",
            "conclusion.showResults": "true",
            "conclusion.survey":"false"
        },
        files={
            "configFiles.consentForm" : ("consent_form.txt", open("tests/assets/consent_form.txt", "rb"), "text/plain"),
            "configFiles.studyInstructions" : ("study_instructions.txt", open("tests/assets/study_instructions.txt", "rb"), "text/plain"),      
            "configFiles.learningList" : ("learning_list.txt", open("tests/assets/learning_list.txt", "rb"), "text/plain"),  
            "configFiles.experimentList" : ("experiment_list.txt", open("tests/assets/experiment_list.txt", "rb"), "text/plain"),  
            "configFiles.studyDebrief" : ("study_debrief.txt", open("tests/assets/study_debrief.txt", "rb"), "text/plain"),  
        }
                           )
    assert response.status_code == 200