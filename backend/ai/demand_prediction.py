import sys
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression


# Allow Python to find database.py in the backend folder
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database import get_connection, get_sqlalchemy_engine


def get_request_data():
    engine = get_sqlalchemy_engine()

    query = """
        SELECT
            DATE(request_date) AS request_date,
            COUNT(*) AS request_count
        FROM food_requests
        GROUP BY DATE(request_date)
        ORDER BY request_date
    """

    df = pd.read_sql(query, engine)

    engine.dispose()

    return df


def predict_food_demand():
    df = get_request_data()

    # We need at least two days of data
    if len(df) < 2:
        return None

    # Convert dates into sequential numbers
    df["day"] = range(1, len(df) + 1)

    X = df[["day"]]
    y = df["request_count"]

    # Create and train the model
    model = LinearRegression()
    model.fit(X, y)

    # Predict the next day
    next_day = pd.DataFrame({
        "day": [len(df) + 1]
    })

    prediction = model.predict(next_day)

    # Never return a negative number of requests
    return max(0, round(prediction[0]))


def get_demand_level(prediction):
    if prediction is None:
        return "Insufficient Data"

    if prediction < 5:
        return "Low"

    if prediction < 10:
        return "Medium"

    return "High"


def get_location_demand():
    connection = get_connection()

    query = """
        SELECT
            location,
            COUNT(*) AS request_count
        FROM food_requests
        GROUP BY location
        ORDER BY request_count DESC
    """

    df = pd.read_sql(query, connection)

    connection.close()

    if df.empty:
        return []

    results = []

    for _, row in df.iterrows():

        request_count = int(row["request_count"])

        if request_count >= 10:
            demand_level = "High"

        elif request_count >= 5:
            demand_level = "Medium"

        else:
            demand_level = "Low"

        results.append({
            "location": row["location"],
            "requests": request_count,
            "demand_level": demand_level
        })

    return results


def predict_location_demand():
    engine = get_sqlalchemy_engine()

    query = """
        SELECT
            location,
            DATE(request_date) AS request_date,
            COUNT(*) AS request_count
        FROM food_requests
        GROUP BY location, DATE(request_date)
        ORDER BY location, request_date
    """

    df = pd.read_sql(query, engine)

    engine.dispose()

    if df.empty:
        return []

    predictions = []

    for location in df["location"].unique():

        location_df = df[
            df["location"] == location
        ].copy()

        # Need at least two days of data
        if len(location_df) < 2:
            continue

        location_df["day"] = range(
            1,
            len(location_df) + 1
        )

        X = location_df[["day"]]
        y = location_df["request_count"]

        model = LinearRegression()
        model.fit(X, y)

        next_day = pd.DataFrame({
            "day": [len(location_df) + 1]
        })

        prediction = model.predict(next_day)

        predicted_requests = max(
            0,
            round(prediction[0])
        )

        demand_level = get_demand_level(
            predicted_requests
        )

        predictions.append({
            "location": location,
            "prediction": predicted_requests,
            "demand_level": demand_level
        })

    return predictions


def generate_recommendations():
    location_predictions = predict_location_demand()

    if not location_predictions:
        return []

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get available food totals for ALL locations in one query
        cursor.execute(
            """
            SELECT
                location,
                COALESCE(SUM(quantity), 0) AS total_food
            FROM food_donations
            WHERE status = 'Available'
            GROUP BY location
            """
        )

        food_by_location = {
            row["location"]: row["total_food"]
            for row in cursor.fetchall()
        }

        recommendations = []

        for location in location_predictions:

            location_name = location["location"]
            prediction = location["prediction"]

            available_food = food_by_location.get(
                location_name,
                0
            )

            if prediction >= 10:

                if available_food < prediction:
                    recommendation = (
                        f"High demand expected at "
                        f"{location_name}. "
                        f"Increase food supply."
                    )
                else:
                    recommendation = (
                        f"High demand expected at "
                        f"{location_name}. "
                        f"Current food supply may be sufficient."
                    )

            elif prediction >= 5:

                if available_food < prediction:
                    recommendation = (
                        f"Moderate demand expected at "
                        f"{location_name}. "
                        f"Consider increasing food supply."
                    )
                else:
                    recommendation = (
                        f"Moderate demand expected at "
                        f"{location_name}. "
                        f"Current supply appears sufficient."
                    )

            else:

                recommendation = (
                    f"Low demand expected at "
                    f"{location_name}. "
                    f"Current supply should be monitored."
                )

            recommendations.append({
                "location": location_name,
                "prediction": prediction,
                "available_food": available_food,
                "recommendation": recommendation
            })

        return recommendations

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":

    prediction = predict_food_demand()

    if prediction is None:

        print(
            "Not enough food request data "
            "to make a prediction."
        )

    else:

        demand_level = get_demand_level(prediction)

        print(
            f"Predicted food requests for the next day: "
            f"{prediction}"
        )

        print(
            f"Demand level: {demand_level}"
        )

    print("\nLocation Predictions:")

    location_predictions = predict_location_demand()

    if location_predictions:

        for item in location_predictions:

            print(
                f"{item['location']}: "
                f"{item['prediction']} requests "
                f"({item['demand_level']})"
            )

    else:

        print(
            "Not enough data for location predictions."
        )

    print("\nRecommendations:")

    recommendations = generate_recommendations()

    if recommendations:

        for item in recommendations:

            print(
                f"{item['location']}: "
                f"{item['recommendation']}"
            )

    else:

        print(
            "No recommendations available."
        )