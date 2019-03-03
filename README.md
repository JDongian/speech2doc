# Speech2Doc

Convert an audio file to a transcript document. Just an example script, feel
free to modify for specific needs.

Currently produces docx, but a latex template is also provided for pdf
generation.

See https://www.rev.ai/ for more information. API key available with free
trial.

## Installation

You can use the standard command `pip install -U requirements.txt`. You will also need to [install pandoc](https://github.com/bebraw/pypandoc#installing-pandoc).


## Usage

After installing all dependencies, run:
```
REVAI_API_KEY=YOUR_API_KEY_FROM_REV.AI_HERE python test.py https://www.rev.ai/FTC_Sample_1.mp3 -o sample.docx
```

This may take a minute or two. After it finishes, open `sample.docx` with your preferred document viewer.


## License

Apache. Free to use and modify.
