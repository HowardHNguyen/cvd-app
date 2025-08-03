import React, { useState } from 'react';
import './App.css';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { Checkbox } from './components/ui/checkbox';
import { Progress } from './components/ui/progress';
import { Alert, AlertDescription } from './components/ui/alert';
import { Badge } from './components/ui/badge';
import { Separator } from './components/ui/separator';
import { Heart, Activity, AlertTriangle, CheckCircle, TrendingUp, Users, Calculator, Shield } from 'lucide-react';

const App = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    age: '',
    gender: '',
    systolic_bp: '',
    total_cholesterol: '',
    hdl_cholesterol: '',
    is_smoker: false,
    has_diabetes: false,
    family_history: false,
    bmi: '',
    physical_activity: ''
  });

  const handleInputChange = (name, value) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const calculateBMI = (weight, height) => {
    if (weight && height) {
      const heightInMeters = height / 100;
      return (weight / (heightInMeters * heightInMeters)).toFixed(1);
    }
    return '';
  };

  const validateStep = (step) => {
    switch (step) {
      case 1:
        return formData.age && formData.gender;
      case 2:
        return formData.systolic_bp && formData.total_cholesterol && formData.hdl_cholesterol;
      case 3:
        return formData.bmi && formData.physical_activity;
      default:
        return true;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const response = await fetch(`${backendUrl}/api/assess-cvd-risk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          age: parseInt(formData.age),
          systolic_bp: parseInt(formData.systolic_bp),
          total_cholesterol: parseInt(formData.total_cholesterol),
          hdl_cholesterol: parseInt(formData.hdl_cholesterol),
          bmi: parseFloat(formData.bmi)
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to assess CVD risk');
      }

      const data = await response.json();
      setResult(data);
      setCurrentStep(5);
    } catch (error) {
      console.error('Error:', error);
      alert('Error calculating CVD risk. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const resetAssessment = () => {
    setCurrentStep(1);
    setResult(null);
    setFormData({
      age: '',
      gender: '',
      systolic_bp: '',
      total_cholesterol: '',
      hdl_cholesterol: '',
      is_smoker: false,
      has_diabetes: false,
      family_history: false,
      bmi: '',
      physical_activity: ''
    });
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      case 'borderline': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'intermediate': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (riskLevel) => {
    switch (riskLevel) {
      case 'low': return <CheckCircle className="w-6 h-6 text-green-600" />;
      case 'borderline': return <TrendingUp className="w-6 h-6 text-yellow-600" />;
      case 'intermediate': return <AlertTriangle className="w-6 h-6 text-orange-600" />;
      case 'high': return <AlertTriangle className="w-6 h-6 text-red-600" />;
      default: return <Activity className="w-6 h-6" />;
    }
  };

  if (result) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 p-4">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <Heart className="w-8 h-8 text-blue-600 mr-3" />
              <h1 className="text-3xl font-bold text-gray-900">CVD Risk Assessment Results</h1>
            </div>
            <p className="text-gray-600">Your personalized cardiovascular disease risk evaluation</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk Score Card */}
            <Card className={`border-2 ${getRiskColor(result.risk_level)}`}>
              <CardHeader className="text-center">
                <div className="flex items-center justify-center mb-2">
                  {getRiskIcon(result.risk_level)}
                </div>
                <CardTitle className="text-2xl">{result.risk_category}</CardTitle>
              </CardHeader>
              <CardContent className="text-center">
                <div className="mb-4">
                  <div className="text-5xl font-bold mb-2">{result.risk_percentage}%</div>
                  <p className="text-sm text-gray-600">10-year CVD risk</p>
                </div>
                <Progress 
                  value={result.risk_percentage} 
                  className="w-full h-3 mb-4"
                />
                <Badge variant="outline" className="text-sm px-3 py-1">
                  Framingham Risk Score
                </Badge>
              </CardContent>
            </Card>

            {/* Risk Interpretation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calculator className="w-5 h-5 mr-2" />
                  Understanding Your Risk
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="font-medium text-green-700">Low Risk</span>
                    <span className="text-sm text-green-600">&lt; 5%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                    <span className="font-medium text-yellow-700">Borderline Risk</span>
                    <span className="text-sm text-yellow-600">5% - 10%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <span className="font-medium text-orange-700">Intermediate Risk</span>
                    <span className="text-sm text-orange-600">10% - 20%</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <span className="font-medium text-red-700">High Risk</span>
                    <span className="text-sm text-red-600">&gt; 20%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-5 h-5 mr-2" />
                Personalized Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {result.recommendations.map((recommendation, index) => (
                  <div key={index} className="flex items-start p-3 bg-gray-50 rounded-lg">
                    <CheckCircle className="w-5 h-5 text-blue-600 mr-3 mt-0.5 flex-shrink-0" />
                    <span className="text-sm text-gray-700">{recommendation}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Important Notice */}
          <Alert className="mt-6 border-blue-200 bg-blue-50">
            <AlertTriangle className="w-4 h-4" />
            <AlertDescription>
              <strong>Important:</strong> This assessment is for educational purposes only and should not replace professional medical advice. 
              Please consult with your healthcare provider for personalized medical guidance and treatment decisions.
            </AlertDescription>
          </Alert>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mt-6">
            <Button onClick={resetAssessment} variant="outline" className="flex-1">
              Take New Assessment
            </Button>
            <Button 
              onClick={() => window.print()} 
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              Print Results
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Heart className="w-8 h-8 text-blue-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">CVD Risk Assessment</h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Assess your 10-year cardiovascular disease risk using the clinically validated Framingham Risk Score. 
            Complete the assessment to receive personalized recommendations.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-4">
            {[1, 2, 3, 4].map((step) => (
              <div key={step} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  step <= currentStep 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {step}
                </div>
                {step < 4 && (
                  <div className={`w-12 h-0.5 mx-2 ${
                    step < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                  }`} />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-2">
            <span className="text-sm text-gray-600">
              Step {currentStep} of 4
            </span>
          </div>
        </div>

        {/* Form Steps */}
        <Card className="mx-auto max-w-2xl">
          <form onSubmit={handleSubmit}>
            {/* Step 1: Basic Demographics */}
            {currentStep === 1 && (
              <div>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Users className="w-5 h-5 mr-2" />
                    Basic Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="age">Age (years)</Label>
                    <Input
                      id="age"
                      type="number"
                      min="20"
                      max="100"
                      value={formData.age}
                      onChange={(e) => handleInputChange('age', e.target.value)}
                      placeholder="Enter your age"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="gender">Gender</Label>
                    <Select value={formData.gender} onValueChange={(value) => handleInputChange('gender', value)}>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="male">Male</SelectItem>
                        <SelectItem value="female">Female</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </div>
            )}

            {/* Step 2: Clinical Measurements */}
            {currentStep === 2 && (
              <div>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Activity className="w-5 h-5 mr-2" />
                    Clinical Measurements
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="systolic_bp">Systolic Blood Pressure (mmHg)</Label>
                    <Input
                      id="systolic_bp"
                      type="number"
                      min="80"
                      max="300"
                      value={formData.systolic_bp}
                      onChange={(e) => handleInputChange('systolic_bp', e.target.value)}
                      placeholder="e.g., 120"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="total_cholesterol">Total Cholesterol (mg/dL)</Label>
                    <Input
                      id="total_cholesterol"
                      type="number"
                      min="100"
                      max="500"
                      value={formData.total_cholesterol}
                      onChange={(e) => handleInputChange('total_cholesterol', e.target.value)}
                      placeholder="e.g., 200"
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="hdl_cholesterol">HDL Cholesterol (mg/dL)</Label>
                    <Input
                      id="hdl_cholesterol"
                      type="number"
                      min="10"
                      max="150"
                      value={formData.hdl_cholesterol}
                      onChange={(e) => handleInputChange('hdl_cholesterol', e.target.value)}
                      placeholder="e.g., 50"
                      className="mt-1"
                    />
                  </div>
                </CardContent>
              </div>
            )}

            {/* Step 3: Physical Health */}
            {currentStep === 3 && (
              <div>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2" />
                    Physical Health
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="bmi">Body Mass Index (BMI)</Label>
                    <Input
                      id="bmi"
                      type="number"
                      step="0.1"
                      min="15"
                      max="50"
                      value={formData.bmi}
                      onChange={(e) => handleInputChange('bmi', e.target.value)}
                      placeholder="e.g., 25.0"
                      className="mt-1"
                    />
                    <p className="text-sm text-gray-500 mt-1">
                      Calculate: Weight (kg) ÷ Height² (m²)
                    </p>
                  </div>
                  <div>
                    <Label htmlFor="physical_activity">Physical Activity Level</Label>
                    <Select value={formData.physical_activity} onValueChange={(value) => handleInputChange('physical_activity', value)}>
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select activity level" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="sedentary">Sedentary (Little to no exercise)</SelectItem>
                        <SelectItem value="light">Light (1-3 days/week)</SelectItem>
                        <SelectItem value="moderate">Moderate (3-5 days/week)</SelectItem>
                        <SelectItem value="vigorous">Vigorous (6-7 days/week)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </div>
            )}

            {/* Step 4: Risk Factors */}
            {currentStep === 4 && (
              <div>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <AlertTriangle className="w-5 h-5 mr-2" />
                    Risk Factors
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="is_smoker"
                      checked={formData.is_smoker}
                      onCheckedChange={(checked) => handleInputChange('is_smoker', checked)}
                    />
                    <Label htmlFor="is_smoker" className="font-medium">
                      I currently smoke tobacco
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="has_diabetes"
                      checked={formData.has_diabetes}
                      onCheckedChange={(checked) => handleInputChange('has_diabetes', checked)}
                    />
                    <Label htmlFor="has_diabetes" className="font-medium">
                      I have diabetes
                    </Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="family_history"
                      checked={formData.family_history}
                      onCheckedChange={(checked) => handleInputChange('family_history', checked)}
                    />
                    <Label htmlFor="family_history" className="font-medium">
                      Family history of heart disease
                    </Label>
                  </div>
                </CardContent>
              </div>
            )}

            {/* Navigation Buttons */}
            <div className="p-6 bg-gray-50 rounded-b-lg">
              <div className="flex justify-between">
                {currentStep > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setCurrentStep(currentStep - 1)}
                  >
                    Previous
                  </Button>
                )}
                
                {currentStep < 4 ? (
                  <Button
                    type="button"
                    onClick={() => setCurrentStep(currentStep + 1)}
                    disabled={!validateStep(currentStep)}
                    className={currentStep === 1 ? 'ml-auto' : ''}
                  >
                    Next
                  </Button>
                ) : (
                  <Button
                    type="submit"
                    disabled={isLoading || !validateStep(currentStep)}
                    className="ml-auto bg-blue-600 hover:bg-blue-700"
                  >
                    {isLoading ? 'Calculating...' : 'Calculate Risk'}
                  </Button>
                )}
              </div>
            </div>
          </form>
        </Card>

        {/* Medical Disclaimer */}
        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500 max-w-2xl mx-auto">
            This tool is for educational purposes only and should not be used as a substitute for professional medical advice, 
            diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions 
            you may have regarding a medical condition.
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;