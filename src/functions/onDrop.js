import axios from "axios";

/**
 * Handles audio file upload and prediction via FastAPI backend
 */
export const onDrop = async (
  acceptedFiles,
  setError,
  setUploading,
  setUploadedFile,
  setActiveStep,
  setPredictions
) => {
    console.log(acceptedFiles,"ACCEPTED files")
  const file = acceptedFiles[0]; // Only process the first file

  if (!file) return;

  // === Validate file type ===
  if (!["audio/mpeg", "audio/wav"].includes(file.type)) {
    setError("Please upload only MP3 or WAV files");
    return;
  }

  setError(null);
  setUploading(true);
  setUploadedFile(file);

  try {
    // Move UI to "uploading" step
    setActiveStep(1);

    // === Prepare form data ===
    const formData = new FormData();
    formData.append("file", file);

    // === Send to backend ===
    const response = await axios.post("http://127.0.0.1:8000/prediction", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    // === Extract predictions ===
    const data = response.data;

    // Optionally log for debugging
    console.log("Prediction response:", data);

    // Update UI states
    setPredictions(data);
    setActiveStep(2); // Move to "results" step
  } catch (err) {
    console.error(err);
    setError("An error occurred during prediction");
  } finally {
    setUploading(false);
  }
};
