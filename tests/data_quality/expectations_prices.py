"""
Great Expectations — Validation des données de prix
"""
import great_expectations as ge
import pandas as pd


def validate_prices_data(df: pd.DataFrame) -> bool:
    """
    Valide les données de prix scrappées
    """
    # Convertir en GE DataFrame
    gdf = ge.from_pandas(df)

    # ─────────────────────────────────────
    # COLONNES OBLIGATOIRES
    # ─────────────────────────────────────
    gdf.expect_column_to_exist("product_id")
    gdf.expect_column_to_exist("price")
    gdf.expect_column_to_exist("timestamp")
    gdf.expect_column_to_exist("platform")
    gdf.expect_column_to_exist("product_name")

    # ─────────────────────────────────────
    # VALEURS NON NULLES
    # ─────────────────────────────────────
    gdf.expect_column_values_to_not_be_null("product_id")
    gdf.expect_column_values_to_not_be_null("price")
    gdf.expect_column_values_to_not_be_null("timestamp")

    # ─────────────────────────────────────
    # PRIX VALIDES
    # ─────────────────────────────────────
    gdf.expect_column_values_to_be_between(
        "price",
        min_value=0,
        max_value=100000
    )

    # ─────────────────────────────────────
    # PLATFORM VALIDE
    # ─────────────────────────────────────
    gdf.expect_column_values_to_be_in_set(
        "platform",
        ["amazon", "jumia"]
    )

    # ─────────────────────────────────────
    # UNICITE
    # ─────────────────────────────────────
    gdf.expect_column_values_to_be_unique("product_id")

    # Récupérer les résultats
    results = gdf.validate()

    # Afficher le résumé
    print(f"Validation réussie : {results['success']}")
    print(f"Tests passés : {results['statistics']['successful_expectations']}")
    print(f"Tests échoués : {results['statistics']['unsuccessful_expectations']}")

    return results["success"]


if __name__ == "__main__":
    # Test avec données exemple
    sample_data = pd.DataFrame({
        "product_id": ["P001", "P002", "P003"],
        "price": [29.99, 49.99, 99.99],
        "timestamp": ["2026-01-01", "2026-01-01", "2026-01-01"],
        "platform": ["amazon", "jumia", "amazon"],
        "product_name": ["Product A", "Product B", "Product C"]
    })
    validate_prices_data(sample_data)