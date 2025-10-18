#!/usr/bin/env python3
"""HTML report generator for ObfuscateLLVM."""

import json
from pathlib import Path
from typing import Dict, Any


HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <title>ObfuscateLLVM Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
        .pass-enabled {{ color: #27ae60; font-weight: bold; }}
        .pass-disabled {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        .chart {{ width: 100%; height: 200px; background: #f8f9fa; border: 1px solid #ddd; 
                 display: flex; align-items: center; justify-content: center; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ObfuscateLLVM Report</h1>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Configuration</h2>
        <table>
            <tr><th>Input</th><td>{input}</td></tr>
            <tr><th>Output</th><td>{output}</td></tr>
            <tr><th>Target</th><td>{target}</td></tr>
            <tr><th>Profile</th><td>{profile}</td></tr>
            <tr><th>Cycles</th><td>{cycles}</td></tr>
            <tr><th>Junk Density</th><td>{junk_density}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Obfuscation Passes</h2>
        <div class="metric">
            String Encryption: <span class="{string_class}">{string_status}</span>
        </div>
        <div class="metric">
            Junk Insertion: <span class="{junk_class}">{junk_status}</span>
        </div>
        <div class="metric">
            Symbol Renaming: <span class="{symbol_class}">{symbol_status}</span>
        </div>
    </div>
    
    <div class="section">
        <h2>Metrics</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Input Size</td><td>{input_size} bytes</td></tr>
            <tr><td>Output Size</td><td>{output_size} bytes</td></tr>
            <tr><td>Size Increase</td><td>{size_increase}%</td></tr>
            <tr><td>Strings Encrypted</td><td>{strings_encrypted}</td></tr>
            <tr><td>Junk Blocks Added</td><td>{junk_blocks_added}</td></tr>
            <tr><td>Symbols Renamed</td><td>{symbols_renamed}</td></tr>
            <tr><td>Processing Time</td><td>{processing_time}s</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Size Comparison</h2>
        <div class="chart">
            <div style="width: {input_bar}%; background: #3498db; height: 30px; margin: 5px; display: flex; align-items: center; justify-content: center; color: white;">
                Input: {input_size} bytes
            </div>
            <div style="width: {output_bar}%; background: #e74c3c; height: 30px; margin: 5px; display: flex; align-items: center; justify-content: center; color: white;">
                Output: {output_size} bytes
            </div>
        </div>
    </div>
    
    {watermark_section}
</body>
</html>"""


def generate_html_report(report_data: Dict[str, Any], output_path: str) -> None:
    """Generate HTML report from JSON data."""
    
    # Calculate derived metrics
    input_size = report_data["metrics"]["input_size"]
    output_size = report_data["metrics"]["output_size"]
    size_increase = round(((output_size - input_size) / input_size * 100), 1) if input_size > 0 else 0
    
    # Calculate bar widths for chart (relative to max size)
    max_size = max(input_size, output_size)
    input_bar = round((input_size / max_size * 80), 1) if max_size > 0 else 50
    output_bar = round((output_size / max_size * 80), 1) if max_size > 0 else 50
    
    # Pass status formatting
    passes = report_data["passes"]
    string_status = "ENABLED" if passes["string_encryption"] else "DISABLED"
    string_class = "pass-enabled" if passes["string_encryption"] else "pass-disabled"
    
    junk_status = "ENABLED" if passes["junk_insertion"] else "DISABLED"
    junk_class = "pass-enabled" if passes["junk_insertion"] else "pass-disabled"
    
    symbol_status = "ENABLED" if passes["symbol_renaming"] else "DISABLED"
    symbol_class = "pass-enabled" if passes["symbol_renaming"] else "pass-disabled"
    
    # Watermark section
    watermark_section = ""
    if report_data.get("watermark"):
        watermark_section = f"""
        <div class="section">
            <h2>Watermark</h2>
            <p>Embedded: {report_data["watermark"]}</p>
        </div>"""
    
    # Fill template
    html_content = HTML_TEMPLATE.format(
        timestamp=report_data["timestamp"],
        input=report_data["input"],
        output=report_data["output"],
        target=report_data["target"],
        profile=report_data.get("profile", "None"),
        cycles=report_data["config"]["cycles"],
        junk_density=report_data["config"]["junk_density"],
        
        string_status=string_status,
        string_class=string_class,
        junk_status=junk_status,
        junk_class=junk_class,
        symbol_status=symbol_status,
        symbol_class=symbol_class,
        
        input_size=input_size,
        output_size=output_size,
        size_increase=size_increase,
        strings_encrypted=report_data["metrics"]["strings_encrypted"],
        junk_blocks_added=report_data["metrics"]["junk_blocks_added"],
        symbols_renamed=report_data["metrics"]["symbols_renamed"],
        processing_time=report_data["performance"]["processing_time_seconds"],
        
        input_bar=input_bar,
        output_bar=output_bar,
        
        watermark_section=watermark_section
    )
    
    with open(output_path, 'w') as f:
        f.write(html_content)


if __name__ == "__main__":
    # Test with example report
    with open("reports/example_report.json") as f:
        data = json.load(f)
    generate_html_report(data, "reports/example_report.html")