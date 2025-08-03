from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os
import math
import logging
from pymongo import MongoClient
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="CVD Prediction API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
try:
    MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    client = MongoClient(MONGO_URL)
    db = client.cvd_prediction_db
    assessments_collection = db.assessments
    logger.info("Connected to MongoDB successfully")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

class HealthAssessment(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    age: int = Field(..., ge=20, le=100, description="Age in years")
    gender: str = Field(..., pattern="^(male|female)$", description="Gender")
    systolic_bp: int = Field(..., ge=80, le=300, description="Systolic blood pressure (mmHg)")
    total_cholesterol: int = Field(..., ge=100, le=500, description="Total cholesterol (mg/dL)")
    hdl_cholesterol: int = Field(..., ge=10, le=150, description="HDL cholesterol (mg/dL)")
    is_smoker: bool = Field(..., description="Current smoking status")
    has_diabetes: bool = Field(..., description="Diabetes status")
    family_history: bool = Field(..., description="Family history of heart disease")
    bmi: float = Field(..., ge=15.0, le=50.0, description="Body Mass Index")
    physical_activity: str = Field(..., regex="^(sedentary|light|moderate|vigorous)$", description="Physical activity level")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)

class CVDRiskResult(BaseModel):
    risk_percentage: float
    risk_category: str
    risk_level: str
    recommendations: list[str]
    assessment_id: str

def calculate_framingham_risk(assessment: HealthAssessment) -> dict:
    """
    Calculate 10-year CVD risk using Framingham Risk Score algorithm
    Based on the 2008 Framingham General CVD Risk Profile
    """
    
    # Risk factors and their point values
    age = assessment.age
    gender = assessment.gender.lower()
    systolic_bp = assessment.systolic_bp
    total_chol = assessment.total_cholesterol
    hdl_chol = assessment.hdl_cholesterol
    smoker = assessment.is_smoker
    diabetes = assessment.has_diabetes
    
    # Initialize points
    points = 0
    
    # Age points (different for men and women)
    if gender == 'male':
        if age >= 20 and age <= 34:
            points += -9
        elif age >= 35 and age <= 39:
            points += -4
        elif age >= 40 and age <= 44:
            points += 0
        elif age >= 45 and age <= 49:
            points += 3
        elif age >= 50 and age <= 54:
            points += 6
        elif age >= 55 and age <= 59:
            points += 8
        elif age >= 60 and age <= 64:
            points += 10
        elif age >= 65 and age <= 69:
            points += 11
        elif age >= 70 and age <= 74:
            points += 12
        elif age >= 75:
            points += 13
    else:  # female
        if age >= 20 and age <= 34:
            points += -7
        elif age >= 35 and age <= 39:
            points += -3
        elif age >= 40 and age <= 44:
            points += 0
        elif age >= 45 and age <= 49:
            points += 3
        elif age >= 50 and age <= 54:
            points += 6
        elif age >= 55 and age <= 59:
            points += 8
        elif age >= 60 and age <= 64:
            points += 10
        elif age >= 65 and age <= 69:
            points += 12
        elif age >= 70 and age <= 74:
            points += 14
        elif age >= 75:
            points += 16
    
    # Total cholesterol points
    if gender == 'male':
        if total_chol < 160:
            points += 0
        elif total_chol < 200:
            points += 4
        elif total_chol < 240:
            points += 7
        elif total_chol < 280:
            points += 9
        else:
            points += 11
    else:  # female
        if total_chol < 160:
            points += 0
        elif total_chol < 200:
            points += 4
        elif total_chol < 240:
            points += 8
        elif total_chol < 280:
            points += 11
        else:
            points += 13
    
    # HDL cholesterol points (same for both genders)
    if hdl_chol >= 60:
        points += -1
    elif hdl_chol >= 50:
        points += 0
    elif hdl_chol >= 40:
        points += 1
    else:
        points += 2
    
    # Systolic blood pressure points (assuming not on treatment)
    if systolic_bp < 120:
        points += 0
    elif systolic_bp < 130:
        points += 0
    elif systolic_bp < 140:
        points += 1
    elif systolic_bp < 160:
        points += 1
    else:
        points += 2
    
    # Smoking points
    if smoker:
        if gender == 'male':
            points += 5
        else:
            points += 9
    
    # Diabetes points
    if diabetes:
        if gender == 'male':
            points += 2
        else:
            points += 3
    
    # Convert points to risk percentage using Framingham equation
    if gender == 'male':
        # Male risk calculation
        risk_percentage = 1 - pow(0.88431, math.exp(points - 23.9802))
    else:
        # Female risk calculation
        risk_percentage = 1 - pow(0.95012, math.exp(points - 26.1931))
    
    risk_percentage = max(0, min(100, risk_percentage * 100))
    
    # Additional risk factors consideration
    risk_modifiers = 1.0
    
    # Family history increases risk
    if assessment.family_history:
        risk_modifiers *= 1.4
    
    # BMI consideration
    if assessment.bmi >= 30:
        risk_modifiers *= 1.2
    elif assessment.bmi >= 25:
        risk_modifiers *= 1.1
    
    # Physical activity consideration
    if assessment.physical_activity == 'sedentary':
        risk_modifiers *= 1.3
    elif assessment.physical_activity == 'light':
        risk_modifiers *= 1.1
    elif assessment.physical_activity == 'vigorous':
        risk_modifiers *= 0.8
    
    # Apply modifiers
    risk_percentage *= risk_modifiers
    risk_percentage = min(risk_percentage, 100)
    
    # Determine risk category
    if risk_percentage < 5:
        risk_category = "Low Risk"
        risk_level = "low"
    elif risk_percentage < 10:
        risk_category = "Borderline Risk"
        risk_level = "borderline"
    elif risk_percentage < 20:
        risk_category = "Intermediate Risk"
        risk_level = "intermediate"
    else:
        risk_category = "High Risk"
        risk_level = "high"
    
    return {
        "risk_percentage": round(risk_percentage, 1),
        "risk_category": risk_category,
        "risk_level": risk_level,
        "points": points
    }

def generate_recommendations(assessment: HealthAssessment, risk_result: dict) -> list[str]:
    """Generate personalized recommendations based on risk factors"""
    recommendations = []
    
    risk_level = risk_result["risk_level"]
    
    # General recommendations for all risk levels
    recommendations.append("Maintain a heart-healthy diet rich in fruits, vegetables, and whole grains")
    
    # Risk-specific recommendations
    if risk_level == "high" or risk_level == "intermediate":
        recommendations.append("Consult with a cardiologist for comprehensive evaluation")
        recommendations.append("Consider medication for cholesterol and blood pressure management")
    
    # Smoking recommendations
    if assessment.is_smoker:
        recommendations.append("⚠️ CRITICAL: Quit smoking immediately - this is your highest risk factor")
        recommendations.append("Seek smoking cessation support programs or medications")
    
    # Blood pressure recommendations
    if assessment.systolic_bp >= 140:
        recommendations.append("Monitor and manage high blood pressure with your doctor")
        recommendations.append("Reduce sodium intake and increase potassium-rich foods")
    
    # Cholesterol recommendations
    if assessment.total_cholesterol >= 240 or assessment.hdl_cholesterol < 40:
        recommendations.append("Work with your doctor to improve cholesterol levels")
        recommendations.append("Increase fiber intake and reduce saturated fats")
    
    # Diabetes recommendations
    if assessment.has_diabetes:
        recommendations.append("Maintain optimal blood sugar control")
        recommendations.append("Regular monitoring and diabetes management")
    
    # Weight recommendations
    if assessment.bmi >= 30:
        recommendations.append("Achieve and maintain a healthy weight (BMI 18.5-24.9)")
        recommendations.append("Consider consulting a nutritionist for weight management")
    elif assessment.bmi >= 25:
        recommendations.append("Consider modest weight loss to reach healthy BMI range")
    
    # Physical activity recommendations
    if assessment.physical_activity in ["sedentary", "light"]:
        recommendations.append("Increase physical activity to at least 150 minutes/week of moderate exercise")
        recommendations.append("Start with walking and gradually increase intensity")
    
    # Family history
    if assessment.family_history:
        recommendations.append("Inform your doctor about family history for enhanced screening")
        recommendations.append("Consider more frequent cardiac check-ups")
    
    # General lifestyle recommendations
    if risk_level != "low":
        recommendations.append("Schedule regular check-ups with your healthcare provider")
        recommendations.append("Monitor blood pressure and cholesterol regularly")
    
    recommendations.append("Manage stress through relaxation techniques or counseling")
    recommendations.append("Get adequate sleep (7-9 hours per night)")
    
    return recommendations[:8]  # Limit to 8 most relevant recommendations

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "CVD Prediction API"}

@app.post("/api/assess-cvd-risk", response_model=CVDRiskResult)
async def assess_cvd_risk(assessment: HealthAssessment):
    try:
        # Calculate risk using Framingham algorithm
        risk_result = calculate_framingham_risk(assessment)
        
        # Generate personalized recommendations
        recommendations = generate_recommendations(assessment, risk_result)
        
        # Create result object
        result = CVDRiskResult(
            risk_percentage=risk_result["risk_percentage"],
            risk_category=risk_result["risk_category"],
            risk_level=risk_result["risk_level"],
            recommendations=recommendations,
            assessment_id=assessment.id
        )
        
        # Save assessment to database
        try:
            assessment_doc = assessment.dict()
            assessment_doc["risk_result"] = risk_result
            assessment_doc["recommendations"] = recommendations
            assessments_collection.insert_one(assessment_doc)
            logger.info(f"Assessment saved with ID: {assessment.id}")
        except Exception as e:
            logger.error(f"Failed to save assessment: {e}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating CVD risk: {e}")
        raise HTTPException(status_code=500, detail="Error calculating CVD risk")

@app.get("/api/assessment/{assessment_id}")
async def get_assessment(assessment_id: str):
    try:
        assessment = assessments_collection.find_one({"id": assessment_id})
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Remove MongoDB _id field
        assessment.pop("_id", None)
        return assessment
        
    except Exception as e:
        logger.error(f"Error retrieving assessment: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving assessment")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)