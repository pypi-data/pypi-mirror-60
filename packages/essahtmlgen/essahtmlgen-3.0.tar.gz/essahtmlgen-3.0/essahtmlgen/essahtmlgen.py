""" Generate essa html assignments """

import argparse
import sys
import textwrap
import time
import os
from pathlib import Path
import shutil

PART_HTML='''\
    <p><li><a href="CIS_457/html/{partfile}">Part {part}</a></li></p>'''

INDEX_HTML='''\
<html>
<div style="width:auto">
<head>
<title> CIS 457 Assignment {assignment}</title>
    <center>
        <p><img src="CIS_457/html/images/CSU_Logo.jpg"width="11%"height="20%"></p>
        <p><h1>EECS Department</h1></p>
        <p><h1>CIS 457 Computer Graphics </h1></p>
        <p><h2>Assignment {assignment}</h2></p>
        <p><h2>{date}</h2></p>
        <p><h2>{name} / {studentid}</h2></p>
    </center>
</head>
<body>

<h3>
    <ul>
        {parts}
    </ul>                                   
</h3>

</div>
</body>
</html>'''

EMBEDDED_CODE='''\
{source_file}
</br>
<pre class="prettyprint">
        {source_code}
</pre>
</br></br></br>
'''

EMBEDDED_PART_HTML='''\
<html>
<head>
<title>Part {part}</title>
    <script src="https://cdn.jsdelivr.net/gh/google/code-prettify@master/loader/run_prettify.js"></script>
</head>

<body>
    <h4>Part {part}</h4>
            <p><h5>Source Code Below</h5></a></p>
            {code}
    </br></br></br>
</body>

</html>'''

REGULAR_PART_HTML='''\
<html>
    <head>
        <title>Part {part}</title>
    </head>

<body>
    <h4>Part {part}</h4>
    </br></br></br>
    <p><h5>Put Your Part Contents Below</h5></a></p>
</body>

</html>'''

def run(sysargs=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--name',
        help='Your Name',
        type=str,
        required=True
    )

    parser.add_argument(
        '--id',
        help='Your Student Id',
        type=int,
        required=True
    )

    parser.add_argument(
        '--parts',
        help='# Of Parts',
        type=int,
        required=True
    )

    parser.add_argument(
        '--assignment',
        help='Assignment #',
        type=int,
        required=True
    )

    parser.add_argument(
        '--embed',
        nargs='+',
        required=False,
        help='Embed source code in files with #:FILES (seperated by commas, parts by spaces)',
        metavar='PART:FILE1,FILE2,...',
        default=[]
    )

    parser.add_argument(
        '--dest',
        type=str,
        help='Output directory',
        default=os.getcwd(),
        required=False
    )

    args = parser.parse_args()

    name = args.name.strip()
    parts = args.parts
    embeds = {}
    for embed in args.embed:
        embeds[int(embed.split(':')[0])] = embed.split(':')[1].split(',')
    studentid = args.id
    assignment = args.assignment
    dest = args.dest
    date = time.strftime('%m/%d/%Y', time.localtime(time.time()))

    process(name, studentid, assignment, date, parts, embeds, dest)


def process(name, studentid, assignment, date, parts, embeds, dest):
    # Create project directory or clobber another
    root = Path(dest).absolute().joinpath('Assignment' + str(assignment))
    packagedir = Path(__file__).absolute().parent
    root.mkdir(exist_ok=True)
    parts_list = []
    
    for part in range(1, parts + 1):
        parts_list.append(PART_HTML.format(partfile='Part' + str(part) + '.html', part=str(part)))

    # Create index.html
    with open(root.joinpath('index.html').absolute(), 'w') as index:
        index.write(INDEX_HTML.format(assignment=assignment,
                                      name=name,
                                      studentid=studentid,
                                      date=date,
                                      parts=''.join(parts_list)))

    cis_folder = root.joinpath('CIS_457')
    cis_folder.mkdir(exist_ok=True)
    html_folder = cis_folder.joinpath('html')
    html_folder.mkdir(exist_ok=True)
    images = html_folder.joinpath('images')
    images.mkdir(exist_ok=True)
    shutil.copy2(packagedir.joinpath('data').joinpath('CSU_Logo.jpg'), images)
    
    for part in range(1, parts + 1):
        sources = []
        data = ''
        if embeds.get(part, 'none') != 'none':
            for source_file in embeds[part]:
                with open(Path(source_file).absolute(), 'r') as code:
                    fname = Path(source_file).name
                    sources.append(EMBEDDED_CODE.format(source_code=code.read(), source_file=fname))
            data = EMBEDDED_PART_HTML.format(part=part, code='\n\n'.join(sources))
            del sources
        else:
            data = REGULAR_PART_HTML.format(part=part)
        
        with open(html_folder.joinpath('Part' + str(part) + '.html').absolute(), 'w') as fd:
            fd.write(data)


def main():
    sys.exit(run())

if __name__ == '__main__':
    main()