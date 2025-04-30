# Brand Finder App

A Streamlit application that identifies brand names for products by matching them against a reference dataset.

## Features

- Automatically loads product reference data from 'public/products.csv'
- Upload a CSV file with product names to identify brands
- Uses exact and partial matching to find the most appropriate brand
- Provides statistics and downloadable results

## Demo

![Brand Finder App Demo](https://via.placeholder.com/800x450.png?text=Brand+Finder+App+Demo)

## Setup and Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/brand-finder-app.git
   cd brand-finder-app
   ```

2. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   streamlit run brand_finder.py
   ```

## How to Use

1. Ensure your products.csv file is in the 'public' folder
2. Upload your CSV file with product names 
3. Select the appropriate columns
4. Click 'Find Brands' to process the data
5. Download the resulting CSV with brand information

## Algorithm

The app uses multiple matching techniques to identify brands:

1. **Exact Matching**: First tries to find exact matches between product names
2. **Partial Matching**: Searches for brand names contained within product names
3. **Similarity Matching**: Checks for similar product names in the reference data

## File Structure

```
brand-finder-app/
├── brand_finder.py        # The main Streamlit application
├── public/
│   └── products.csv       # Reference dataset with product and brand information
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Requirements

- Python 3.7+
- Streamlit
- Pandas

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).