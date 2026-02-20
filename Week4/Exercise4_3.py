import pandas as pd

def clean_student_data(file_path):
    print(f"Loading data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Could not find '{file_path}'. Please make sure the file exists.")
        return None
        
    print("\n--- Original Data ---")
    print(df.head(10))
    print("\nDataFrame Info:")
    df.info()

    print("\n--- 1. Handling Missing Values ---")
    # Identify missing values
    print("Missing values per column:\n", df.isnull().sum())
    
    # Fill missing numeric values (Math, Science, English, History) with the mean of the column
    numeric_cols = ['Math', 'Science', 'English', 'History']
    for col in numeric_cols:
        if col in df.columns:
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val) # Best practice in Pandas
            print(f"Filled missing values in '{col}' with mean: {mean_val:.2f}")

    # Fill missing categorical values (Class, Name)
    if 'Name' in df.columns:
        df['Name'] = df['Name'].fillna('Unknown')
        print("Filled missing values in 'Name' with 'Unknown'.")
    if 'Class' in df.columns:
        df = df.dropna(subset=['Class']).copy() # Important to use .copy() to avoid SettingWithCopyWarning later
        print("Dropped rows where 'Class' is missing.")
        
    print("\nMissing values after cleaning:\n", df.isnull().sum())

    print("\n--- 2. Renaming Columns ---")
    # Rename columns to be lowercase and more standard snake_case
    df = df.rename(columns={
        'Student ID': 'student_id',
        'Name': 'name',
        'Math': 'math_score',
        'Science': 'science_score',
        'English': 'english_score',
        'History': 'history_score',
        'Class': 'class_name'
    })
    
    print("Columns renamed successfully.")
    print("\n--- Cleaned Data ---")
    print(df.head(10))
    
    return df

if __name__ == "__main__":
    cleaned_data = clean_student_data('student_data.csv')
    if cleaned_data is not None:
        # Save the cleaned data to be used by the next exercise optionally
        cleaned_data.to_csv('cleaned_student_data.csv', index=False)
        print("\nCleaned data saved to 'cleaned_student_data.csv'")
