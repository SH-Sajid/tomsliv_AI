from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.responses import Response
from app.routes.ai_routes import router as ai_router
import json

# Custom JSON response that preserves dictionary order
class OrderPreservingJSONResponse(Response):
    media_type = "application/json"
    
    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

app = FastAPI(
    title="Tomsliv AI Service",
    description="AI-powered candidate analysis and matching service",
    version="1.0.0"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Define the exact field order for JobCreationRequest
    field_orders = {
        "BasicInformation": ["jobTitle", "farmSize_ha", "peakHerdSize_cows", "typicalOnFarmStaff", "closingDateForApplications", "positionStartDate"],
        "PrimaryLocation": ["type", "options"],
        "JobDescriptionInfo": ["primaryLocation", "role", "workType"],
        "RemunerationDetails": ["from", "to", "period"],
        "WorkingInformation": ["hourType", "averageHoursPerWeek", "roster", "remunerationPaidBy", "remunerationIfHourlyDailyWeeklyMonthlyYearly", "remunerationIfTotalPackageValue", "remunerationIfPerKgMS", "remunerationIfPercentageOfMilkCheque"],
        "JobCreationRequest": ["basicInformation", "jobDescription", "workingInformation"]
    }
    
    # Helper function to reorder dict based on field order
    def reorder_dict(d, order):
        if not isinstance(d, dict):
            return d
        ordered = {}
        for key in order:
            if key in d:
                ordered[key] = d[key]
        for key in d:
            if key not in ordered:
                ordered[key] = d[key]
        return ordered
    
    # Reorder properties in schemas
    if "components" in openapi_schema and "schemas" in openapi_schema["components"]:
        schemas = openapi_schema["components"]["schemas"]
        for schema_name, order in field_orders.items():
            if schema_name in schemas and "properties" in schemas[schema_name]:
                props = schemas[schema_name]["properties"]
                # Create ordered properties dict
                ordered_props = {}
                for field in order:
                    if field in props:
                        ordered_props[field] = props[field]
                # Add any remaining fields not in the order list
                for field in props:
                    if field not in ordered_props:
                        ordered_props[field] = props[field]
                schemas[schema_name]["properties"] = ordered_props
        
        # Replace the example for JobCreationRequest with properly ordered version
        if "JobCreationRequest" in schemas:
            schemas["JobCreationRequest"]["example"] = {
                "basicInformation": {
                    "jobTitle": "Farm assistant",
                    "farmSize_ha": "1200",
                    "peakHerdSize_cows": "60",
                    "typicalOnFarmStaff": "Full time",
                    "closingDateForApplications": "",
                    "positionStartDate": ""
                },
                "jobDescription": {
                    "primaryLocation": {
                        "type": "Single farm",
                        "options": ["Single farm", "Multiple farm", "Corporate farm"]
                    },
                    "role": "",
                    "workType": "Full-time"
                },
                "workingInformation": {
                    "hourType": "",
                    "averageHoursPerWeek": "60",
                    "roster": "",
                    "remunerationPaidBy": "",
                    "remunerationIfHourlyDailyWeeklyMonthlyYearly": {
                        "from": "",
                        "to": "",
                        "period": "Yearly"
                    },
                    "remunerationIfTotalPackageValue": "",
                    "remunerationIfPerKgMS": "",
                    "remunerationIfPercentageOfMilkCheque": ""
                }
            }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include AI routes
app.include_router(ai_router)

# Custom OpenAPI JSON endpoint that preserves field order
@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json():
    return OrderPreservingJSONResponse(content=app.openapi())

@app.get("/")
async def root():
    return {
        "message": "Welcome to Tomsliv AI Service",
        "status": "running",
        "endpoints": {
            "process_candidate": "/ai/process-candidate"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)