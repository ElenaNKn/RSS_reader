<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h2>Description</h2>
    <p>This application is Python RSS-reader. It is implemented to read news from a given feed with prescribed arguments.</p>
    <h2>Requirements</h2>
    <p>The application requires the next Python libraries to be installed: <br><i>fpdf<br>requests<br>beautifulsoup4<br>lxml<br>jsonlines<br>python-dateutil</i></p>
    <p>Necessary libraries may be installed by entering the next command in a command line:<br><b>pip install library_name</b></p>
    <h2>Running</h2>
    <p>User can run the application from a command line (from a folder, where scripts of rss_reader are situated) in two ways:</p>
    <ul>
        <li>running the script itself <b>(if all requirements are installed)</b> by a command:<br> <b>python rss_reader.py source [--version] [--json] [--verbose] [--limit LIMIT] [--date DATE] [--html HTML] [--pdf PDF] [-h]</b><br>positional arguments:
        <dl>
            <dt>source</dt><dd><i>RSS URL</i></dd>
        </dl>
        optional arguments:
        <dl>
            <dt>--version</dt><dd><i>Print version info</i></dd>
            <dt>--json</dt><dd><i>Print result as JSON in stdout</i></dd>
            <dt>--verbose</dt><dd><i>Outputs verbose status messages</i></dd>
            <dt>--limit LIMIT</dt><dd><i>Limit news topics if this parameter provided</i></dd>
            <dt>--date DATE</dt><dd><i>Print result from a cash for a given date</i></dd>
            <dt>--html HTML</dt><dd><i>Print result to HTML file</i></dd>
            <dt>--pdf PDF</dt><dd><i>Print result to PDF file</i></dd>
            <dt>-h, --help</dt><dd><i>Show a help message and exit</i></dd>
        </dl>
        </li>
        <li>installing of application by a command:<br><b>python setup.py develop</b><br>The application may be then run by a command:<br><b>rss_reader source [--version] [--json] [--verbose] [--limit LIMIT] [--date DATE] [--html HTML] [--pdf PDF] [-h]</b>
        </li>
    </ul>
    <h3>* About a JSON structure</h3>
    <p>This application generates JSON with the next structure:<br>{"feed": "Name of sourse feed", <br> "news": [<br>{<br>"title": "title of news_1",<br>"pubdate": "publication date of a news_1",<br>"link": "sourse link for a news_1",<br>"description": "Short description of a content of a news_1"<br>},<br>{<br>"title": "title of news_2",<br>"pubdate": "publication date of a news_2",<br>"link": "sourse link for a news_2",<br>"description": "Short description of a content of a news_2"<br>},<br>...<br>]}</p>
    <h3>** About a cashed news storage structure</h3>
    <p>A cashed news storage is provided by a file <i>dates.json</i> and folders <i>cashed_feeds</i> and <i>cashed_img</i>.<br>When rss_reader is started without a --date argument, dates of publication of news are stored in the file <i>dates.json</i> together with path to file, where all news for this date are stored. All news (including title, link, date of publication, description, feed name, URL of media content, if a new has it, and path to media file in storage) are stored in the folder <i>cashed_feeds</i>. Media content of stored news is stored in the folder <i>cashed_img</i>.  Names of files in the folder <i>cashed_feeds</i> corresponds to dates of publication of news.<br>When rss_reader is started with --date argument, it reads news from the cash for entered date and source.</p>
    <h3>*** Additional remarks</h3>
    <p>A folder <i>font</i> contains a font for creating a PDF result file. A file <i>rss_downloads.html</i> contains initial template for creating a HTML result file. </p>
    <h2>Running tests</h2>
    <p>User can run tests from a command line (from a folder, where scripts of rss_reader are situated) by a command:<br> <b>python -m unittest discover</b> </p>
</body>
</html>