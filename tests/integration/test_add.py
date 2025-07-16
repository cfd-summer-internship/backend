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
            "configFiles.consentForm" : ("Consent Form", open("tests/assets/Test File.pdf", "rb"), "application/pdf"),
            "configFiles.studyInstructions" : ("Study Instructions", open("tests/assets/Test File.pdf", "rb"), "application/pdf"),     
            "configFiles.learningList" : ("Learning List", open("tests/assets/Test List.csv", "rb"), "application/pdf"),  
            "configFiles.experimentList" : ("Experiment List", open("tests/assets/Test List.csv", "rb"), "application/pdf"), 
            "configFiles.studyDebrief" : ("Study Debrief", open("tests/assets/Test File.pdf", "rb"), "application/pdf"),
        }
                           )
    assert response.status_code == 200
    assert response.json()["message"] == "Configuration added succesfully"