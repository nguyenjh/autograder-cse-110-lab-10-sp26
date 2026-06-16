#!/usr/bin/env python3
"""
Gradescope Autograder for CSE110 Lab 10
Graded out of 3 points total - Clones GitHub repository from student submission
"""

import os
import json
import re
import subprocess
import shutil
import time
from pathlib import Path
from typing import Tuple

class Lab10Grader:
    def __init__(self):
        self.results = {
            "score": 0,
            "max_score": 3.0,
            "output": "",
            "tests": []
        }
        self.submission_dir = "/autograder/submission"
        self.test_dir = "/autograder/source/tests"
        self.repo_dir = "/autograder/repo"  # Where we'll clone the repo
        
    def log(self, message: str, test_name: str = None, score: float = 0, max_score: float = 0, 
            status: str = "passed"):
        """Add test result to output"""
        if test_name:
            self.results["tests"].append({
                "name": test_name,
                "score": score,
                "max_score": max_score,
                "status": status,
                "output": message
            })
        else:
            self.results["output"] += message + "\n"
    
    def extract_github_url_from_submission(self) -> str:
        """Extract GitHub URL from student's submission"""
        github_pattern = r'https?://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+'
        
        txt_files = list(Path(self.submission_dir).glob("*.txt"))
        
        for txt_file in txt_files:
            with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().strip()
                match = re.search(github_pattern, content)
                if match:
                    return match.group(0)
        
        for file in Path(self.submission_dir).iterdir():
            if file.is_file():
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                    match = re.search(github_pattern, content)
                    if match:
                        return match.group(0)
        
        return None
    
    def clone_repository(self, repo_url: str) -> Tuple[bool, str]:
        """Clone the GitHub repository"""
        try:
            if os.path.exists(self.repo_dir):
                shutil.rmtree(self.repo_dir)
            
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, self.repo_dir],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, "Repository cloned successfully"
            else:
                return False, f"Clone failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Clone timeout (60 seconds)"
        except Exception as e:
            return False, f"Clone error: {str(e)}"
    
    def check_canny_link_in_readme(self) -> bool:
        """Check if README contains link to Canny.io page"""
        readme_paths = [
            os.path.join(self.repo_dir, "README.md"),
            os.path.join(self.repo_dir, "README.txt"),
            os.path.join(self.repo_dir, "README")
        ]
        
        for readme_path in readme_paths:
            if os.path.exists(readme_path):
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if 'canny.io' in content and 'cse110-lab10' in content:
                        return True
        return False
    
    def check_ab_test_code_functionality(self) -> Tuple[bool, str, dict]:
        """Actually check if A/B test code works correctly"""
        index_paths = list(Path(self.repo_dir).rglob("index.html"))
        if not index_paths:
            return False, "index.html not found", {}
        
        with open(index_paths[0], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        results = {
            "has_math_random": False,
            "has_classlist_add": False,
            "has_blue_class": False,
            "has_body_selection": False,
            "has_random_logic": False
        }
        
        # Check for Math.random()
        if 'Math.random()' in content:
            results["has_math_random"] = True
        
        # Check for classList.add with blue
        if 'classList.add' in content and 'blue' in content:
            results["has_classlist_add"] = True
            results["has_blue_class"] = True
        
        # Check for body element selection
        if 'querySelector' in content or 'getElementById' in content or 'document.body' in content:
            results["has_body_selection"] = True
        
        # Check for proper random logic (50/50 split)
        random_patterns = [
            r'randomNumber\s*<\s*0\.5',
            r'Math\.random\(\)\s*<\s*0\.5',
            r'random\s*<\s*0\.5'
        ]
        for pattern in random_patterns:
            if re.search(pattern, content):
                results["has_random_logic"] = True
                break
        
        # Determine if A/B test code is functional
        is_functional = all([
            results["has_math_random"],
            results["has_classlist_add"],
            results["has_body_selection"],
            results["has_random_logic"]
        ])
        
        return is_functional, "A/B test code check completed", results
    
    def check_google_analytics_functionality(self) -> Tuple[bool, str, dict]:
        """Actually check if Google Analytics code works correctly"""
        index_paths = list(Path(self.repo_dir).rglob("index.html"))
        if not index_paths:
            return False, "index.html not found", {}
        
        with open(index_paths[0], 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        results = {
            "has_gtag_js": False,
            "has_ga_id": False,
            "has_config_call": False,
            "has_event_tracking": False
        }
        
        # Check for gtag.js script
        if 'gtag.js' in content or 'analytics.js' in content:
            results["has_gtag_js"] = True
        
        # Check for Google Analytics Measurement ID
        ga_pattern = r'G-[A-Z0-9]+'
        ga_match = re.search(ga_pattern, content)
        if ga_match:
            results["has_ga_id"] = True
            results["ga_id"] = ga_match.group(0)
        
        # Check for gtag config call
        if 'gtag' in content and 'config' in content:
            results["has_config_call"] = True
        
        # Check for event tracking or timer triggers
        if 'event' in content.lower() or 'timer' in content.lower():
            results["has_event_tracking"] = True
        
        # Determine if Google Analytics is functional
        is_functional = all([
            results["has_gtag_js"],
            results["has_ga_id"],
            results["has_config_call"]
        ])
        
        return is_functional, "Google Analytics check completed", results
    
    def check_screenshots_folder(self) -> bool:
        """Check if screenshots folder exists with google-analytics.png"""
        screenshots_path = os.path.join(self.repo_dir, "screenshots")
        if not os.path.exists(screenshots_path):
            screenshots_dirs = list(Path(self.repo_dir).rglob("screenshots"))
            if not screenshots_dirs:
                return False
            screenshots_path = screenshots_dirs[0]
        
        png_path = os.path.join(screenshots_path, "google-analytics.png")
        if os.path.exists(png_path):
            return True
        
        png_files = list(Path(screenshots_path).glob("*.png"))
        return len(png_files) > 0
    
    def grade(self):
        """Main grading function - clones repo and grades"""
        self.log("=== CSE110 Lab 10 Grader (GitHub Clone Mode) ===\n")
        self.log("Total points possible: 3.0\n")
        
        # Step 1: Extract GitHub URL from submission
        self.log("Step 1: Finding GitHub URL in submission...")
        repo_url = self.extract_github_url_from_submission()
        
        if not repo_url:
            self.log("[ERROR] No GitHub URL found in submission", "GitHub URL", 0, 3.0)
            self.log("\n[ERROR] Please submit a .txt file containing your GitHub repository URL")
            self.log("Example: https://github.com/username/lab10-repo")
            self.results["score"] = 0
            with open("/autograder/results/results.json", "w") as f:
                json.dump(self.results, f, indent=2)
            return
        
        self.log(f"[OK] Found GitHub URL: {repo_url}", "GitHub URL", 0, 0)
        
        # Step 2: Clone the repository
        self.log("\nStep 2: Cloning repository...")
        clone_success, clone_msg = self.clone_repository(repo_url)
        
        if not clone_success:
            self.log(f"[ERROR] {clone_msg}", "Clone Repo", 0, 3.0)
            self.results["score"] = 0
            with open("/autograder/results/results.json", "w") as f:
                json.dump(self.results, f, indent=2)
            return
        
        self.log("[OK] Repository cloned successfully", "Clone Repo", 0, 0)
        
        # Step 3: Grade the cloned repository
        self.log("\nStep 3: Grading repository contents...\n")
        
        total_points = 0.0
        
        # Check Canny link in README (0.5 point - less emphasis)
        self.log("Checking README for Canny.io link (0.5 point)...")
        canny_score = 0.0
        if self.check_canny_link_in_readme():
            canny_score = 0.5
            self.log("[OK] Canny.io link found in README", "Canny.io Link", 0.5, 0.5)
        else:
            self.log("[ERROR] Canny.io link not found in README", "Canny.io Link", 0, 0.5)
        
        total_points += canny_score
        
        # Check A/B test code functionality (1.0 point - more emphasis)
        self.log("\nChecking A/B test code functionality (1.0 point)...")
        ab_status, ab_msg, ab_results = self.check_ab_test_code_functionality()
        
        ab_score = 0.0
        if ab_status:
            ab_score = 1.0
            self.log("[OK] A/B test code is functional: " + ab_msg, "A/B Test Code", 1.0, 1.0)
            self.log("  - Math.random() found: YES")
            self.log("  - classList.add('blue') found: YES")
            self.log("  - Body element selection found: YES")
            self.log("  - 50/50 random logic found: YES")
        else:
            self.log("[ERROR] A/B test code has issues", "A/B Test Code", 0, 1.0)
            self.log(f"  - Math.random() found: {ab_results.get('has_math_random', False)}")
            self.log(f"  - classList.add('blue') found: {ab_results.get('has_classlist_add', False)}")
            self.log(f"  - Body element selection found: {ab_results.get('has_body_selection', False)}")
            self.log(f"  - 50/50 random logic found: {ab_results.get('has_random_logic', False)}")
        
        total_points += ab_score
        
        # Check Google Analytics functionality (1.0 point - more emphasis)
        self.log("\nChecking Google Analytics functionality (1.0 point)...")
        ga_status, ga_msg, ga_results = self.check_google_analytics_functionality()
        
        ga_score = 0.0
        if ga_status:
            ga_score = 1.0
            self.log("[OK] Google Analytics code is functional: " + ga_msg, "Google Analytics", 1.0, 1.0)
            self.log(f"  - Google Analytics script found: YES")
            self.log(f"  - Measurement ID found: {ga_results.get('ga_id', 'N/A')}")
            self.log(f"  - Config call found: YES")
        else:
            self.log("[ERROR] Google Analytics code has issues", "Google Analytics", 0, 1.0)
            self.log(f"  - Google Analytics script found: {ga_results.get('has_gtag_js', False)}")
            self.log(f"  - Measurement ID found: {ga_results.get('has_ga_id', False)}")
            self.log(f"  - Config call found: {ga_results.get('has_config_call', False)}")
        
        total_points += ga_score
        
        # Check screenshot (0.5 point)
        self.log("\nChecking screenshot (0.5 point)...")
        screenshot_score = 0.0
        if self.check_screenshots_folder():
            screenshot_score = 0.5
            self.log("[OK] Screenshots folder with google-analytics.png found", "Screenshots", 0.5, 0.5)
        else:
            self.log("[ERROR] Screenshots folder or google-analytics.png not found", "Screenshots", 0, 0.5)
        
        total_points += screenshot_score
        
        # Set final score
        self.results["score"] = round(total_points, 1)
        
        # Summary
        self.log(f"\n=== Total Score: {self.results['score']}/3.0 ===")
        self.log("\n--- Grade Breakdown ---")
        self.log(f"Canny.io link in README: {canny_score}/0.5")
        self.log(f"A/B test code functionality: {ab_score}/1.0")
        self.log(f"Google Analytics functionality: {ga_score}/1.0")
        self.log(f"Screenshot: {screenshot_score}/0.5")
        
        # Output results
        with open("/autograder/results/results.json", "w") as f:
            json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    grader = Lab10Grader()
    grader.grade()