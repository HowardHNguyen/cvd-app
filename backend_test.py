import requests
import sys
import json
from datetime import datetime

class CVDAPITester:
    def __init__(self, base_url="https://da8efc7e-af0a-4c3c-ac72-4297907ac4b4.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                print(f"Request data: {json.dumps(data, indent=2)}")
                response = requests.post(url, json=data, headers=headers, timeout=30)

            print(f"Response status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    print("Response: (non-JSON)")
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error response: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Error response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        return self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )

    def test_cvd_assessment_high_risk(self):
        """Test CVD assessment with high-risk profile"""
        high_risk_data = {
            "age": 65,
            "gender": "male",
            "systolic_bp": 160,
            "total_cholesterol": 280,
            "hdl_cholesterol": 30,
            "is_smoker": True,
            "has_diabetes": True,
            "family_history": True,
            "bmi": 32.0,
            "physical_activity": "sedentary"
        }
        
        success, response = self.run_test(
            "CVD Assessment - High Risk Profile",
            "POST",
            "api/assess-cvd-risk",
            200,
            data=high_risk_data
        )
        
        if success:
            # Validate response structure
            required_fields = ['risk_percentage', 'risk_category', 'risk_level', 'recommendations', 'assessment_id']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Check if high risk is detected
            if response['risk_percentage'] > 15:  # Should be high risk
                print(f"✅ High risk correctly detected: {response['risk_percentage']}%")
            else:
                print(f"⚠️ Expected higher risk percentage, got: {response['risk_percentage']}%")
            
            print(f"Risk Category: {response['risk_category']}")
            print(f"Recommendations count: {len(response['recommendations'])}")
            
        return success

    def test_cvd_assessment_low_risk(self):
        """Test CVD assessment with low-risk profile"""
        low_risk_data = {
            "age": 25,
            "gender": "female",
            "systolic_bp": 110,
            "total_cholesterol": 180,
            "hdl_cholesterol": 60,
            "is_smoker": False,
            "has_diabetes": False,
            "family_history": False,
            "bmi": 22.0,
            "physical_activity": "vigorous"
        }
        
        success, response = self.run_test(
            "CVD Assessment - Low Risk Profile",
            "POST",
            "api/assess-cvd-risk",
            200,
            data=low_risk_data
        )
        
        if success:
            # Check if low risk is detected
            if response['risk_percentage'] < 10:  # Should be low risk
                print(f"✅ Low risk correctly detected: {response['risk_percentage']}%")
            else:
                print(f"⚠️ Expected lower risk percentage, got: {response['risk_percentage']}%")
            
            print(f"Risk Category: {response['risk_category']}")
            
        return success

    def test_cvd_assessment_sample_data(self):
        """Test CVD assessment with the sample data from the request"""
        sample_data = {
            "age": 45,
            "gender": "male",
            "systolic_bp": 140,
            "total_cholesterol": 240,
            "hdl_cholesterol": 35,
            "is_smoker": True,
            "has_diabetes": False,
            "family_history": True,
            "bmi": 28.5,
            "physical_activity": "light"
        }
        
        success, response = self.run_test(
            "CVD Assessment - Sample Data",
            "POST",
            "api/assess-cvd-risk",
            200,
            data=sample_data
        )
        
        if success:
            print(f"Risk Percentage: {response['risk_percentage']}%")
            print(f"Risk Category: {response['risk_category']}")
            print(f"Risk Level: {response['risk_level']}")
            print(f"Assessment ID: {response['assessment_id']}")
            
            # Test retrieving the assessment
            assessment_id = response['assessment_id']
            retrieve_success, _ = self.run_test(
                f"Retrieve Assessment {assessment_id}",
                "GET",
                f"api/assessment/{assessment_id}",
                200
            )
            
            return retrieve_success
            
        return success

    def test_invalid_data(self):
        """Test API with invalid data"""
        invalid_data = {
            "age": 150,  # Invalid age
            "gender": "invalid",  # Invalid gender
            "systolic_bp": 50,  # Invalid BP
            "total_cholesterol": 50,  # Invalid cholesterol
            "hdl_cholesterol": 200,  # Invalid HDL
            "is_smoker": "yes",  # Should be boolean
            "has_diabetes": "no",  # Should be boolean
            "family_history": "maybe",  # Should be boolean
            "bmi": 5.0,  # Invalid BMI
            "physical_activity": "extreme"  # Invalid activity level
        }
        
        success, response = self.run_test(
            "CVD Assessment - Invalid Data",
            "POST",
            "api/assess-cvd-risk",
            422,  # Expecting validation error
            data=invalid_data
        )
        
        if success:
            print("✅ API correctly rejected invalid data")
        
        return success

def main():
    print("🏥 Starting CVD Risk Assessment API Tests")
    print("=" * 50)
    
    # Setup
    tester = CVDAPITester()
    
    # Run tests
    print("\n📋 Running API Tests...")
    
    # Test health check
    tester.test_health_check()
    
    # Test CVD assessments
    tester.test_cvd_assessment_sample_data()
    tester.test_cvd_assessment_high_risk()
    tester.test_cvd_assessment_low_risk()
    
    # Test error handling
    tester.test_invalid_data()
    
    # Print results
    print(f"\n📊 Test Results:")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())