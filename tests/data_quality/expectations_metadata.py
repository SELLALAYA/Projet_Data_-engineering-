"""
Great Expectations — Validation des métadonnées produits
"""
import great_expectations as ge
import pandas as pd


def validate_metadata(df: pd.DataFrame) -> bool:
    """
    Valide les métadonnées des produits scrappés
    """
    gdf = ge.from_pandas(df)

    # ─────────────────────────────────────
    # COLONNES OBLIGATOIRES
    # ─────────────────────────────────────
    gdf.expect_column_to_exist("product_id")
    gdf.expect_column_to_exist("product_name")
    gdf.expect_column_to_exist("category")
    gdf.expect_column_to_exist("platform")
    gdf.expect_column_to_exist("rating")
    gdf.expect_column_to_exist("reviews_count")

    # ─────────────────────────────────────
    # VALEURS NON NULLES
    # ─────────────────────────────────────
    gdf.expect_column_values_to_not_be_null("product_id")
    gdf.expect_column_values_to_not_be_null("product_name")
    gdf.expect_column_values_to_not_be_null("category")

    # ─────────────────────────────────────
    # RATING VALIDE (0 à 5)
    # ─────────────────────────────────────
    gdf.expect_column_values_to_be_between(
        "rating",
        min_value=0,
        max_value=5
    )

    # ─────────────────────────────────────
    # REVIEWS COUNT POSITIF
    # ─────────────────────────────────────
    gdf.expect_column_values_to_be_between(
        "reviews_count",
        min_value=0,
        max_value=1000000
    )

    # ─────────────────────────────────────
    # PLATFORM VALIDE
    # ─────────────────────────────────────
    gdf.expect_column_values_to_be_in_set(
        "platform",
        ["amazon", "jumia"]
    )

    # ─────────────────────────────────────
    # LONGUEUR NOM PRODUIT
    # ─────────────────────────────────────
    gdf.expect_column_value_lengths_to_be_between(
        "product_name",
        min_value=3,
        max_value=500
    )

    # Résultats
    results = gdf.validate()

    print(f"Validation réussie : {results['success']}")
    print(f"Tests passés : {results['statistics']['successful_expectations']}")
    print(f"Tests échoués : {results['statistics']['unsuccessful_expectations']}")

    return results["success"]


if __name__ == "__main__":
    # Test avec données exemple
    sample_data = pd.DataFrame({
        "product_id": ["P001", "P002", "P003"],
        "product_name": ["Product A", "Product B", "Product C"],
        "category": ["electronics", "clothing", "electronics"],
        "platform": ["amazon", "jumia", "amazon"],
        "rating": [4.5, 3.8, 4.2],
        "reviews_count": [150, 89, 320]
    })
    validate_metadata(sample_data)