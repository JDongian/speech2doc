#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-
# Copyright 2019 Joshua Dong
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
"""Example to convert audio URI to polished transcript file.

The basic program idea is to convert the audio to a JSON transcript.
Then, using a templater, create a simple markdown file.
Finally, use pandoc to convert the markdown file to a docx.
"""
from argparse import ArgumentParser
import re
import os
import json
import logging
from time import sleep
from rev_ai.apiclient import RevAiAPIClient
from rev_ai.models.job_status import JobStatus
import jinja2
import pypandoc

API_KEY = os.environ.get('REVAI_API_KEY')


def _init_args():
    parser = ArgumentParser(description="Invert text normalization.")
    parser.add_argument(
        'input',
        type=str,
        help="Provide a URI to transcribe."
    )
    parser.add_argument(
        '-o', metavar="output",
        type=str,
        default="output.doc",
        help="Provide a file which to output to."
    )
    parser.add_argument(
        '--api_key',
        type=str,
        default=API_KEY,
        help="Provide Rev.ai API key."
    )
    args = parser.parse_args()
    return args


def wait_for(client, job):
    status = JobStatus.IN_PROGRESS
    while status == JobStatus.IN_PROGRESS:
        sleep(7)
        status = client.get_job_details(job.id).status


def _main(args):
    # create your client
    client = RevAiAPIClient(args.api_key)

    # or send a link to the file you want transcribed
    job = client.submit_job_url(args.input)

    wait_for(client, job)

    transcript = client.get_transcript_json(job.id)

    with open('transcript.json', 'w') as fp:
        json.dump(transcript, fp)

    render_md('transcript.json', 'transcript.md')

    produce_docx('transcript.md', args.o)


def _main2(key, job_id):
    # create your client
    client = RevAiAPIClient(key)

    transcript = client.get_transcript_json(job_id)

    with open('transcript.json', 'w') as fp:
        json.dump(transcript, fp)


def _escape_latex(text):
    return re.sub("(?=_|&|{|}|%|#|\$)", r"\\", text)


def render_md(f_in, f_out):
    with open(f_in, 'r') as fp:
        transcript = json.load(fp)

    monologues = transcript['monologues']
    texts = [
        (f"<b>Speaker {m['speaker']}:</b>\t"
         f"{''.join(e['value'] for e in m['elements'])}")
        for m in monologues
    ]

    md_jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    template = md_jinja_env.get_template('template.md')

    result = template.render(
        texts=texts
    )

    with open(f_out, 'w') as f:
        f.write(result)


def render_latex(f_in, f_out):
    """Unused because latex->docx is difficult.
    """
    with open(f_in, 'r') as fp:
        transcript = json.load(fp)

    monologues = transcript['monologues']
    speakers = [m['speaker'] for m in monologues]
    texts = [
        _escape_latex(''.join(e['value'] for e in m['elements']))
        for m in monologues
    ]

    latex_jinja_env = jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.abspath('.'))
    )
    template = latex_jinja_env.get_template('template.tex')

    result = template.render(
        speaker_set=sorted(set(speakers)),
        data=zip(speakers, texts)
    )

    with open(f_out, 'w') as f:
        f.write(result)


def produce_docx(md_in, docx_out):
    """Use pandoc to convert markdown to docx."""
    output = pypandoc.convert_file(md_in, 'docx', outputfile=docx_out)


if __name__ == "__main__":
    ARGS = _init_args()
    logging.basicConfig(level=logging.INFO,
        format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
    _main(ARGS)
    # render('transcript.json', 'transcript.tex')
