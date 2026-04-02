import numpy as np
import pandas as pd
import great_expectations as gx

class DataValidator:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def run_validation(self):
        df = self.df
        context = gx.get_context(mode="ephemeral")

        data_source  = context.data_sources.add_pandas(name="pandas")
        data_asset   = data_source.add_dataframe_asset(name="dataset")
        batch_def    = data_asset.add_batch_definition_whole_dataframe("batch")

        suite = context.suites.add(
            gx.ExpectationSuite(name="dataset_validation_suite")
        )


        #add suits here
        #----------------------------------------------
        
        # ------------------------------------------------------------------ #
        #  1. COMPLETENESS                                                   #
        # ------------------------------------------------------------------ #
        for col in df.columns:
            suite.add_expectation(
                gx.expectations.ExpectColumnValuesToNotBeNull(column=col)
            )
 
        # ------------------------------------------------------------------ #
        #  2. ACCURACY                                                       #
        # ------------------------------------------------------------------ #
 
        numeric_ranges = {
            "age": (0, 120),
            "bmi": (10, 70),
            "HbA1c_level": (3, 15),
            "blood_glucose_level": (50, 400)
        }
        for col, (min_val, max_val) in numeric_ranges.items():
            suite.add_expectation(
                gx.expectations.ExpectColumnValuesToBeBetween(
                    column=col, min_value=min_val, max_value=max_val
                )
            )

        # Categorical columns
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="gender",
                value_set=["Male", "Female"]
            )
        )
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="smoking_history",
                value_set=["never", "former", "current", "ever", "not current", "No Info"]
            )
        )

        # Binary columns
        for binary_col in ["hypertension", "heart_disease", "diabetes"]:
            suite.add_expectation(
                gx.expectations.ExpectColumnValuesToBeInSet(
                    column=binary_col,
                    value_set=[0, 1]
                )
            )
 
        # ------------------------------------------------------------------ #
        #  3. CONSISTENCY                                                    #
        # ------------------------------------------------------------------ #
 
        df_consistency = df.copy()
 
        # Flag: high HbA1c (>=7.5) labelled as non-diabetic
        df_consistency["_high_hba1c_no_diabetes"] = (
            (df_consistency["HbA1c_level"] >= 7.5) & (df_consistency["diabetes"] == 0)
        ).astype(int)
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="_high_hba1c_no_diabetes",
                value_set=[0],
                notes="High HbA1c (>=7.5%) must not appear in non-diabetic records.",
            )
        )
 
        # Flag: blood_glucose > 300 without diabetes label
        df_consistency["_high_glucose_no_diabetes"] = (
            (df_consistency["blood_glucose_level"] > 300) & (df_consistency["diabetes"] == 0)
        ).astype(int)
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="_high_glucose_no_diabetes",
                value_set=[0],
                notes="Blood glucose > 300 must not appear in non-diabetic records.",
            )
        )
 
        # Flag: age < 10 with hypertension or heart_disease
        df_consistency["_young_with_conditions"] = (
            (df_consistency["age"] < 10)
            & ((df_consistency["hypertension"] == 1) | (df_consistency["heart_disease"] == 1))
        ).astype(int)
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="_young_with_conditions",
                value_set=[0],
                notes="Patients under 10 should not have hypertension or heart disease.",
            )
        )
 
        # ------------------------------------------------------------------ #
        #  4. UNIQUENESS                                                     #
        # ------------------------------------------------------------------ #
        df_consistency["_is_duplicate"] = (
            df_consistency[df.columns.tolist()]
            .duplicated(keep="first")
            .astype(int)
        )
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeInSet(
                column="_is_duplicate",
                value_set=[0],
                notes="Each row should be unique across all columns.",
            )
        )
        
        #----------------------------------------------
        batch = batch_def.get_batch(batch_parameters={"dataframe": df_consistency})

        validation_def = context.validation_definitions.add(
            gx.ValidationDefinition(
                name="dataset_validation",
                data=batch_def,
                suite=suite,
            )
        )
 
        results = validation_def.run(batch_parameters={"dataframe": df_consistency})
 
        self._print_report(results)
 
        return results


    def _print_report(self, results):
        """Print a clean summary of GX v1.x validation results."""

        success = results.success

        print("=" * 58)
        print("    DATA VALIDATION REPORT  (Great Expectations v1.x)")
        print("=" * 58)
        print(f"  Overall Result : {'PASSED' if success else 'FAILED'}")
        print("=" * 58)

        for exp_result in results.results:
            exp_type = exp_result.expectation_config.type
            col      = exp_result.expectation_config.kwargs.get("column", "table-level")
            passed   = exp_result.success
            status   = "PASS" if passed else "FAIL"

            print(f"\n[{status}] {exp_type}")
            print(f"   Column : {col}")

            if not passed and exp_result.result:
                r = exp_result.result
                if r.get("unexpected_count"):
                    print(f"   Issues : {r['unexpected_count']} unexpected values")
                if r.get("partial_unexpected_list"):
                    print(f"   Sample : {r['partial_unexpected_list'][:3]}")

        print("\n" + "=" * 58)

if __name__ == "__main__":
    df = pd.read_csv("data/raw/diabetes_prediction_dataset.csv")
    validator = DataValidator(df)
    validator.run_validation()