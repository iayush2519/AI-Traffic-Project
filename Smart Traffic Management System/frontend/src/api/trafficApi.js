import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const trafficApi = {
  // Get all intersection states
  async getStatus() {
    const response = await axios.get(`${API_BASE_URL}/traffic/status`);
    return response.data;
  },

  // Get prediction for an intersection
  async getPrediction(intersectionId, horizon = '15min') {
    const response = await axios.post(`${API_BASE_URL}/predict/congestion`, {
      intersection_id: intersectionId,
      model_name: 'xgboost',
      horizon: horizon
    });
    return response.data;
  },

  // Trigger training (manual action from dashboard maybe)
  async triggerTraining(modelType = 'both') {
    const response = await axios.post(`${API_BASE_URL}/model/train`, {
      model_type: modelType,
      quick: true
    });
    return response.data;
  }
};
