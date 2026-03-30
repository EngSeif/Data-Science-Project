import numpy as np
import pandas as pd
import great_expectations as gx

class DataValidator:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def run_validation(self, df: pd.DataFrame):
        context = gx.get_context(mode="ephemeral")

        data_source  = context.data_sources.add_pandas(name="pandas")
        data_asset   = data_source.add_dataframe_asset(name="dataset")
        batch_def    = data_asset.add_batch_definition_whole_dataframe("batch")
        batch        = batch_def.get_batch(batch_parameters={"dataframe": df})


        suite = context.suites.add(
            gx.ExpectationSuite(name="dataset_validation_suite")
        )


        #add suits here
        #----------------------------------------------
        
        
        #----------------------------------------------

        validation_def = context.validation_definitions.add(
            gx.ValidationDefinition(
                name="users_validation",
                data=batch_def,
                suite=suite
            )
        )


        results = validation_def.run(batch_parameters={"dataframe": df})


        self._print_report(results)
        
        context.build_data_docs()
        context.open_data_docs()

        return results
    


    def _print_report(self, results):
        """Print a clean summary of GX v1.x validation results."""

        pass





