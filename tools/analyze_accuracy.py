import re
import os

def parse_truth(filename):
    print(f"Parsing {filename}...")
    truth = {}
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return truth
        
    with open(filename, 'r') as f:
        for line in f:
            # Look for: email_2_safe.txt (SAFE)
            match = re.search(r'email_(\d+)_.*?\((SAFE|PHISHING)\)', line)
            if match:
                email_id = match.group(1)
                label = match.group(2)
                truth[email_id] = label
    print(f" -> Found {len(truth)} records in truth file.")
    if len(truth) > 0:
        print(f" -> First few IDs: {list(truth.keys())[:5]}")
    return truth

def parse_predictions(filename):
    print(f"Parsing {filename}...")
    predictions = {}
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return predictions

    current_email_id = None
    
    with open(filename, 'r') as f:
        for line in f:
            # Look for: Scanning ...email_2_safe.txt...
            # Handle both forward slash and backslash
            file_match = re.search(r'email_(\d+)_', line)
            if file_match:
                current_email_id = file_match.group(1)
            
            if "Verdict: SAFE" in line and current_email_id:
                predictions[current_email_id] = "SAFE"
                # Reset after finding verdict
                current_email_id = None
            elif "Verdict: MALICIOUS" in line and current_email_id:
                predictions[current_email_id] = "PHISHING"
                current_email_id = None
                
    print(f" -> Found {len(predictions)} records in gateway log.")
    if len(predictions) > 0:
        print(f" -> First few IDs: {list(predictions.keys())[:5]}")
    return predictions

def main():
    truth = parse_truth("generatetrafficoutput.txt")
    preds = parse_predictions("gatewayoutput.txt")
    
    correct = 0
    total = 0
    errors = []

    # Find intersection of IDs
    common_ids = set(truth.keys()) & set(preds.keys())
    print(f"Matching IDs found: {len(common_ids)}")

    for email_id in common_ids:
        expected = truth[email_id]
        actual = preds[email_id]
        total += 1
        
        if expected == actual:
            correct += 1
        else:
            errors.append(f"Email {email_id}: Expected {expected}, Got {actual}")

    if total == 0:
        print("Cannot calculate accuracy (No matching IDs).")
        return

    accuracy = (correct / total) * 100
    print(f"\n--- ACCURACY RESULTS ---")
    print(f"Analyzed {total} emails.")
    print(f"Accuracy: {accuracy:.2f}%")
    
    if errors:
        print(f"\n{len(errors)} Mismatches found:")
        for e in errors:
            print(e)
    else:
        print("Perfect Match!")

if __name__ == "__main__":
    main()
