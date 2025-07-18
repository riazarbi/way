#!/bin/bash

# Code Quality Scoring Script
# Uses cloc and jscpd to evaluate code quality metrics

set -e

# Check if required tools are installed
check_dependencies() {
    if ! command -v cloc &> /dev/null; then
        echo "Error: cloc is not installed. Please install it first."
        echo "Install with: sudo apt install cloc"
        exit 1
    fi
    
    if ! command -v jscpd &> /dev/null; then
        echo "Error: jscpd is not installed. Please install it first."
        echo "Install with: npm install -g jscpd"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo "Error: jq is not installed. Please install it first."
        echo "Install with: sudo apt install jq"
        exit 1
    fi
}



# Calculate LOC metrics using cloc
calculate_loc_metrics() {
    # Check if cloc is available
    if ! command -v cloc &> /dev/null; then
        echo "Warning: cloc not found, using fallback method..."
        # Fallback: count Python files manually
        python_files=$(find "$PWD" -name "*.py" -not -path "*/\.git/*" -not -path "*/__pycache__/*" -not -path "*/.pytest_cache/*" -not -path "*/.venv/*" | wc -l)
        total_files=$python_files
        total_code=0
        total_comment=0
        total_blank=0
        return
    fi
    
    # Get source directories from quality config
    source_dirs="."
    if [ -f ".quality-config.json" ]; then
        source_dirs=$(jq -r '.code_source_directories // ["."] | join(",")' .quality-config.json)
    fi
    
    # Debug: Show what directories we're analyzing
    echo "Analyzing directories: $source_dirs"
    
    # Run cloc with JSON output, focusing on source directories
    echo "Running cloc on: $source_dirs"
    cloc_output=$(cloc --json --exclude-dir=docs,.git,__pycache__,.pytest_cache,.venv,.cache,.local,.npm,completions.egg-info,.claude,node_modules,build,dist,*.egg-info $source_dirs 2>&1)
    
    # Debug: Show what cloc actually output
    echo "cloc output: $cloc_output"
    
    # Check if cloc output is valid JSON
    if ! echo "$cloc_output" | jq empty 2>/dev/null; then
        echo "Warning: cloc output is not valid JSON, using fallback..."
        cloc_output='{}'
    fi
    
    # Debug: Check if cloc found any files
    if [ "$cloc_output" = "{}" ]; then
        echo "Warning: cloc found no files. Checking what files exist..."
        echo "Looking in directories: $source_dirs"
        for dir in $(echo "$source_dirs" | tr ',' ' '); do
            echo "Files in $dir:"
            find "$PWD/$dir" -name "*.py" 2>/dev/null | head -3
        done
    fi
    
    # Parse JSON output
    total_files=0
    total_code=0
    total_comment=0
    total_blank=0
    
    # Extract totals from cloc output
    if [ "$cloc_output" != "{}" ]; then
        total_files=$(echo "$cloc_output" | jq -r '.SUM.nFiles // 0')
        total_code=$(echo "$cloc_output" | jq -r '.SUM.code // 0')
        total_comment=$(echo "$cloc_output" | jq -r '.SUM.comment // 0')
        total_blank=$(echo "$cloc_output" | jq -r '.SUM.blank // 0')
    fi
    
    # Calculate averages
    avg_lines_per_file=0
    if [ $total_files -gt 0 ]; then
        avg_lines_per_file=$((total_code / total_files))
    fi
    
    # Calculate ratios
    comment_ratio=0
    if [ $total_code -gt 0 ]; then
        comment_ratio=$(echo "scale=2; $total_comment * 100 / $total_code" | bc -l 2>/dev/null || echo "0")
    fi
    
    blank_ratio=0
    total_lines=$((total_code + total_comment + total_blank))
    if [ $total_lines -gt 0 ]; then
        blank_ratio=$(echo "scale=2; $total_blank * 100 / $total_lines" | bc -l 2>/dev/null || echo "0")
    fi
}

# Calculate duplication metrics using jscpd
calculate_duplication_metrics() {
    # Check if jscpd is available
    if ! command -v jscpd &> /dev/null; then
        echo "Warning: jscpd not found, skipping duplication analysis..."
        duplication_percentage=0
        duplicated_lines=0
        duplicated_blocks=0
        return
    fi
    
    # Get source directories from quality config
    source_dirs="."
    if [ -f ".quality-config.json" ]; then
        source_dirs=$(jq -r '.code_source_directories // ["."] | join(" ")' .quality-config.json)
    fi
    
    # Run jscpd with JSON output, focusing on source directories
    jscpd_output=$(jscpd --reporters json --exclude "docs/**/*,.git/**/*,__pycache__/**/*,.pytest_cache/**/*,.venv/**/*,.cache/**/*,.local/**/*,.npm/**/*,completions.egg-info/**/*,node_modules/**/*,build/**/*,dist/**/*,*.egg-info/**/*" $source_dirs 2>/dev/null || echo '{}')
    
    # Parse JSON output
    duplication_percentage=0
    duplicated_lines=0
    duplicated_blocks=0
    
    if [ "$jscpd_output" != "{}" ]; then
        duplication_percentage=$(echo "$jscpd_output" | jq -r '.statistics.total.percentage // 0')
        duplicated_lines=$(echo "$jscpd_output" | jq -r '.statistics.total.duplicatedLines // 0')
        duplicated_blocks=$(echo "$jscpd_output" | jq -r '.statistics.total.duplicatedBlocks // 0')
    fi
}

# Calculate test and linting metrics using quality config
calculate_quality_metrics() {
    # Initialize metrics
    test_count=0
    test_failure_rate=0
    lint_error_count=0
    lint_warning_count=0
    
    # Check if quality config exists
    if [ -f ".quality-config.json" ]; then
        # Extract test count
        test_count_cmd=$(jq -r '.metrics.test_count.command // "echo 0"' .quality-config.json)
        test_count=$(eval "$test_count_cmd" 2>/dev/null || echo "0")
        
        # Extract test failure rate
        test_failure_cmd=$(jq -r '.metrics.test_failure_rate.command // "echo 0"' .quality-config.json)
        test_failure_rate=$(eval "$test_failure_cmd" 2>/dev/null || echo "0")
        
        # Extract lint error count
        lint_error_cmd=$(jq -r '.metrics.lint_error_count.command // "echo 0"' .quality-config.json)
        lint_error_count=$(eval "$lint_error_cmd" 2>/dev/null || echo "0")
        
        # Extract lint warning count
        lint_warning_cmd=$(jq -r '.metrics.lint_warning_count.command // "echo 0"' .quality-config.json)
        lint_warning_count=$(eval "$lint_warning_cmd" 2>/dev/null || echo "0")
    fi
}

# Display results
display_results() {
    echo "========================================"
    echo "CODE QUALITY METRICS"
    echo "========================================"
    echo ""
    echo "LINES OF CODE:"
    echo "  Total Files: $total_files"
    echo "  Total Lines of Code: $total_code"
    echo "  Total Comments: $total_comment"
    echo "  Total Blank Lines: $total_blank"
    echo "  Average Lines per File: $avg_lines_per_file"
    echo ""
    echo "RATIOS:"
    echo "  Comment Ratio: ${comment_ratio}%"
    echo "  Blank Line Ratio: ${blank_ratio}%"
    echo ""
    echo "DUPLICATION:"
    echo "  Code Duplication: ${duplication_percentage}%"
    echo "  Duplicated Lines: $duplicated_lines"
    echo "  Duplicated Blocks: $duplicated_blocks"
    echo ""
    echo "TESTING:"
    echo "  Test Count: $test_count"
    echo "  Test Failures: $test_failure_rate"
    echo ""
    echo "LINTING:"
    echo "  Lint Errors: $lint_error_count"
    echo "  Lint Warnings: $lint_warning_count"
}

# Main execution
main() {
    check_dependencies
    calculate_loc_metrics
    calculate_duplication_metrics
    calculate_quality_metrics
    display_results
}

# Run main function
main "$@"
