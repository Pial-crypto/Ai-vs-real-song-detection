import { addDashboard } from "./addDashboard";
import { getFromLocal } from "./localStorage";
import axios from "axios";

export const savePrediction = async (predictionData) => {
  try {
    // Prepare payload
      

    console.log("Saving prediction data:", predictionData);
    const userId=getFromLocal('user')?.id;
    console.log("USER ID:",userId);
    
    const response = await axios.post(
      "http://127.0.0.1:8000/save_prediction",
      {
        chunkWisePrediction: predictionData.chunkPrediction,
        modelWiseMajorityPrediction: predictionData.model_predictions,
        finalPrediction: predictionData.final_decision,
        user_id: userId,
        fileName: predictionData.fileName
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

     console.log("Saved prediction response:", response.data);
     addDashboard(response.data).then((res)=>{
      console.log("Dashboard added:", res);
     }).catch((err)=>{
      console.error("Error adding dashboard:", err);
     });
    // setSuccess("Prediction saved successfully!");
  } catch (err) {
    console.error(err);
    
  }
};