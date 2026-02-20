import pandas as pd

def aggregate_student_data(file_path):
    print(f"Loading data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find '{file_path}'. Please run Exercise4_3.py first.")
        return
        
    print("\n--- Loaded Data ---")
    print(df.head())

    print("\n--- 1. Grouping by Class ---")
    # Assuming 'class_name' is the column after running Exercise4_3.py
    grouped_by_class = df.groupby('class_name')
    
    # Calculate Mean scores per class
    print("\nAverage Scores per Class (Mean):")
    mean_scores = grouped_by_class[['math_score', 'science_score', 'english_score', 'history_score']].mean()
    print(mean_scores)
    
    print("\n--- 2. Summing up values ---")
    # Calculate Total scores per class
    print("\nTotal Scores per Class (Sum):")
    total_scores = grouped_by_class[['math_score', 'science_score', 'english_score', 'history_score']].sum()
    print(total_scores)
    
    print("\n--- 3. Multiple Aggregations ---")
    # Using agg() to compute multiple statistics at once for math_score
    agg_stats = grouped_by_class['math_score'].agg(['mean', 'max', 'min', 'count'])
    print("\nMath Score Statistics per Class:")
    print(agg_stats)

if __name__ == "__main__":
    # We will use the cleaned data from Exercise 4.3
    # Make sure to run Exercise4_3.py before running this script
    aggregate_student_data('cleaned_student_data.csv')
