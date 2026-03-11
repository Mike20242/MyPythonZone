import pandas as pd
import matplotlib.pyplot as plt

def load_and_preprocess_data(file_path):
    """Load the student data and perform basic preprocessing."""
    try:
        df = pd.read_csv(file_path)
        print("Data loaded successfully.")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
        
    # We will use the raw student_data for a complete pipeline demonstration
    if 'Student ID' in df.columns:
        # 1. Clean column names (make lowercase and replace spaces with underscores)
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # 2. Fill missing scores with 0 (assuming missing means didn't take the test)
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # 3. Drop rows with missing class
        class_col_name = 'class' if 'class' in df.columns else 'class_name'
        df = df.dropna(subset=[class_col_name]).copy()
        
    return df

def analyze_grades(df):
    """Calculate average scores and overall performance."""
    if df is None or df.empty:
        return None
        
    # Determine score columns
    score_cols = [col for col in df.columns if col in ['math', 'science', 'english', 'history']]
    
    if not score_cols:
        print("Error: Could not find score columns.")
        return None

    # Calculate overall average for each student across all subjects
    df['overall_average'] = df[score_cols].mean(axis=1)
    
    # Determine the class column name
    class_col = 'class' if 'class' in df.columns else 'class_name'
        
    # Calculate average by class for all subjects AND overall average
    print(f"\n--- Calculating averages by {class_col} ---")
    class_avg = df.groupby(class_col)[['overall_average'] + score_cols].mean()
    print(class_avg)
    
    return class_avg, df, class_col

def plot_results(class_avg, class_col):
    """Plot the results using matplotlib."""
    if class_avg is None:
        return
        
    print("\n--- Plotting Results ---")
    
    # 1. Bar chart for Overall Average by Class
    plt.figure(figsize=(8, 5))
    class_avg['overall_average'].plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('Overall Average Score by Class', fontsize=14)
    plt.xlabel('Class', fontsize=12)
    plt.ylabel('Average Score', fontsize=12)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('class_average.png')
    print("Saved -> 'class_average.png'")
    
    # 2. Multi-bar chart for Subject Averages by Class
    subject_cols = [col for col in class_avg.columns if col != 'overall_average']
    if subject_cols:
        plt.figure(figsize=(10, 6))
        # Pandas plot wrapper makes side-by-side grouped bar charts easy
        class_avg[subject_cols].plot(kind='bar', figsize=(10,6), colormap='Set2', edgecolor='black')
        plt.title('Subject Average Scores by Class', fontsize=14)
        plt.xlabel('Class', fontsize=12)
        plt.ylabel('Average Score', fontsize=12)
        plt.xticks(rotation=0)
        plt.legend(title='Subjects', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('subject_averages.png')
        print("Saved -> 'subject_averages.png'")

def main():
    print("=== Student Grade Analysis System ===")
    
    # 1. Load data point to original student data
    data_file = 'student_data.csv'
    
    # Load and preprocess
    df = load_and_preprocess_data(data_file)
    
    if df is not None:
        # 2. Compute averages
        class_avg, modified_df, class_col = analyze_grades(df)
        
        # 3. Plot results
        plot_results(class_avg, class_col)
        
        # Save processed data results
        modified_df.to_csv('processed_student_grades.csv', index=False)
        print("\nProcessed data saved to 'processed_student_grades.csv'. Analysis complete!")

if __name__ == "__main__":
    main()
