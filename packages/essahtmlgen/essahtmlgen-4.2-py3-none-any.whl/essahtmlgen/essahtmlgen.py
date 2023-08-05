""" Generate essa html assignments """

import argparse
import sys
import textwrap
import time
import os
from pathlib import Path
import shutil

PART_HTML='''\
    <p><li><a href="CIS_457/html/{partfile}">{partname}</a></li></p>'''

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
        <p><h2>{name} {studentid}</h2></p>
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

SOURCE_CODE_HTML='''\
    {name}
    </br></br>
    <pre class="prettyprint">
        {data}
    </pre>
    </br></br>
'''

TEXT_HTML='''\
    </br></br>
    <p>
    {data}
    </p>
    </br></br>
'''

IMAGE_HTML='''\
    </br></br>
    <p>
        <img src="images/{name}">
    </p>
'''

PART_ENTITY='''\
    {data}
'''

PART_START_HTML='''\
<html>
    <head>
        <title>{name}</title>
        <script src="https://cdn.jsdelivr.net/gh/google/code-prettify@master/loader/run_prettify.js"></script>
    </head>

<body>
    <h4>{name}</h4>
'''

PART_END_HTML='''\
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
        '--studentid',
        help='Your Student Id',
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
        '--parts',
        help='Number of parts',
        type=int,
        required=True
    )

    parser.add_argument(
        '--source',
        type=str,
        required=False,
        help='Directory filed with part subdirectories filled with (.txt for desc, .jpg/.png for images, .java for source code)',
    )

    parser.add_argument(
        '--destination',
        type=str,
        help='Output directory',
        default=os.getcwd(),
        required=False
    )

    args = parser.parse_args()

    name = args.name.strip()
    parts = args.parts
    studentid = args.studentid
    assignment = args.assignment
    date = time.strftime('%m/%d/%Y', time.localtime(time.time()))
    source = ''
    destination = ''

    try:
        destination = Path(args.destination).resolve().absolute()
        if args.source:
            source = Path(args.source).resolve().absolute()
    except Exception as e:
        sys.stderr.write('Invalid Source or Destination Directory')
        sys.exit(1)

    return process(name, studentid, assignment, date, parts, destination, source)


def process(name, studentid, assignment, date, parts, destination, source):
    # Create project directory or clobber another
    print('Creating Directories...')
    root = destination.joinpath('Assignment' + str(assignment))
    packagedir = Path(__file__).absolute().parent
    root.mkdir(exist_ok=True)
    cis_folder = root.joinpath('CIS_457')
    cis_folder.mkdir(exist_ok=True)
    html_folder = cis_folder.joinpath('html')
    html_folder.mkdir(exist_ok=True)
    images = html_folder.joinpath('images')
    images.mkdir(exist_ok=True)
    shutil.copy2(packagedir.joinpath('data').joinpath('CSU_Logo.jpg'), images)

    entity_list = []
    parts_list = []
    index_parts = []

    # If there are source files parse those
    if source:
        for path in source.iterdir():
            if not path.name.startswith('.'):
                parts_list.append(path.absolute())

        # Get part vars
        for part in parts_list:
            partname = part.name
            partfile = partname + '.html'
            print('Creating: ' + partfile)
            index_parts.append(PART_HTML.format(partfile=partfile, partname=partname))

        # Create index.html
        with open(root.joinpath('index.html').absolute(), 'w') as index:
            print('Creating: index.html')
            index.write(INDEX_HTML.format(assignment=assignment,
                                          name=name,
                                          studentid=studentid,
                                          date=date,
                                          parts=''.join(index_parts)))

        # Go through each part directory in parts_list and extract contents, turning them into what we need
        for part in parts_list:
            part_items = []
            for htmlentity in part.iterdir():
                if htmlentity.suffix == '.txt':
                    part_items.append(TEXT_HTML.format(data=open_and_read(htmlentity)))
                elif htmlentity.suffix == '.java':
                    part_items.append(SOURCE_CODE_HTML.format(data=open_and_read(htmlentity), name=htmlentity.name))
                elif htmlentity.suffix == '.png' or htmlentity.suffix == '.jpg' or htmlentity.suffix == '.jpeg':
                    part_items.append(IMAGE_HTML.format(name=htmlentity.name))
                    shutil.copy2(htmlentity, images)
                else:
                    pass

            with open(str(html_folder.joinpath(part.name)) + '.html', 'w') as html:
                html.write(PART_START_HTML.format(name=part.name))
                for item in part_items:
                    html.write(PART_ENTITY.format(data=item))
                html.write(PART_END_HTML)

            del part_items
    else:
        # Get part vars
        for part in range(1, parts + 1):
            partfile = 'Part' + str(part) + '.html'
            partname = 'Part' + str(part)
            index_parts.append(PART_HTML.format(partfile=partfile, partname=partname))

        # Create index.html
        with open(root.joinpath('index.html').absolute(), 'w') as index:
            index.write(INDEX_HTML.format(assignment=assignment,
                                          name=name,
                                          studentid=studentid,
                                          date=date,
                                          parts=''.join(index_parts)))

         # Go through each part directory in parts_list and extract contents, turning them into what we need
        for part in range(1, parts + 1):
            partname = 'Part' + str(part)
            with open(str(html_folder.joinpath(partname)) + '.html', 'w') as html:
                html.write(PART_START_HTML.format(name=partname))
                html.write(PART_END_HTML)

    print('Done Processing!')
    return 0


def open_and_read(filename):
    with open(filename, 'r') as fd:
        return fd.read()

def main():
    sys.exit(run())

if __name__ == '__main__':
    main()