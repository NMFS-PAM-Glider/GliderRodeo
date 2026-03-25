# Interactive Workflow Survey System

> A template for creating interactive workflow diagrams with embedded survey functionality. Click on shapes to track status, progress, and updates over time.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![R](https://img.shields.io/badge/R-4.0%2B-blue.svg)
![Quarto](https://img.shields.io/badge/Quarto-1.3%2B-blue.svg)

## 🎯 Overview

This system allows you to:
- ✅ Create interactive workflow diagrams
- ✅ Click shapes to fill out surveys
- ✅ Track changes over time with automatic logging
- ✅ Export data as CSV for version control
- ✅ Pre-fill forms with previous responses for easy editing
- ✅ Password-protect survey submissions

Perfect for tracking project status, workflow documentation, and iterative process improvement!

## 🚀 Quick Start

### Prerequisites

- R (4.0+)
- RStudio
- Quarto (1.3+)
- A workflow diagram from [diagrams.net](https://app.diagrams.net/)

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/YOUR_ORG/PAM-OpenScience.git
   cd PAM-OpenScience
   ```

2. **Copy your diagram:**
   - Export your diagram from diagrams.net as SVG
   - Place it in the `output/` folder

3. **Configure settings:**
   - Open `workflow-survey-system.qmd`
   - Edit the configuration in the R setup chunk:
   ```r
   SURVEY_PASSWORD <- "your_password"
   DIAGRAM_FILE <- "your_diagram.svg"
   ```

4. **Add survey links to your diagram:**
   - See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for detailed instructions
   - Use the R function for automatic link generation:
   ```r
   source("add_survey_links.R")
   add_survey_links_to_svg("output/your_diagram.svg")
   ```

5. **Render and preview:**
   ```bash
   quarto preview workflow-survey-system.qmd
   ```

## 📚 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Comprehensive setup and customization guide
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick reference for adding survey links
- **[add_survey_links.R](add_survey_links.R)** - R function documentation

## 🎨 Features

### Interactive Diagram
- Pan and zoom with mouse
- Click and drag to navigate
- Scroll wheel to zoom in/out
- Reset view button

### Survey System
- Sliding panel interface
- Password-protected submissions
- Pre-filled forms for editing
- Complete response history
- Timestamp and user tracking

### Data Management
- Browser localStorage for persistence
- CSV export for version control
- Easy GitHub integration
- No backend server required

## 📖 How to Use

### For Users

1. **View your workflow diagram**
2. **Click on any shape** to open the survey panel
3. **Review previous entry** (if exists)
4. **Update responses** as needed
5. **Submit** with password
6. **Download CSV** regularly and commit to GitHub

### For Template Users

1. **Copy the template files** to your project
2. **Add your own diagram** to `output/` folder
3. **Configure password and filename** in the QMD
4. **Add survey links** to your diagram shapes
5. **Customize questions** if needed
6. **Render and deploy** to GitHub Pages

## 🔗 Adding Survey Links

### Manual Method (Recommended for <20 shapes)

In diagrams.net:
1. Select a shape
2. Right-click → Edit Link
3. Enter: `#survey:SHAPE_ID|SHAPE_NAME`
4. Example: `#survey:data_collection|Data Collection`

### Automatic Method (For >20 shapes)

```r
source("add_survey_links.R")
add_survey_links_to_svg("output/your_diagram.svg")
```

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for detailed instructions.

## 🛠️ Customization

### Change Survey Questions

Edit the form section in `workflow-survey-system.qmd`:

```html
<div class="form-group">
  <label for="question1">Your question here:</label>
  <select id="question1" required>
    <option value="">-- Select --</option>
    <option value="Option1">Option 1</option>
    <option value="Option2">Option 2</option>
  </select>
</div>
```

### Change Password

```r
SURVEY_PASSWORD <- "new_password"
```

### Add More Questions

1. Add form fields in the HTML
2. Update the JavaScript `saveResponse()` function
3. Update the CSV headers in `downloadCSV()`

See [SETUP_GUIDE.md](SETUP_GUIDE.md#customization-guide) for details.

## 📊 Data Structure

Responses are stored as CSV with this structure:

```csv
timestamp,username,shape_id,shape_text,question1,question2,question3,question4,question5
2024-02-02T10:30:00.000Z,"Alice","step_1","Data Collection","In Progress","High","No Blockers","Adequate","On Track"
```

## 🔧 Technical Stack

- **Frontend:** HTML, CSS, JavaScript
- **Diagram:** SVG from diagrams.net
- **Framework:** Quarto (R Markdown)
- **Storage:** Browser localStorage
- **Export:** CSV files
- **Hosting:** GitHub Pages
- **Version Control:** Git/GitHub

## 📁 File Structure

```
your-project/
├── workflow-survey-system.qmd    # Main Quarto document
├── add_survey_links.R            # Helper R function
├── SETUP_GUIDE.md                # Comprehensive guide
├── QUICK_REFERENCE.md            # Quick reference
├── output/
│   └── your_diagram.svg          # Your workflow diagram
├── data/                         # Downloaded CSV files
│   └── workflow_responses_YYYY-MM-DD.csv
└── _site/                        # Rendered output
    └── workflow-survey-system.html
```

## 🤝 Contributing

We welcome contributions! Here are ways you can help:

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests

## ❓ FAQ

**Q: Can multiple people use this simultaneously?**  
A: Yes! Each person's data is stored in their own browser. They download and commit CSVs separately.

**Q: Is this secure?**  
A: This uses a simple shared password and is designed for internal team use, not sensitive data requiring encryption.

**Q: What if I lose my data?**  
A: Download CSV files regularly and commit them to GitHub. This is your backup!

**Q: Can I use this without GitHub?**  
A: Yes! The system works locally. Just share CSV files manually.

**Q: How many responses can it handle?**  
A: Browser localStorage typically allows 5-10MB, which is 25,000-50,000 responses.

See [SETUP_GUIDE.md](SETUP_GUIDE.md#faq) for more questions.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Quarto](https://quarto.org/)
- Diagrams created with [diagrams.net](https://www.diagrams.net/)
- Inspired by needs for workflow tracking and documentation

## 📧 Contact

For questions or support:
- Open an issue on GitHub
- Contact: [your.email@organization.org]

## 🎓 Citation

If you use this template in your work, please cite:

```bibtex
@software{interactive_workflow_survey,
  author = {Your Name},
  title = {Interactive Workflow Survey System},
  year = {2024},
  url = {https://github.com/YOUR_ORG/PAM-OpenScience}
}
```

---

**Happy surveying! 📊✨**
