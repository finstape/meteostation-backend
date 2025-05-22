import joblib
import pandas as pd

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Central
from app.utils.queries import get_last_data


def predict_weather(
    temperature: float, humidity: float, pressure_mmhg: float, timestamp: str
) -> dict:
    """
    Function to predict temperature and rain probability

    Args:
        temperature (float): Temperature in degrees Celsius
        humidity (float): Humidity in percentage
        pressure_mmhg (float): Pressure in mmHg
        timestamp (str): Timestamp in the format YYYY-MM-DD HH:MM

    Returns:
        dict: Dictionary with predicted temperature and rain probability
    """
    # Load the model and scaler
    model = joblib.load('app/utils/weather_predict/best_model.pkl')
    scaler = joblib.load('app/utils/weather_predict/scaler.pkl')

    # Convert the timestamp to datetime
    dt = pd.to_datetime(timestamp)
    hour = dt.hour
    day = dt.day
    month = dt.month

    # Create feature set
    X_input = pd.DataFrame(
        [
            {
                'Temperature': temperature,
                'Humidity': humidity,
                'Pressure (mmHg)': pressure_mmhg,
                'Month': month,
                'Hour': hour,
                'DayOfMonth': day,
            }
        ]
    )

    # Scale the features
    X_scaled = scaler.transform(X_input)

    # Make predictions
    y_pred = model.predict(X_scaled)[0]
    predicted_temp = y_pred[0]
    predicted_rain = int(y_pred[1] >= 0.5)

    # Return the result
    return {
        "predicted_temp": round(predicted_temp, 1),
        "predicted_rain": bool(predicted_rain),
    }


async def get_data_weather_prediction(session: AsyncSession):
    """
    Main function that retrieves the latest data from the Central model
    and calls the function to predict values

    Args:
        session (AsyncSession): Asynchronous session for database interaction

    Returns:
        dict: Dictionary with predicted temperature and rain probability
    """
    # Retrieve the latest data from the Central model
    last_data = await get_last_data(session, Central)
    if not last_data:
        raise ValueError("No data available in the Central table")

    # Extract necessary data
    temperature = last_data.temperature
    humidity = last_data.humidity
    pressure_mmhg = last_data.pressure
    timestamp = last_data.created_at.strftime("%Y-%m-%d %H:%M")

    # Call the prediction function
    return predict_weather(temperature, humidity, pressure_mmhg, timestamp)
