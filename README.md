<h1><p align = 'center'><strong> HTML-Text-Parser</strong> </p></h1>

This project is designed to extract text from documents and prepare it for processing by Large Language Models (LLM). It not only pulls text but also preserves its styles and decorations by converting everything into structured data. This approach ensures that the style information is maintained through tags or classes, helping to keep the text's original formatting and emphasis.

Handling large blocks of text directly is often impractical for LLMs, as they can struggle to process and interpret extensive, undivided text effectively. To solve this, we implement a chunking strategy where text is divided based on its styling cues, such as font size, boldness, or italics, etc. Text with larger fonts or emphasized styles is typically deemed more significant, often representing headings or subheadings, which are treated as separate chunks. This method enhances the readability and usability of the text in LLM applications.

<h2><p><b>Installation</b></p></h2>

First, clone the GitHub repository.

```zsh
git clone https://github.com/ChenTaHung/HTML-Text-Parser.git path/to/clone/the/repository # HTTPS
git cloen git@github.com:ChenTaHung/HTML-Text-Parser.git path/to/clone/the/repository # SSH
```

Then, switch to the directory where the repository has been cloned.

```python
import os
os.chdir('/path/to/the/cloned/repository')
from src.main.TextParsing.HTMLParser import HTMLParser
from src.main.TextParsing.TextChunker import TextChunker
```

<h2><p><b>Usage</b></p></h2>

**_Input a html file (.html):_**

```python
# Open the html file and read into the program
with open('data/FASB_2022_html/ASU_2022-01.html', 'r') as html_file:
    html_content = html_file.read()

# instantiate the Parser object
parser = HTMLParser(html_content)
text_info_df = parser.parse()

# Get all the text out:
allText = parser.get_text()
```

The `text_info_df` holds all the extracted text along with its styles and decorations in a structured format.

<p align = 'center'><img src = 'https://github.com/ChenTaHung/HTML-Text-Parser/blob/main/doc/images/text_info_df.png' alt = 'Image' style = 'width: 800px'/></p>


Now that we have the dataframe containing all the text segments, we can use the chunker to break the text into smaller pieces, making it more manageable for processing by the LLMs.

```python
# instantiate the Chunker object
# The constructor accepts the dataframe we parsed out as the input
chunker = TextChunker(text_info_df)

# Chunk text
result_chunks_list = chunker.chunk_text()
```


The critical step here is the `chunk_text()` function, it includes the following parameters:

```python
def chunk_text(self, 
               cutoff = 7, 
               auto_adjust_cutoff=False, 
               keep_text_only=True, 
               refine=True, 
               sel_metric='words', 
               lower_bound=100, 
               upper_bound=650
               )
```

The `chunk_text` function is designed to segment text into smaller chunks based on various criteria, making it easier for Large Language Models to process the text effectively. Here’s how you can utilize this function:

- **cutoff** (int, optional): This parameter sets the threshold for including a row in a chunk. The default value is 7.
  
- **auto_adjust_cutoff** (bool, optional): Enables automatic adjustment of the cutoff value based on the data. It is set to False by default.

- **keep_text_only** (bool, optional): If set to True, the function returns only the concatenated text of each chunk, omitting any DataFrame structure. This is the default behavior.

- **refine** (bool, optional): Activates a refinement process on the chunks using the selected metric. This is set to True by default.

- **sel_metric** (str, optional): Specifies the metric used for refining the chunks, with 'words' as the default option.

- **lower_bound** (int, optional): Sets the minimum size of a chunk when refining. The default is set at 100 words.

- **upper_bound** (int, optional): Sets the maximum size of a chunk when refining. The default is set at 650 words.

The function returns a list of chunks. These chunks are either simple concatenated `text contents` or `DataFrames`, depending on the `keep_text_only` parameter. This function is essential for preparing large texts in a format that is more manageable for LLMs to process.

<h2><p><b>Environment</b></p></h2>

```bash
OS : macOS Sonoma 14.5

IDE: Visual Studio Code 

Language : Python       3.9.7 
    - numpy             1.20.3
    - numpydoc          1.1.0
    - pandas            1.5.3
    - regex             2021.8.3
    - beautifulsoup4    4.10.0
```

<h2><p><b>Developers</b></p></h2>

Denny Chen
   -  LinkedIn Profile : https://www.linkedin.com/in/dennychen-tahung/
   -  E-Mail : denny20700@gmail.com
