from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine, get_db
import schemas, crud
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import os
from prediction import ensemble_predict
# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # বা ["*"] সব origin allow করতে পারো (development only)
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, PUT, DELETE সব
    allow_headers=["*"],         # Content-Type, Authorization ইত্যাদি
)

@app.get("/")
def read_root():
    return {"message": "Fake Song Detection API running..."}

# ----------------- Create User -----------------
@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print("Creating user:", user)
    
    return crud.create_user(db, user.dict())

# ----------------- Get User by ID -----------------
@app.post("/users/login", response_model=schemas.UserOut)
def read_user(user:schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user.email,user.password)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user




@app.post("/save_prediction")
def save_prediction(
    prediction: schemas.PredictionCreate,  
    db: Session = Depends(get_db)
):
    print("Saving prediction for user_id:", prediction);
    db_prediction = crud.create_prediction_history(db=db, prediction_data=prediction)
    return db_prediction

@app.post("/get_predictions/{user_id}")
def get_predictions(user_id: int, db: Session = Depends(get_db)):
    predictions = crud.get_prediction_history_by_user(db, user_id=user_id)
    return predictions


@app.delete("/delete_prediction/{prediction_id}")
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    crud.delete_prediction_by_id(db, prediction_id)
    return {"detail": "Prediction deleted successfully"}
    

@app.post("/addDashboard/{prediction_id}")
def add_dashboard(prediction_id: int, dashboard: schemas.DashBoardCreate, db: Session = Depends(get_db)):
    crud.add_dashboard(db, prediction_id, dashboard)
    return {"detail": "Dashboard added successfully"}

@app.get("/getDashboards/")
def get_dashboards(db: Session = Depends(get_db)):
    dashboards=crud.get_dashboards(db)
    return dashboards
   

@app.get("/getAllUsers/")
def get_all_users(db: Session = Depends(get_db)):
    users=crud.get_all_users(db)
    return users
    




@app.post("/prediction")
async def prediction(file: UploadFile = File(...)):
    print("Predicsion is going on")

    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            temp_path = tmp.name
            contents = await file.read()
            tmp.write(contents)
        
        print("Here is the uploaded file",file)
        # Run prediction
        chunk_preds, model_preds = ensemble_predict(temp_path)

        # === Final Decision Logic ===
        # Chunk-wise majority
        from collections import Counter
        final_majority_counts = Counter([c['chunk_majority'] for c in chunk_preds])
        final_prediction = final_majority_counts.most_common(1)[0][0]

        # Model-wise majority
        final_model_vote = Counter(model_preds.values()).most_common(1)[0][0]

        # Clean up temp file
        os.remove(temp_path)

        # Return structured JSON response
        return JSONResponse(
            content={
                "status": "success",
                "final_decision": {
                    "chunk_majority": final_prediction,
                    "model_majority": final_model_vote
                },
                "chunk_predictions": chunk_preds,
                "model_predictions": model_preds
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )
