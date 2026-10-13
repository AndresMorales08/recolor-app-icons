# Recolor App Icons 🎨

![Recolor App Icons](https://img.shields.io/badge/version-1.0.0-blue.svg) ![Python](https://img.shields.io/badge/python-3.8%2B-green.svg) ![License](https://img.shields.io/badge/license-MIT-yellow.svg)

Welcome to the **Recolor App Icons** repository! This Python script allows you to batch recolor application icons into a minimalist, posterized style with a specific base hue. Whether you're a developer looking to enhance your app's aesthetic or just someone who enjoys customizing visuals, this tool is designed to make the process easy and efficient.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Supported Formats](#supported-formats)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Batch Processing**: Process multiple icons at once, saving you time.
- **Image Manipulation**: Utilize the powerful Pillow library for image processing.
- **Posterization**: Create visually appealing, posterized icons.
- **Multiple Formats**: Support for PNG and WEBP formats.
- **Customizable Colors**: Choose your base color for recoloring.

## Installation

To get started, you need to have Python installed on your machine. You can download Python from [python.org](https://www.python.org/downloads/).

1. Clone the repository:

   ```bash
   git clone https://github.com/AndresMorales08/recolor-app-icons.git
   cd recolor-app-icons
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Download the latest release of the script from the [Releases section](https://github.com/AndresMorales08/recolor-app-icons/releases). You will need to download the appropriate file and execute it.

## Usage

After installation, you can use the script to recolor your icons. Here’s how:

1. Place your icons in a designated folder.
2. Open a terminal and navigate to the script's directory.
3. Run the script with the following command:

   ```bash
   python recolor.py --input <path_to_your_icons> --output <path_to_save_recolored_icons> --color <base_color>
   ```

   Replace `<path_to_your_icons>` with the folder containing your icons, `<path_to_save_recolored_icons>` with the desired output folder, and `<base_color>` with the color you want to apply.

### Example

```bash
python recolor.py --input ./icons --output ./recolored_icons --color "#FF5733"
```

This command will take all icons from the `icons` folder, recolor them with the specified base color, and save them to the `recolored_icons` folder.

## Supported Formats

The script supports the following image formats:

- PNG
- WEBP

Make sure your icons are in one of these formats for optimal results.

## Contributing

We welcome contributions to the Recolor App Icons project! If you have ideas for new features, bug fixes, or improvements, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Make your changes and commit them.
4. Push to your forked repository.
5. Submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or suggestions, feel free to reach out:

- GitHub: [AndresMorales08](https://github.com/AndresMorales08)
- Email: andres.morales@example.com

## Explore More

You can find more information and updates in the [Releases section](https://github.com/AndresMorales08/recolor-app-icons/releases). 

![Icon Example](https://example.com/icon-sample.png)

Thank you for checking out Recolor App Icons! Enjoy customizing your application icons! 🎉