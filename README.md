# Instagram Reel Scraper with Excel Input

This script reads usernames and target post links from an Excel file, scrapes the posts for those usernames, matches them with the provided links, and outputs the matched data in JSON format.

## Features

- **Excel Input**: Reads from an Excel file with `username` and `post_link` columns
- **Concurrent Scraping**: Uses multiple workers to scrape accounts efficiently
- **Smart Matching**: Matches scraped posts with target links based on shortcode
- **JSON Output**: Saves matched data in structured JSON format
- **Error Handling**: Robust error handling and logging

## Input Format

Create an Excel file (`input.xlsx`) with the following columns:

| username | post_link |
|----------|-----------|
| nasa | https://www.instagram.com/reel/C8X9Y2Z1ABC/ |
| nasa | https://www.instagram.com/reel/C8X9Y2Z1DEF/ |
| user123 | https://www.instagram.com/p/C8X9Y2Z1GHI/ |

### Column Requirements:
- **username**: Instagram username (without @ symbol)
- **post_link**: Full Instagram post/reel URL

## Output Format

The script generates a JSON file (`matched_posts.json`) with the following structure:

```json
[
  {
    "username": "nasa",
    "target_link": "https://www.instagram.com/reel/C8X9Y2Z1ABC/",
    "matched_post_data": {
      "url": "https://www.instagram.com/reel/C8X9Y2Z1ABC/",
      "shortcode": "C8X9Y2Z1ABC",
      "likes": 1500,
      "comments": 250,
      "views": 50000,
      "posted_time": 1640995200,
      "video_duration": 30.5,
      "dimensions": {
        "width": 1080,
        "height": 1920
      },
      "numbers_of_qualities": 3
    }
  }
]
```

## Usage

1. **Prepare your Excel file** with the required columns
2. **Update the file path** in the script:
   ```python
   excel_file_path = "your_input_file.xlsx"
   ```
3. **Run the script**:
   ```bash
   python bulk_main.py
   ```

## Configuration

You can modify these parameters in the script:

- `max_posts_per_profile`: Maximum posts to scrape per user (default: 10)
- `max_workers`: Number of concurrent workers (default: 5)
- `timeout`: Request timeout in seconds (default: 30)

## Dependencies

Make sure you have the following packages installed:
```bash
pip install pandas openpyxl reelscraper
```

## Notes

- The script creates a temporary `temp_accounts.txt` file during execution
- Only posts that match the target links will be included in the output
- If a target link doesn't match any scraped posts, it won't appear in the results
- The script supports both `/reel/` and `/p/` URL formats

## Error Handling

The script includes comprehensive error handling for:
- Missing or invalid Excel files
- Missing required columns
- Network errors during scraping
- Invalid URLs or shortcodes
- File I/O errors

## Example Output

```
📊 Loaded 3 rows from input.xlsx
📋 Processing 3 valid rows
👥 Found 2 unique usernames
🚀 Starting to scrape accounts...
📹 Scraped 15 total reels
🔍 Processing 8 reels for nasa
🔍 Looking for 2 target shortcodes: ['C8X9Y2Z1ABC', 'C8X9Y2Z1DEF']
✅ Matched: C8X9Y2Z1ABC for user nasa
✅ Matched: C8X9Y2Z1DEF for user nasa
🔍 Processing 7 reels for namanhsuit
🔍 Looking for 1 target shortcodes: ['C8X9Y2Z1GHI']
✅ Matched: C8X9Y2Z1GHI for user namanhsuit
✅ Total matched posts: 3
💾 Results saved to matched_posts.json

📊 Summary:
Total matched posts: 3
Users with matched posts: 2
  - nasa: 2 posts
  - namanhsuit: 1 posts
``` 