# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "pandas",
#     "tenacity",
#     "openpyxl",
# ]
# ///
from tenacity import retry, stop_after_attempt, wait_exponential
import pandas as pd
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from llm_classify_article import classify_article_relevance

MAX_WORKERS = 20

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def process_batch(batch, title_col, abstract_col):
    """Process a batch with parallel classification"""
    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for _, row in batch.iterrows():
            future = executor.submit(
                classify_article_relevance,
                title=row[title_col],
                abstract=row[abstract_col] if pd.notna(row[abstract_col]) else "",
                use_cot=False,
            )
            futures.append(future)

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error in classification: {str(e)}")
                results.append(("#error", 0.0))  # Default values on error

    return pd.DataFrame(
        results,
        columns=["relevance", "probability", "prompt_tokens", "completion_tokens"],
    )


def process_excel_articles(input_path, batch_size=50):
    """Process Excel with reliable partial saves"""
    # Initialize tracking variables
    partial_base = None
    last_saved_file = None

    try:
        # Read and validate input
        df = pd.read_excel(input_path, sheet_name="Sheet1", engine="openpyxl")

        title_col = "article_title"
        abstract_col = "article_abstract"

        required_columns = [title_col, abstract_col]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            available = "\n- ".join(df.columns)
            raise ValueError(
                f"Missing required columns: {missing}\nAvailable columns:\n- {available}"
            )

        # Initialize result columns as pd.NA (proper nullable type)
        df = df.assign(
            relevance=pd.NA,
            probability=pd.NA,
            prompt_tokens=pd.NA,
            completion_tokens=pd.NA,
        )
        total = len(df)
        partial_base = f"partial_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Process batches sequentially
        for start in range(0, total, batch_size):
            end = min(start + batch_size, total)
            batch_number = (start // batch_size) + 1
            partial_file = f"{partial_base}_batch_{batch_number}.xlsx"

            try:
                print(f"\nProcessing batch {batch_number}: rows {start + 1}-{end}")

                # Process ONLY the current batch slice
                batch_slice = df.iloc[start:end].copy()
                batch_results = process_batch(batch_slice, title_col, abstract_col)

                # Directly update main dataframe
                df.loc[
                    start : end - 1,
                    ["relevance", "probability", "prompt_tokens", "completion_tokens"],
                ] = batch_results.values

                # Save FULL STATE including previous batches
                current_progress = df.iloc[:end]  # All rows processed so far
                current_progress.to_excel(partial_file, index=False)
                last_saved_file = partial_file
                print(f"Saved progress to {partial_file}")

            except Exception as batch_error:
                print(f"⚠️ Failed batch {batch_number} after retries")
                if last_saved_file:
                    print(f"Last valid save: {last_saved_file}")
                raise

        # Final save with all results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_output = f"final_excel_{timestamp}.xlsx"
        df.to_excel(final_output, index=False)
        print(f"\n✅ Successfully processed {total} rows. Final output: {final_output}")

    except Exception as e:
        print(f"🛑 Critical error: {str(e)}")
        if last_saved_file:
            print(f"Recover data from: {last_saved_file}")
        raise


if __name__ == "__main__":
    process_excel_articles(
        input_path="input_articles.xlsx",
        batch_size=100,  # Process 100 rows at a time (10 parallel workers × 10 classifications)
    )
